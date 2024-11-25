from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta
import json
import logging
import re
import time
from typing import Dict, List
from urllib.parse import urljoin
from bs4 import BeautifulSoup

from blog_parser import BlogParser
from db.mongodb_local import test_save_article

logger = logging.getLogger(__name__)


class MsdmanualsParser(BlogParser):
  def __init__(self, main_url, pagination, parse_weeks_count = 1, save_action=test_save_article):
    super().__init__(main_url, pagination, parse_weeks_count, save_action)
    self.topics_list = []

  def extract_topics(self, data):
    if isinstance(data, dict):
        if "TopicName" in data and "TopicUrl" in data:
            self.topics_list.append({
                "TopicName": data["TopicName"]["value"],
                "TopicUrl": data["TopicUrl"]["path"]
            })
        for key, value in data.items():
            self.extract_topics(value)
    elif isinstance(data, list):
        for item in data:
            self.extract_topics(item)

  def find_articles(self, soup: BeautifulSoup):
    # Locate the <script> tag with id="__NEXT_DATA__"
    script_tag = soup.find('script', id='__NEXT_DATA__', type='application/json')

    if script_tag:
      # Extract the JSON data from the tag
      json_data = json.loads(script_tag.string)
      
      # Navigate through the JSON structure to find "ChapterChildren"
      page_props = json_data.get("props", {}).get("pageProps", {})
      layout_data = page_props.get("componentProps", {}).get("29d953c3-ae1e-436d-bc73-9a65abb23ea1", {})
      fields = layout_data.get("fields", {}).get("data", {})
      results = fields.get('item', {}).get("SectionChildrens", {}).get('results', {})

      topic_list = []

      # Iterate through the results to extract TopicName and TopicUrl
      for chapter in results:
          chapter_children = chapter.get("ChapterChildren", {}).get("results", [])
          
          for topic in chapter_children:
              topic_name = topic.get("TopicName", {}).get("value", "")
              topic_url = topic.get("TopicUrl", {}).get("path", "")
              
              if topic_name and topic_url:
                  topic_list.append({
                      "TopicName": topic_name,
                      "TopicUrl": topic_url
                  })

    return topic_list

  def get_card_title_a_tag(self, card):
    return card['TopicUrl']
  
  def get_card_title_url(self, title_a_tag):
    return urljoin(self.domain, title_a_tag)

  def get_article_page_date(self, soup: BeautifulSoup):
    # # Define a regex pattern to match "Month Year" format
    # Define regex pattern for "Month Year" format

    text = soup.find('div', class_='TopicHead_topic__revision__iWf71')

    text = text.get_text()

    # Define regex pattern for "Month Year" format
    pattern = r'([A-Za-z]+ \d{4})'

    # # Search for the date in the text
    match = re.search(pattern, text)

    if match:
        date_str = match.group(1)
        # Handle special case for "Sept"
        date_str = date_str.replace("Sept", "Sep")

        try:
            # Parse the date
            date_obj = datetime.strptime(date_str, "%b %Y")
            return date_obj
        except ValueError:
            return "No date"
    else:
        return "No date"

  def get_article_page_title(self, soup):
    title_tag = soup.find('title')
    if title_tag:
        return title_tag.text.strip() 
    return ''
  
  def get_article_page_content(self, soup):
    content_div = soup.find('div', class_='TopicMainContent_content__MEmoN')
    if content_div:
        return self.convert_html_to_markdown(str(content_div))
    else:
        return "NO content"
    
  def stop_parsing(self, date):
    return False

      