from rq import Worker

from tasks.util import *

class BookishWorker(Worker):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
    def handle_job_success(self, job, queue, started_job_registry):
        set_task_status("Completed", job = job)
        super().handle_job_success(job = job, queue = queue, started_job_registry = started_job_registry)

    def handle_job_failure(self, job, started_job_registry=None):
        set_task_status("Failed", job = job)
        super().handle_job_failure(job = job, started_job_registry = started_job_registry)