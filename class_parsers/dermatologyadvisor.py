from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta
import logging
import time
from typing import Dict, List
from urllib.parse import urljoin
from bs4 import BeautifulSoup

from blog_parser import BlogParser
from db.mongodb_local import test_save_article

logger = logging.getLogger(__name__)


class DermatologyadvisorParser(BlogParser):
  def __init__(self, main_url, pagination, parse_weeks_count = 1, save_action=test_save_article):
    super().__init__(main_url, pagination, parse_weeks_count, save_action)

  def find_articles(self, soup):
    return soup.find_all('article', class_='list-card show-excerpt no-thumb') 

  def get_card_title_a_tag(self, card):
    title_div = card.find('div', class_='title')
    return title_div.find('a')
  
  def get_card_title_url(self, title_a_tag):
    title_link = title_a_tag['href']
    return title_link

  def get_article_page_title(self, soup):
    title_tag = soup.find('h1', class_='post-heading heading')
    if title_tag:
        return title_tag.text.strip() 
    return ''
  
  def get_article_page_date(self, soup: BeautifulSoup):
     date_div = soup.find('div', class_='post-date')
     time_tag = date_div.find('time')
     datetime_str = time_tag['datetime']
     return datetime.strptime(datetime_str, '%a, %d %b %Y %H:%M:%S %z')
  
  def get_article_page_content(self, soup):
    content_div = soup.find('div', class_='post-content')
    if content_div:
        return self.convert_html_to_markdown(str(content_div))
    else:
        return "NO content" 

  
      