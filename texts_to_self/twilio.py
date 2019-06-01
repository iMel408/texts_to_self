from flask import Blueprint, request
from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse
from texts_to_self.model import *

bp = Blueprint('twilio', __name__)

CLIENT = Client(os.environ['TWILIO_ACCOUNT_SID'], os.environ['TWILIO_AUTH_TOKEN'])

@bp.route('/outgoing', methods=['GET', 'POST'])
# @app.route('/outgoing', methods=['GET', 'POST'])
def send_sms(to, body, job_id, from_=os.environ['FROM_PHONE']):
    """create sms event"""

    message = CLIENT.messages.create(
        to=to,
        from_=from_,
        body=body
    )

    msg_type = 'outbound'
    job_id = job_id
    msg_sid = message.sid
    user_phone = message.to
    body = message.body
    msg_body = body.replace('Sent from your Twilio trial account - ', '')
    msg_status = message.status

    new_event = Event(
        msg_type=msg_type,
        job_id=job_id,
        msg_sid=msg_sid,
        user_phone=user_phone,
        msg_body=msg_body,
        msg_status=msg_status
    )

    db.session.add(new_event)


@bp.route('/incoming', methods=['GET', 'POST'])
# @app.route("/incoming", methods=['GET', 'POST'])
def receive_reply():
    """Respond to incoming messages with a friendly SMS."""

    job = Job.query.filter_by(phone=request.values.get('From')).first()

    msg_type = 'inbound'
    job_id = job.id
    msg_sid = request.values.get('MessageSid')
    user_phone = request.values.get('From')
    msg_body = request.values.get('Body')
    msg_status = request.values.get('SmsStatus')

    existing_entry = Event.query.filter_by(job_id=job.id, date_added=datetime.utcnow().strftime("%Y-%m-%d")).first()

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
        existing_entry.msg_sid = msg_sid
        existing_entry.msg_body = msg_body
        existing_entry.date_updated = datetime.utcnow()

    db.session.commit()

    resp = MessagingResponse()
    resp.message("Your response has been logged.")

    print(resp)

    return str(resp)
