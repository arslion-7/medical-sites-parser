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


class MedscapeParser(BlogParser):
  def __init__(self, main_url, pagination, parse_weeks_count = 1, save_action=test_save_article):
    super().__init__(main_url, pagination, parse_weeks_count, save_action)

  def find_articles(self, soup: BeautifulSoup):
    archives = soup.find('div', { "id" : "archives" })
    return archives.find_all('li')

  def get_card_title_a_tag(self, card):
    return card.find('a', class_='title')
  
  def get_card_title_url(self, title_a_tag):
    url = title_a_tag['href']
    if url.startswith('//'):
      updated_url = 'http:' + url
    else:
      updated_url = url

    return updated_url

  def get_article_page_date(self, soup: BeautifulSoup):
    # Find the span tag with the data-datestring attribute
    # Find the span with class "article-date"
    # date_span = soup.find('span', {'class': 'article-date'})
    # # Extract the date text
    # date_str = date_span.get_text(strip=True)
    # # Convert to datetime object
    # date_format = "%B %d, %Y"  # Format matching "July 19, 2024"
    # return datetime.strptime(date_str, date_format)
    date_span = soup.find('span', {'class': 'article-date'})
    if date_span:
        # Extract the date text, stripping any extra content
        date_str = date_span.get_text(strip=True).split(' | ')[-1]
        # Define the date formats to handle different cases
        date_formats = ["%B %d, %Y", "%B %d, %Y"]  # Adjust if different formats are expected
        for date_format in date_formats:
            try:
                return datetime.strptime(date_str, date_format)
            except ValueError:
                return 'No date'
    return 'No date'

  def get_article_page_title(self, soup):
    title_tag = soup.find('h1', class_='article__title')
    if title_tag:
        return title_tag.text.strip() 
    return ''
  
  def get_article_page_content(self, soup):
    content_div = soup.find('div', class_='article__main-content')
    if content_div:
        return self.convert_html_to_markdown(str(content_div))
    else:
        return "NO content" 

      