import time

from redis import Redis
import rq
from app.jobs import tasks
from app.models import JobEntry
from flask import current_app
from flask_login import current_user

# Need to first start script run_worker.py.
def schedule_job(task, params, name = None, description = None):
	job = current_app.task_queue.enqueue(task, *params)
	job_id = job.get_id()
	job.meta['progress'] = 0.0
	job.meta['status'] = 'Queued'
	job.save_meta()

	job_entry = JobEntry(id = job_id, 
						 task = task.__name__,
						 name = name, 
						 status = 'Queued',
						 user_id = current_user.get_id(),
						 description = description)
	job_entry.save()

def get_job(id):
	job = JobEntry.objects(id = id)
	if len(jobs) != 1:
		return None
	job = job[0]

def get_user_jobs(user_id):
	return JobEntry.objects(user_id = user_id)