# Custom RQ worker.
from config import DevConfig, ProdConfig
from tasks.util import init_db_connection, set_config

from mongoengine import register_connection
from rq import Connection, Worker
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
from tasks.worker import BookishWorker

# Provide queue names to listen to as arguments to this script,
# similar to rq worker
with Connection():
    qs = [config['REDIS_QUEUE_NAME']]
    print("Starting BookishWorker...")
    w = BookishWorker(qs)
    w.work()
