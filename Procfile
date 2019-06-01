web: gunicorn app:app
worker: celery worker --app=celery.app
worker: celery beat --app=celery.app
