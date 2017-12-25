#!/bin/sh
set -e

if [ -n "$STARTUP_DELAY" ]; then
    echo "Sleeping $STARTUP_DELAY seconds..."
    sleep $STARTUP_DELAY
    echo "Starting..."
fi

if [ "x$DJANGO_MANAGEPY_MIGRATE" = 'xon' ]; then
    /venv/bin/python manage.py migrate --noinput
fi

if [ "x$DJANGO_MANAGEPY_COLLECTSTATIC" = 'xon' ]; then
    /venv/bin/python manage.py collectstatic --noinput
fi

if [ -n "$ADMIN_USERNAME" -a -n "$ADMIN_PASSWORD" -a -n "$ADMIN_EMAIL" ]; then
    echo "Creating Admin user $ADMIN_USERNAME ($ADMIN_EMAIL)"
    # create super user
    echo "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.create_superuser('$ADMIN_USERNAME', '$ADMIN_EMAIL', '$ADMIN_PASSWORD')" | /venv/bin/python manage.py shell
fi
exec "$@"
