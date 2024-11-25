import requests
from bs4 import BeautifulSoup
from typing import List, Dict
import time
import random
from urllib.parse import urljoin
from db.mongodb import save_article
from helper import parse_date, fetch_url, create_session
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

def parse_news_card(card: BeautifulSoup) -> Dict[str, str]:
    result = {}
    result['url'] = card.get('data-url')    
    return result

def parse_article_page(session: requests.Session, url: str) -> Dict[str, str]:
    html_content = fetch_url(session, url)
    soup = BeautifulSoup(html_content, 'html.parser')
    
    result = {}
    
    h2_tag = soup.find('h2')
    if h2_tag:
        result['article_title'] = h2_tag.text.strip()
    
    description_div = soup.find('div', class_='news-details__description')
    if description_div:
        # Find all p tags within this div
        allowed_tags = ['p', 'li']
        text_parts = []

        for element in description_div.descendants:
            if element.name in allowed_tags:
                text = element.get_text(strip=True)
                if element.name == 'li':
                    text = '- '+text
                text_parts.append(text)
        
        result['article_text'] = '\n\n'.join(text_parts)
    else:
        result['article_text'] = "Article text not found."
    
    date_div = soup.find('div', class_='news-details__info__time')
    if date_div:
        result['article_date'] = date_div.text.strip()
    
    return result

def parse_page(html_content: str) -> List[Dict[str, str]]:
    soup = BeautifulSoup(html_content, 'html.parser')
    news_cards = soup.find_all('div', class_='news-list-item')
    return [parse_news_card(card) for card in news_cards]

def process_article(base_url, session: requests.Session, item: Dict[str, str]):
    try:
        article_url = urljoin("https://practicaldermatology.com", item['url'])
        article_info = parse_article_page(session, article_url)
        one_week_ago = (datetime.now() - timedelta(days=7)).replace(hour=0, minute=0, second=0, microsecond=0)
        if parse_date(article_info["article_date"]) < one_week_ago:
            return "Parsed"
        
        save_article(base_url, article_url, article_info["article_title"], parse_date(article_info["article_date"]), article_info["article_text"])

        # print(f"Processed article: {article_info['article_title']}")
        return article_info['article_title']
    except Exception as e:
        logger.error(f"Failed process_article: {str(e)}")
        return None

def main(base_url: str):
    """Main function to fetch all pages and parse them."""
    logger.info(f">>> Started parsing {base_url}")
    session = create_session()
    page = 1

    try:
        while True:
            url = f"{base_url}?page={page}"
            logger.info(f"Fetching page {page}...")
            html_content = fetch_url(session, url)
            news_items = parse_page(html_content)
            
            if not news_items:
                logger.info(f"No more news items found on page {page}. Stopping.")
                break
            
            with ThreadPoolExecutor(max_workers=5) as executor:  # Reduced max_workers to avoid overwhelming the server
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
            # if page == 200: break
            time.sleep(random.uniform(0.1, 0.3))  # Delay between pages
        
        
    except requests.exceptions.RequestException as e:
        logger.info(f"An error occurred while fetching the page: {e}")
    except Exception as e:
        logger.info(f"An unexpected error occurred: {e}")

def parse_practicaldermotology_site():

    base_urls = ["https://practicaldermatology.com/medical-news"#,"https://practicaldermatology.com/medical-news/pediatric/",
                ]
    
    for base_url in base_urls:
        main(base_url)