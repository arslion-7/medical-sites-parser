from datetime import datetime
import logging
import re
from typing import Dict
from bs4 import BeautifulSoup

from class_parsers.pubmed_doi.sub_parser import SubParser

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s')


class AafpOrgParser(SubParser):
  def __init__(self, url, main_url, is_selenium=False):
     super().__init__(url, main_url, is_selenium)
     self.domain = 'https://www.aafp.org'

  def get_article_page_date(self, soup: BeautifulSoup):    
      # Find the span with the class "adl-next-and-previous__link-text"
      span = soup.find('span', {'class': 'adl-next-and-previous__link-text'})
      if not span:
          return 'No date'
      
      # Extract the date text
      date_text = span.get_text().strip()
      
      try:
          # Parse the date text to datetime object
          return datetime.strptime(date_text, '%b %d, %Y')
      except ValueError:
          return 'No date'

  def get_article_page_title(self, soup):
    try:
       h1_element = soup.find('h1', class_='adl-h1')
       return h1_element.text.strip()
    except Exception as e:
       logger.info(f'Error on title', e)
       return ''
    
  def get_authors(self, soup: BeautifulSoup):
    try:
     # Find all div elements with class "profile-card-drop"
      author_divs = soup.find('div', class_='adl-body adl-space__sm__m-t-xs')

      # Find the <p> tag with the class 'adl-body'
      p_tag = author_divs.find('p', class_='adl-body')
      
      if p_tag:
          # Extract the text from the <p> tag
          text = p_tag.get_text(strip=True)
          
          # Extract the author name, assuming it's the part before the first comma
          author_name = text.split(',')[0]
          return author_name
    except Exception as e:
       logger.info(f'Error on get_authors', e)
       return []
  
  def get_article_references(self, soup):

    references_list = []
    try:
    # Extracting references
      # Find all list items in the ordered list
      references = soup.find_all('li', class_='adl-journal-article-references__list-item')

      # Extract and format each reference
      for i, ref in enumerate(references, 1):
          reference_text = ref.get_text(separator=" ", strip=True)
          references_list.append(f'{i}. {reference_text}')
     
    except Exception as e:
       logger.info(f'Error on get_article_references', e)
       return []

    return references_list
  
  def get_article_page_content(self, soup: BeautifulSoup):
    try:
      content_div = soup.find('div', class_='aem-Grid aem-Grid--12 aem-Grid--default--12')
      remaining_content = content_div
      if remaining_content:
          return self.convert_html_to_markdown(str(remaining_content), remaining_content, self.domain)
      else:
          return "" 
    except Exception as e:
       logger.info(f'Error on get_article_page_content', e)
       return ''
  