web: gunicorn app:app
worker: celery worker --app=app
beat: celery beat --app=app
