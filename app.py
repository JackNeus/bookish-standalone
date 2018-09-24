from flask import Flask, render_template, jsonify
from ngram import ngram
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

if __name__=="__main__":
    app.run(threaded=True)
