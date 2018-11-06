import threading
from queue import Queue

class InvalidArgumentError(Exception):
	pass

# Params
# process_func: task function to be called. function should pop elements from input_queue
# func_input: list of elements to be added to a queue
# kwargs: parameters for process_func
# num_threads: number of threads to be spawned
def start_job(process_func, func_input, kwargs = None, num_threads = 1):
	if "input_queue" in kwargs:
		raise InvalidArgumentError("\"input_queue\" is a reserved parameter name.")

	input_queue = Queue()
	for elt in func_input:
		input_queue.put(elt)
	for i in range(num_threads):
		t = threading.start(target = process_func, kwargs = {"input_queue": input_queue, **kwargs})
		t.daemon = True
		t.start()

