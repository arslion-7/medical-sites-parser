import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import time
from helper import parse_date, create_session, fetch_url
from db.mongodb import save_article
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging

logger = logging.getLogger(__name__)

# API_URL_NEWS = "https://www.mdedge9-ma1.mdedge.com/api/v1/taxonomy?alias=dermatology&page={page_number}&topic=0&_format=json"
# headers ={
#     "Authorization" : "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsImp0aSI6IjkwNzViYWVjYTFhYzhlNTgwYWI5ZjQwMzQ3M2JiZjQxYzRlNWY2OWE2MWRmYWY4ODI2N2I1MjA4NGMwZTgxZjE3ZTEwZDljM2YzMmQ4MDI4In0.eyJhdWQiOiIxNzIwMDE5MS00MjlkLTQyMzgtOTY1My1kZTNhMDRhN2MwYzUiLCJqdGkiOiI5MDc1YmFlY2ExYWM4ZTU4MGFiOWY0MDM0NzNiYmY0MWM0ZTVmNjlhNjFkZmFmODgyNjdiNTIwODRjMGU4MWYxN2UxMGQ5YzNmMzJkODAyOCIsImlhdCI6MTcxODk4OTM1MiwibmJmIjoxNzE4OTg5MzUyLCJleHAiOjE3MjAxOTg5NTIuOTM0MDc1LCJzdWIiOiIxNDM5NzgiLCJzY29wZSI6WyJhdXRoZW50aWNhdGVkIiwicmVzdF9hcGkiXX0.J-F5Kyy1DbpwfZtqIWRTchuoy19NDOpGLol2cYOBt_eBmDdULuj4fxKxXL0CXOS7y7IvtsI8n3luVJBAtjc9UIl7yOT57ZEZfwqh0b5vg6sW_49W47qmb3n65oAMzbDqvsZt1rndwbx_9DU9TpJIQIe-c1SIpiB5WswWB3gcmOSx6pc1CEEWUpHSYgRfTZPP_SaMVAf2IlL5wrF6FtIfDLtANhHh1dJ3bfw56D0NUl1zDVrC6MB1iJUamneMQPJyHuK-ar1gxOAeW01cUdkD_zKqqYExdtRNgwsPuSHokjBT_puLBuYq1lCG-Guvg8DPdAHMo6gMtf9RRv26rEdLjnvzuo1xmv6V8GQjjWv535FfbPuKUuDypumuLBjICZS-b84Oiy-LBEkbNpByKRYaAQ0QsPhmyrho1D3ZdmFqzq9IZwuRwfJyKWIgOqVsyTPtK6mM8Lb9qYTL0yhwzC6Ivaykjtv4YjSN6V1B7TTVE4AAww9ojnZqcRXaX6txGqjsZXXJRZ7FyyGujHAT12AKl7SfQSkbONXMNODdbq-D6q7pa0yVZE3pTbwC8BmmwAlDUWFcq0P6k2ImHcrIMoSpHAuVla5ECjAfTtiH63BqVPSpmt5-r9jwpg54nok4T9JvPVJXCaQcZa5LhX-74ABSDGKDyOab2cahZNh7Zh7k7Sc"
# }

def get_articles_info_from_page(session, base_url, page):
    url = f"{base_url}?page={page}" 
    html_content = fetch_url(session, url)
    soup = BeautifulSoup(html_content, 'html.parser')
    news_cards = soup.find_all('div', class_='publication-content-flexbox-wrapper')
    cards = []
    for card in news_cards:
        newCard = {}
        publication_text = card.find("div", class_="publication-text")
        link = publication_text.find("a")
        date_div = card.find("div", class_="date")
        newCard["title"] = publication_text.text.strip()
        newCard['url'] = link.get("href")
        newCard["date"] = date_div.text.strip()
        cards.append(newCard)
          
    if not cards:
        return []

    result = []
    one_week_ago = (datetime.now() - timedelta(days=7)).replace(hour=0, minute=0, second=0, microsecond=0)
    for card in cards:      
        postedDate = parse_date(card.get('date',''))
        if postedDate >= one_week_ago:
            result.append({
            'title': card.get('title', ''),
            "postedDate": postedDate,
            "url" : card.get('url', '')
        })
            
    return result   

def get_content_of_article(session, url):
    #  Fetch the HTML content of the page
    html_content = fetch_url(session, url)

    # Parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(html_content, 'html.parser')

    # Find the div with class "article__content"
    article_div = soup.find('section', class_='field field-name-field-body field-type-text-long field-label-hidden')
    allowed_tags = ['h2', 'p', 'li']
    text_parts = []

    for element in article_div.descendants:
        if element.name in allowed_tags:
            text = element.get_text(strip=True)
            if element.name == 'li':
                text = '- ' + text
            text_parts.append(text)

    # Join the extracted text parts into a single string
    article_text = '\n\n'.join(text_parts)
      
    return article_text

def process_article(session: requests.Session, mainUrl, article):
    try:
        url = article.get('url')
        content = get_content_of_article(session, url)
        if content == "":
            logger.info(f"empty content in the article: {article.get('title')}")
            return None
        save_article(mainUrl, url, article.get('title'), article.get('postedDate'), content)
        logger.info(f"added {article.get('title')}")
    except Exception as e:
        logger.info(f"failed process_article: {str(e)}")
        return None


def main(base_url):
    start = time.time()
    logger.info(f">>> Started parsing {base_url}")
    page = 1
    session = create_session()
    while True:
        articles_on_page = get_articles_info_from_page(session, base_url, page)
        if not articles_on_page:
            logger.info('parsed all pages')
            logger.info(f'parsing took {time.time() - start} seconds')
            break
        
        with ThreadPoolExecutor(max_workers=10) as executor:  # Reduced max_workers to avoid overwhelming the server
            future_to_item = {executor.submit(process_article, session, base_url, item): item for item in articles_on_page}
            for future in as_completed(future_to_item):
                result = future.result()
                if result:
                    logger.infoint(f"Added {result}")
        logger.info(f'Parsed page No {page}')
        page += 1
        # if page == 201 : break

def parse_mdedge_site():
    base_url = 'https://www.mdedge.com/dermatology'
    main(base_url)

# parse_mdedge_site()
