import datetime
import json
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
from tasks.util import set_task_status


def get_job_entry(id):
    job = JobEntry.objects(id = id, user_id = current_user.get_id())
    if len(job) != 1:
        return None
    return job[0]

def get_job_entry_by_name(name):
    job = JobEntry.objects(name = name, user_id = current_user.get_id())
    if len(job) != 1:
        return None
    return job[0]

def get_rq_job(id):
    job = BookishJob.fetch(id, connection = current_app.redis)
    return job

def get_user_jobs(user_id):
    return JobEntry.objects(user_id = user_id).order_by("time_created", "time_started", "time_finished")

def get_user_jobs_json(user_id):
    def job_entry_to_json(job_entry):
        time_started = ""
        if job_entry.time_started:
            time_started = datetime.date.strftime(job_entry.time_started, "%c")
        time_finished = ""
        if job_entry.time_finished:
            time_finished = datetime.date.strftime(job_entry.time_finished, "%c")
        job = {
            "id": job_entry.id,
            "name": job_entry.name,
            "task": job_entry.task,
            "status": job_entry.get_status(),
            "time_started": time_started,
            "time_finished": time_finished,
            "progress": job_entry.get_progress(),
            "description": job_entry.get_description()
        }
        return job
    return [job_entry_to_json(job) for job in get_user_jobs(user_id)]

# Need to first start script start_worker.py.
def schedule_job(task, params, name = None):
    # Temporarily made TTL 0 to test DB logging.
    job = current_app.task_queue.enqueue(task, *params, result_ttl = 120, timeout = -1)
    job_id = job.get_id()
    job.meta['progress'] = 0.0
    job.save_meta()

    job_entry = JobEntry(id = job_id, 
                         task = task.__name__,
                         name = name, 
                         status = 'Queued',
                         time_created = datetime.datetime.now(),
                         user_id = current_user.get_id())
    job_entry.save()


def kill_job(id):
    job = get_rq_job(id)

    if job is None:
        return False
    job_entry = get_job_entry(id)
    job_status = job_entry.get_status()

    if job_status == "Running":
        try:
            job.kill()
            return True
        except Exception as e:
            return False
    elif job_status == "Queued":
        current_app.task_queue.remove(job)
        job_entry.status = "Aborted"
        job_entry.save()
        return True
    else:
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

def get_job_results(id, truncate = True):
    job = get_job_entry(id)
    if not job:
        return None
    try:
        filename = current_app.config["TASK_RESULT_PATH"] + id
        f = open(filename)
        file_size = os.path.getsize(filename)
        read_size = file_size
        max_file_size = 500000
        if truncate: 
            # Read at most ~500K
            read_size = min(read_size, max_file_size)
        data = f.read(read_size)
        
        # If data was truncated
        if file_size > read_size:
            data += "[truncated]\n"
 
        f.close()
        return data
    except FileNotFoundError:
        return "Results could not be found."

def get_seed_jobs():
    print(current_user)
    if not current_user:
        return []
        
    seed_tasks = ["ucsf_api_aggregate_task"]
    jobs = JobEntry.objects(task__in = seed_tasks, status = "Completed", user_id = current_user.get_id())
    jobs = list(map(lambda x: (x.id, "%s (%s)" % (x.name, x.task)), jobs))
    if current_app.config["DEBUG"]:
        jobs.append(("dummy", "dummy job (all local files)"))
    return jobs
