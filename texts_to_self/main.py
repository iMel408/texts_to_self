from flask import Blueprint, render_template
from texts_to_self.auth import login_required
from texts_to_self.model import *

bp = Blueprint('main', __name__)


@bp.route('/user/<int:id>')
@login_required
def user_page(id):
    """show user page/info"""

    user = User.query.get(id)
    active_job = Job.query.filter_by(user=user, active=True).first()

    if active_job:

        events = Event.query.filter_by(job_id=active_job.id, msg_type='inbound').all()

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