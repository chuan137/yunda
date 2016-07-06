run uwsgi
uwsgi yunda_web_app_uwsgi.ini -d uwsgi.log

directly run uwsgi
uwsgi --http :8000 --pidfile /tmp/project-master.pid --wsgi-file yunda_web_app/wsgi.py

