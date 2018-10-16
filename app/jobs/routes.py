from flask import current_app, flash, redirect, render_template, url_for
from flask_login import current_user
from app.jobs import bp, scheduler, tasks
from app.jobs.forms import ScheduleForm

@bp.route('/jobs')
def jobs_index():
	return render_template("jobs/jobs.html", jobs=scheduler.get_user_jobs(current_user.get_id()))

@bp.route('/schedule', methods=["GET", "POST"])
def schedule():
	form = ScheduleForm()
	if form.validate_on_submit():
		task = tasks.resolve_task(form.task_name.data)
		job_name = form.job_name.data
		params = form.params.data.split()
		try:
			scheduler.schedule_job(task, params, job_name)
		except Exception as e:
			if current_app.config["DEBUG"]:
				raise e
			flash("Something went wrong.")
			return render_template("jobs/schedule.html", form=form)
		return redirect(url_for("jobs.jobs_index"))
	return render_template("jobs/schedule.html", form=form)

	#print(str(tasks.ucsf_api_aggregate))
	#scheduler.schedule_job(tasks.ucsf_api_aggregate, ['author:glantz'], 'test1')
	#return redirect(url_for('jobs.jobs_index'))