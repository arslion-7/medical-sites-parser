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

logger = logging.getLogger(__name__)

def parse_news_card(card: BeautifulSoup) -> Dict[str, str]:
    result = {}
    title_tag = card.find('a', class_='title')
    if title_tag:
        result['url'] = urljoin('https://www.medscape.com', title_tag['href'])
        result['title'] = title_tag.text.strip()
    
    return result

def parse_article_page(session: requests.Session, url: str) -> Dict[str, str]:
    html_content = fetch_url(session, url)
    soup = BeautifulSoup(html_content, 'html.parser')
    
    result = {}
    
    title_tag = soup.find('h1', class_='article__title')
    if title_tag:
        result['article_title'] = title_tag.text.strip()
    
    date_tag = soup.find('span', class_='article-date')
    if date_tag:
        result['article_date'] = date_tag.text.strip()
    
    content_div = soup.find('div', class_='article__main-content')
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
    news_cards = []
    for li in soup.find_all('li'):
        news_cards.append(li)
    return [parse_news_card(card) for card in news_cards]

def process_article(base_url, session: requests.Session, item: Dict[str, str]):
    try:
        article_info = parse_article_page(session, item['url'])

        one_week_ago = (datetime.now() - timedelta(days=7)).replace(hour=0, minute=0, second=0, microsecond=0)
        if parse_date(article_info["article_date"]) < one_week_ago:
            return "Parsed"
        
        save_article(base_url, item['url'], article_info['article_title'], parse_date(article_info["article_date"]), article_info["article_text"])
        
        return article_info['article_title']
    except Exception as e:
        logger.error(f"Error processing article {item.get('url', 'Unknown URL')}: {e}")
        return None


def main(base_url: str):
    logger.info(f">>> Started parsing {base_url}")
    session = create_session()
    page = 0

    try:
        while True:
            logger.info(f"parsing page: {page}")
            url = f"{base_url}_{page}"
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

def parse_medscape_site():
    base_url = "https://www.medscape.com/index/list_11732"
    main(base_url)

# parse_medscape_site()
# if __name__ == "__main__":
#     base_urls = [ "https://www.medscape.com/index/list_11732" ''',"https://www.medscape.com/index/list_3809"''']
    
#     for base_url in base_urls:
#         main(base_url)