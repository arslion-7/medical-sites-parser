import requests
from bs4 import BeautifulSoup
import logging
import time
from datetime import datetime, timedelta
from helper import fetch_url, parse_date, create_session
from db.mongodb import save_article
from concurrent.futures import ThreadPoolExecutor, as_completed

logger = logging.getLogger(__name__)

API_URL_NEWS = "https://www.healio.com/h5news/specialtylanding/searchjson?page={page_number}&specialtyId=5a4b1579-8df3-4360-a047-43471f40e728&pageId=%7B84FE6BF2-F044-44E6-902D-61AFE752D322%7D&userId=00000000-0000-0000-0000-000000000000"
# API_URL_PEDIATRIC = "https://www.healio.com/h5news/specialtylanding/searchjson?page={page_number}&specialtyId=5a4b1579-8df3-4360-a047-43471f40e728&pageId=%7BE992B6BA-5A95-41A6-930A-E9E426488EB2%7D&subspecialtyId=54116a61-f277-4651-9c67-6a08deac9f39&userId=00000000-0000-0000-0000-000000000000"

DOMAIN = "https://www.healio.com"

def get_articles_info_from_page(page, url):
    response = requests.get(url=url.format(page_number=page))

    if response.status_code != 200:
        raise "Failed to get articles info from healio.com"
    
    response = response.json()

    cards = response.get('cards', [])
    if not cards:
        return []
    
    featured = response.get('featured', {})
    if featured:
        cards.append(featured)

    result = []
    for card in cards:
        id = card.get('Id', '')
        if not id:
            continue
        
        postedDate = parse_date(card.get('PostedDate',''))
        # if postedDate >= datetime(2024, 6, 1, 0, 0):
        result.append({
            'title': card.get('Title', ''),
            "postedDate": postedDate,
            "link" : card.get('Link', '')
        })

    return result   

def get_content_of_article(session, url):
    #  Fetch the HTML content of the page
    response = requests.get(url)

    if response.status_code != 200:
        logger.error(f"failed to fetch content {url}")
        return None
    
    html_content = response.content
    if not html_content:
        logger.error(f"failed to fetch html content {url}")
        return None
    # Parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(html_content, 'html.parser')
 
    # Find the div with class "article__content"
    article_div = soup.find('div', class_='article__content')
    if not article_div:
        logger.error(f"failed to parse 'article__content' div {url}")
        return None
    
    allowed_tags = ['h2', 'p', 'li']
    text_parts = []
    for element in article_div:
        if element.name in allowed_tags:
            text = element.get_text(strip=True)
            if element.name == 'li':
                text = '- ' + text
            text_parts.append(text)

    # Join the extracted text parts into a single string
    article_text = '\n\n'.join(text_parts)
            
    return article_text

def process_article(session: requests.Session, mainUrl :str, article):
    try:
        url = DOMAIN + article.get('link')
        content = get_content_of_article(session, url)
        save_article(mainUrl, url, article.get('title'), article.get('postedDate'), content)
        return article.get('title')
    except Exception as e:
        logger.error(f"failed process_article: {str(e)}")
        return None

def main(url_api):
    logger.info(f">>> Started parsing {url_api[0]}")
    start = time.time()
    session = create_session()
    page = 1
    while True:    
        articles_on_page = get_articles_info_from_page(page, url_api[1])
        if not articles_on_page:
            logger.info('parsed all pages')
            logger.info(f'parsing took {time.time() - start} seconds')
            break

        one_week_ago = (datetime.now() - timedelta(days=7)).replace(hour=0, minute=0, second=0, microsecond=0)

        filtered_articles = [
            item for item in articles_on_page
            if item["postedDate"] >= one_week_ago
        ]
        if not filtered_articles:
            logger.info("parsed all articles for last 7 days")
            break
        
        with ThreadPoolExecutor(max_workers=10) as executor:  # Reduced max_workers to avoid overwhelming the server
                future_to_item = {executor.submit(process_article, session, url_api[0], item): item for item in filtered_articles}
                for future in as_completed(future_to_item):
                    result = future.result()
                    if result:
                        logger.info(f"Added {result}")
        logger.info(f'Parsed page No {page}')
        page += 1

def parse_heailo_site():
    url_api = ("https://www.healio.com/news/dermatology", API_URL_NEWS)
    main(url_api)

# parse_heailo_site() 
