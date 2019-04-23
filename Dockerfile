FROM python:3.6-alpine

# Copy in your requirements file
ADD django_app/requirements-py3.txt /requirements.txt

# OR, if you’re using a directory for your requirements, copy everything (comment out the above and uncomment this if so):
# ADD requirements /requirements

# Install build deps, then run `pip install`, then remove unneeded build deps all in a single step. Correct the path to your production requirements file, if needed.
RUN set -ex \
    && apk add --no-cache vim libxml2 libxslt libjpeg openjpeg tiff pcre libuuid freetype \
    && apk add --no-cache --virtual .build-deps \
            gcc \
            make \
            libc-dev \
            musl-dev \
            linux-headers \
            pcre-dev \
            postgresql-dev \
            jpeg-dev zlib-dev freetype-dev lcms2-dev openjpeg-dev tiff-dev tk-dev tcl-dev \
            libxml2-dev libxslt-dev \
    && pyvenv /venv \
    && /venv/bin/pip install -U pip \
    && LIBRARY_PATH=/lib:/usr/lib /bin/sh -c "/venv/bin/pip install --no-cache-dir -r /requirements.txt" \
    && runDeps="$( \
            scanelf --needed --nobanner --recursive /venv \
                    | awk '{ gsub(/,/, "\nso:", $2); print "so:" $2 }' \
                    | sort -u \
                    | xargs -r apk info --installed \
                    | sort -u \
    )" \
    && apk add --virtual .python-rundeps $runDeps \
    && apk del .build-deps \
    && apk add --no-cache vim

# Copy your application code to the container (make sure you create a .dockerignore file if any large files or directories should be excluded)
RUN mkdir /django_app/
WORKDIR /django_app/
ADD django_app /django_app/
ADD tools /tools/

# uWSGI will listen on this port
EXPOSE 8000

# Add any custom, static environment variables needed by Django or your settings file here:

# 数据库后端，可以使sqlite或者mysql
ENV DATABASE_BACKEND=mysql \
    MYSQL_DATABASE_NAME=word_master \
    MYSQL_HOST=172.17.0.1 \
    MYSQL_USERNAME=trent \
    MYSQL_PASSWORD=trenttrent \
    EMAIL_HOST=smtp.sina.com \
    EMAIL_PORT=25 \
    EMAIL_HOST_USER="word_master@sina.com" \
    EMAIL_HOST_PASSWORD="word_master" \
    EMAIL_FROM="word_master@sina.com" \
    WILDDOG_APP_ID="wd7515031248wztsxi" \
    WILDDOG_API_KEY="NYBxLJDMl9Pliv8GyOXWmS1eKGYNXe3IUz0RobMg"

# uWSGI configuration (customize as needed):
ENV UWSGI_VIRTUALENV=/venv UWSGI_WSGI_FILE=word_master/wsgi.py UWSGI_HTTP=:8000 UWSGI_MASTER=1 UWSGI_WORKERS=2 UWSGI_THREADS=8 UWSGI_UID=1000 UWSGI_GID=1000 UWSGI_LAZY_APPS=1 UWSGI_WSGI_ENV_BEHAVIOR=holy
ENV DJANGO_SETTINGS_MODULE=word_master.settings_prod
ENV MEDIA_ROOT=/upload
RUN mkdir /upload && chown 1000:1000 /upload
# Call collectstatic (customize the following line with the minimal environment variables needed for manage.py to run):
RUN DATABASE_URL=none /venv/bin/python manage.py collectstatic --noinput

# Start uWSGI
CMD ["/venv/bin/uwsgi", "--http-auto-chunked", "--http-keepalive"]
VOLUME [ "/upload" ]
ENTRYPOINT ["/django_app/docker-entrypoint.sh"]
