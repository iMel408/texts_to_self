from datetime import timedelta

# broker_url = 'redis://127.0.0.1:6379/0'
# result_backend = 'redis://127.0.0.1:6379/1'
broker_url = 'redis://localhost:6379'
result_backend = 'redis://localhost:6379'
beat_schedule = {
    'run_every_hour': {
        'task': 'texts_to_self.tasks.run_jobs',
        'schedule': timedelta(seconds=60)
    },
}
