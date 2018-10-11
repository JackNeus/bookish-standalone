from flask import Flask
from config import Config

def create_app(config_class=Config):
	app = Flask(__name__)
	app.config.from_object(config_class)

	from app.jobs import bp as jobs_bp
	app.register_blueprint(jobs_bp, url_prefix='')

	from app.web import bp as web_bp
	app.register_blueprint(web_bp, url_prefix='')

	return app

#app.config["DEBUG"] = True
#app.config["TEMPLATES_AUTO_RELOAD"] = True

from app import models