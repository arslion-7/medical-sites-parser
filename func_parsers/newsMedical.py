import requests
from bs4 import BeautifulSoup
from typing import List, Dict
from urllib.parse import urljoin
from db.mongodb import save_article
from helper import create_session, fetch_url, parse_date
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta
import time
import logging

logger = logging.getLogger(__name__)

def parse_news_card(card: BeautifulSoup) -> Dict[str, str]:
    result = {}
    link = card.find('h3').find('a')
    result['url'] = link['href']
    result['title'] = link.text.strip()
    return result

def parse_article_page(session: requests.Session, url: str) -> Dict[str, str]:
    html_content = fetch_url(session, url)
    soup = BeautifulSoup(html_content, 'html.parser')
    
    result = {}
    
    title_span = soup.find('h1', class_='page-title')
    if title_span:
        result['article_title'] = title_span.text.strip()
    
    date_span = soup.find('span', class_='article-meta-date')
    if date_span:
        result['article_date'] = date_span.text.strip()
    
    content_div = soup.find('div', class_='page-content clearfix')
    if content_div:
        allowed_tags = ['p', 'li', 'h2']
        text_parts = []

        for element in content_div.descendants:
            if element.name in allowed_tags:
                text = element.get_text(strip=True)
                if element.name == 'li':
                    text = '- '+text
                text_parts.append(text)
        
        result['article_text'] = '\n\n'.join(text_parts)
    else:
        result['article_text'] = "Article text not found."
    
    return result

def parse_page(html_content: str) -> List[Dict[str, str]]:
    soup = BeautifulSoup(html_content, 'html.parser')
    news_cards = soup.find_all('div', class_='row')
    return [parse_news_card(card) for card in news_cards if card.find('div', class_='col-xs-3')]

def process_article(session: requests.Session, mainUrl, item: Dict[str, str]):
    try:
        article_url = urljoin("https://www.news-medical.net/", item['url'])
        article_info = parse_article_page(session, article_url)
        one_week_ago = (datetime.now() - timedelta(days=7)).replace(hour=0, minute=0, second=0, microsecond=0)
        if parse_date(article_info["article_date"]) < one_week_ago:
            return "Parsed"
        
        save_article(mainUrl, article_url, article_info["article_title"], parse_date(article_info["article_date"]), article_info["article_text"])
        logger.info(f"Added {article_info['article_title']}")
        return article_info["article_title"]
    except Exception as e:
        logger.info(f"failed process_article {item['url']}: {str(e)}")
        return None

def main(base_url: str):
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
            
            with ThreadPoolExecutor(max_workers=10) as executor:
                future_to_item = {executor.submit(process_article, session, base_url, item): item for item in news_items}
                for future in as_completed(future_to_item):
                    result = future.result()
                    if result == "Parsed":
                        time.sleep(5)
                        logger.info("Parsed all articles for last 7 days")
                        return

                
                # print(f"Processed article: {item['title']}")
            logger.info(f"Parsed page No {page}")
            page += 1
            # if page == 101: break
        
    except requests.exceptions.RequestException as e:
        logger.error(f"An error occurred while fetching the page: {e}")
    except Exception as e:
        logger.info(f"An unexpected error occurred: {e}")

def parse_newsmedical_site():
    base_url = "https://www.news-medical.net/condition/Dermatology"
    main(base_url)