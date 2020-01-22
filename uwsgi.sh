#!/bin/bash

# make it work with uwsgi!
uwsgi --chdir=/web/htdocs/evalr/evalr \
    --module=evalr.wsgi:application \
    --master --pidfile=/tmp/uwsgi.evalr.pid \
    --socket=127.0.0.1:8002 \
    --processes=5 \
    --uid=1000 --gid=2000 \
    --harakiri=20 \
    --max-requests=5000 \
    --vacuum \
    --home=/web/htdocs/evalr/venvpython.3.6.6
#    --daemonize=/var/log/uwsgi/django-evalr-uwsgi.log
