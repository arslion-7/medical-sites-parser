from datetime import datetime
import logging
import re
from bs4 import BeautifulSoup

from class_parsers.pubmed_doi.sub_parser import SubParser


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s')


class JournalsViamedicaParser(SubParser):
  def __init__(self, url, main_url, is_selenium=False):
     super().__init__(url, main_url, is_selenium)

  def get_article_page_date(self, soup: BeautifulSoup):
      # Find the element with class 'citation-date'
      date_div = soup.find('div', class_='citation-date')
      if date_div:
          date_text = date_div.text.strip()

          # Use regex to extract the day, month, and year
          full_date_match = re.search(r'(\d{1,2})\s+([A-Za-z]+)\s+(\d{4})', date_text)
          if full_date_match:
              day, month_abbr, year = full_date_match.groups()
              try:
                  # Convert to datetime object
                  date_obj = datetime.strptime(f'{day} {month_abbr} {year}', '%d %B %Y')
                  # Return in format 'YYYY-MM-DDT00:00:00.000+00:00'
                  return date_obj.strftime('%Y-%m-%dT00:00:00.000+00:00')
              except ValueError:
                  return 'No date'
      
      return 'No date'

  def get_article_page_title(self, soup):
    title_tag = soup.find('h1', class_='wi-article-title')
    if title_tag:
        return title_tag.text.strip()
    return ''
  
  def get_article_page_content(self, soup):
    try:
      content_div = soup.find('div', {'data-widgetname': "ArticleFulltext"})
      # Get the remaining content
      remaining_content = content_div.find_all()
      if remaining_content:
          return self.convert_html_to_markdown(str(remaining_content))
      else:
          return "" 
    except Exception as e:
       logger.info(f'Error on get_article_page_content', e)
       return ''
    
  def get_authors(self, soup: BeautifulSoup):
    try:
      # Find all buttons with class "linked-name"
      author_buttons = soup.find_all('button', class_='linked-name')

      # Extract the text from each button (the author names)
      author_names = [button.text.strip() for button in author_buttons]

      return author_names
    except Exception as e:
       logger.info(f'Error on get_authors', e)
       return []
  
  def get_article_references(self, soup):
   # Extract all references as strings
    references = []
    try:
      for ref in soup.select('.ref-content'):
          surname_tags = ref.find_all('div', class_='surname')
          given_names_tags = ref.find_all('div', class_='given-names')
          article_title = ref.find('div', class_='article-title') or ""
          source = ref.find('div', class_='source') or ""
          year = ref.find('div', class_='year') or ""
          volume = ref.find('div', class_='volume') or ""
          fpage = ref.find('div', class_='fpage') or ""
          lpage = ref.find('div', class_='lpage') or ""

          # Build the author part, handling missing surnames or given names
          authors = ', '.join([f"{surname.get_text() if surname else ''} {given.get_text() if given else ''}".strip() for surname, given in zip(surname_tags, given_names_tags)])
          
          # Build the full reference, using empty strings if elements are missing
          reference = f"{authors}. {article_title.get_text() if article_title else ''}. {source.get_text() if source else ''} {year.get_text() if year else ''};{volume.get_text() if volume else ''}: {fpage.get_text() if fpage else ''}–{lpage.get_text() if lpage else ''}.".strip()
          
          references.append(reference)
    except Exception as e:
       logger.info(f'Error on get_article_references', e)
       return []

    return references
