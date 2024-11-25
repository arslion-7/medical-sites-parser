from datetime import datetime
import logging
import re
from typing import Dict
from bs4 import BeautifulSoup

from class_parsers.pubmed_doi.sub_parser import SubParser

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s')


class CureusParser(SubParser):
  def __init__(self, url, main_url, is_selenium=False):
     super().__init__(url, main_url, is_selenium)

  def get_article_page_date(self, soup: BeautifulSoup):      
      return 'No date'

  def get_article_page_title(self, soup):
    return ''
    
  def get_authors(self, soup: BeautifulSoup):
    try:
     # Find all div elements with class "profile-card-drop"
      author_divs = soup.find_all('div', class_='profile-card-drop')

      # Extract the text from each div (the author names)
      author_names = [div.text.strip() for div in author_divs]

      return author_names
    except Exception as e:
       logger.info(f'Error on get_authors', e)
       return []
  
  def get_article_references(self, soup):
   # Extract all references as strings
    ref_ol = soup.find('ol', class_='references')

    references_list = []
    try:
    # Extracting references
      references = []
      for li in ref_ol.find_all('li'):
          reference_text = li.get_text(separator=" ", strip=True)
          references.append(reference_text)

      # Iterate and extract information
      for i, ref in enumerate(references, start=1):
          if ref != '':
            # title = ref.a.text
            # journal_info = ref.text.split('. ')[-1]
            # doi_link = ref.find('span', class_='citation-doi').a['href']
            references_list.append(f'{i}. {ref}')
     
    except Exception as e:
       logger.info(f'Error on get_article_references', e)
       return []

    return references_list
  
  def get_article_page_content(self, soup: BeautifulSoup):
    try:
      content_div = soup.find('div', class_='new-article-content-wrap')

      references = content_div.find('ol', class_='references')
      references.extract()
      
      remaining_content = content_div
      if remaining_content:
          return self.convert_html_to_markdownify(str(remaining_content))
      else:
          return "" 
    except Exception as e:
       logger.info(f'Error on get_article_page_content', e)
       return ''
  