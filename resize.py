import os, sys
from PIL import Image
import boto3

size = 128, 128

S3_BUCKET_NAME="zappa-lambda-bucket-ireland-thumb"

def resize(event, context):
    print "Stampo evento:"
    print event
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
            save_to_s3(outfile, S3_BUCKET_NAME, key)
        except Exception as e:
            print e

def save_to_s3(filename, bucket_name, key_name):
    s3 = boto3.resource('s3')
    s3.meta.client.upload_file(filename, bucket_name, key_name)