import requests
from bs4 import BeautifulSoup
from typing import Dict
from datetime import datetime, timedelta
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from db.mongodb import save_article
from helper import fetch_url, create_session, parse_date

logger = logging.getLogger(__name__)

def parse_news_card(card: BeautifulSoup) -> Dict[str, str]:
    result = {}
    link = card.find('a', class_='css-1izc1yn')
    if link:
        result['url'] = link.get('href')
        result['title'] = link.find('h2', class_='css-1jmt90a').text.strip()
    return result

def parse_article_page(session: requests.Session, url: str) -> Dict[str, str]:
    html_content = fetch_url(session, url)
    soup = BeautifulSoup(html_content, 'html.parser')
    
    result = {}
    
    title_h1 = soup.find('div', class_='css-z468a2').find('h1')
    if title_h1:
        result['article_title'] = title_h1.text.strip()
    else:
        logger.warning(f"Could not find article title for URL: {url}")
        result['article_title'] = "Title not found"
    
    date_p = soup.find('p', class_='css-1kir5of')
    if date_p:
        result['article_date'] = date_p.text.strip().split('Last medically reviewed on')[-1].strip()
    else:
        logger.warning(f"Could not find article date for URL: {url}")
        result['article_date'] = "Date not found"
    
    content = []
    for tag in soup.find_all(['p', 'a']):
        if tag.name == 'a' and tag.get('href', '').startswith('http'):
            continue  # Skip external links
        content.append(tag.text.strip())
    result['article_text'] = '\n\n'.join(content)
    
    # logging.info(f"Successfully parsed article page: {url}")
    return result


def process_article(session: requests.Session, mainUrl, item: Dict[str, str]) -> Dict[str, str]:
    try:
        article_info = parse_article_page(session, item['url'])
        one_week_ago = (datetime.now() - timedelta(days=7)).replace(hour=0, minute=0, second=0, microsecond=0)
        if parse_date(article_info["article_date"]) < one_week_ago:
            return "Parsed"
        
        save_article(mainUrl, item['url'] ,article_info["article_title"], parse_date(article_info["article_date"]), article_info["article_text"])
        
        # logging.info(f"Processed article: {item['title']}")
        return article_info["article_title"]
    except Exception as e:
        logger.error(f"Error processing article {item['url']}: {str(e)}")
        return None

def main(url: str):
    session = create_session()
    all_news_items = []
    '''There is only one page in this site'''
    try:
        logger.info(f"Fetching main page: {url}")
        html_content = fetch_url(session, url)
        soup = BeautifulSoup(html_content, 'html.parser')
        news_cards = soup.find_all('li', class_='css-kbq0t')
        
        news_items = [parse_news_card(card) for card in news_cards]
        
        # Process articles in parallel
        with ThreadPoolExecutor(max_workers=5) as executor:
            future_to_item = {executor.submit(process_article, session, url, item): item for item in news_items}
            for future in as_completed(future_to_item):
                result = future.result()
                if result:
                    all_news_items.append(result)
                    if result == "Parsed":
                        logger.info("parsed all articles for last 7 days")
                        return
        
        logger.info(f"Scraped {len(all_news_items)} news items")
        
    except requests.exceptions.RequestException as e:
        logger.error(f"An error occurred while fetching the page: {str(e)}")
    except Exception as e:
        logger.error(f"An unexpected error occurred: {str(e)}")

def parse_medicalnewstoday_site():
    url = "https://www.medicalnewstoday.com/categories/dermatology"
    logger.info("Starting the scraper")
    main(url)
    logger.info("Scraper finished")