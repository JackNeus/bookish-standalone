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
    name = StringField(required = True, unique = True)
    params = ListField(field = StringField(), default = [])
    user_id = StringField(required = True)
    status = StringField(required = True)
    complete = BooleanField(required = True, default = False)
    time_started = DateTimeField(required = True, default = datetime.now())
    time_finished = DateTimeField()

    # Generic metadata dict.
    task_metadata = DictField()

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

    def get_description(self):
        try:
            if self.task == "ucsf_api_aggregate":
                return "%d files found. (%s)" % (self.task_metadata["files_found"], ",".join(self.params))
            if self.task == "word_freq":
                seed_task_id = self.params[0]
                seed_task_name = "n/a"
                seed_task = JobEntry.objects(id=seed_task_id)
                if len(seed_task) > 0:
                    seed_task_name = seed_task[0].name
                return "%d files analyzed. (%s, %s)" % (self.task_metadata["files_analyzed"], seed_task_name, self.params[1])
            return ",".join(self.params)
        except Exception as e:
            if self.name in ["test1", "new_test"]:
                raise e
            return "n/a"

    def get_progress(self):
        job = self.get_rq_job()
        if job is None:
            if self.get_status() == "Completed":
                return "100.00"
            else:
                return ""
        progress = job.meta.get('processed', 0) / job.meta.get('size', 1) * 100
        return "%.2f" % progress
        
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
    def __init__(self, uid, username, is_admin = False):
        self.uid = str(uid)
        self.username = username
        self.is_admin = is_admin
        
    def is_authenticated(self):
        return True

    def get_id(self):
        return self.uid

class UserEntry(Document):
    username = StringField(required = True, unique = True)
    name = StringField(required = True, default = '')
    password_hash = StringField(required = True, default = '')
    is_admin = BooleanField(default = False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        self.save()

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)