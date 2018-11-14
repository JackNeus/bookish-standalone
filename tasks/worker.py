from rq import Worker, Queue
from rq.job import Job
import os
import rq
import signal
from threading import Thread
from mongoengine import register_connection
import time

from app.models import JobEntry
from tasks.util import *

# Kill code taken from rminderhoud at https://github.com/rq/rq/issues/684

kill_key = "rq:jobs:kill"

class KillJob(Job):
    def kill(self):
        """ Force kills the current job causing it to fail """
        if self.is_started:
            set_task_status("Aborting", self)
            self.connection.sadd(kill_key, self.get_id())

    def _execute(self):
        def check_kill(conn, id, interval=5):
            init_db_connection()
            while True:
                res = conn.srem(kill_key, id)
                if res > 0:
                    set_task_status("Aborted", job_id = id)
                    os.kill(os.getpid(), signal.SIGKILL)
                time.sleep(interval)

        t = Thread(target=check_kill, args=(self.connection, self.get_id()))
        t.start()

        return super()._execute()

class KillQueue(rq.Queue):
    job_class = KillJob

class BookishWorker(Worker):
    queue_class = KillQueue
    job_class = KillJob

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
    def handle_job_success(self, job, queue, started_job_registry):
        set_task_status("Completed", job = job)
        super().handle_job_success(job = job, queue = queue, started_job_registry = started_job_registry)

    def handle_job_failure(self, job, started_job_registry=None):
        if get_task_status(job) not in ["Aborting", "Aborted"]:
            set_task_status("Failed", job = job)
        super().handle_job_failure(job = job, started_job_registry = started_job_registry)

