import boto3
import os
import subprocess

def lambda_handler(event, context):
    s3_bin_dir = 'bin/'
    mysqldump_bin = 'mysqldump'
    mysqldump_option = ' --single-transaction'
    work_dir = '/tmp'

    # sets environmental variables (needs to be set in AWS Lambda)
    s3_bucket_name = os.environ['S3_BUCKET_NAME']

    mysql_endpoint = os.environ['ENDPOINT']
    mysql_user = os.environ['DB_USER']
    mysql_pass = os.environ['DB_PASSWORD']
    mysql_dbname = os.environ['DB_NAME']

    s3 = boto3.resource('s3')
    bucket = s3.Bucket(s3_bucket_name)
    bucket.download_file(s3_bin_dir + mysqldump_bin, work_dir + '/' + mysqldump_bin)

    mysqldump_ret = os.path.isfile(work_dir + '/' + mysqldump_bin)
    if mysqldump_ret is False:
        print(mysqldump_ret)
        return 1
    print('download finished')

    cmd = 'chmod 700 ' + work_dir + '/' + mysqldump_bin
    mysqldump_ret = os.system(cmd)
    if mysqldump_ret is False:
        print('chmod failed')
        return 2
    print('chmod finished')

    mysqldump_filename = mysql_dbname + '_current.sql'
    cmd = work_dir +  '/mysqldump' + ' -u' + mysql_user + ' -p' + \
          mysql_pass + ' -h' + mysql_endpoint + ' ' + mysql_dbname + \
          mysqldump_option + ' > ' + work_dir + '/' + mysqldump_filename
    ret = subprocess.getoutput(cmd)
    if ret.find('error') >-1:
        print(ret)
        return 3
    print('dump finished')

    backup_dir = 'backups/'
    s3 = boto3.client('s3') # change library
    s3.upload_file(work_dir + '/' + mysqldump_filename, s3_bucket_name, backup_dir + mysqldump_filename)
    print('upload finished')
