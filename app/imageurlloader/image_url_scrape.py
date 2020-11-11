import boto3
import logging
import os
import requests
import pandas as pd
from bs4 import BeautifulSoup
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

def getImageUrlForTitle(reftitle, reftitleid):
    url = 'http://www.imdb.com/title/{}'.format(reftitleid)
    titleString = '{} Poster'.format(reftitle)
    response = requests.get(url).content
    soup = BeautifulSoup(response, 'html.parser')
    imgs = []
    for link in soup.find_all('img', title=titleString):
        imgs.append(link.get('src'))
    if len(imgs) > 0:
        logger.info("Img URL for {} is {}".format(reftitle, imgs[0]))
        return imgs[0]
    else:
        logger.info("No Img URL found for {}".format(reftitle))
        return ""
        
def updateImagesUrls(df_titles, table_name, dynamodb_resource):
    for index, row in df_titles.iterrows():
        #logger.info("checking row {}".format(row))
        if (not 'imageurl' in row) or (pd.isna(row['imageurl'])) or (pd.isnull(row['imageurl'])) or (row['imageurl'] == ""):
            img_url_for_title = getImageUrlForTitle(row['title'], row['titleid'])
            if img_url_for_title != "":
                logger.info("updating img_url for {} to {}".format(index, img_url_for_title))
                table = dynamodb_resource.Table(table_name)
                response = table.update_item(
                    Key={
                        'label': row['label'],
                        'titleid': row['titleid']
                    },
                    UpdateExpression='SET imageurl = :val1',
                    ExpressionAttributeValues={
                        ':val1': img_url_for_title
                    }
                )


def main(args):
    tableName = args['tableName']
    loggerLevel = logging.__dict__[args['loggerLevel']]
    dynamodb_resource = boto3.resource('dynamodb', region_name='ap-southeast-2')
    
    try: 
        setupLogger(loggerLevel)
        logger.info('Starting...')
        response = getTableScanResponse(tableName, dynamodb_resource)
        df_titles = getTitles(response)
        #logger.info('titles[0]: {}'.format(df_titles.iloc[0]))
        updateImagesUrls(df_titles, tableName, dynamodb_resource)
        logger.info('Done!')
    except:
        logger.exception('Error in processing!')
    finally:
        logger.info('Finally block done!')
 
def event_handler(event, context):
    args = dict()
    args['loggerLevel'] = os.environ['LOGGER_LEVEL']
    args['tableName'] = os.environ['TABLE_NAME']
    
    logger.info('Args: {}'.format(args))
    
    main(args)      

