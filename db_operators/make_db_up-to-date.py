import boto3
import os
import subprocess

def lambda_handler(event, context):
    s3_bin_dir = 'bin/'
    mysqldump_bin = 'mysqldump'
    mysqldump_option = ' --single-transaction'
    mysqlcmd = 'mysql'
    work_dir = '/tmp'

    # sets environmental variables (needs to be set in AWS Lambda)
    s3_bucket_name = os.environ['S3_BUCKET_NAME']
    path_mask_sql_file = os.environ['PATH_TO_MASK_SQL_FILE']

    mysql_endpoint = os.environ['ENDPOINT']
    mysql_user = os.environ['DB_USER']
    mysql_pass = os.environ['DB_PASSWORD']
    mysql_dbname = os.environ['DB_NAME']

    mysql_target_endpoint = os.environ['TARGET_ENDPOINT']
    mysql_target_user = os.environ['TARGET_DB_USER']
    mysql_target_pass = os.environ['TARGET_DB_PASSWORD']
    mysql_target_dbname = os.environ['TARGET_DB_NAME']

    print('process started')
    s3 = boto3.resource('s3')
    bucket = s3.Bucket(s3_bucket_name)
    bucket.download_file(s3_bin_dir + mysqldump_bin, work_dir + '/' + mysqldump_bin)
    bucket.download_file(s3_bin_dir + mysqlcmd, work_dir + '/' + mysqlcmd)
    bucket.download_file(path_mask_sql_file, work_dir + '/mask_private.sql')

    mysqldump_ret = os.path.isfile(work_dir + '/' + mysqldump_bin)
    mysqldump_ret = os.path.isfile(work_dir + '/' + mysqlcmd)
    mask_sql_ret = os.path.isfile(work_dir + '/mask_private.sql')
    # check if downloaded files exist
    if mysqldump_ret is False or mysql_ret is False or mask_sql_ret is False:
        print(mysqldump_ret)
        print(mysql_ret)
        print(mask_sql_ret)
        return 1
    print('download finished')

    cmd = 'chmod 700 ' + work_dir + '/' + mysqldump_bin
    mysqldump_ret = os.system(cmd)
    cmd = 'chmod 700 ' + work_dir + '/' + mysqlcmd
    mysql_ret = os.system(cmd)
    if mysqldump_ret is False or mysql_ret is False:
        print('chmod failed')
        return 2
    print('chmod finished')

    mysqldump_filename = mysql_dbname + '.sql'
    cmd = work_dir +  '/mysqldump' + ' -u' + mysql_user + ' -p' + \
          mysql_pass + ' -h' + mysql_endpoint + ' ' + mysql_dbname + \
          mysqldump_option + ' > ' + work_dir + '/' + mysqldump_filename
    ret = subprocess.getoutput(cmd)
    if ret.find('error') >-1:
        print(ret)
        return 3
    print('dump finished')

    importcmd = work_dir + '/' + mysqlcmd + ' -u' + mysql_target_user + ' -p' + mysql_target_pass + ' -h' + mysql_target_endpoint + ' ' + mysql_target_dbname + ' < ' + work_dir + '/' + mysqldump_filename
    ret = subprocess.getoutput(importcmd)
    if ret.find('error') >-1:
        print(ret)
        return 5
    print('import finished')

    maskcmd = work_dir + '/' + mysqlcmd + ' -u' + mysql_target_user + ' -p' + mysql_target_pass + ' -h' + mysql_target_endpoint + ' ' + mysql_target_dbname + ' < ' + work_dir + '/mask_private.sql'
    ret = subprocess.getoutput(maskcmd)
    if ret.find('error') >-1:
        print(ret)
        return 6
    print('masking private data was finished')

    backup_dir = 'backups/'
    s3 = boto3.client('s3')
    #s3.upload_file(work_dir + '/' + mysqldump_filename, s3_bucket_name, backup_dir + mysqldump_filename)
    #print('upload finished')
