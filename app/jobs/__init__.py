from flask import Blueprint

bp = Blueprint('jobs', __name__)

from app.jobs import routes
from app.jobs import tasks
from app.jobs import scheduler