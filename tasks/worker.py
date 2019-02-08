from rq import Worker, Queue
from rq.job import Job
from datetime import datetime
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

class BookishJob(Job):
    def kill(self):
        """ Force kills the current job causing it to fail """
        if self.is_started:
            set_task_status_bare("Aborting", job = self)
            self.connection.sadd(kill_key, self.get_id())


    def _execute(self):
        def check_kill(conn, id, interval=5):
            init_db_connection()
            while True:
                res = conn.srem(kill_key, id)
                if res > 0:
                    set_task_status_bare("Aborted", job_id = id)
                    os.kill(os.getpid(), signal.SIGKILL)
                time.sleep(interval)

        t = Thread(target=check_kill, args=(self.connection, self.get_id()))
        t.start()

        return super()._execute()

class BookishQueue(rq.Queue):
    job_class = BookishJob

class BookishWorker(Worker):
    queue_class = BookishQueue
    job_class = BookishJob

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
    def handle_job_success(self, job, queue, started_job_registry):
        set_task_status("Completed", job = job)
        set_task_db_field("time_finished", datetime.now(), job = job)
        super().handle_job_success(job = job, queue = queue, started_job_registry = started_job_registry)

    def handle_job_failure(self, job, started_job_registry=None):
        if get_task_status(job) not in ["Aborting", "Aborted"]:
            set_task_status_bare("Failed", job = job)
            set_task_db_field("time_finished", datetime.now(), job = job)
        super().handle_job_failure(job = job, started_job_registry = started_job_registry)

