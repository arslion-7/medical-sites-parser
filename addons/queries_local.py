import re
import pymongo
from pymongo import MongoClient

from helper import write_to_file


client = MongoClient('localhost', 27017)
# Specify the database name
db = client['parser_db']
# Specify the collection name
collection = db['parser_collection']

# Define the query
query = {
    "articleUrl": {
        "$regex": "onlinelibrary.wiley.com",
    },
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
    #   print(i)
      print(f'"{result['articleUrl']}",')
      write_to_file('resul.md', f'"{result['articleUrl']}",\n', mode='a')
      i += 1