from rq import Worker

class BookishWorker(Worker):
    def __init__(self, *args, **kwargs):
        super(BookishWorker, self).__init__(*args, **kwargs)
        
    def handle_job_success(self, job, queue, started_job_registry):
        # Do Work
        super(BookishWorker, self).handle_job_success(job = job, queue = queue, started_job_registry = started_job_registry)

    def handle_job_failure(self, job, started_job_registry=None):
        # Do Work
        super(BookishWorker, self).handle_job_failure(job = job, started_job_registry = started_job_registry)