import redis
import rq
from mongoengine import *

class JobEntry(Document):
    id = StringField(required = True, primary_key = True) 
    name = StringField(required = True)
    description = StringField(max_length = 128)
    user_id = IntField(required = False)
    complete = BooleanField(required = True, default = False)

    def get_rq_job(self):
        try:
            rq_job = rq.job.Job.fetch(self.id, connection=current_app.redis)
        except (redis.exceptions.RedisError, rq.exceptions.NoSuchJobError):
            return None
        return rq_job

    def get_progress(self):
        job = self.get_rq_job()
        return job.meta.get('progress', 0) if job is not None else 100