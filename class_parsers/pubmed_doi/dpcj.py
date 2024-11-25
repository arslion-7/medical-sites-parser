from datetime import datetime
import logging
import re
from typing import Dict
from bs4 import BeautifulSoup

from class_parsers.pubmed_doi.sub_parser import SubParser

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s')


class DpcjParser(SubParser):
  def __init__(self, url, main_url, is_selenium=False):
     super().__init__(url, main_url, is_selenium)

  def get_article_page_date(self, soup: BeautifulSoup):
     published_div = soup.find('div', class_='item published')
     if published_div:
        # Locate the span inside the div containing the date
        date_span = published_div.find('span')
        if date_span:
            date_text = date_span.text.strip()

            try:
                # Convert the date text to a datetime object
                date_obj = datetime.strptime(date_text, '%Y-%m-%d')
                # Return in the desired format 'YYYY-MM-DDT00:00:00.000+00:00'
                return date_obj.strftime('%Y-%m-%dT00:00:00.000+00:00')
            except ValueError:
                return 'No date'
        
        return 'No date'

  def get_article_page_title(self, soup):
    title_tag = soup.find('h3', class_='page_title')
    if title_tag:
        return title_tag.text.strip()
    return ''
  
  def get_article_page_content(self, soup: BeautifulSoup):
    try:
      content_div = soup.find('section', class_='item abstract')
      if content_div:
          return self.convert_html_to_markdown(str(content_div))
      else:
          return "" 
    except Exception as e:
       logger.info(f'Error on get_article_page_content', e)
       return ''
    
  def get_authors(self, soup: BeautifulSoup):
    try:
      authors_list = []
      authors = []
      for li in soup.find_all('li'):
          name = li.find('span', class_='name').get_text(strip=True)
          affiliation = li.find('span', class_='affiliation').get_text(strip=True)
          authors_list.append((name, affiliation))

      # Print the extracted authors and affiliations
      for name, affiliation in authors_list:
          authors.append(name)
          return authors
    except Exception as e:
      logger.info(f'Error on get_authors', e)
      return []
  
  def get_article_references(self, soup):
   # Extract all references as strings
    # references = []
    # Find the section with id="html-references_list"
    references_section = soup.find('section', id='html-references_list')

    # Extract the references within that section
    try:
      references_list = []
      # Find the section with class "item references"
      references_section = soup.find('section', class_='item references')

      # Extract the references within that section
      references = []
      if references_section:
          for p in references_section.find_all('p'):
              reference_text = p.get_text(separator=" ", strip=True)
              references.append(reference_text)

      # Print the references
      for i, ref in enumerate(references, 1):
          references_list.append(f"{i}. {ref}")
    except Exception as e:
       logger.info(f'Error on get_article_references', e)
       return []

    return references_list
  