from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta
import logging
import random
import time
from typing import Dict, List
from urllib.parse import urljoin
from bs4 import BeautifulSoup
import html2text
import requests

from blog_parser import BlogParser
from db.mongodb_local import test_save_article

logger = logging.getLogger(__name__)


class AgapovmdParser(BlogParser):
  def __init__(self, main_url, pagination, parse_weeks_count = 1, save_action=test_save_article):
    super().__init__(main_url, pagination, parse_weeks_count, save_action)

  def fetch_url(self, session: requests.Session, url: str) -> str:
    headers = self.get_random_headers()
    session.headers.update(headers)
    time.sleep(random.uniform(0, 2))
    response = session.get(url)
    response.encoding = 'utf-8'
    response.raise_for_status()
    return response.text

  def get_parsed_soup(self, session: requests.Session, url: str):
      html_content = self.fetch_url(session, url)
      soup = BeautifulSoup(html_content, 'lxml')
      return soup

  def find_articles(self, soup: BeautifulSoup):
    table = soup.find('table', {'style': "margin-top:5px"})

    return table.find_all('tr')

  def get_card_title_a_tag(self, card):
    # Find the <td> element with the onclick attribute
    td_element = card.find('td')

    # Extract the value of the onclick attribute
    onclick_value = td_element['onclick']

    # Extract the URL fragment from the onclick value
    url_fragment = onclick_value.split("'")[1]
    base_url = "https://agapovmd.ru/dis/skin/"
    full_url = base_url + url_fragment
    return full_url
  
  def get_card_title_url(self, title_a_tag):
    return title_a_tag

  def get_article_page_date(self, soup: BeautifulSoup):
    return 'No date'
  
  def stop_parsing(self, date):
    return False

  def get_article_page_title(self, soup):
    title_tag = soup.find('title')
    if title_tag:
        return title_tag.text.strip() 
    return ''
  
  def get_article_page_content(self, soup: BeautifulSoup):
    # Extract the text from the specific <td> element
    # Find all <div> elements with class "spoiler_body"
    div_elements = soup.find_all('div', class_='spoiler_body')

    # Find the <td> element with class "int"
    td_element = soup.find('td', class_='int')

    # Combine HTML of all elements to be converted to Markdown
    html_text = ''.join(str(div) for div in div_elements)
    if td_element:
      html_text += str(td_element)

    # Convert the combined HTML to Markdown
    markdown_text = html2text.html2text(html_text)

    # Save all text to a variable
    full_text = markdown_text

    return full_text

  def save_article_in_db(self, mainUrl, articleUrl, title, date, content, pdf_text, references):
      self.save_action(mainUrl='https://agapovmd.ru/dis/index.htm',
                          articleUrl=articleUrl,
                          title=title,
                          date=date,
                          content=content,
                          pdf_text=pdf_text,
                          references=references)
      