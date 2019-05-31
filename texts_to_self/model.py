from datetime import datetime
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


class User(db.Model):
    """ create a user """

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    password = db.Column(db.String(120))
    created = db.Column(db.DateTime(), default=datetime.utcnow)
    updated = db.Column(db.DateTime(), default=datetime.utcnow)

    def __repr__(self):
        return f'<username: {self.username}, user_id: {self.id}>'


class Job(db.Model):
    """ setup/schedule a job associated with a user """

    __tablename__ = 'jobs'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    active = db.Column(db.Boolean, default=False)
    phone = db.Column(db.String(20), unique=True, nullable=True)
    msg_txt = db.Column(db.String(160))
    frequency = db.Column(db.String, default='daily')
    time = db.Column(db.String(5), default='12:00')
    timezone = db.Column(db.String, default='America/Los_Angeles')
    created = db.Column(db.DateTime(), default=datetime.utcnow)
    updated = db.Column(db.DateTime(), default=datetime.utcnow)

    user = db.relationship('User', backref=db.backref('jobs', order_by=id), lazy='joined')

    def __repr__(self):
        return f'<User Name: {self.user.username}, Job ID: {self.id}, Active: {self.active}>'


class Event(db.Model):
    """ run and log an instance of a job """

    __tablename__ = 'events'
    __table_args__ = (
        db.UniqueConstraint('job_id', 'date_added', name='unique_job_event_event'),
    )

    id = db.Column(db.Integer, primary_key=True)
    msg_sid = db.Column(db.String(256))
    job_id = db.Column(db.Integer, db.ForeignKey('jobs.id'))
    user_phone = db.Column(db.String(20))
    msg_type = db.Column(db.String(20))
    msg_body = db.Column(db.String(256), nullable=True)
    msg_status = db.Column(db.String(20), nullable=True)
    date_added = db.Column(db.Date(), default=datetime.utcnow)
    date_updated = db.Column(db.DateTime(), default=datetime.utcnow)

    job = db.relationship('Job', backref=db.backref('events'), lazy='joined')

    def __repr__(self):
        return f'<Phone #: {self.user_phone}, Msg Text: {self.msg_body}>'


def connect_to_db(app):
    """Connect the database to app."""

    # app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///textstoself'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql-triangular-57469'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
    app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
    db.app = app

if __name__ == "__main__":
    from app import app

    connect_to_db(app)
    print("Connected to DB.")

    db.create_all()