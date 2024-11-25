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

# Define the projection to return only the field you want
projection = {
    "_id": 0,  # Exclude the _id field
    "pdf_text_translation_human": 1  # Include only the addons.doi_url field
}

if __name__ == '__main__':
  document = collection.find_one({"articleUrl": 'https://www.pubmed.ncbi.nlm.nih.gov/39152890/'})
