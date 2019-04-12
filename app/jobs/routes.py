from flask import current_app, flash, jsonify, redirect, render_template, url_for
from flask_security import login_required
from flask_login import current_user
import json

from app.jobs import bp, controllers as controller
from app.jobs.forms import ScheduleForm
from tasks import tasks

@bp.route('/jobs')
@login_required
def jobs_index():
	return render_template("jobs/jobs.html", jobs=controller.get_user_jobs_json(current_user.get_id()))

@bp.route('/jobs.json')
@login_required
def user_jobs_json():
	jobs = controller.get_user_jobs_json(current_user.get_id())
	return jsonify(jobs)

@bp.route('/schedule', methods=["GET", "POST"])
@login_required
def schedule():
	seed_jobs = controller.get_seed_jobs()
	form = ScheduleForm()
	if form.validate_on_submit():
		task = tasks.resolve_task(form.task_name.data)
		job_name = form.job_name.data

		# Make sure job name is not already in use.
		if controller.get_job_entry_by_name(job_name) is not None:
			flash("That name is already in use.")
			return render_template("jobs/schedule.html", form=form)

		params = []
		for field in str(form["param_metadata"].data).split(";"):
			params.append(form[field].data)

		try:
			controller.schedule_job(task, params, job_name)
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

@bp.route('jobs/kill/<id>')
@login_required
def kill(id):
	job = controller.get_job_entry(id)
	if job is None:
		flash("Job does not exist.")
	if not controller.kill_job(id):
		flash("Failed to cancel job. Job may still be running.")
	return redirect(url_for("jobs.jobs_index"))

@bp.route('jobs/delete/<ids>')
@login_required
def delete(ids):
	ids = ids.split(";");
	for id in ids:
		# TODO: Prevent users from cancelling each other's jobs
		job = controller.get_job_entry(id)
		if job is None:
			flash("Job does not exist.")
		if not controller.delete_job(id):
			flash("Failed to delete job.")
	return redirect(url_for("jobs.jobs_index"))

@bp.route('jobs/replay/<id>')
@login_required
def replay(id):
	job = controller.get_job_entry(id)
	if job is None:
		flash("Job does not exist.")

	task = tasks.resolve_task(job.task)
	job_name = job.name + " (Replay)"

	# Make sure job name is not already in use.
	if controller.get_job_entry_by_name(job_name) is not None:
		flash("That name is already in use.")
		return redirect(url_for("jobs.jobs_index"))
	print(task, job.params, job_name)
	try:
		controller.schedule_job(task, job.params, job_name)
	except Exception as e:
		if current_app.config["DEBUG"]:
			raise e
		flash("Something went wrong.")
		return redirect(url_for("jobs.jobs_index"))
	return redirect(url_for("jobs.jobs_index"))

@bp.route('jobs/view/<ids>')
@login_required
def view(ids):
	ids = ids.split(";")
	results = {}
	for id in ids:
		job = controller.get_job_entry(id)
		if job is None:
			flash("Job does not exist.")
			return redirect(url_for("jobs.jobs_index"))
		results[job.name] = controller.get_job_results(id);

	# TODO: Support multivis for all tasks.
	if job.task == "word_freq_task":
		return render_template("jobs/ngram_viewer.html", data = results[ids[0]])
	elif job.task == "top_bigrams_task":
		return render_template("jobs/graph_viewer.html", vis_name="bigram", data = results[ids[0]])
	elif job.task == "word_family_graph_task":
		for id in results:
			results[id] = results[id].strip().split("\n")
		return render_template("jobs/graph_viewer.html", vis_name="wordfam", data = json.dumps(results))
	else:
		return render_template("jobs/default_viewer.html", data = results)
	return redirect(url_for("jobs.jobs_index"))