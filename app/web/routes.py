from flask import current_app, redirect, render_template, jsonify, url_for
from app.ngram import ngram, ucsf_aggregate

from app.web import bp

@bp.route('/')
def index():
	return redirect(url_for('jobs.jobs'))
	#return render_template("index.html")

@bp.route('/api/ngram/<word>/<divide>')
def api(word, divide):
	divide = divide == "true"
	return jsonify(ngram(word, divide))

@bp.route('/api/ucsf/<query>', defaults = {"wt": "html"})
@bp.route('/api/ucsf/<query>/<wt>')
def ucsf_doclist(query, wt):
	doclist = ucsf_aggregate(query)
	if wt == "html":
		return "%d documents<br />" % len(doclist) + "<br />".join(doclist)
	return jsonify(doclist)