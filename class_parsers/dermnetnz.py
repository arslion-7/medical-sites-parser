from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta
import logging
import random
import re
import time
from typing import Dict, List
from urllib.parse import urljoin
from bs4 import BeautifulSoup
import html2text
import requests

from blog_parser import BlogParser
from db.mongodb_local import test_save_article

logger = logging.getLogger(__name__)


class DermnetnzParser(BlogParser):
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
    # Find all divs with the class 'topics__wrap__grid__column__list'
    topics_sections = soup.find_all('div', class_='topics__wrap__grid__column__list')

    # Collect all <a> tags within these divs
    all_a_tags = []
    for section in topics_sections:
        a_tags = section.find_all('a')
        all_a_tags.extend(a_tags)
    
    return all_a_tags

  def get_card_title_a_tag(self, card):
    return card
  
  def get_card_title_url(self, title_a_tag):
    url = title_a_tag['href']
    return urljoin(self.domain, url)

  def get_article_page_date(self, soup: BeautifulSoup):
   # Extract the text from the <p> tag
    authors_content = soup.find('div', class_='authors-content')
    text = authors_content.find('p').get_text()
    
    # Define the regex pattern to extract dates in the format "Month Year"
    pattern = r'([A-Za-z]+ \d{4})'
    
    # Search for the date in the text
    match = re.search(pattern, text)
    if match:
        try:
          date_str = match.group(1)
          # Define the date format and parse the date string
          date_format = "%B %Y"
          date_obj = datetime.strptime(date_str, date_format)
          return date_obj
        except Exception as e:
           print('Error on date_format', e)
           
    return 'No date'

  def get_article_page_title(self, soup):
    title_tag = soup.find('title')
    if title_tag:
        return title_tag.text.strip() 
    return ''
  
  def get_article_page_content(self, soup):
    # Parse the HTML content
    # Find all div elements with the class text-block__wrap
    text_blocks = soup.find_all('div', class_='text-block__wrap')

    # Initialize html2text converter
    converter = html2text.HTML2Text()
    converter.ignore_links = False  # To keep links in the markdown
    converter.ignore_images = True  # To ignore images if any

    # Convert each text block to Markdown and concatenate them
    markdown_result = ""
    for block in text_blocks:
        block_str = str(block)
        if 'ADVERTISEMENT' in block_str:
           continue

        markdown = converter.handle(block_str)
        markdown_result += markdown.strip() + "\n\n"  # Add two newlines to separate blocks


    if markdown_result == "":
      return "NO content" 

    return markdown_result
    
  def stop_parsing(self, date):
    return False

      