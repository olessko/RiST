release: python manage.py migrate
web: gunicorn rstt.wsgi --log-file -
worker: python manage.py qcluster
