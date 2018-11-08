import threading
from rq import get_current_job
from queue import Queue

#from app.models import JobEntry

def get_job_entry(id):
    job = JobEntry.objects(id = id)
    if len(job) != 1:
        return None
    return job[0]

def set_task_progess(progress):
    job = get_current_job()
    if job:
        job.meta['progress'] = round(progress, 2)
        job.save_meta()

def set_task_status(status, job = None):
    if not job:
        job = get_current_job()
    if job:
        print("Setting status: %s" % status)
        job_entry = get_job_entry(job.get_id())
        print(job_entry, job_entry.status)
        job_entry.status = status
        job_entry.save()
    else:
        # TODO: Raise exception
        pass

def write_task_results(data):
    job = get_current_job()
    if job is None:
        # TODO: Raise exception
        return
    else:
        filename = job.get_id()
    # TODO: Put this in config file without using current_app
    path = 'rq_results/'
    f = open(path + filename, "w")

    if type(data) == type([]):
        for row in data:
            f.write(str(row) + '\n')
    else:
        with str(data) as out:
            f.write(out)
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
def start_job(process_func, func_input, kwargs = {}, num_threads = 1):
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

