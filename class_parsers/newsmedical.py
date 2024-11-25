from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta
import logging
import random
import time
from typing import Dict, List
from urllib.parse import urljoin
from bs4 import BeautifulSoup
import requests

from blog_parser import BlogParser
from db.mongodb_local import test_save_article

logger = logging.getLogger(__name__)


class NewsmedicalParser(BlogParser):
  def __init__(self, main_url, pagination, parse_weeks_count = 1, save_action=test_save_article):
    super().__init__(main_url, pagination, parse_weeks_count, save_action)

  def get_random_headers(self) -> Dict[str, str]:
    return {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "accept-language": "en-US,en;q=0.9",
        "cache-control": "max-age=0",
        "priority": "u=0, i",
        "sec-ch-ua": "\"Not)A;Brand\";v=\"99\", \"Google Chrome\";v=\"127\", \"Chromium\";v=\"127\"",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "\"macOS\"",
        "sec-fetch-dest": "document",
        "sec-fetch-mode": "navigate",
        "sec-fetch-site": "same-origin",
        "sec-fetch-user": "?1",
        "upgrade-insecure-requests": "1"
    }

  def find_articles(self, soup: BeautifulSoup):
    posts_div = soup.find('div', class_='posts publishables-list-wrap')
    rows = posts_div.find_all('div', class_='row')
    filtered_rows = [row for row in rows if not row.find('div', class_='article-meta')]

    return filtered_rows

  def get_card_title_a_tag(self, card):
    return card.find('a')
  
  def get_card_title_url(self, title_a_tag):
    url = title_a_tag['href']

    return urljoin(self.domain, url)

  def get_article_page_date(self, soup: BeautifulSoup):
    # Extract the date string
    date_str = soup.find('span', class_='article-meta-date').text.strip()

    # Parse the date string into a datetime object
    parsed_date = datetime.strptime(date_str, '%b %d %Y')
    return parsed_date

  def get_article_page_title(self, soup):
    title_tag = soup.find('title')
    if title_tag:
        return title_tag.text.strip() 
    return ''
  
  def get_article_page_content(self, soup):
    content_div = soup.find('div', class_='content')
    if content_div:
        return self.convert_html_to_markdown(str(content_div))
    else:
        return "NO content" 

      