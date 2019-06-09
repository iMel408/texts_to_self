import pytz
from datetime import timedelta, date
from flask import Blueprint, flash, request, render_template, g, redirect, url_for
from texts_to_self.auth import login_required
from twilio.twiml.messaging_response import MessagingResponse


from texts_to_self.model import *

bp = Blueprint('main', __name__)


@bp.route('/')
@login_required
def user_page():
    """show user page/info. before_app_request is checking on g.user"""
    user = g.user
    user_job = Job.query.filter_by(user=user).first()
    current_time_utc = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    # start_date = datetime.today() - timedelta(days=30)
    # end_date = datetime.today()

    if user_job:

        local_job_time = datetime.now(pytz.utc).replace(hour=int(user_job.time[:2]), minute=int(user_job.time[3:4]),
                                                        second=00).astimezone(pytz.timezone(user_job.timezone)).strftime("%I:%M %p %Z")

        start_date = request.args.get("start_date", default=date.today() - timedelta(days=30))
        end_date = request.args.get("end_date", default=date.today())


        # events = Event.query.filter_by(job_id=user_job.id, msg_type='inbound').order_by(Event.date_added).all()
        events = Event.query.filter(Event.job_id==user_job.id, Event.msg_type=='inbound', Event.date_added >= start_date).order_by(Event.date_added).all()

        line_labels = []
        line_values = []
        line_comments = []

        for event in events:
            line_labels.append(event.date_added.strftime("%m-%d-%y"))
            line_values.append(event.msg_body)
            line_comments.append(event.comment)
            print("event.date_added:",event.date_added)
            print("event.date_added.strftime('%Y-%m-%d'):",event.date_added.strftime('%Y-%m-%d'))
            print("type(event.date_added):", type(event.date_added))
            print("start_date:",start_date)
            print("type(start_date):",type(start_date))
            print("end_date:",end_date)
            print("type(end_date):", type(end_date))

        return render_template('main/user.html',
                               user=user,
                               job=user_job,
                               events=events,
                               title='Daily Levels',
                               max=10,
                               labels=line_labels,
                               values=line_values,
                               comments=line_comments,
                               max_date=line_labels[-1],
                               start_date=str(start_date),
                               end_date=str(end_date),
                               current_time_utc=current_time_utc,
                               local_job_time=local_job_time)

    return render_template('main/user.html', user=user, current_time_utc=current_time_utc)


@bp.route('/setup', methods=('GET', 'POST'))
@login_required
def setup():

    user = g.user

    # tz_list = pytz.country_timezones('us')
    tz_list = ['US/Pacific', 'US/Central', 'US/Eastern', 'US/Mountain', 'US/Hawaii', 'US/Alaska', 'US/Arizona',
               'US/East-Indiana', 'US/Indiana-Starke', 'US/Michigan']

    msg_lst = ['What was your level of anxiety today? (1-10)',
               'What was your level of depression today? (1-10)',
               'What level were you at today? (1-10)']

    if request.method == 'POST':
        print(request.form)
        # for k,v in request.form:
        #     print(k,v)

        phone = request.form['phone']
        msg_txt = request.form['msg_txt']
        frequency = request.form['frequency']
        user_time = request.form['user_time']
        timezone = request.form['timezone']
        is_active = request.form['active']
        error = None

        if is_active == 'Yes':
            active = True
        else:
            active = False

        if not user_time:
            error = 'Time is Required!'

        if not phone:
            error = 'Phone Number is Required!'

        if error is not None:
            flash(error)
        else:
            new_job = Job(
                user_id=user.id,
                phone='+1'+phone.replace('-', ''),
                msg_txt=msg_txt,
                frequency=frequency.lower(),
                time=datetime.now(pytz.timezone(timezone)).replace(hour=int(user_time[:2]), minute=int(user_time[3:5]), second=00).astimezone(pytz.utc).strftime('%H:%M'),
                timezone=timezone,
                active=active
            )
            db.session.add(new_job)
            db.session.commit()
            resp = MessagingResponse()
            resp.message("Your account is now active.")
            flash('Setup Completed')
            return redirect(url_for('main.user_page'))

    return render_template('main/setup.html', user=user, tz_list=tz_list, msg_lst=msg_lst)


@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):

    user = g.user
    job_id = Job.query.get(id)
    # job_id = id
    print(job_id)

    tz_list = ['US/Pacific', 'US/Central', 'US/Eastern', 'US/Mountain', 'US/Hawaii', 'US/Alaska', 'US/Arizona',
               'US/East-Indiana', 'US/Indiana-Starke', 'US/Michigan']

    msg_lst = ['What was your level of anxiety today? (1-10)',
               'What was your level of depression today? (1-10)',
               'What level were you at today? (1-10)']

    local_job_time = datetime.now(pytz.utc).replace(hour=int(job_id.time[:2]), minute=int(job_id.time[3:4]),
                                                    second=00).astimezone(pytz.timezone(job_id.timezone)).strftime(
        "%I:%M %p")
    print("local_job_time:", local_job_time)

    if request.method == 'POST':

        phone = request.form['phone']
        msg_txt = request.form['msg_txt']
        frequency = request.form['frequency']
        user_time = request.form['user_time']
        timezone = request.form['timezone']
        active = request.form['active']
        error = None

        if not user_time:
            error = 'Time is Required!'

        if error is not None:
            flash(error)
        else:
            update_job = Job.query.get(id)
            update_job.user_id = user.id
            update_job.phone = '+1'+phone.replace('-', '')
            update_job.msg_txt = msg_txt
            update_job.frequency = frequency.lower()
            update_job.time = datetime.now(pytz.timezone(timezone)).replace(hour=int(user_time[:2]), minute=int(user_time[3:5]), second=00).astimezone(pytz.utc).strftime('%H:%M')
            update_job.timezone = timezone

            if active == 'Yes':
                update_job.active = True
            else:
                update_job.active = False

            db.session.commit()
            flash('Settings Updated')
            return redirect(url_for('main.user_page'))

    return render_template('main/update.html', user=user, tz_list=tz_list, msg_lst=msg_lst, local_job_time=local_job_time, job_id=job_id)


@bp.route('/<int:id>/edit', methods=('GET', 'POST'))
@login_required
def edit(id):

    user = g.user
    event_id = Event.query.get(id)
    print(event_id)

    if request.method == 'POST':

        date_added = request.form['date_added']
        msg_body = request.form['msg_body']
        comment = request.form['comment']
        error = None

        if not msg_body:
            error = 'Level is required.'

        if error is not None:
            flash(error)
        else:
            update_event = Event.query.get(id)
            update_event.user_id = user.id
            update_event.date_added = date_added
            update_event.msg_body = msg_body
            update_event.comment = comment

            db.session.commit()
            flash('Event has been updated')
            return redirect(url_for('main.user_page'))

    return render_template('main/edit.html', user=user, event_id=event_id)
