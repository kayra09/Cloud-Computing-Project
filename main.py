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
def get_post_table():
    db = mysql.connector.connect(host='localhost', database='capstone_project', user='root', password='root')
    cursor = db.cursor()
    cursor.execute("SELECT * FROM post")
    posts = cursor.fetchall()
    return posts

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
    cursor.execute("SELECT * FROM post WHERE course_code = %s", (course_code,))
    result = cursor.fetchall()
    result = result[-1]
    result = result[0] +1
    name += str(result)
    # Close the database connection
    cursor.close()
    db.close()
    return name
def publish(course):
    aws_access_key_id = 'AKIA2CXPV6DKX4F46E4S'
    aws_secret_access_key = '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'
    sns_client = boto3.client('sns', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key,
                              region_name="us-east-1")
    topic_arn = "arn:aws:sns:us-east-1:693066133717:" + str(course)
    message = "There is a new upload in " + str(course) + "."
    response = sns_client.publish(
        TopicArn=topic_arn,
        Message=message,
        Subject='New upload',  # Replace with your subject
    )
    return 0


def delete_file(file_name):
    aws_access_key_id = 'AKIA2CXPV6DKX4F46E4S'
    aws_secret_access_key = 'IfO7aBeFYUWfh5viG+k8SjpFG7qOC7fDNbIXhSms'
    bucket_name = 'cng495'
    s3_key = str(file_name) + ".jpg"

    # Delete from S3 bucket
    s3 = boto3.client('s3', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)
    s3.delete_object(Bucket=bucket_name, Key=s3_key)

    # Delete from the database
    db = mysql.connector.connect(host='localhost', database='capstone_project', user='root', password='root')
    cursor = db.cursor()

    # Assuming file_name is the primary key in the database
    file_name_parts = file_name.split("_")
    cursor.execute("DELETE FROM POST WHERE idpost = %s AND course_code = %s", (int(file_name_parts[1]), file_name_parts[0]))
    db.commit()

def permission():
    aws_access_key_id = 'AKIA2CXPV6DKX4F46E4S'
    aws_secret_access_key = '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'
    bucket_name = 'cng495'
    s3 = boto3.client('s3', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)
    object_key = 'cng499_3.jpg'
    response = s3.get_object_acl(Bucket=bucket_name, Key=object_key)

    print("Object ACLs:")
    for grant in response['Grants']:
        print(grant)

@app.route("/")
def main_page():
    session["admin_login"] = 0
    course_codes = get_course_table()
    remove_temporary_file()
    return render_template("index.html",course_codes=course_codes)
@app.route("/admin")
def admin_login_page():
    if session["admin_login"] == 1:
        return render_template("admin_panel.html")
    else:
        return render_template("admin_login_page.html")
@app.route("/admin_login",methods=['GET', 'POST'])
def admin_login():
    username = request.form.get('username')
    password = request.form.get('password')

    db = mysql.connector.connect(host='localhost', database='capstone_project', user='root', password='root')
    cursor = db.cursor()
    cursor.execute("SELECT * FROM admin")
    user_list = cursor.fetchall()

    for user in user_list:
        if user[0] == username and user[1] == password:
            session["admin_login"] = 1
            return render_template("admin_panel.html")
        else:
            return redirect(url_for("main_page"))
@app.route("/see_course/<course_code>")
def see_course(course_code):
    retrieve_files(str(course_code))
    image_directory = os.path.join("static", "cloud_files_temporary", course_code)

    # Check if the directory exists
    if os.path.exists(image_directory):
        # Get a list of image files in the directory
        image_files = [file for file in os.listdir(image_directory) if file.endswith(('.jpg', '.jpeg', '.png', '.gif'))]
    else:
        image_files = []
    return render_template("see_course.html", course_code=course_code, image_files=image_files)
@app.route("/delete_photos")
def delete_photos_page():
    posts=get_post_table()
    return render_template("delete_photos_page.html",posts=posts)
@app.route("/view_and_delete/<post_id>/<course_code>")
def get_selected_photo(post_id,course_code):
    retrieve_file(course_code + "_" + str(post_id), post_id)
    return render_template("selected_photo.html",post_id=post_id,course_code=course_code)

@app.route("/delete_image/<course_code>/<post_id>")
def delete_post(course_code, post_id):
    file_name = str(course_code) + "_" + str(post_id)
    delete_file(file_name)
    return render_template("admin_panel.html")

@app.route("/logout")
def logout():
    session["admin_login"] = 0
    return redirect(url_for("main_page"))
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
                os.remove(path)
                print("File uploaded to the S3, {}".format(file_name))
    publish(course)
    return redirect(url_for("main_page"))
@app.route("/sub_page")
def sub_page():
    courses = get_course_table()
    return render_template("sub_page.html",courses=courses)
@app.route("/add_sub",methods=['POST'])
def add_sub():
    aws_access_key_id = 'AKIA2CXPV6DKX4F46E4S'
    aws_secret_access_key = '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'
    email = request.form.get('email')
    course = request.form.get('course')
    sns_client = boto3.client('sns', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key, region_name="us-east-1")
    if course == "cng100":
        response = sns_client.subscribe(
            TopicArn="arn:aws:sns:us-east-1:693066133717:cng100",
            Protocol='email',
            Endpoint=email
        )
    if course == "cng499":
        response = sns_client.subscribe(
            TopicArn="arn:aws:sns:us-east-1:693066133717:cng499",
            Protocol="email",
            Endpoint=email
        )
    return redirect(url_for("main_page"))
if __name__ == '__main__':
    permission()
    app.run()
