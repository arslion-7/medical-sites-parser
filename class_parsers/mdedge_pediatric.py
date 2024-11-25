from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta
import logging
import os
import time
from typing import Dict, List
from urllib.parse import urljoin
from bs4 import BeautifulSoup
import requests

from blog_parser import BlogParser
from db.mongodb_local import test_save_article

logger = logging.getLogger(__name__)


class MdedgePediatricParser(BlogParser):
  def __init__(self, main_url, pagination, parse_weeks_count = 1, save_action=test_save_article):
    super().__init__(main_url, pagination, parse_weeks_count, save_action)

  def find_articles(self, soup: BeautifulSoup):
    articles = soup.find_all('div', class_='views-row')
    return articles

  def get_card_title_a_tag(self, card: BeautifulSoup):
    h2 = card.find('h2')
    return h2.find('a', {'rel': 'bookmark'})

  def get_card_title_text(self, title_a_tag: BeautifulSoup):
    return title_a_tag.get_text(strip=True)
  
  def get_card_title_url(self, title_a_tag):
    title_link = title_a_tag['href']
    return urljoin(self.domain, title_link)

  def get_article_page_date(self, soup: BeautifulSoup):
    # Find the span with class "article-citation"
    citation_span = soup.find('span', {'class': 'article-citation'})

    # Extract the citation text
    citation_text = citation_span.get_text(strip=True)

    # Extract the date part "2017 January"
    date_part = citation_text.split(';')[0].split()[-2:]

    # Convert to datetime object
    date_str = ' '.join(date_part)
    date_format = "%Y %B"  # Format matching "2017 January"
    return datetime.strptime(date_str, date_format)

  def get_article_page_title(self, soup):
    # Find the <h1> tag with the specific id
    title_tag = soup.find('h1', id='page-title')

    # Extract and print the text
    if title_tag:
        title_text = title_tag.get_text(strip=True)
        return title_text
    else:
        return ''
  
  def get_article_page_content(self, soup):
    content_div = soup.find('div', class_='panel-pane pane-article-slideshows')
    if content_div:
        return self.convert_html_to_markdown(str(content_div))
    else:
        return "NO content" 
    
  def parse_article_page(self, session: requests.Session, url: str) -> Dict[str, str]:
    soup = self.get_parsed_soup(session, url)
    
    article = {}
    article['title'] = self.get_article_page_title(soup)
    article['content'] = self.get_article_page_content(soup)
    article['date'] = self.get_article_page_date(soup)
    # pdf
    article['pdf_text'], article['references'] = self.get_article_page_pdf_text(soup)
    
    return article

  def get_article_page_pdf_text(self, soup: BeautifulSoup):
    import re

    pdf_url = self.extract_pdf_url(soup)
    file_name = self.download_pdf(pdf_url)
    text  = self.extract_text_from_pdf(file_name)

    # references
    references = re.findall(r'\n\s*\d+\.\s+(.+?)(?=\n\s*\d+\.|\Z)', text, re.DOTALL)

    from markdownify import markdownify
    # Convert the text to Markdown
    markdown_text = markdownify(text)
    return markdown_text, references

  def extract_pdf_url(self, soup: BeautifulSoup):
    pdf_link_tag = soup.find('div', class_='download-pdf').find('a')
    pdf_url = pdf_link_tag['href']

    # Ensure the URL is absolute
    if not pdf_url.startswith("http"):
        pdf_url = requests.compat.urljoin(self.domain, pdf_url)      

    return pdf_url

  def download_pdf(self, pdf_url):
    # Download the PDF file
    pdf_response = requests.get(pdf_url)

    # Extract the file name from the URL
    pdf_filename = os.path.basename(pdf_url)

    # Define the directory to save the PDF
    pdf_directory = 'pdf'

    # Ensure the directory exists
    os.makedirs(pdf_directory, exist_ok=True)

    # Full path for the PDF file
    pdf_filepath = os.path.join(pdf_directory, pdf_filename)

    # Save the PDF file locally
    with open(pdf_filepath, 'wb') as file:
        file.write(pdf_response.content)

    return pdf_filepath
  
  def extract_text_from_pdf(self, file_name):
    import fitz  # PyMuPDF

    text = ""

    with fitz.open(file_name) as doc:
      for page in doc:
          text += page.get_text()

    return text