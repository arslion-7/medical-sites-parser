from pymongo import MongoClient


# client = MongoClient('localhost', 27017)

# # Specify the database and collection
# db = client['parser_db']
# collection = db['parser_collection']

DATABASE_NAME = 'telegram_client'
DB_URL = "mongodb://{user}:{pw}@{host}/{db}?replicaSet={rs}&appName=mongosh+2.0.0".format(
    user='telegram_user',
    pw='zaiv6ahdohp8eicheereeph5ieBah9qu',
    host='rc1b-ozt5tmyq4i4zzdxw.mdb.yandexcloud.net:27018',
    db=DATABASE_NAME,
    rs='rs01'
)

db = MongoClient(
    DB_URL,
    tls=True,
    tlsCAFile='root.crt')[DATABASE_NAME]

collection = db.parsedSites
# Connect to MongoDB

# Define the string to remove
string_to_remove = "Открыть в программе просмотра слайдов PowerPoint"

# Find all documents and update the "pdf_text" field
for document in collection.find({"pdf_text_translation_human": {"$regex": string_to_remove}}):
    # updated_pdf_text = document["pdf_text"].replace(string_to_remove, "")
    updated_pdf_text_translation_ai_text = document["pdf_text_translation_ai"].replace(string_to_remove, "")
    updated_pdf_text_translation_human_text = document["pdf_text_translation_human"].replace(string_to_remove, "")

    
    # Update the document in the collection
    collection.update_one(
        {"_id": document["_id"]},
        {"$set": {
            "pdf_text_translation_ai": updated_pdf_text_translation_ai_text,
              "pdf_text_translation_human": updated_pdf_text_translation_human_text
              }}
    )

print("Text removal complete.")