from flask import Flask, render_template, jsonify
from ngram import ngram, ucsf_aggregate
app = Flask(__name__)
app.config["DEBUG"] = True
app.config["TEMPLATES_AUTO_RELOAD"] = True

@app.route('/')
def index():
	return render_template("index.html")

@app.route('/api/ngram/<word>/<divide>')
def api(word, divide):
	divide = divide == "true"
	return jsonify(ngram(word, divide))

@app.route('/api/ucsf/<query>', defaults = {"wt": "html"})
@app.route('/api/ucsf/<query>/<wt>')
def ucsf_doclist(query, wt):
	doclist = ucsf_aggregate(query)
	if wt == "html":
		return "%d documents<br />" % len(doclist) + "<br />".join(doclist)
	return jsonify(doclist)

if __name__=="__main__":
    app.run(threaded=True)
