import pymongo
from datetime import datetime
import tiktoken

def get_num_tokens(text: str) -> int:
    encoding = tiktoken.encoding_for_model("gpt-4")
    return len(encoding.encode(text))

DATABASE_NAME = 'some_name'
DB_URL = 'some_url'

db = pymongo.MongoClient(
    DB_URL,
    tls=True,
    tlsCAFile='root.crt')[DATABASE_NAME]


# def save_article(mainUrl, articleUrl, title, date, content, authors = [], pdf_text='', references=[], doi_url = ''):
#     content_token, pdf_token = 0, 0 
#     if content: 
#         content_token = get_num_tokens(content)

#     if pdf_text:
#         pdf_token = get_num_tokens(pdf_text)
        
#     db.parsedSites.update_one(
#         {'articleUrl': articleUrl},
#         {'$set': {
#             'mainUrl': mainUrl,
#             'articleUrl': articleUrl,
#             'title': title,
#             'publishedDate': date,
#             'content': content,
#             'authors': authors,
#             'pdf_text': pdf_text,
#             'references': references,
#             'tokenCount': {
#                 'contentTokenCount': content_token,
#                 'pdfTokenCount': pdf_token,
#             },
#             'addons.doi_url': doi_url, 
#             "updatedAt": datetime.utcnow()
#         },
#          "$setOnInsert": {"createdAt": datetime.utcnow()}
#         },
#         upsert=True,
#     )

def save_article(mainUrl, articleUrl, title, date, content, authors=[], pdf_text='', references=[], doi_url='', has_images=False, category=None, subcategory=None):
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
    db.parsedSites.update_one(
        {'articleUrl': articleUrl},
        update_doc,
        upsert=True,
    )


def get_not_indexed_articles():
    query = {
    "$or": [
        {"isIndexed": False},
        {"isIndexed": {"$exists": False}}
    ]
}
    documents = db.parsedSites.find(query)

    return documents

def get_not_indexed_pdf_articles():
    query = {
        "$and": [
            {"pdf_text": {"$exists": True}},
            {"pdf_text": {"$ne": ""}},
            {"$or": [
                {"isPDFIndexed": False},
                {"isPDFIndexed": {"$exists": False}}
            ]}
        ]
    }
    documents = db.parsedSites.find(query)

    return documents

def get_not_indexed_published_articles():
    query = {
        "$and": [
            {"isPublished": True},
            {"isTranslationIndexed": {"$ne": True}}
        ]
    }

    documents = db.parsedSites.find(query)

    return documents

def update_translation_indexed_status(articleUrl:str, isTranslationIndexed:bool):
    db.parsedSites.update_one(
        {"articleUrl": articleUrl},
        {'$set': {
            "isTranslationIndexed": isTranslationIndexed,
            "updatedAt": datetime.utcnow()
        }},
        upsert=False,
    )

def update_indexed_status(articleUrl:str, isIndexed:bool):
     db.parsedSites.update_one(
        {'articleUrl': articleUrl},
        {'$set': {
            'isIndexed': isIndexed,
            "updatedAt": datetime.utcnow()
        },
        },
        upsert=False,
    )
     
def update_pdf_indexed_status(articleUrl:str, isPDFIndexed:bool):
    db.parsedSites.update_one(
        {'articleUrl': articleUrl},
        {'$set': {
            'isPDFIndexed': isPDFIndexed,
            "updatedAt": datetime.utcnow()
        },
        },
        upsert=False,
    )