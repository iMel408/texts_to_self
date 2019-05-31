import os
import datetime
from flask import Flask, request
from celery import Celery
from texts_to_self.model import *
from twilio.twiml.messaging_response import MessagingResponse


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
    # app.config.from_object('texts_to_self.config')
    app.secret_key = os.environ['SECRET_KEY']

    # @app.route('/')
    # def hello():
    #     return 'Flask is Live!'

    from texts_to_self.model import connect_to_db, db

    connect_to_db(app)
    db.init_app(app)

    from . import main, auth

    app.register_blueprint(auth.bp)
    app.register_blueprint(main.bp)
    app.add_url_rule('/', endpoint='user')

    @app.route("/incoming", methods=['GET', 'POST'])
    def receive_reply():
        """Respond to incoming messages with a friendly SMS."""

        job = Job.query.filter_by(phone=request.values.get('From')).first()

        msg_type = 'inbound'
        job_id = job.id
        msg_sid = request.values.get('MessageSid')
        user_phone = request.values.get('From')
        msg_body = request.values.get('Body')
        msg_status = request.values.get('SmsStatus')

        existing_entry = Event.query.filter_by(job_id = job.id, date_added=datetime.utcnow().strftime("%Y-%m-%d")).first()

        print("existing_entry:", existing_entry)

        if not existing_entry:

            new_reply = Event(
                msg_type=msg_type,
                job_id=job_id,
                msg_sid=msg_sid,
                user_phone=user_phone,
                msg_body=msg_body,
                msg_status=msg_status
            )
            db.session.add(new_reply)
            db.session.commit()

        else:
            existing_entry.msg_sid=msg_sid
            existing_entry.msg_body=msg_body
            existing_entry.date_updated=datetime.utcnow()

        db.session.commit()

        resp = MessagingResponse()
        resp.message("Your response has been logged.")

        print(resp)

        return str(resp)

    from . import tasks

    app.celery = make_celery(app)
    return app

