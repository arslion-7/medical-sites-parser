from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta
import logging
import time
import traceback
from typing import Dict, List
from urllib.parse import urljoin
from bs4 import BeautifulSoup
import requests

from blog_parser import BlogParser
from db.mongodb_local import test_save_article

logger = logging.getLogger(__name__)


class MedilibParser(BlogParser):
  def __init__(self, main_url, pagination, parse_weeks_count = 1, save_action=test_save_article):
    super().__init__(main_url, pagination, parse_weeks_count, save_action)

  def find_articles(self, soup: BeautifulSoup):
    print('soup', soup)
    return soup.find_all('h6', class_='title')

  def get_card_title_a_tag(self, card):
    print('card', card)
    return card.find('a')
  
  def get_card_title_url(self, title_a_tag):
    url = title_a_tag['href']

    return url
  
  def get_article_page_date(self, soup: BeautifulSoup):

    # Find the element containing the date
    # date_section = soup.find('div', class_='litReviewSingleLine')
   # Find the element containing the date
    # Extract "Literature review current through" date
    # print('soup1111', soup)
    # literature_review_bdi = soup.find_all('bdi')[0]
    # literature_review_str = literature_review_bdi.get_text(strip=True).replace('Literature review current through: ', '').strip()
    # literature_review_date = datetime.strptime(literature_review_str, "%B %Y")

    # # Extract "This topic last updated" date
    try:
      last_updated_bdi = soup.find_all('bdi')[1]
      last_updated_str = last_updated_bdi.get_text(strip=True).replace('This topic last updated: ', '').strip()
      last_updated_date = datetime.strptime(last_updated_str, "%b %d, %Y")

      return last_updated_date
    except:
      return 'No date'

  def get_article_page_title(self, soup):
    title_tag = soup.find('title')
    if title_tag:
        return title_tag.text.strip() 
    return ''
  
  def get_article_page_content(self, soup):
    content_div = soup.find('div', {'id': 'topicText'})
    if content_div:
        return self.convert_html_to_markdown(str(content_div))
    else:
        return "NO content" 
    
  def get_random_headers(self) -> Dict[str, str]:
    # ua = UserAgent()
    return {
        'DNT': '1',
        'Referer': 'https://medilib.ir/UpToDate/9',
        'Sec-ch-ua': 'Not)A;Brand";v="99", "Google Chrome";v="127", "Chromium";v="127',
        'Sec-ch-ua-mobile': '?0',
        'Sec-ch-ua-platform': '"macOS"',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36',
    }
  
  def stop_parsing(self, date):
     return False
  
  def process_article(self, mainUrl, session: requests.Session, card: Dict[str, str]):
    try:
        # get by card
        articleUrl = card['url']
        # date = card['date']

        article = self.parse_article_page(session, articleUrl)
        # get by article
        title = article['title']
        content = article['content']

        if content == 'NO content':
           return

        date = article['date']
        pdf_text = article['pdf_text'] if 'pdf_text' in article else ''
        references = article['references'] if 'references' in article else []
        
        if self.stop_parsing(date):
            return "Parsed"
            
        # mainUrl, articleUrl, title, date, content
        self.save_action(mainUrl='https://medilib.ir/UpToDate/9',
                         articleUrl=articleUrl,
                         title=title,
                         date=date,
                         content=content,
                         pdf_text=pdf_text,
                         references=references,
                         )
        
        return article['title']
    
    except Exception as e:
        logger.error(f"Error processing article {card.get('url', 'Unknown URL')}: {e}")
        logger.info(traceback.format_exc())
        return None


      