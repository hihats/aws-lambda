import json

def lambda_handler(event, context):
    datastr = event['data']
    print(datastr)
