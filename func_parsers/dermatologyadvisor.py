import requests
from bs4 import BeautifulSoup
from typing import List, Dict
from helper import parse_date, fetch_url, create_session
from db.mongodb import save_article
from urllib.parse import urljoin
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta
import time
import logging

# from draft.mongodb_local import test_save_article

logger = logging.getLogger(__name__)


def parse_news_card(card: BeautifulSoup) -> Dict[str, str]:
    result = {}

    title_div = card.find('div', class_='title')
    title_a_tag = title_div.find('a')
    # Find the time tag within the div with class post-date
    publish_date_div = card.find('div', class_='post-date')
    publish_date_time = publish_date_div.find('time')
    publish_date_str = publish_date_time['datetime']
    # Convert the publish date to a datetime object
    publish_date = datetime.strptime(publish_date_str, '%a, %d %b %Y %H:%M:%S %z')

    if title_a_tag:
        result['url'] = title_a_tag['href']
        result['title'] = title_a_tag.get_text(strip=True)
        result['article_date'] = publish_date

    return result

def parse_article_page(session: requests.Session, url: str) -> Dict[str, str]:
    html_content = fetch_url(session, url)
    soup = BeautifulSoup(html_content, 'html.parser')
    
    result = {}
    
    title_tag = soup.find('h1', class_='post-heading heading')
    if title_tag:
        result['article_title'] = title_tag.text.strip()
    
    content_div = soup.find('div', class_='post-content')
    if content_div:
        allowed_tags = ['p', 'li']
        text_parts = []

        for element in content_div.descendants:
            if element.name in allowed_tags:
                text = element.get_text(strip=True)
                if element.name == 'li':
                    text = '- '+text
                text_parts.append(text)

        result['article_text'] = '\n\n'.join(text_parts)
        # p_tags = content_div.find_all('p')
        # if p_tags:
        #     result['article_text'] = '\n\n'.join([p.text.strip() for p in p_tags])
    else:
        result['article_text'] = "NO content"
    
    return result

def parse_page(html_content: str) -> List[Dict[str, str]]:
    soup = BeautifulSoup(html_content, 'html.parser')
    articles = soup.find_all('article', class_='list-card show-excerpt no-thumb')

    return [parse_news_card(article) for article in articles]

def process_article(base_url, session: requests.Session, item: Dict[str, str]):
    try:
        article_info = parse_article_page(session, item['url'])
        article_date = item['article_date']
        current_date = datetime.now(article_date.tzinfo)  # Ensures both dates have the same timezone
        one_week_ago = current_date - timedelta(weeks=1)
        if article_date < one_week_ago:
            return "Parsed"
        save_article(base_url, item['url'], article_info['article_title'], article_date, article_info['article_text'])
        # test_save_article(base_url, item['url'], article_info['article_title'], article_date, article_info['article_text'])
        
        return article_info['article_title']
    except Exception as e:
        logger.error(f"Error processing article {item.get('url', 'Unknown URL')}: {e}")
        return None

def main(base_url: str):
    logger.info(f">>> Started parsing {base_url}")
    session = create_session()
    page = 1

    try:
        while True:
            logger.info(f"parsing page: {page}")
            url = f"{base_url}/page/{page}/"
            html_content = fetch_url(session, url)
            news_items = parse_page(html_content)
            
            if not news_items:
                logger.info(f"No more news items found on page {page}. Stopping.")
                break
            
            with ThreadPoolExecutor(max_workers=10) as executor:  # Reduced max_workers to avoid overwhelming the server
                future_to_item = {executor.submit(process_article, base_url, session, item): item for item in news_items}
                for future in as_completed(future_to_item):
                    result = future.result()
                    if result == "Parsed":
                        time.sleep(5)
                        logger.info("Parsed all articles for last 7 days")
                        return
                    else:    
                        logger.info(f"Added {result}")

                
            page += 1
            
    except requests.exceptions.RequestException as e:
        logger.info(f"An error occurred while fetching the page: {e}")
    except Exception as e:
        logger.info(f"An unexpected error occurred: {e}")

def parse_dermatologyadvisor_site():
    base_url = "https://www.dermatologyadvisor.com/news/"
    main(base_url)
