import logging
import re
import pymongo


# set up logging to file
logging.basicConfig(
     filename='move_conflicts.log',
     level=logging.INFO, 
     format= '[%(asctime)s] {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s',
     datefmt='%H:%M:%S'
 )

logger = logging.getLogger(__name__)


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
# query = {
#     "addons.doi_url": {
#         "$regex": "mdpi.com",
#     },
# }

query = {
    "content": {
        "$regex": "^## Conflict of interest statement",
    },
}

# Define the projection to return only the field you want
# projection = {
#     "_id": 0,  # Exclude the _id field
#     "articleUrl": 1  # Include only the addons.doi_url field
# }

if __name__ == '__main__':
#   documents = collection.find(query, projection)[:1]
  documents = collection.find(query)

  logger.info('aaaa')
  # Print the results
# for doc in documents:
#     content = doc['content']
#     # Split the content into lines
#     lines = content.split('\n')
    
#     # Extract the first two lines
#     first_two_lines = lines[0:2]
#     # Extract the remaining lines
#     remaining_content = lines[2:]
    
#     # Combine remaining content with the first two lines at the end
#     updated_content = '\n'.join(remaining_content + first_two_lines)
    
#     # Update the document
#     collection.update_one(
#         {"_id": doc["_id"]},
#         {"$set": {"content": updated_content}}
#     )

#     print(f"Updated document ID: {doc['_id']}")
#     print(f'"{doc['articleUrl']}",')