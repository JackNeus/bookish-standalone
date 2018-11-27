import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class Config(object):
	SECRET_KEY = os.environ.get('SECRET_KEY')
	DEBUG = True
	TEMPLATES_AUTO_RELOAD = True
	REDIS_QUEUE_NAME = 'bookish-tasks'
	REDIS_URL = os.environ.get('REDIS_URL') or 'redis://'
	TASK_RESULT_PATH = 'rq_results/'

	DB_URL = os.environ.get('DB_URL')
	DB_PORT = int(os.environ.get('DB_PORT'))
	DB_NAME = os.environ.get('DB_NAME')
	DB_USER = os.environ.get('DB_USER')
	DB_PASSWORD = os.environ.get('DB_PASSWORD')

	SESSION_LENGTH = 7

	NUM_CORES = 1