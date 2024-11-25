from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta
import json
import logging
import random
import re
import time
from typing import Dict, List
from urllib.parse import urljoin
from bs4 import BeautifulSoup
import requests

from blog_parser import BlogParser
from db.mongodb_local import test_save_article

logger = logging.getLogger(__name__)


class UptodateParser(BlogParser):
  def __init__(self, main_url, pagination, parse_weeks_count = 1, save_action=test_save_article):
    super().__init__(main_url, pagination, parse_weeks_count, save_action)

  def get_random_headers(self) -> Dict[str, str]:
    return {
        "accept": "*/*",
        "accept-language": "en-US,en;q=0.9",
        "sec-ch-ua": "\"Not)A;Brand\";v=\"99\", \"Google Chrome\";v=\"127\", \"Chromium\";v=\"127\"",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "\"macOS\"",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin"
    }
  
  def fetch_url_json(self, session: requests.Session, url: str):
    headers = self.get_random_headers()
    session.headers.update(headers)
    time.sleep(random.uniform(0, 2))
    response = session.get(url)
    response.raise_for_status()
    return response.json()

  def find_articles(self, soup: BeautifulSoup):
    json_data = self.fetch_url_json(self.session, 'https://www.uptodate.com/services/app/contents/topic/whats-new-in-dermatology/json')
    bodyHtml = json_data.get("data", {}).get("bodyHtml", {})
    soup_bodyHtml =  BeautifulSoup(bodyHtml, 'lxml')
        
    # Find all <p> tags that contain a <span> with class "h2"
    # a_tags = soup_bodyHtml.find_all('div', class_='medical_review')
    a_tags = soup_bodyHtml.find_all('a', class_='medical_review')

    return a_tags

  def get_card_title_a_tag(self, card):
    return card
  
  def get_card_title_url(self, title_a_tag):
    url = title_a_tag['href']

    return urljoin(self.domain, url)

  def parse_article_page(self, session: requests.Session, url: str) -> Dict[str, str]:
    soup = self.get_parsed_soup(session, url)
    transformed_url = self.transform_url(url)

    json_data = self.fetch_url_json(self.session, transformed_url)
    bodyHtml = json_data.get("data", {}).get("bodyHtml", {})
    soup_bodyHtml =  BeautifulSoup(bodyHtml, 'lxml')

    # with open('draft/soup_bodyHtml.html', 'w') as file:
    #   file.write(str(soup_bodyHtml))

    topic_text = soup_bodyHtml.find('div', {'id': 'topicText'})
    p_tags = topic_text.find_all('p')
    content = "\n\n".join([p.get_text() for p in p_tags])

    title = ''
    title_tag = soup_bodyHtml.find('div', {"id": "topicTitle"})
    if title_tag:
        title = title_tag.text.strip() 

    text_date = soup_bodyHtml.get_text()
    # Define regex patterns for both formats
    month_year_pattern = r'([A-Za-z]+ \d{4})'
    full_date_pattern = r'([A-Za-z]+ \d{1,2}, \d{4})'

    dates = re.findall(month_year_pattern, text_date) + re.findall(full_date_pattern, text_date)
    date_obj = 'No date'
    # Parse and print each date
    for date_str in dates:
        try:
            if ',' in date_str:
                # Parse full date (e.g., Jun 24, 2024)
                date_obj = datetime.strptime(date_str, "%b %d, %Y")
            else:
                # Parse month and year only (e.g., Jul 2024)
                date_obj = datetime.strptime(date_str, "%b %Y")
            print(f"Extracted Date: {date_obj}")
        except ValueError:
            print(f"Failed to parse date: {date_str}")

    article = {}
    article['title'] = title
    article['content'] = content
    article['date'] = date_obj
    
    return article
  
  def transform_url(self, original_url):
    from urllib.parse import urlparse, parse_qs, urlencode
    
    # Parse the original URL
    parsed_url = urlparse(original_url)
    
    # Extract the path and query parameters
    path = parsed_url.path
    query_params = parse_qs(parsed_url.query)
    
    # Construct the new base URL
    new_base_url = "https://www.uptodate.com/services/app/contents/topic"
    
    # Extract the topic name from the original path (ignoring leading '/contents/')
    topic_name = path.split('/contents/')[-1]
    
    # Reconstruct the new URL with the topic name and the existing query parameters
    new_url = f"{new_base_url}/{topic_name}/json?{urlencode(query_params, doseq=True)}"
    
    return new_url

  def get_article_page_date(self, soup: BeautifulSoup):
    # Find the span tag with the data-datestring attribute
    # Find the span with class "article-date"
    date_span = soup.find('span', {'class': 'article-date'})

    # Extract the date text
    date_str = date_span.get_text(strip=True)

    # Convert to datetime object
    date_format = "%B %d, %Y"  # Format matching "July 19, 2024"
    return datetime.strptime(date_str, date_format)

  def get_article_page_title(self, soup):
    title_tag = soup.find('div', {"id": "topicTitle"})
    if title_tag:
        return title_tag.text.strip() 
    return ''
  
  def get_article_page_content(self, soup):
    content_div = soup.find('div', class_='article__main-content')
    if content_div:
        return self.convert_html_to_markdown(str(content_div))
    else:
        return "NO content" 
    
  def stop_parsing(self, date):
    return False

      