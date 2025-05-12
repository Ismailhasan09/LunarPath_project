from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def hello_world():

    return render_template('index.html')


@app.route('/bootstrap')
def bootstrap():
    return render_template(('bootstrap.html'))

app.run(port=5200, debug=True)
