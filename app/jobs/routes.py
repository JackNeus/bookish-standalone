from flask import current_app, render_template\

from app.jobs import bp

@bp.route('jobs')
def index():
	return render_template("jobs.html")

