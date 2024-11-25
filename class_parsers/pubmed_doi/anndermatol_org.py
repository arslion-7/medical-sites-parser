from datetime import datetime
import logging
import re
from typing import Dict
from bs4 import BeautifulSoup

from class_parsers.pubmed_doi.sub_parser import SubParser

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s')


class AnndermatolOrgParser(SubParser):
  def __init__(self, url, main_url, is_selenium=False):
     super().__init__(url, main_url, is_selenium)

  def get_article_page_date(self, soup: BeautifulSoup):
    # Find the div with the id "article-front-meta-left"
    div = soup.find('div', {'id': 'article-front-meta-left'})
    if not div:
        return 'No date'
    
    # Look for the "Published online" line
    published_line = div.find(text=lambda x: x and 'Published online' in x)
    if published_line:
        # Extract the date text
        date_text = published_line.split('Published online')[1].strip().split('<br>')[0].strip()
        try:
            # Parse the date text to datetime object
            date = datetime.strptime(date_text, '%b %d, %Y')
            return date.isoformat() + '.000+00:00'
        except ValueError:
            return 'No date'
    
    return 'No date'

  def get_article_page_title(self, soup):
    title_tag = soup.find('h1', class_='content-title')
    if title_tag:
        return title_tag.text.strip()
    return ''
  
  def get_article_page_content(self, soup: BeautifulSoup):
    content = ''
    try:
      body = soup.find('div', {'id': 'article-level-0-body'})
      if body:
          content += self.convert_html_to_markdown(str(body))
      else:
          return "" 
    except Exception as e:
       logger.info(f'Error on get_article_page_content dpabstract', e)

    return content
    
  def get_authors(self, soup: BeautifulSoup):
    try:
        # Find all span elements with class 'capture-id'
        author_tags = soup.find_all('span', class_='capture-id')
        
        # Extract the names from the <a> tags within each span
        authors = []
        for tag in author_tags:
            # Find the <a> tag within the span
            a_tag = tag.find('a')
            if a_tag:
                # Extract the author's name
                author_name = a_tag.get_text(strip=True)
                authors.append(author_name)
        
        return authors
    except Exception as e:
      logger.info(f'Error on get_authors', e)
      return []
  
  def get_article_references(self, soup):
    # Extract the references within that section
    try:
      result = []

      # Find all references
      references = soup.find_all('li', class_='skip-numbering')

      # Extract and print each reference
      for ref in references:
          # Extract the number
          number = ref.get('value')
          
          # Extract the reference text
          ref_data = ref.find('span', class_='ref-data').get_text(separator=" ", strip=True)
          
          # Extract the URLs
          urls = ref.find_all('a', href=True)
          pubmed_url = [a['href'] for a in urls if 'pubmed' in a['href']]
          crossref_url = [a['href'] for a in urls if 'doi' in a['href']]
          
          # Combine the reference into a single string
          pubmed_link = f"[PubMed: {pubmed_url[0]}]" if pubmed_url else ""
          crossref_link = f"[CrossRef: {crossref_url[0]}]" if crossref_url else ""
          
          reference_text = f"{number}. {ref_data} {pubmed_link} {crossref_link}"
          result.append(reference_text)
    except Exception as e:
       logger.info(f'Error on get_article_references', e)
       return []

    return result
  