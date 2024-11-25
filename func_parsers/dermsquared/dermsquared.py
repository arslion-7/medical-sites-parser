import requests
from bs4 import BeautifulSoup
from typing import List, Dict
import time
import random
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import json
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
            parsed_date = datetime.strptime(date_str, "%m/%d/%Y")  # Example format: "11/03/2023"
        
        # Combine parsed date with time string into a datetime object
        return parsed_date
    
    except ValueError:
        return None

def create_session() -> requests.Session:
    session = requests.Session()
    retry = Retry(total=5, backoff_factor=0.1, status_forcelist=[500, 502, 503, 504])
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    
    session.headers.update({
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'ru,en;q=0.9',
        'Cache-Control': 'no-cache',
        'Origin': 'https://dermsquared.com',
        'Pragma': 'no-cache',
        'Referer': 'https://dermsquared.com/',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-site',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 YaBrowser/24.4.0.0 Safari/537.36',
        'sec-ch-ua': '"Chromium";v="122", "Not(A:Brand";v="24", "YaBrowser";v="24.4", "Yowser";v="2.5"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"'
    })
    return session

def fetch_api(session: requests.Session, page: int, page_size: int = 24) -> Dict:
    url = f'https://admin.dermsquared.com/api/news-and-researches'
    params = {
        'sort[0]': 'releaseDate:desc',
        'sort[1]': 'publishedAt:desc',
        'sort[2]': 'updatedAt:desc',
        'fields[0]': 'id',
        'fields[1]': 'author',
        'fields[2]': 'title',
        'fields[3]': 'description',
        'fields[4]': 'releaseDate',
        'fields[5]': 'slug',
        'pagination[page]': page,
        'pagination[pageSize]': page_size
    }
    response = session.get(url, params=params)
    response.raise_for_status()
    return response.json()

def parse_article_page(session: requests.Session, url: str) -> Dict[str, str]:
    response = session.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')
    
    result = {}
    
    title_span = soup.find('h3', class_='text-[32px] font-semibold leading-[39px] sm:text-[48px] sm:leading-[58px] mb-2')
    if title_span:
        result['article_title'] = title_span.text.strip()
    
    date_span = soup.find('p', class_='text-[14px] font-light leading-[17px] mt-2 text-gray-300')
    if date_span:
        result['article_date'] = date_span.text.strip().split("|")[1].strip()
    
    content_div = soup.find('div', class_='wysiwyg !text-light dangerouslySetInnerHTML dangerouslySetNewsInnerHTML')
    if content_div:
         # Find all p tags within this div
        allowed_tags = ['p', 'li']
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

def save_to_markdown(item: Dict[str, str], article_info: Dict[str, str]) -> str:
    safe_filename = re.sub(r'[^\w\-_\. ]', '_', item['attributes']['title'])
    safe_filename = safe_filename.replace(' ', '_')
    filename = f"{safe_filename}.md"
    
    os.makedirs('articles', exist_ok=True)
    
    filepath = os.path.join('articles', filename)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(f"# {article_info['article_title']}\n\n")
        f.write(f"Date: {article_info['article_date']}\n\n")
        f.write(f"{article_info['article_text']}\n")
    
    return filepath

def main():
    session = create_session()
    page = 1
    all_news_items = []

    try:
        while True:
            print(f"Fetching page {page}...")
            api_response = fetch_api(session, page)
            
            if not api_response['data']:
                print(f"No more news items found on page {page}. Stopping.")
                break
            
            for item in api_response['data']:
                article_url = f"https://dermsquared.com/news-research/{item['attributes']['slug']}"
                article_info = parse_article_page(session, article_url)
                
                save_article("https://dermsquared.com/news-research", article_url, article_info["article_title"], parse_date(article_info["article_date"]), article_info["article_text"])

                print(f"Processed article: {item['attributes']['title']}")
    
            page += 1
            if page == 21:
                break
            time.sleep(random.uniform(0.1, 0.3))
        
        
    except requests.exceptions.RequestException as e:
        print(f"An error occurred while fetching the data: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()