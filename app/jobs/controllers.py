from flask import current_app
from rq.job import Job
from tasks.worker import KillJob

from app.models import JobEntry

def get_job_entry(id):
    job = JobEntry.objects(id = id)
    if len(job) != 1:
        return None
    return job[0]

def get_rq_job(id):
	job = KillJob.fetch(id, connection = current_app.redis)
	return job

def kill_job(id):
	job = get_rq_job(id)
	print("Job: ", job)
	if job is None:
		return False
		
	try:
		job.kill()
		return True
	except:
		return False