import copy
import json
from mongoengine import register_connection
import threading
from rq import get_current_job
from queue import Queue

from app.models import JobEntry

from config import Config
config = vars(Config)

def init_db_connection():
    register_connection (
        alias = "default",
        name = config["DB_NAME"],
        username = config["DB_USER"],
        password = config["DB_PASSWORD"],
        host = config["DB_URL"],
        port = config["DB_PORT"]
    )

def init_dict(keys, default_value):
    new_dict = {}
    for k in keys:
        new_dict[k] = copy.deepcopy(default_value)
    return new_dict

def init_job(params = []):
    # RQ setup.
    job = get_current_job()
    if job: 
        print("Job exists (%s)" % job.get_id())
        init_db_connection()
        set_task_status('Running')
        set_task_params([str(param) for param in params])

        job.meta['processed'] = 0
        job.save_meta()
    else:
        print("Job DNE.")

def get_job_entry(id):
    job = JobEntry.objects(id = id)
    if len(job) != 1:
        return None
    return job[0]

def get_task_status(job = None):
    if not job:
        job = get_current_job()
    if job:
        job = get_job_entry(job.get_id())
        if not job:
            return None
        return job.status 

def set_task_status(status, job = None, job_id = None):
    if not job_id:
        if not job:
            job = get_current_job()
        if job:
            job_id = job.get_id()

    if job_id:
        print("Setting status: %s" % status)
        job_entry = get_job_entry(job_id)
        job_entry.status = status
        job_entry.save()
    else:
        # TODO: Raise exception
        pass

def set_task_params(params):
    job = get_current_job()
    job_entry = get_job_entry(job.get_id())
    job_entry.params = params
    job_entry.save()

def inc_task_processed(amt = 1):
    job = get_current_job()
    if job:
        job.meta['processed'] += amt
        job.save_meta()

def set_task_size(size):
    job = get_current_job()
    if job:
        job.meta['size'] = size
        job.save_meta()

def set_task_metadata(k, v, job = None):
    if not job:
        job = get_current_job()
    if job:
        job_id = job.get_id()
        job_entry = get_job_entry(job_id)
        job_entry.task_metadata[k] = v
        job_entry.save()

def open_task_output_file():
    job = get_current_job()
    if job is None:
        # TODO: Raise exception
        return None
    else:
        filename = job.get_id()
        
    path = config["TASK_RESULT_PATH"]
    f = open(path + filename, "w")  
    return f  

# 11/26/18: Introduced new parameter file_obj.
# If None, the function opens a file, writes to it, and closes the file.
# If not None, the function will write to the file, but will not open or close it.
def write_task_results(data, file_obj = None):
    if file_obj is None:
        f = open_task_output_file()
        if f is None:
            return    
    else:
        f = file_obj

    if isinstance(data, list):
        for row in data:
            f.write(str(row) + '\n')
    elif isinstance(data, dict):
        f.write(json.dumps(data))
    else:
        f.write(str(data) + '\n')
   
    if file_obj is None:
        f.close()

def return_from_task(return_value):
    write_task_results(return_value)
    #set_task_status('Done')

class InvalidArgumentError(Exception):
	pass

# Params
# process_func: task function to be called. function should pop elements from input_queue
# func_input: list of elements to be added to a queue
# kwargs: parameters for process_func
# num_threads: number of threads to be spawned
def multi_work(process_func, func_input, kwargs = {}, num_threads = 1):
	if "input_queue" in kwargs:
		raise InvalidArgumentError("\"input_queue\" is a reserved parameter name.")

	input_queue = Queue()
	for elt in func_input:
		input_queue.put(elt)
	for i in range(num_threads):
		t = threading.Thread(target = process_func, kwargs = {"input_queue": input_queue, **kwargs})
		t.daemon = True
		t.start()
	input_queue.join()
    # TODO: join with exception 

