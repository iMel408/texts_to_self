import pytz
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
    tz_list = pytz.common_timezones

    if request.method == 'POST':

        phone = request.form['phone']
        msg_txt = request.form['msg_txt']
        frequency = request.form['frequency']
        time = request.form['time']
        timezone = request.form['timezone']
        active = request.form['active']
        error = None

        if not time:
            error = 'Time is Required!'

        if error is not None:
            flash(error)
        else:
            new_job = Job(
                user_id=user.id,
                phone=phone,
                msg_txt=msg_txt,
                frequency=frequency,
                time=time,
                timezone=timezone,
                active=active
            )

            db.session.add(new_job)
            db.session.commit()
            return redirect(url_for('main.user'))

    return render_template('main/setup.html', user=user, tz_list=tz_list)
