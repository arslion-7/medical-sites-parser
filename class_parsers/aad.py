from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta
import logging
import time
from typing import Dict, List
from urllib.parse import urljoin
from bs4 import BeautifulSoup
import requests

from blog_parser import BlogParser
from db.mongodb_local import test_save_article

logger = logging.getLogger(__name__)


class AadParser(BlogParser):
  def __init__(self, main_url, pagination, parse_weeks_count = 1, save_action=test_save_article):
    super().__init__(main_url, pagination, parse_weeks_count, save_action)

  def get_diseases(self):
    url = 'https://cdn.contentful.com/spaces/1ny4yoiyrqia/environments/master/entries/79dpzufO8k62Gi8RtI8hiQ?access_token=ad09cc96e755c4534eef8b60b5be3600acc229a58731818e6c1e0ca71791662f'
    response = requests.get(url)
    data = response.json()

    diseases = []
    for item in data["fields"]["diseasesAndConditionsLinks"]:
        diseases.append(item["sys"]["id"])

    return diseases
  
  def get_page_urls(self, disease_link_items):
    base_url = 'https://www.aad.org'
    sitemap_url = 'https://www.aad.org/sitemap.json'
    
    # Fetch the sitemap JSON data
    response = requests.get(sitemap_url)
    data = response.json()
    
    # Create a mapping from ID to URL
    id_to_url = {item['Id']: item['Url'] for item in data}

    links = []
    
    # Update disease_link_items with full URLs
    for item in disease_link_items:
        if 'linkToEntry' in item['fields']:
            entry_id = item['fields']['linkToEntry']['sys']['id']
            if entry_id in id_to_url:
                item['fields']['link'] = base_url + id_to_url[entry_id]
                links.append(base_url + id_to_url[entry_id])

    return links

  def parse_page(self, html_content: str) -> List[Dict[str, str]]:
    disease_links =  self.get_diseases()

    url = 'https://cdn.contentful.com/spaces/1ny4yoiyrqia/environments/master/entries?access_token=ad09cc96e755c4534eef8b60b5be3600acc229a58731818e6c1e0ca71791662f&content_type=linkItem'

    response = requests.get(url)

    links = []

    if response.status_code == 200:
        data = response.json()

        print(type(data))  # Output: <class 'dict'>
        disease_link_items = []

        for item in data["items"]:
            if item["sys"]["id"] in disease_links:
                disease_link_items.append(item)

        links = self.get_page_urls(disease_link_items)

    else:
        print("Request failed with status code:", response.status_code)

    return [self.parse_news_card(article) for article in links]

  def get_card_title_a_tag(self, link):
    return link
  
  def get_card_title_url(self, link):
    return link

  def get_article_page_date(self, soup: BeautifulSoup):

    return 'No date'

  def get_article_page_title(self, soup: BeautifulSoup):
    title_tag = soup.find('title')
    if title_tag:
        return title_tag.text.strip() 
    return ''
  
  def get_article_page_content(self, soup):
    content_main = soup.find('main')
    print('content_main', content_main)
    if content_main:
        return self.convert_html_to_markdown(str(content_main))
    else:
        return "NO content" 

  def stop_parsing(self, date):
    # There is no date on page, and have to parse all pages
    return False

      