import boto3
import logging
import os
import pandas as pd
import json
import requests
from bs4 import BeautifulSoup

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

def searchForTitles(df_titles, searchString):
    logger.info("Searching for {}".format(searchString))
    movies = df_titles[df_titles['title'].str.contains(searchString, case=False)]
    return movies

def recommendTitlesForTitleId(df_titles, reftitle):
    logger.info("Recommending for {}".format(reftitle))
    label = df_titles[df_titles['titleid'] == reftitle]['label'].iloc[0]
    movies = df_titles[df_titles['label'] == label].sample(20)
    return movies
    
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

def getImagesUrlColumn(df_titles):
    img_urls = []
    for index, row in df_titles.iterrows():
        val = getImageUrlForTitle(row['title'], row['titleid'])
        img_urls.append(val)
    return img_urls

def main(args, event):
    tableName = args['tableName']
    loggerLevel = logging.__dict__[args['loggerLevel']]
    dynamodb_resource = boto3.resource('dynamodb', region_name='ap-southeast-2')
    return_titles = pd.DataFrame()

    try: 
        setupLogger(loggerLevel)
        logger.info('Starting...')
        logger.info('Event: {}'.format(event))
        response = getTableScanResponse(tableName, dynamodb_resource)
        df_titles = getTitles(response)

        if "queryStringParameters" in event and event["queryStringParameters"]:
            if "search" in event["queryStringParameters"] and event["queryStringParameters"]["search"]:
                return_titles = searchForTitles(df_titles, event["queryStringParameters"]["search"])
            elif "recommendfortitle" in event["queryStringParameters"] and event["queryStringParameters"]["recommendfortitle"]:
                return_titles = recommendTitlesForTitleId(df_titles, event["queryStringParameters"]["recommendfortitle"])
            else:
                logger.error('Invalid query type!')
                
        #DON'T ENABLE THIS, (a) T.O.S for IMDB probably forbids scraping of data, and (b), it's reaaaaly slow!
        # Consider saving the jpg data to the movie data table or s3 for use
        #df_img_urls = getImagesUrlColumn(return_titles)
        #return_titles = pd.concat([return_titles, df_img_urls], axis=1, sort=False)

        logger.info('Done!')
    except:
        logger.exception('Error in processing!')
        return { 
            'statusCode': 500,
            'headers': {
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
            },
            'body': json.dumps({'Error' : 'Error in processing!'}),
            'isBase64Encoded': False
        }
    finally:
        logger.info('Finally Done!')

    return { 
        'statusCode': 200,
        'headers': {
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
        },
        'body': json.dumps({'titles' : return_titles.to_json(orient="records")}),
        'isBase64Encoded': False
    }
 
def event_handler(event, context):
    args = dict()
    args['loggerLevel'] = os.environ['LOGGER_LEVEL']
    args['tableName'] = os.environ['TABLE_NAME']
    
    logger.info('Args: {}'.format(args))
    
    return main(args, event)

