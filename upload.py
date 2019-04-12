import os
from flask import Flask, flash, request, redirect, render_template
from werkzeug.utils import secure_filename
import boto3

UPLOAD_FOLDER = '/tmp'

FUNC_NAME='upload'

app = Flask(__name__)
app.secret_key = "secret key"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

S3_BUCKET_NAME="zappa-lambda-bucket-ireland"
S3_BUCKET_NAME_THUMBNAIL="zappa-lambda-bucket-ireland-thumb"

ALLOWED_EXTENSIONS = set(['jpg', 'jpeg'])

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_to_s3(filename, bucket_name, key_name):
    s3 = boto3.resource('s3')
    s3.meta.client.upload_file(filename, bucket_name, key_name)

def resize(event, context):
    client = boto3.client('s3')
    for record in event['Records']:
        bucket_name = record['s3']['bucket']['name']
        key = record['s3']['object']['key']
        local_path = '/tmp/' + key.split('/')[-1]
        print "Download del file %s dal bucket %s" % (key, bucket_name)
        client.download_file(bucket_name, key, local_path)
        outfile = os.path.splitext(local_path)[0] + ".thumbnail"
        try:
            im = Image.open(local_path)
            im.thumbnail(size)
            im.save(outfile, "JPEG")
            im.close()
            save_to_s3(outfile, S3_BUCKET_NAME_THUMBNAIL, key)
        except Exception as e:
            print e

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
             print "ok"
             filename = secure_filename(file.filename)
             file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
             save_to_s3(os.path.join(app.config['UPLOAD_FOLDER'], filename), S3_BUCKET_NAME, file.filename)
             flash('File(s) successfully uploaded')
             return redirect('/upload')
    except Exception as e:
        flash('Error in uploading file')
        print e
        return redirect('/upload')

@app.route('/gallery/')
@app.route('/gallery')
def gallery():
    conn = client('s3')
    for key in conn.list_objects(Bucket=S3_BUCKET_NAME_THUMBNAIL)['Contents']:
        print(key['Key'])
    return render_template('gallery.html')

if __name__ == "__main__":
    app.run(port=8080, host='0.0.0.0')