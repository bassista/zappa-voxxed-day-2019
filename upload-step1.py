import os
from flask import Flask, flash, request, redirect, render_template
from werkzeug.utils import secure_filename
import boto3

# Global ariables
UPLOAD_FOLDER = '/tmp'
S3_BUCKET_NAME="zappa-lambda-bucket-ireland"
S3_BUCKET_NAME_THUMBNAIL="zappa-lambda-bucket-ireland-thumb"
ALLOWED_EXTENSIONS = set(['jpg', 'jpeg'])
##

app = Flask(__name__)
app.secret_key = "secret key"

## Utility function
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_to_s3(filename, bucket_name, key_name):
    s3 = boto3.resource('s3')
    s3.meta.client.upload_file(filename, bucket_name, key_name)
##

# Lambda Function
@app.route('/')
def upload_form():
    return render_template('upload.html')

@app.route('/', methods=['POST'])
def upload_file():
    print "upload start"
    try:
        if request.method == 'POST':
            # check if the post request has the file part
           if 'file' not in request.files:
             flash('No file part')
             return redirect(request.url)
           file = request.files['file']
           if file.filename == '':
             flash('No file selected for uploading')
             return redirect(request.url)
           if file and allowed_file(file.filename):
             filename = secure_filename(file.filename)
             file.save(os.path.join(UPLOAD_FOLDER, filename))
             save_to_s3(os.path.join("thumbnail-", UPLOAD_FOLDER, filename), S3_BUCKET_NAME, file.filename)
             flash('File(s) successfully uploaded')
             return redirect('/upload')
    except Exception as e:
        flash('Error in uploading file')
        print e
        return redirect('/upload')

if __name__ == "__main__":
    app.run(port=8080, host='0.0.0.0')