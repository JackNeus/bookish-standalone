from flask import current_app, render_template, jsonify
from app.ngram import ngram, ucsf_aggregate

from app.web import bp

@bp.route('/')
def index():
	return render_template("index.html")

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