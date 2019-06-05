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

        data_dict = {
                    labels: line_labels,
                    datasets: [
                        {
                            "fillColor": "gradient",
                            "strokeColor": "#ff6c23",
                            "pointColor": "#fff",
                            "pointStrokeColor": "#ff6c23",
                            "pointHighlightFill": "#fff",
                            "pointHighlightStroke": "#ff6c23",
                            "data": line_values
                        }
                    ]
                };


    print("data_dict:", data_dict)

    return jsonify(data_dict)
