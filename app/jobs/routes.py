from flask import current_app, redirect, render_template, url_for
from flask_login import current_user
from app.jobs import bp, scheduler, tasks

@bp.route('/jobs')
def jobs_index():
	print(str(tasks.ucsf_api_aggregate))
	return render_template("jobs/jobs.html", jobs=scheduler.get_user_jobs(current_user.get_id()))

@bp.route('/schedule')
def schedule():
	print(str(tasks.ucsf_api_aggregate))
	scheduler.schedule_job(tasks.ucsf_api_aggregate, ['author:glantz'], 'test1')
	return redirect(url_for('jobs.jobs_index'))