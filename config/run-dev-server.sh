set -e

SERVER_DIR=/Users/ace/cloudpass/code/server-side
SOCK=$SERVER_DIR/app-server.sock
WSGI=$SERVER_DIR/django/cryptoService.wsgi

mongod &
#uwsgi --socket $SOCK --module $WSGI  --chmod-socket=666 &

#uwsgi --ini django-uwsgi-dev.ini &
uwsgi --ini django-uwsgi-dev.ini 2>&1 1> /dev/null &
sudo nginx &
