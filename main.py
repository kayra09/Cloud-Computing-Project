import os
import shutil

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


def upload_file(file_name,file_path):
    aws_access_key_id = 'AKIA2CXPV6DKX4F46E4S'
    aws_secret_access_key = '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'
    bucket_name = 'cng495'
    #file_path = 'templates/requests/1.jpg'  # Path to the file you want to upload
    s3_key = str(file_name) + ".jpg"  # Key/name under which the file will be stored in the S3 bucket
    s3 = boto3.client('s3', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)
    s3.upload_file(file_path, bucket_name, s3_key)

    db = mysql.connector.connect(host='localhost', database='capstone_project', user='root', password='root')
    cursor = db.cursor()
    file_name=file_name.split("_")
    cursor.execute("INSERT INTO POST VALUES (%s, %s, %s, %s)", (int(file_name[1]), "not implemented", file_name[0], "not implemented"))
    db.commit()


def retrieve_file(file_name, number):
    aws_access_key_id = 'AKIA2CXPV6DKX4F46E4S'
    aws_secret_access_key = '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'
    bucket_name = 'cng495'
    s3_key = str(file_name) + ".jpg"  # Key/name under which the file will be stored in the S3 bucket
    fileName = file_name.split("_")[0]

    # Base directory where cloud_files_temporary will be located.
    base_directory = 'static'

    cloud_files_temp_directory = os.path.join(base_directory, 'cloud_files_temporary')

    # Check and create cloud_files_temporary if it does not exist.
    if not os.path.exists(cloud_files_temp_directory):
        os.makedirs(cloud_files_temp_directory)

    # Now, set up the local file path with the specific file name and number.
    local_file_path = os.path.join(cloud_files_temp_directory, fileName, f'{number}.jpg')

    # Ensure that the directory for file_name exists.
    file_name_directory = os.path.dirname(local_file_path)
    if not os.path.exists(file_name_directory):
        os.makedirs(file_name_directory)

    s3 = boto3.client('s3', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)
    s3.download_file(bucket_name, s3_key, local_file_path)
    return 0


def course_post_count(courseCode):
    db = mysql.connector.connect(host='localhost', database='capstone_project', user='root', password='root')
    cursor = db.cursor()
    query = "SELECT COUNT(*) FROM post WHERE course_code = %s"
    cursor.execute(query, (courseCode,))
    count = cursor.fetchone()[0]
    cursor.close()
    db.close()
    return count


def retrieve_files(courseCode):
    count = course_post_count(courseCode)

    for num in range(1, count+1):
        retrieve_file(courseCode+"_" + str(num), num)


def update_course_materials():
    retrieve_files("cng100")
    retrieve_files("cng499")


def remove_temporary_file():
    directory_path = 'static/cloud_files_temporary'

    # Check if the directory exists
    if os.path.exists(directory_path):
        # Remove the directory and all its contents
        shutil.rmtree(directory_path)


def generate_amazon_S3_name(course_code):
    name = str(course_code) + "_"
    db = mysql.connector.connect(host='localhost', database='capstone_project', user='root', password='root')
    cursor = db.cursor()
    cursor.execute("SELECT COUNT(*) FROM post WHERE course_code = %s", (course_code,))
    count_result = cursor.fetchone()
    # Ensure count_result is not None before accessing the count
    if count_result:
        count = count_result[0]
        name += str(count + 1)  # You might want to adjust this logic based on your requirements
    # Close the database connection
    cursor.close()
    db.close()
    return name


@app.route("/")
def main_page():
    course_codes = get_course_table()
    return render_template("index.html",course_codes=course_codes)


@app.route("/see_course/<course_code>")
def see_course(course_code):
    # Construct the path to the directory where images are stored
    image_directory = os.path.join("static", "cloud_files_temporary", course_code)

    # Check if the directory exists
    if os.path.exists(image_directory):
        # Get a list of image files in the directory
        image_files = [file for file in os.listdir(image_directory) if file.endswith(('.jpg', '.jpeg', '.png', '.gif'))]
    else:
        image_files = []

    return render_template("see_course.html", course_code=course_code, image_files=image_files)


@app.route("/upload")
def upload():
    courses = get_course_table()
    return render_template("upload.html",courses=courses)


@app.route('/save', methods=['GET', 'POST'])
def save():
    course = request.form.get('course')
    if request.method == 'POST':
        if 'file' in request.files:
            file = request.files['file']
            if file.filename != '':
                path = "templates/requests/" + file.filename
                file.save(path)
                file_name = generate_amazon_S3_name(course)
                upload_file(file_name,path)
                print("File uploaded to the S3, {}".format(file_name))
    return redirect(url_for("main_page"))


if __name__ == '__main__':
    update_course_materials()
    app.run()
    remove_temporary_file()
