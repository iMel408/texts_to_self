from flask import Flask
from celery import Celery

def make_celery(app):
    celery = Celery(app.import_name)
    celery.config_from_object('texts_to_self.celery_config')

    celery.conf.update(app.config)

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery


def create_app():
    app = Flask(__name__)
    app.config.from_object('texts_to_self.config')

    @app.route('/')
    def hello():
        return 'Flask is Live!'

    from texts_to_self.model import connect_to_db, db

    connect_to_db(app)
    db.init_app(app)

    from . import tasks

    app.celery = make_celery(app)
    return app

