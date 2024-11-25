from db.mongodb import get_not_indexed_articles, update_indexed_status, get_not_indexed_pdf_articles, update_pdf_indexed_status, get_not_indexed_published_articles, update_translation_indexed_status
import http.client
import json, logging

logger = logging.getLogger(__name__)

def index_articles():
    notIndexedArticles = get_not_indexed_articles()

    for article in notIndexedArticles:
        try:
            status, msg = index_article(article["articleUrl"], article["content"], namespace="atopianews", index="atopianews")
            if status == 200 and msg == "Success indexed an article":
                update_indexed_status(article["articleUrl"], True)
                # logger.info("successfully indexed article {}".format(article["articleUrl"]))
            else:
                update_indexed_status(article["articleUrl"], False)
                logger.error("failed to index article {}.".format(article["articleUrl"]))

        except Exception as e:
            logger.error("something went wrong while indexing article {} : {}".format(article["articleUrl"], str(e)))

def index_articles_pdf():
    notIndexedArticles = get_not_indexed_pdf_articles()

    for article in notIndexedArticles:
        try:
            status, msg = index_article(article["articleUrl"], article["pdf_text"], namespace="atopianews", index="atopianews")
            if status == 200 and msg == "Success indexed an article":
                update_pdf_indexed_status(article["articleUrl"], True)
                # logger.info("successfully indexed article pdf {}".format(article["articleUrl"]))
            else:
                update_pdf_indexed_status(article["articleUrl"], False)
                logger.error("failed to index article pdf {}".format(article["articleUrl"]))

        except Exception as e:
            logger.error("something went wrong while indexing article pdf {} : {}".format(article["articleUrl"], str(e)))


def index_published_articles():
    published_articles = get_not_indexed_published_articles()
    
    for article in published_articles:
        try:
            status, msg = index_article(article["articleUrl"], article["translation_human"], namespace="atopianews2", index="atopianews")
            if status == 200 and msg == "Success indexed an article":
                update_translation_indexed_status(article['articleUrl'], True)
                logger.info("indexed {}".format(article["articleUrl"]))

            else:
                update_translation_indexed_status(article['articleUrl'], False)
                logger.error("failed to index article translation {}.".format(article["articleUrl"]))

        except Exception as e:
            logger.error("something went wrong while indexing article translation {} : {}".format(article["articleUrl"], str(e)))

def index_article(url, text, namespace, index):
    conn = http.client.HTTPSConnection("functions.yandexcloud.net")

    payload = {
        "url": url,
        "text": text
    }
    payload_str = json.dumps(payload)
    headers = {
        'Content-Type': "application/json",
        'User-Agent': "insomnia/9.0.0"
        }

    conn.request("POST", f"/d4ejq3uthmcfado341qo?action=index_article_text_with_url&namespace={namespace}&index={index}", payload_str, headers)

    res = conn.getresponse()
    data = res.read()

    return res.status, data.decode("utf-8")


# index_articles()