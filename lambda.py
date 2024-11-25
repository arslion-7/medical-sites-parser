import json
from datetime import datetime
import pymongo

DATABASE_NAME = 'telegram_client'
DB_URL = "mongodb://{user}:{pw}@{host}/{db}?replicaSet={rs}&appName=mongosh+2.0.0".format(
    user='telegram_user',
    pw='zaiv6ahdohp8eicheereeph5ieBah9qu',
    host='rc1b-ozt5tmyq4i4zzdxw.mdb.yandexcloud.net:27018',
    db=DATABASE_NAME,
    rs='rs01'
)

db = pymongo.MongoClient(
    DB_URL,
    tls=True,
    tlsCAFile='root.crt')[DATABASE_NAME]

def get_parsed_articles(event, context):
    query = event.get("queryStringParameters", {})
    date_str = query.get('date', '')
    if not date_str:
        return {
            'statusCode': 400,
            'headers': {'Content-Type': 'application/json; charset=utf-8'},
            'body': json.dumps({'error': 'date parameter is required'})
        }

    try:
        date = datetime.strptime(date_str, '%Y-%m-%d')
    except ValueError:
        return {
            'statusCode': 400,
            'headers': {'Content-Type': 'application/json; charset=utf-8'},
            'body': json.dumps({'error': 'date parameter must be in YYYY-MM-DD format'})
        }
    
    query = {
        '$or': [
            {'createdAt': {'$gte': date, '$lt': date.replace(hour=23, minute=59, second=59, microsecond=999999)}},
            {'updatedAt': {'$gte': date, '$lt': date.replace(hour=23, minute=59, second=59, microsecond=999999)}}
        ]
    }

    documents = list(db.parsedSites.find(query, {'_id': 0}))

    filtered_docs = []
    # Convert dates to ISO format
    for doc in documents:
        if 'publishedDate' in doc:
            doc['publishedDate'] = doc['publishedDate'].isoformat()
        if 'createdAt' in doc:
            doc['createdAt'] = doc['createdAt'].isoformat()
        if 'updatedAt' in doc:
            doc['updatedAt'] = doc['updatedAt'].isoformat()
        
        filtered_docs.append(doc)
    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'application/json; charset=utf-8'},
        'body': json.dumps(filtered_docs)
    }

# result = get_parsed_articles("", "")
# print(result)