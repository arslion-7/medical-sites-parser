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


class NcbiNlmNihParser(BlogParser):
  def __init__(self, main_url, pagination, parse_weeks_count = 1, save_action=test_save_article):
    super().__init__(main_url, pagination, parse_weeks_count, save_action)

  def find_articles(self, soup: BeautifulSoup):
    ul = soup.find('ul', {'id': 'toc_tllNBK430685_'})
    list_items = ul.find_all('li', class_='half_rhythm') 
    filtered_items = [li for li in list_items if "Editorial Board" not in li.get_text()]

    return filtered_items

  def get_card_title_a_tag(self, card):
    return card.find('a', class_='toc-item')
  
  def get_card_title_url(self, title_a_tag) -> str:
    title_link = title_a_tag['href']
    return urljoin(self.domain, title_link)

  def get_article_page_title(self, soup: BeautifulSoup) -> str:
    title = soup.find('title')
    return title.text
  
  def get_article_page_date(self, soup: BeautifulSoup) -> datetime:
    # Find the section with data-testid="byline"
    # Find the element with itemprop="dateModified"
    date_span = soup.find('span', itemprop='dateModified')
    # Extract the date text
    date_str = date_span.get_text(strip=True)
    # Convert to datetime object
    date_format = "%B %d, %Y"  # Format matching "October 7, 2022"
    return datetime.strptime(date_str, date_format)
  
  def get_article_page_content(self, soup) -> str:
    article = soup.find('div', class_='body-content')
    if article:
        return self.convert_html_to_markdown(str(article))
    else:
        return "NO content" 

  def stop_parsing(self, date):
    # There is no date on page, and have to parse all pages
    return False
  
      