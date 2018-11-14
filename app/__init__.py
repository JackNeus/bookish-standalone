from redis import Redis
import rq
from mongoengine import register_connection
from flask import Flask
from flask_bootstrap import Bootstrap
from flask_login import LoginManager
from config import Config
from app.nav import nav

login_manager = LoginManager()
bootstrap = Bootstrap()

def create_app(config_class=Config):
	app = Flask(__name__)
	app.config.from_object(config_class)

	# Initialize MongoEngine
	try:
		register_connection (
			alias = "default",
			name = app.config["DB_NAME"],
			username = app.config["DB_USER"],
			password = app.config["DB_PASSWORD"],
			host = app.config["DB_URL"],
			port = app.config["DB_PORT"]
		)
	except:
		print("Database could not be configured.")
		return None
		
	nav.init_app(app)

	login_manager.init_app(app)
	bootstrap.init_app(app)

	app.redis = Redis.from_url(app.config['REDIS_URL'])
	app.task_queue = rq.Queue(app.config['REDIS_QUEUE_NAME'], connection = app.redis)

	from app.jobs import bp as jobs_bp
	app.register_blueprint(jobs_bp, url_prefix='')

	from app.web import bp as web_bp
	app.register_blueprint(web_bp, url_prefix='')

	from app.user import bp as user_bp
	app.register_blueprint(user_bp, url_prefix='')

	return app

#app.config["DEBUG"] = True
#app.config["TEMPLATES_AUTO_RELOAD"] = True

from app import models