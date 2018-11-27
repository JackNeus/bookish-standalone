from app import create_app
from config import DevConfig, ProdConfig
import sys

if __name__== "__main__":
	mode = "dev"
	if len(sys.argv) > 1:
		mode = sys.argv[1]
	if mode == "prod":
		config_class = ProdConfig
	elif mode == "dev":
		config_class = DevConfig
	else:
		exit("Invalid argument.")
	app = create_app(config_class)
	
	app.run(threaded=True)
