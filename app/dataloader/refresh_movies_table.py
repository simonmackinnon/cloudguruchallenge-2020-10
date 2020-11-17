import argparse
import boto3
import logging
import os
import pandas as pd

from datetime import datetime, timedelta
from botocore.exceptions import ClientError

logger = logging.getLogger()

def setupLogger(loggerLevel):
    global logger
    logger.setLevel(loggerLevel)
    logging.basicConfig(
        format='%(asctime)s %(levelname)-8s %(message)s',
        level=loggerLevel,
        datefmt='%d-%m-%Y %H:%M:%S')

def tableIsEmpty(response):
    return response['Count'] == 0

def getTitles(response):
    if not tableIsEmpty(response):
        items = response['Items']
        items.sort(key=lambda x: x['titleid'], reverse=True)
        df_items = pd.DataFrame(items)
        return df_items
    
    return pd.DataFrame()

def getTableScanResponse(table_name, dynamodb_resource):
    table = dynamodb_resource.Table(table_name)
    response = table.scan()
    return response
    
def getMoviesFile(bucket_name):
    if not os.path.exists('/tmp/download'):
        logger.info('Making dir: /tmp/download/')
        os.makedirs('/tmp/download/')
    
    filename = "titles/clustered_titles.csv"
    boto3.resource('s3').Bucket(bucket_name).download_file(filename, '/tmp/download/clustered_titles.csv')

    return '/tmp/download/clustered_titles.csv'

def getMoviesDataFrame(filename):
    df_titles = pd.read_csv(filename)
    df_titles.rename(columns={"Unnamed: 0": "title"}, inplace=True)
    return df_titles

def truncateTable(tableName):
    dynamodb_resource = boto3.resource('dynamodb', region_name='ap-southeast-2')

    table = dynamodb_resource.Table(tableName)
    
    #get the table keys
    tableKeyNames = [key.get("AttributeName") for key in table.key_schema]

    #Only retrieve the keys for each item in the table (minimize data transfer)
    projectionExpression = ", ".join('#' + key for key in tableKeyNames)
    expressionAttrNames = {'#'+key: key for key in tableKeyNames}
    
    counter = 0
    page = table.scan(ProjectionExpression=projectionExpression, ExpressionAttributeNames=expressionAttrNames)
    with table.batch_writer() as batch:
        while page["Count"] > 0:
            counter += page["Count"]
            # Delete items in batches
            for itemKeys in page["Items"]:
                batch.delete_item(Key=itemKeys)
            # Fetch the next page
            if 'LastEvaluatedKey' in page:
                page = table.scan(
                    ProjectionExpression=projectionExpression, ExpressionAttributeNames=expressionAttrNames,
                    ExclusiveStartKey=page['LastEvaluatedKey'])
            else:
                break
    logger.info("Deleted {}".format(counter))

def loadDataIntoTable(df_titles, tableName):
    
    dynamodb_resource = boto3.resource('dynamodb', region_name='ap-southeast-2')

    table = dynamodb_resource.Table(tableName)
    
    for index, row, in df_titles.iterrows(): 
        try:
            logger.info("putting record {}".format(row['title']))
            table.put_item(
                Item={
                    'titleid': row['title'].split(' ')[0],
                    'title': " ".join(row['title'].split()[1:]),
                    'label': row['labels']
                }
            )
        except ClientError as e:
            # Ignore the ConditionalCheckFailedException, bubble up
            # other exceptions.
            if e.response['Error']['Code'] != 'ConditionalCheckFailedException':
                raise

def updateDataInTable(df_titles, tableName):
    
    dynamodb_resource = boto3.resource('dynamodb', region_name='ap-southeast-2')

    table = dynamodb_resource.Table(tableName)

    scan_titles = getTitles(getTableScanResponse(tableName, dynamodb_resource))
    
    for index, row, in df_titles.iterrows(): 
        try:
            row_titleid = row['title'].split(' ')[0]
            row_title = " ".join(row['title'].split()[1:])
            row_label = row['labels']

            if not scan_titles[scan_titles['titleid'] == row_titleid].any():
                logger.info("putting record {}".format(row['title']))
                response = table.update_item(
                    Key={
                        'titleid': row_titleid,
                        'label': row_label
                    },
                    UpdateExpression='SET titleid = :titleid, title = :title, label = :lable',
                    ExpressionAttributeValues={
                        ':titleid': row_titleid,
                        ':title': row_title,
                        ':label': row_label
                    }
                )
        except ClientError as e:
            # Ignore the ConditionalCheckFailedException, bubble up
            # other exceptions.
            if e.response['Error']['Code'] != 'ConditionalCheckFailedException':
                raise


def main(args, event, context):
    bucketName = args['bucketName']
    tableName = args['tableName']
    loggerLevel = logging.__dict__[args['loggerLevel']]
    
    try: 
        setupLogger(loggerLevel)
        logger.info('Starting...')
        filename = getMoviesFile(bucketName)
        df_titles = getMoviesDataFrame(filename)
        if event.body.refresh:
            truncateTable(tableName)
            loadDataIntoTable(df_titles, tableName)
        else:
            updateDataInTable(df_titles, tableName)
        logger.info('Done!')
    except:
        logger.exception('Error in processing!')
    finally:
        logger.info('Finally Done!')
 
def event_handler(event, context):
    args = dict()
    args['loggerLevel'] = os.environ['LOGGER_LEVEL']
    args['bucketName'] = os.environ['BUCKET_NAME']
    args['tableName'] = os.environ['TABLE_NAME']
    
    logger.info('Args: {}'.format(args))
    
    main(args, event, context)      

