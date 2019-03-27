from app import create_app
from config import DevConfig, ProdConfig
import sys
import os

def build_app(mode):
	if mode == "prod":
		config_class = ProdConfig
	elif mode == "dev":
		config_class = DevConfig
	else:
		exit("Invalid argument.")

	return create_app(config_class)

if __name__== "__main__":	
	mode = "dev"
	if len(sys.argv) > 1:
		mode = sys.argv[1]
	os.environ["in_bookish"] = True
	app = build_app(mode)
	app.run(threaded=True)
