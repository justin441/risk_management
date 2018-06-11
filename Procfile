web: gunicorn config.wsgi:application
worker: celery worker --app=risk_management.taskapp --loglevel=info
