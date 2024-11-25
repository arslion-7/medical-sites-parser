from datetime import datetime
import logging
import re
from typing import Dict
from bs4 import BeautifulSoup

from class_parsers.pubmed_doi.sub_parser import SubParser

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s')


class WjgnetParser(SubParser):
  def __init__(self, url, main_url, is_selenium=False):
     super().__init__(url, main_url, is_selenium)

  def get_article_page_date(self, soup: BeautifulSoup):
      # Try to find the publication date in the specific div with id "dpjournal"
    date_text = soup.find('div', {'id': 'dpjournal'}).find_all('span')[1].text.strip()
    
    # Parse the date text to datetime object
    try:
        date = datetime.strptime(date_text, '%b %d, %Y')
        return date.isoformat() + '.000+00:00'
    except ValueError:
        return 'No date'


  def get_article_page_title(self, soup):
    title_tag = soup.find('div', {'id': 'dptitle'})
    if title_tag:
        return title_tag.text.strip()
    return ''
  
  def get_article_page_content(self, soup: BeautifulSoup):
    content = ''
    try:
      dpabstract = soup.find('div', {'id': 'dpabstract'})
      if dpabstract:
          content += self.convert_html_to_markdown(str(dpabstract))
      else:
          return "" 
    except Exception as e:
       logger.info(f'Error on get_article_page_content dpabstract', e)

    try:
      sec11 = soup.find('div', {'id': 'sec11'})
      if sec11:
          content += self.convert_html_to_markdown(str(sec11))
      else:
          return "" 
    except Exception as e:
       logger.info(f'Error on get_article_page_content', e)

    return content
    
  def get_authors(self, soup: BeautifulSoup):
    try:
        # Find all author names
        # Find all elements that contain author names
        authors = []
        for author_tag in soup.find_all('a', class_='author-name-link'):
            # Extract the 'data-name' attribute
            author_name = author_tag.get('data-name')
            authors.append(author_name)
        
        return authors
    except Exception as e:
      logger.info(f'Error on get_authors', e)
      return []
  
  def get_article_references(self, soup):
    # Extract the references within that section
    try:
      references = soup.find_all('div', class_='article-ref')

      result = []

    # Extract and print each reference
      for ref in references:
        # Extract the number
        number = ref.find('a', class_='article-ref-vol').get_text(strip=True)
        
        # Extract the title and journal information
        title_parts = ref.find_all('span')
        title_text = ' '.join(part.get_text(strip=True) for part in title_parts if not part.find('a'))
        
        # Extract the URLs
        urls = ref.find_all('a', href=True)
        pubmed_url = [a['href'] for a in urls if 'pubmed' in a['href']]
        doi_url = [a['href'] for a in urls if 'doi' in a['href']]
        
        # Combine the reference into a single string
        pubmed_link = f"[PubMed: {pubmed_url[0]}]" if pubmed_url else ""
        doi_link = f"[DOI: {doi_url[0]}]" if doi_url else ""
        
        reference_text = f"{number} {title_text} {pubmed_link} {doi_link}"
        result.append(reference_text)
    except Exception as e:
       logger.info(f'Error on get_article_references', e)
       return []

    return result
  