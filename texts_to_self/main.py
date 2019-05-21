import pytz
import datetime
from flask import Blueprint, flash, request, render_template, g, redirect, url_for
from texts_to_self.auth import login_required




from texts_to_self.model import *

bp = Blueprint('main', __name__)


# @bp.route('/user/<int:id>')
@bp.route('/')
@login_required
def user_page():
    """show user page/info. before_app_request is checking on g.user"""
    user = g.user
    active_job = Job.query.filter_by(user=user, active=True).first()

    if active_job:

        events = Event.query.filter_by(job_id=active_job.id, msg_type='inbound').order_by(Event.date_added).all()

        line_labels = []
        line_values = []

        for event in events:
            line_labels.append(event.date_added)
            line_values.append(event.msg_body)

        return render_template('main/user.html',
                               user=user,
                               job=active_job,
                               events=events,
                               title='Daily Levels',
                               max=10,
                               labels=line_labels,
                               values=line_values)

    return render_template('main/user.html', user=user)


@bp.route('/setup', methods=('GET', 'POST'))
@login_required
def setup():

    user = g.user

    tz_list = pytz.country_timezones('us')
    # tz_list = ['US/Pacific', 'US/Central', 'US/Eastern', 'US/Mountain', 'US/Hawaii', 'US/Alaska', 'US/Arizona',
    #            'US/East-Indiana', 'US/Indiana-Starke', 'US/Michigan']

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
        # active = request.form['active']
        error = None

        if not user_time:
            error = 'Time is Required!'

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
                active=True
            )
            db.session.add(new_job)
            db.session.commit()
            return redirect(url_for('main.user_page'))

    return render_template('main/setup.html', user=user, tz_list=tz_list, msg_lst=msg_lst)
