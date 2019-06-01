web: gunicorn app:app
worker: celery worker --app=celery.app
beat: celery beat --app=celery.app
