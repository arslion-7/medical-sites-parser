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

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s')


class EjcrimParser(SubParser):
  def __init__(self, url, main_url, is_selenium=False):
     super().__init__(url, main_url, is_selenium)
     self.domain = 'https://www.ejcrim.com'

  def get_soup_by_selenium(self):
    try:
      # driver = get_selenium_driver()
      driver = selenium_base()
      # Open the URL
      driver.get(self.url)
      element = WebDriverWait(driver, 10).until(
          EC.presence_of_element_located((By.CSS_SELECTOR, ".obj_galley_link.file"))
      )
      element.click()
      
      # Optional: Wait for a specific element or condition (can be adjusted)
      driver.implicitly_wait(10)  # Wait for up to 10 seconds for the page to load
      print('step 2 -> selenium')
      # Get the fully loaded page's HTML
      html = driver.page_source
      write_to_file('aaa.html', html)
      soup = BeautifulSoup(html, 'html.parser')
      # Find the iframe by its 'name' attribute
      iframe = soup.find('iframe', {'name': 'htmlFrame'})

      # If you want to get the 'src' attribute
      iframe_src = iframe['src'] if iframe else None

      if iframe_src:
         driver.get(iframe_src)
         title = WebDriverWait(driver, 10).until(
          EC.presence_of_element_located((By.CSS_SELECTOR, ".head"))
         )
         html = driver.page_source
         write_to_file('bbb.html', str(html))
         soup = BeautifulSoup(html, 'html.parser')
         return soup


    finally:
        # Close the browser
      driver.quit()

    return soup  

  def get_article_page_date(self, soup: BeautifulSoup):
    div = soup.find('div', {'class': 'reference'})
    if not div:
        return 'No date'
    
    # Look for the "Published" line
    published_line = div.find(text=lambda x: x and 'Published:' in x)
    if published_line:
        # Extract the date text
        date_text = published_line.split('Published:')[1].strip()
        try:
            # Parse the date text to datetime object
            date = datetime.strptime(date_text, '%d/%m/%Y')
            return date.isoformat() + '.000+00:00'
        except ValueError:
            return 'No date'
    
    return 'No date'

  def get_article_page_title(self, soup):
    title_tag = soup.find('div', {'class': 'head'})
    if title_tag:
        return title_tag.text.strip()
    return ''
  
  def get_article_page_content(self, soup: BeautifulSoup):
    content = ''
    try:
      all_content = soup.find('div', {'id': 'contenutoARTICOLO'})
        # Convert the modified HTML to markdown
      content = self.convert_html_to_markdown(str(all_content), all_content, domain=self.domain)
      return content
    except Exception as e:
       logger.info(f'Error on get_article_page_content all', e)

    return content
    
  def get_authors(self, soup: BeautifulSoup):
    return []
  
  def get_article_references(self, soup):
    # Extract the references within that section
    result = []
    try:
      references_div = soup.find('div', {'id': 'reference'})
      
      # Find all list items in the ordered list
      references = references_div.find('ol').find_all('li')

      # Extract and format each reference
      for i, ref in enumerate(references, 1):
          reference_text = ref.get_text(separator=" ", strip=True)
          result.append(f'{i}. {reference_text}')
    except Exception as e:
       logger.info(f'Error on get_article_references', e)
       return []

    return result
  