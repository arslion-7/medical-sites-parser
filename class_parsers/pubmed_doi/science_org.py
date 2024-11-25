from datetime import datetime
import logging
import re
import time
from typing import Dict
from bs4 import BeautifulSoup
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

from class_parsers.pubmed_doi.sub_parser import SubParser
from helper import get_selenium_driver, selenium_base, write_to_file
from seleniumbase import SB



logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s')


class ScienceOrgParser(SubParser):
  def __init__(self, url, main_url, is_selenium=False):
     super().__init__(url, main_url, is_selenium)
     self.domain = 'https://www.science.org'

  def get_soup_by_selenium(self):
    with SB(headless=False, uc=True) as sb:
      sb.open(self.url)
      sb.sleep(20)
      html = sb.get_page_source()
      write_to_file('aaa.html', html)
      soup = BeautifulSoup(html, 'lxml')
      return soup  
    # finally:
    #   driver.quit()

  def get_article_page_date(self, soup: BeautifulSoup):
    date = 'No date'
    # Find the span with the property "datePublished"
    try:
        span = soup.find('span', {'property': 'datePublished'})
        if not span:
            return 'No date'
        # Extract the date text
        date_text = span.get_text().strip()
        
        # Parse the date text to a datetime object
        date = datetime.strptime(date_text, '%d %b %Y')
        return date  # Return datetime object
    except Exception as e:
        print('Exception in get_article_page_date', e)

    return date
  
  def get_article_page_content(self, soup: BeautifulSoup):
    content = ''
    try:
      all_content = soup.find('section', {'id': 'bodymatter'})
        # Convert the modified HTML to markdown
      content = self.convert_html_to_markdownify(str(all_content), all_content, domain=self.domain)
      return content
    except Exception as e:
       logger.info(f'Error on get_article_page_content all', e)

    return content
    
  def get_authors(self, soup: BeautifulSoup):
    # Find all authors with givenName and familyName
    result = []
    try:
      authors = soup.find_all('span', {'property': 'author', 'typeof': 'Person'})

      # Extract author details
      for author in authors:
          given_name = author.find('span', {'property': 'givenName'}).text if author.find('span', {'property': 'givenName'}) else ''
          family_name = author.find('span', {'property': 'familyName'}).text if author.find('span', {'property': 'familyName'}) else ''
          orcid_link = author.find('a', {'class': 'orcid-id'})
          orcid = orcid_link['href'] if orcid_link else ''
          author_result = f"{given_name} {family_name}, ORCID: {orcid}"
          result.append(author_result)
    except Exception as e:
      print('Error on get_authors', e)

    return result
  
  def get_article_references(self, soup):
    # Extract the references within that section
    result = []
    try:
      citations = soup.find_all('div', class_='citation-content')

      # Extract and format each citation
      for i, citation in enumerate(citations, 1):
          citation_text = citation.get_text(separator=" ", strip=True)
          result.append(f"{i}. {citation_text}")
    except Exception as e:
       logger.info(f'Error on get_article_references', e)
       return []

    return result
  