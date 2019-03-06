#!/bin/sh
set -e

if [ -n "$STARTUP_DELAY" ]; then
    echo "Sleeping $STARTUP_DELAY seconds..."
    sleep $STARTUP_DELAY
    echo "Starting..."
fi

if [ "$1" = "celery" ]; then
    exec /venv/bin/celery -A word_master worker -E -l info 2>&1
elif [ "$1" = "beat" ]; then
    exec /venv/bin/celery -A word_master beat -l info 2>&1
else
    if [ "x$DJANGO_MANAGEPY_MIGRATE" = 'xon' ]; then
        /venv/bin/python manage.py migrate --noinput
    fi

    if [ "x$DJANGO_MANAGEPY_COLLECTSTATIC" = 'xon' ]; then
        /venv/bin/python manage.py collectstatic --noinput
        if [ -d /static ]; then
            cp -r static/* /static/
        fi
    fi

    if [ -n "$ADMIN_USERNAME" -a -n "$ADMIN_PASSWORD" -a -n "$ADMIN_EMAIL" ]; then
        echo "Creating Admin user $ADMIN_USERNAME ($ADMIN_EMAIL)"
        # create super user
        echo "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.create_superuser('$ADMIN_USERNAME', '$ADMIN_EMAIL', '$ADMIN_PASSWORD')" | /venv/bin/python manage.py shell
    fi

    exec "$@"
fi
