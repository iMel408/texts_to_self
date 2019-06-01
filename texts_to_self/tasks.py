import celery
from texts_to_self.twilio_routes import *
from texts_to_self.model import *
from datetime import datetime

@celery.task()
def run_jobs():
    """send sms messages due for current hour"""

    with app.app_context():
        db.init_app(app)

    now = datetime.utcnow()
    print("Current Hour:", now.hour)
    jobs_due = Job.query.filter_by(
        time=now.hour + ':00').all()

    # jobs_due = session.query(Job).filter_by(time=str(now.hour)+':00').options(joinedload('*')).all()

    print(jobs_due)

    for job in jobs_due:

        print("User:", job.user.username, "User Phone:", job.phone, "User Msg:", job.msg_txt, "Status:", job.active)

        if job.active:
            job_id = job.id
            to = job.phone
            body = job.msg_txt

            send_sms(to, body, job_id)
            # print(to, body, job_id)
            print("Sending:", job.phone, job.msg_txt, job.id)
            # send_sms(job.phone, job.msg_txt, job.id)

    db.session.commit()
