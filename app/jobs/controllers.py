import os
import rq
import time
from flask import current_app
from flask_login import current_user
from redis import Redis
from rq.job import Job
from tasks.worker import BookishJob

from app.models import JobEntry
from tasks import tasks


def get_job_entry(id):
    job = JobEntry.objects(id = id, user_id = current_user.get_id())
    if len(job) != 1:
        return None
    return job[0]

def get_rq_job(id):
	job = BookishJob.fetch(id, connection = current_app.redis)
	return job

def get_user_jobs(user_id):
	return JobEntry.objects(user_id = user_id)

# Need to first start script start_worker.py.
def schedule_job(task, params, name = None):
	# Temporarily made TTL 0 to test DB logging.
	job = current_app.task_queue.enqueue(task, *params, result_ttl = 0, timeout = -1)
	job_id = job.get_id()
	job.meta['progress'] = 0.0
	job.save_meta()

	job_entry = JobEntry(id = job_id, 
						 task = task.__name__,
						 name = name, 
						 status = 'Queued',
						 user_id = current_user.get_id())
	job_entry.save()


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

def delete_job(id):
	job = get_job_entry(id)
	if job is None:
		return False
		
	try:
		job.delete()
	except:
		return False

	# Additional cleanup, but not a huge deal if it fails.
	try: 
		os.remove(current_app.config["TASK_RESULT_PATH"] + id)
		print("Results file (%s) removed." %id)
	except:
		pass

	return True

def get_job_results(id):
	job = get_job_entry(id)
	if not job:
		return None
	try:
		filename = current_app.config["TASK_RESULT_PATH"] + id
		f = open(filename)
		file_size = os.path.getsize(filename)
		# Read at most ~500K
		max_file_size = 500000
		data = f.read(min(file_size, max_file_size))
		# If data was truncated
		if file_size > max_file_size:
			data += "[truncated]\n"
		f.close()
		return data
	except FileNotFoundError:
		return "Results could not be found."

def get_seed_jobs():
	print(current_user)
	if not current_user:
		return []
	print(current_user.get_id())
	seed_tasks = ["ucsf_api_aggregate_task"]
	jobs = JobEntry.objects(task__in = seed_tasks, status = "Completed", user_id = current_user.get_id())
	jobs = list(map(lambda x: (x.id, "%s (%s)" % (x.name, x.task)), jobs))
	jobs.append(("dummy", "dummy job (all local files)"))
	print(jobs)
	return jobs
