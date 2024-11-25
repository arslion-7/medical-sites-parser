import pymongo
import re

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

# client = pymongo.MongoClient('localhost', 27017)
# db = client['parser_db']
# collection = db['parser_collection']

# Define the query
query = {
    "addons.doi_url": {
        "$regex": "ijdvl",
    },
    "pdf_text_translation_human": {
      "$regex": r"\(/content/[^)]+\)",
    }
}

# Define the projection to return only the fields you want
projection = {
    "_id": 1,  # Include _id to be able to update the document
    "pdf_text": 1,
    "pdf_text_translation_human": 1,
    "pdf_text_translation_ai": 1
}

# Define the replacement function
def replace_content_urls(text):
    # Check if the text is None and replace it with an empty string
    if text is None:
        text = ''
    return re.sub(r"\(/content/", "(https://ijdvl.com/content/", text)

if __name__ == '__main__':
    doc_count = collection.count_documents(query)
    print('doc_count:', doc_count)
    
    # Find documents matching the query
    results = collection.find(query, projection)
    
    for result in results:
        # Get the current values and handle None by defaulting to an empty string
        pdf_text = result.get('pdf_text', '') or ''
        pdf_text_translation_human = result.get('pdf_text_translation_human', '') or ''
        pdf_text_translation_ai = result.get('pdf_text_translation_ai', '') or ''
        
        # Replace the values
        updated_pdf_text = replace_content_urls(pdf_text)
        updated_pdf_text_translation_human = replace_content_urls(pdf_text_translation_human)
        updated_pdf_text_translation_ai = replace_content_urls(pdf_text_translation_ai)
        
        # Update the document if changes were made
        if (pdf_text != updated_pdf_text or
            pdf_text_translation_human != updated_pdf_text_translation_human or
            pdf_text_translation_ai != updated_pdf_text_translation_ai):
            
            collection.update_one(
                {'_id': result['_id']},
                {'$set': {
                    'pdf_text': updated_pdf_text,
                    'pdf_text_translation_human': updated_pdf_text_translation_human,
                    'pdf_text_translation_ai': updated_pdf_text_translation_ai
                }}
            )
            print(f'Document with _id {result["_id"]} updated.')