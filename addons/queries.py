import re
import pymongo

from helper import write_to_file


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

collection = db.parsedSites

# Define the query
query = {
    "articleUrl": {
        "$regex": "onlinelibrary.wiley.com",
    },
    'pdf_text_translation_ai': {'$exists': True, '$ne': ''},
    'pdf_text': {'$regex': 'Table '}
}



# { articleUrl: RegExp('onlinelibrary.wiley.com'), pdf_text: RegExp('table '), pdf_text_summary_human: {$exists: true, $ne: ''} }

# query = {
#     "addons.doi_url": {
#         "$regex": "mdpi",
#     },
#     'pdf_text_translation_ai': {'$exists': True, '$ne': ''},
#     'pdf_text': {'$regex': 'Table '}
# }

# query = {
#     "content": {
#         "$regex": "^## Conflict of interest statement",
#     },
# }

# Define the projection to return only the field you want
projection = {
    "_id": 0,  # Exclude the _id field
    "articleUrl" : 1,
    "pdf_text_translation_human": 1  # Include only the addons.doi_url field
}

if __name__ == '__main__':
  results = collection.find(query, projection)
  # Print the results
#   write_to_file('resul.md', result['pdf_text_translation_human'])
  i = 1
  for result in results:
      print(i)
      print(f'"{result['articleUrl']}",')
      write_to_file('resul.md', f'"{result['articleUrl']}",\n', mode='a')
      i += 1