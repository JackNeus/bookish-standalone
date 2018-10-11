import time

from redis import Redis
import rq

from app.models import JobEntry

def experiment():
	# start queue with rq worker bookish-rq
	queue = rq.Queue('bookish-rq', connection=Redis.from_url('redis://'))
	job = queue.enqueue('jobs.ucsf_api_aggregate', 'industry:drug')
	print(job.get_id())
	while not job.is_finished:
		time.sleep(5)
		job.refresh()
		print(job.meta)

def schedule_job(task_name, params, name = None, desription = None):
	job = app.task_queue.enqueue(task_name, *params)
	job_id = job.get_id()
	job.meta['progress'] = 0.0
    job.meta['status'] = 'Queued'
    job.save_meta()

	job_entry = JobEntry(id = job_id, name = name, desription = desription)
	job_entry.save()

def get_job(id):
	job = JobEntry.objects(id = id)
	if len(jobs) != 1:
		return None
	job = job[0]