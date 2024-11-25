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


class MedicaldialoguesParser(BlogParser):
  def __init__(self, main_url, pagination, parse_weeks_count = 1, save_action=test_save_article):
    super().__init__(main_url, pagination, parse_weeks_count, save_action)

  def find_articles(self, soup):
    return soup.find_all('article', class_='listing-item-blog') 

  def get_card_title_a_tag(self, card):
    inner_element = card.find('div', class_='item-inner clearfix')
    title_div = inner_element.find('h2', class_='title')
    return title_div.find('a')
  
  def get_card_title_url(self, title_a_tag):
    title_link = title_a_tag['href']
    return urljoin(self.domain, title_link)

  def get_article_page_date(self, soup: BeautifulSoup):
    # Find the span tag with the data-datestring attribute
    span_tag = soup.find('span', {'data-datestring': True})
    # Extract the data-datestring attribute
    datetime_str = span_tag['data-datestring']
    # Parse the datetime string to a datetime object
    return datetime.strptime(datetime_str, '%Y-%m-%d %H:%M:%S')

  def get_article_page_title(self, soup):
    title_tag = soup.find('h1', class_='single-post-title')
    title_span = title_tag.find('span', class_='post-title')
    if title_tag:
        return title_span.text.strip() 
    return ''
  
  def get_article_page_content(self, soup):
    content_div = soup.find('div', class_='story')
    if content_div:
        return self.convert_html_to_markdown(str(content_div))
    else:
        return "NO content" 

      