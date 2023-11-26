from flask import *
import mysql.connector
import boto3


app = Flask(__name__)
app.secret_key = "not so secret key"

def get_course_table():
    db = mysql.connector.connect(host='localhost', database='capstone_project', user='root', password='root')
    cursor = db.cursor()
    cursor.execute("SELECT * FROM course_code")
    course_codes=cursor.fetchall()
    return course_codes
def upload_file(file_name):
    aws_access_key_id = 'AKIA2CXPV6DKX4F46E4S'
    aws_secret_access_key = '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'
    bucket_name = 'cng495'
    file_path = 'templates/requests/1.jpg'  # Path to the file you want to upload
    s3_key = str(file_name) + ".jpg"  # Key/name under which the file will be stored in the S3 bucket
    s3 = boto3.client('s3', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)
    s3.upload_file(file_path, bucket_name, s3_key)
def retrieve_file(file_name):
    aws_access_key_id = 'AKIA2CXPV6DKX4F46E4S'
    aws_secret_access_key = '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'
    bucket_name = 'cng495'
    s3_key = str(file_name) + ".jpg"  # Key/name under which the file will be stored in the S3 bucket
    local_file_path = 'templates/cloud_files_temporary/1.jpg'  # Path where you want to save the downloaded file
    s3 = boto3.client('s3', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)
    s3.download_file(bucket_name, s3_key, local_file_path)
    return 0
@app.route("/")
def main_page():
    course_codes = get_course_table()
    return render_template("index.html",course_codes=course_codes)
@app.route("/see_course/<course_code>")
def see_course(course_code):
    return render_template("see_course.html",course_code=course_code)
if __name__ == '__main__':
    upload_file(1)
    retrieve_file(1)
    app.run()