from datetime import datetime
import logging
import re
from typing import Dict
from urllib.parse import urljoin
from bs4 import BeautifulSoup

from class_parsers.pubmed_doi.sub_parser import SubParser

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s')


class IjdvlParser(SubParser):
  def __init__(self, url, main_url, is_selenium=False):
     super().__init__(url, main_url, is_selenium)
     self.domain = 'https://ijdvl.com'

  def get_article_page_date(self, soup: BeautifulSoup):
      published_time = soup.find('time', itemprop='datePublished')
      if published_time:
            date_text = published_time.text.strip()
            try:
                # Parse the date based on different possible formats
                if len(date_text) == 10:  # Full date 'YYYY-MM-DD'
                    date_obj = datetime.strptime(date_text, '%Y-%m-%d')
                elif len(date_text) == 7:  # Year and month 'YYYY-MM'
                    date_obj = datetime.strptime(date_text, '%Y-%m')
                    # Assuming the first day of the month if day is not provided
                    date_obj = date_obj.replace(day=1)
                elif len(date_text) == 4:  # Only year 'YYYY'
                    date_obj = datetime.strptime(date_text, '%Y')
                    # Assuming the first day of the year if only year is provided
                    date_obj = date_obj.replace(month=1, day=1)
                else:
                    return 'No date'

                # Return in the desired format 'YYYY-MM-DDT00:00:00.000+00:00'
                return date_obj.strftime('%Y-%m-%dT00:00:00.000+00:00')
            except ValueError:
                return 'No date'
      return 'No date'


  def get_article_page_title(self, soup):
    title_tag = soup.find('h1', class_='article-title')
    if title_tag:
        return title_tag.text.strip()
    return ''
  
  def get_article_page_content(self, soup: BeautifulSoup):
    try:
      content_div = soup.find('div', class_='body')
      if content_div:
        # Update img src to include domain if necessary
        return self.convert_html_to_markdownify(str(content_div), content_div, self.domain)
        #   return self.convert_html_to_markdown(str(content_div), content_div, self.domain)
      else:
          return ""
    except Exception as e:
       logger.info(f'Error on get_article_page_content', e)
       return ''
    
  def get_authors(self, soup: BeautifulSoup):
    try:
      # Find all author names
      authors = []
      for author in soup.find_all('span', class_='contrib'):
          given_name = author.find('span', class_='given-names').get_text(strip=True)
          surname = author.find('span', class_='surname').get_text(strip=True)
          full_name = f"{given_name} {surname}"
          authors.append(full_name)
      
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
      reference_list = soup.find_all('li', class_='ref')
      result = []

# Extract and print each reference
      for i, reference in enumerate(reference_list, start=1):
          # Extract authors
          authors = reference.find('span', class_='citation-authors-year').get_text(separator=" ", strip=True)
          
          # Extract title
          title = reference.find('span', itemprop='name').get_text(strip=True)
          
          # Extract publication details
          volume_info = reference.find('span', class_='volume')
          publication_details = volume_info.get_text(separator=" ", strip=True) if volume_info else "No publication details found"
          
          # Extract Google Scholar link
          google_scholar_link = reference.find('a', href=True)
          link = google_scholar_link['href'] if google_scholar_link else "No link available"
          
          # Combine the reference into a single string
          reference_text = f"{i}. {authors}. {title}. {publication_details}. {link}"
          
          # Print the extracted reference with numbering
          result.append(reference_text)
    except Exception as e:
       logger.info(f'Error on get_article_references', e)
       return []

    return result
  