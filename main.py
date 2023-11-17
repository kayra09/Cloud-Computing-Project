from flask import *

app = Flask(__name__)
app.secret_key = "not so secret key"


@app.route("/")
def main_page():
    return render_template("index.html")

if __name__ == '__main__':
    app.run()