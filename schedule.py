import time

from redis import Redis
import rq

# start queue with rq worker bookish-rq
queue = rq.Queue('bookish-rq', connection=Redis.from_url('redis://'))
job = queue.enqueue('jobs.ucsf_api_aggregate', 'industry:drug')
print(job.get_id())
while not job.is_finished:
	time.sleep(5)
	job.refresh()
	print(job.meta)