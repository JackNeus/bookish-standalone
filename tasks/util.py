import copy
from datetime import datetime
import json
from mongoengine import register_connection
import multiprocessing
from rq import get_current_job
from queue import Queue

from app.models import JobEntry
from tasks.multi_util import *

config = None
def set_config(config_):
    global config
    config = config_

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

def make_locks_global(rq_lock, db_lock):
    global rq_obj_lock
    global db_obj_lock
    rq_obj_lock = rq_lock
    db_obj_lock = db_lock

def init_job(params = []):
    # RQ setup.
    job = get_current_job()
    if job: 
        print("Job exists (%s)" % job.get_id())

        job.is_master = True        
        init_db_connection()
        make_locks_global(multiprocessing.Lock(), multiprocessing.Lock())
 
        set_task_status('Running')
        set_task_db_field("time_started", datetime.now())
        set_task_params([str(param) for param in params])

        job.meta['processed'] = 0
        job.save_meta()

    else:
        print("Job DNE.")

def init_slave(rq_lock, db_lock):
    make_locks_global(rq_lock, db_lock)

    job = get_current_job()
    job.is_master = False
    # Need to reregister DB connection.
    init_db_connection()

def get_pool():
    job = get_current_job()
    if job is None:
        return None
    lock_args = (rq_obj_lock, db_obj_lock)
    return multiprocessing.Pool(config["NUM_CORES"], initializer = init_slave, initargs=lock_args)

def partition_map(map_func, items, size_func = lambda *a: 1, max_partition_size = 25):
    items = [item + (size_func(item),) for item in items]
    partitions = partition(items, max_partition_size)
    mapped_values = get_pool().starmap(map_func, partitions)
    return mapped_values

    # Calculate max_partition_size in bytes.
    #bytes_per_gb = 1024 * 1024 * 1024
    #usable_memory = 1 * bytes_per_gb
    #max_partition_size = usable_memory / config["NUM_CORES"]

# Get the file list for the rq result associated with file_list_path.
# If include_without_year is True, return files regardless of whether or not they are
# associated with a year.
def get_file_list(file_list_path, include_without_year = False):
    # Make sure file_list_path is a valid task ID.
    if file_list_path not in ["dummy"] and get_job_entry(file_list_path) is None:
        return None

    file_list_file = open(config["TASK_RESULT_PATH"] + file_list_path)
    def extract(line):
        line = line.split(" ")
        line[0] += ".clean"
        if len(line) > 1:
            line[1] = int(line[1][:-1])
        return tuple(line)

    file_list = map(lambda line: extract(line), file_list_file.readlines())
    
    if not include_without_year:
        # Remove files without years.
        file_list = list(filter(lambda x: len(x) > 1, file_list))

    return file_list

### JOB ENTRY CODE

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

def set_task_db_field(k, v, job = None, job_id = None):
    if not job_id:
        if not job:
            job = get_current_job()
        if job:
            job_id = job.get_id()

    if job_id:
        job_entry = get_job_entry(job_id)

        # Make sure DB write is thread-safe.
        db_obj_lock.acquire()
        setattr(job_entry, k, v)
        job_entry.save()
        db_obj_lock.release()
    else:
        # TODO: Raise exception
        pass   

def set_task_status(status, job = None, job_id = None):    
    set_task_db_field("status", status, job = job, job_id = job_id)

def set_task_status_bare(status, job = None, job_id = None):
    if not job_id:
        if not job:
            job = get_current_job()
        if job:
            job_id = job.get_id()
            
    job_entry = get_job_entry(job_id)
    job_entry.status = status
    job_entry.save()
    
def set_task_params(params):
    set_task_db_field("params", params)

def set_task_metadata(k, v, job = None):
    if not job:
        job = get_current_job()
    if job:
        job_id = job.get_id()
        job_entry = get_job_entry(job_id)

        # Make sure DB write is thread-safe.
        db_obj_lock.acquire()
        job_entry.task_metadata[k] = v
        job_entry.save()
        db_obj_lock.release()

# If job.meta[rq_metadata_k] % step == 0 (or forced),
# set job_entry.metadata[db_metadata_k] = job.meta[rq_metadata_k].
def push_metadata_to_db(db_metadata_k, rq_metadata_k = "processed", step = 100, force = False):
    job = get_current_job()
    if not job:
        return
    rq_obj_lock.acquire()
    job.refresh()
    rq_metadata_v = job.meta[rq_metadata_k]
    rq_obj_lock.release()
    if rq_metadata_v % step == 0 or force:     
        set_task_metadata(db_metadata_k, rq_metadata_v, job = job)

### END JOB ENTRY CODE

### RQ JOB CODE

# TODO: Put this in metadata instead.
# Actually, it may be worth it to keep it local. 
# As it is, it's pretty expensive to write many updates to the DB.

def inc_task_processed(amt = 1):
    job = get_current_job()
    if job:
        rq_obj_lock.acquire()
        job.refresh()
        job.meta['processed'] += amt
        job.save_meta()
        rq_obj_lock.release()

def set_task_size(size):
    job = get_current_job()
    if job:
        rq_obj_lock.acquire()
        job.meta['size'] = size
        job.save_meta()
        rq_obj_lock.release()

### END RQ JOB CODE

### TASK OUTPUT FILE CODE

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

### END TASK OUTPUT FILE CODE