from flask import Blueprint, g, jsonify
from texts_to_self.model import *

bp = Blueprint('chart', __name__)

@bp.route('/event_data.json')
def event_data():
    user = g.user
    user_job = Job.query.filter_by(user=user).first()
    events = Event.query.filter_by(job_id=user_job.id, msg_type='inbound').order_by(Event.date_added).all()

    line_labels = []
    line_values = []

    for event in events:
        line_labels.append(event.date_added.strftime("%m-%d-%y"))
        line_values.append(event.msg_body)
        line_comments.append(event.comment)

    data_dict = {
                "labels": line_labels,
                "datasets": [
                    {
                        "data": [line_values,
                                line_comments]
                    }]
            }
    return jsonify(data_dict)


# @bp.route('/melon-times.json')
# def melon_times_data():
#     """Return time series data of Melon Sales."""
#
#     data_dict = {
#         "labels": ["January", "February", "March", "April", "May", "June", "July"],
#         "datasets": [
#             {
#                 "label": "Watermelon",
#                 "fill": True,
#                 "lineTension": 0.5,
#                 "backgroundColor": "rgba(220,220,220,0.2)",
#                 "borderColor": "rgba(220,220,220,1)",
#                 "borderCapStyle": 'butt',
#                 "borderDash": [],
#                 "borderDashOffset": 0.0,
#                 "borderJoinStyle": 'miter',
#                 "pointBorderColor": "rgba(220,220,220,1)",
#                 "pointBackgroundColor": "#fff",
#                 "pointBorderWidth": 1,
#                 "pointHoverRadius": 5,
#                 "pointHoverBackgroundColor": "#fff",
#                 "pointHoverBorderColor": "rgba(220,220,220,1)",
#                 "pointHoverBorderWidth": 2,
#                 "pointRadius": 3,
#                 "pointHitRadius": 10,
#                 "data": [65, 59, 80, 81, 56, 55, 40],
#                 "spanGaps": False},
#             {
#                 "label": "Cantaloupe",
#                 "fill": True,
#                 "lineTension": 0.5,
#                 "backgroundColor": "rgba(151,187,205,0.2)",
#                 "borderColor": "rgba(151,187,205,1)",
#                 "borderCapStyle": 'butt',
#                 "borderDash": [],
#                 "borderDashOffset": 0.0,
#                 "borderJoinStyle": 'miter',
#                 "pointBorderColor": "rgba(151,187,205,1)",
#                 "pointBackgroundColor": "#fff",
#                 "pointBorderWidth": 1,
#                 "pointHoverRadius": 5,
#                 "pointHoverBackgroundColor": "#fff",
#                 "pointHoverBorderColor": "rgba(151,187,205,1)",
#                 "pointHoverBorderWidth": 2,
#                 "pointHitRadius": 10,
#                 "data": [28, 48, 40, 19, 86, 27, 90],
#                 "spanGaps": False}
#         ]
#     }
#     return jsonify(data_dict)
