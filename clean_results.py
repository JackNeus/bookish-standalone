# Custom RQ worker.
from config import DevConfig, ProdConfig
from tasks.util import get_job_entry, init_db_connection, set_config
import os
import sys

config_class = DevConfig
if len(sys.argv) > 1:
	mode = sys.argv[1]
	if mode == "prod":
		print("Running in production mode.")
		config_class = ProdConfig
	elif mode == "dev":
		print("Running in development mode.")
		config_class = DevConfig
	else:
		exit("Invalid argument.")
else:
	print("Running in development mode (default).")
config = vars(config_class)
set_config(config)

init_db_connection()
for file in os.listdir(config["TASK_RESULT_PATH"]):
	# Only look at actual task result files.
	if len(file) != 36:
			continue
	job_entry = get_job_entry(file)
	if job_entry is None:
		os.remove(config["TASK_RESULT_PATH"] + file)
