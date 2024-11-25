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


class MedicalnewstodayParser(BlogParser):
  def __init__(self, main_url, pagination, parse_weeks_count = 1, save_action=test_save_article):
    super().__init__(main_url, pagination, parse_weeks_count, save_action)

  def find_articles(self, soup):
    return soup.find_all('li', class_='css-kbq0t') 

  def get_card_title_a_tag(self, card):
    title_div = card.find('div', class_='css-ps3vwz')
    return title_div.find('a', class_='css-1izc1yn')
  
  def get_card_title_url(self, title_a_tag) -> str:
    title_link = title_a_tag['href']
    return title_link

  def get_article_page_title(self, soup) -> str:
    common_div = soup.find('div', class_='css-z468a2')
    title_tag = common_div.find('h1')
    if title_tag:
        return title_tag.text.strip() 
    return ''
  
  def get_article_page_date(self, soup: BeautifulSoup) -> datetime:
    # Find the section with data-testid="byline"
    byline_section = soup.find('section', {'data-testid': 'byline'})

    # Extract the date text
    date_text = byline_section.find(text=lambda x: ' on ' in x)
    date_str = date_text.split(' on ')[-1]

    # Convert to datetime object
    date_format = "%B %d, %Y"  # Format matching "July 26, 2024"
    return datetime.strptime(date_str, date_format)
  
  def get_article_page_content(self, soup) -> str:
    article = soup.find('article', class_='article-body')
    if article:
        return self.convert_html_to_markdown(str(article))
    else:
        return "NO content" 

  
      