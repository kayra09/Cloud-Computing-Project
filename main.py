from flask import *
import mysql.connector


app = Flask(__name__)
app.secret_key = "not so secret key"

def database_test():
    db = mysql.connector.connect(host='localhost', database='capstone_project', user='root', password='root')
    cursor = db.cursor()
    cursor.execute("SELECT * FROM course_code")
    records=cursor.fetchall()
    for data in records:
        print(data)
@app.route("/")
def main_page():
    return render_template("index.html")

if __name__ == '__main__':
    database_test()
    app.run()