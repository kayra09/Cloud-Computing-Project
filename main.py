from flask import *
import mysql.connector


app = Flask(__name__)
app.secret_key = "not so secret key"

def get_course_table():
    db = mysql.connector.connect(host='localhost', database='capstone_project', user='root', password='root')
    cursor = db.cursor()
    cursor.execute("SELECT * FROM course_code")
    course_codes=cursor.fetchall()
    return course_codes

@app.route("/")
def main_page():
    course_codes = get_course_table()
    return render_template("index.html",course_codes=course_codes)
@app.route("/see_course/<course_code>")
def see_course(course_code):
    return render_template("see_course.html",course_code=course_code)
if __name__ == '__main__':
    app.run()