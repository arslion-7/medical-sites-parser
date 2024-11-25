import requests
from bs4 import BeautifulSoup
from typing import List, Dict
import time
import random
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import json
from urllib.parse import urljoin
import os
import re
import pymongo
from datetime import datetime

DATABASE_NAME = 'telegram_client'
DB_URL = "mongodb://{user}:{pw}@{host}/{db}?replicaSet={rs}&appName=mongosh+2.0.0".format(
    user='telegram_user',
    pw='zaiv6ahdohp8eicheereeph5ieBah9qu',
    host='rc1b-ozt5tmyq4i4zzdxw.mdb.yandexcloud.net:27018',
    db=DATABASE_NAME,
    rs='rs01'
)

db = pymongo.MongoClient(
    DB_URL,
    tls=True,
    tlsCAFile='root.crt')[DATABASE_NAME]

def save_article(mainUrl, articleUrl, title, date, content):
    db.parsedSites.update_one(
        {'articleUrl': articleUrl},
        {'$set': {
            'mainUrl': mainUrl,
            'articleUrl': articleUrl,
            'title': title,
            'publishedDate': date,
            'content': content
        }},
        upsert=True,
    )

def parse_date(date_str):
    try:
        # Attempt to parse the date string in different formats
        try:
            parsed_date = datetime.strptime(date_str, "%B %d, %Y")  # Example format: "June 20, 2024"
        except ValueError:
            try:
                parsed_date = datetime.strptime(date_str, "%m/%d/%Y")  # Example format: "11/03/2023"
            except ValueError:
                try:
                    parsed_date = datetime.strptime(date_str, "%B %d %Y")  # Example format: "May 22 2024"
                except ValueError:
                    try:
                        parsed_date = datetime.strptime(date_str, "%b %d %Y")  # Example format: "Jun 8 2024"
                    except ValueError:
                        parsed_date = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S.%f")  # Example format: "2024-06-11T17:12:48.596"
        
        return parsed_date
    
    except ValueError:
        return None
    
def parse_news_card(card: BeautifulSoup) -> Dict[str, str]:
    result = {}
    link = card.find('a')
    if link:
        result['url'] = link.get('href')
        title_p = card.find('p', class_='font-bold')
        if title_p and title_p.find('a'):
            result['title'] = title_p.find('a').text.strip()
    return result

def parse_article_page(session: requests.Session, url: str) -> Dict[str, str]:
    html_content = fetch_url(session, url)
    soup = BeautifulSoup(html_content, 'html.parser')
    
    result = {}
    
    title_span = soup.find('h1', class_='text-2xl sm:text-3xl')
    if title_span:
        result['article_title'] = title_span.text.strip()
    
    date_time = soup.find('time', class_='tex-sm')
    if date_time:
        result['article_date'] = date_time.get('datetime')
    
    content_div = soup.find('div', class_='blockText_blockContent__TbCXh')
    if content_div:
         # Find all p tags within this div
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
    news_cards = soup.find_all('div', class_='w-full h-full')
    return [parse_news_card(card) for card in news_cards]

def create_session() -> requests.Session:
    session = requests.Session()
    retry = Retry(total=5, backoff_factor=0.1, status_forcelist=[500, 502, 503, 504])
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    })
    return session

def fetch_url(session: requests.Session, url: str) -> str:
    time.sleep(random.uniform(0.1, 0.3))
    response = session.get(url)
    response.raise_for_status()
    return response.text

def save_to_markdown(item: Dict[str, str], article_info: Dict[str, str]) -> str:
    safe_filename = re.sub(r'[^\w\-_\. ]', '_', item['title'])
    safe_filename = safe_filename.replace(' ', '_')
    filename = f"{safe_filename}.md"
    
    os.makedirs('articles', exist_ok=True)
    
    filepath = os.path.join('articles', filename)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(f"# {article_info['article_title']}\n\n")
        f.write(f"Date: {article_info['article_date']}\n\n")
        f.write(f"{article_info['article_text']}\n")
    
    return filepath

def main(base_url: str):
    session = create_session()
    page = 1
    all_news_items = []

    try:
        while True:
            url = f"{base_url}/?page={page}"
            print(f"Fetching page {page}...")
            html_content = fetch_url(session, url)
            news_items = parse_page(html_content)
            
            if not news_items:
                print(f"No more news items found on page {page}. Stopping.")
                break
            
            for item in news_items:
                article_url = urljoin("https://www.hcplive.com/", item['url'])
                article_info = parse_article_page(session, article_url)
                
                save_article("https://www.hcplive.com/clinical/dermatology", article_url, article_info["article_title"], parse_date(article_info["article_date"]), article_info["article_text"])
                
                print(f"Processed article: {item['title']}")
                
            page += 1
            if page == 21:
                break
            time.sleep(random.uniform(0.1, 0.3))
        
    except requests.exceptions.RequestException as e:
        print(f"An error occurred while fetching the page: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    base_url = "https://www.hcplive.com/clinical/dermatology"  # Replace with the actual base URL
    main(base_url)