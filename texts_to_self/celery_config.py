import os

broker_url = os.environ.get('CELERY_BROKER_URL') or 'redis://127.0.0.1:6379/0'
result_backend = os.environ.get('CELERY_RESULT_BACKEND') or 'redis://127.0.0.1:6379/1'
