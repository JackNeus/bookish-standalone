import redis
import rq
from datetime import datetime
from flask import current_app, has_app_context
from flask_login import UserMixin
from mongoengine import *
from werkzeug.security import generate_password_hash, check_password_hash

class JobEntry(Document):
    id = StringField(required = True, primary_key = True) 
    task = StringField(required = True)
    name = StringField(required = True)
    description = StringField(max_length = 128)
    user_id = StringField(required = True)
    status = StringField(required = True)
    complete = BooleanField(required = True, default = False)
    time_started = DateTimeField(required = True, default = datetime.now())
    time_finished = DateTimeField()

    def get_rq_job(self):
        if not has_app_context():
            return None
        try:   
            rq_job = rq.job.Job.fetch(self.id, connection=current_app.redis)
        except (redis.exceptions.RedisError, rq.exceptions.NoSuchJobError):
            return None
        return rq_job

    def get_status(self):
        self.update_status()
        self.save()
        return self.status

    def get_progress(self):
        job = self.get_rq_job()
        return job.meta.get('progress', 0) if job is not None else 100

    def update_status(self):
        # If in the app, do the following:
        if has_app_context():
            # If the job is Queued or Running but doesn't exist in RQ (or has failed),
            # something went wrong.
            # TODO: This isn't perfect (if you kill everything a job may still appear as "Running"),
            # but it's better than nothing.
            rq_job = self.get_rq_job()
            if self.status in ["Queued", "Running"] and (rq_job is None or rq_job.get_status() == "failed"):
                self.status = "Internal Error"

    def clean(self):
        self.update_status()
        
class User(UserMixin):
    def __init__(self, uid, username):
        self.uid = str(uid)
        self.username = username
        
    def is_authenticated(self):
        return True

    def get_id(self):
        return self.uid

class UserEntry(Document):
    username = StringField(required = True)
    name = StringField(required = True, default = "Bob")
    password_hash = StringField(required = True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        self.save()

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)