from datetime import datetime
# for testing purposes
from pymongo import MongoClient

from db.mongodb import get_num_tokens
# Connect to the local MongoDB instance
client = MongoClient('localhost', 27017)
# Specify the database name
db = client['parser_db']
# Specify the collection name
collection = db['parser_collection']


def test_save_article(mainUrl, articleUrl, title, date, content, authors=[], pdf_text='', references=[], doi_url='', has_images=False, category=None, subcategory=None):
    content_token, pdf_token = 0, 0
    if content:
        content_token = get_num_tokens(content)
    if pdf_text:
        pdf_token = get_num_tokens(pdf_text)
    
    # Construct the base update document
    update_doc = {
        '$set': {
            'mainUrl': mainUrl,
            'articleUrl': articleUrl,
            'title': title,
            'publishedDate': date,
            'content': content,
            'authors': authors,
            'pdf_text': pdf_text,
            'references': references,
            'has_images': has_images,
            'tokenCount': {
                'contentTokenCount': content_token,
                'pdfTokenCount': pdf_token,
            },
            'addons.doi_url': doi_url,
            "updatedAt": datetime.utcnow()
        },
        "$setOnInsert": {"createdAt": datetime.utcnow()}
    }

    # Add category and subcategory only if they are not None
    if category is not None:
        update_doc['$set']['category'] = category
    if subcategory is not None:
        update_doc['$set']['subcategory'] = subcategory

    # Perform the update
    collection.update_one(
        {'articleUrl': articleUrl},
        update_doc,
        upsert=True,
    )
