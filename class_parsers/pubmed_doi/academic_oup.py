from datetime import datetime
import logging
import re
from bs4 import BeautifulSoup

from class_parsers.pubmed_doi.sub_parser import SubParser
from helper import get_selenium_driver


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s')


class AcademicOupParser(SubParser):
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
  
  def get_article_page_content(self, soup: BeautifulSoup):
    try:
      references = soup.find_all('div', class_='mixed-citation citation')
      for r in references:
         r.extract()
      author_buttons = soup.find_all('button', class_='linked-name')
      for author in author_buttons:
         author.extract()
         
      content_div = soup.find('div', {'data-widgetname': "ArticleFulltext"})
      # Get the remaining content
      # remaining_content = content_div.find_all()
      if content_div:
          return self.convert_html_to_markdownify(str(content_div))
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
    print('aaaa', soup)
    references = []
    try:
      # Find all citation divs
      citations = soup.find_all('div', class_='mixed-citation citation')

      # Process each citation
      citation_list = []
      for i, citation in enumerate(citations, start=1):
          # Extract author names
          authors = []
          for surname, given_names in zip(citation.find_all('div', class_='surname'), citation.find_all('div', class_='given-names')):
              authors.append(f"{surname.get_text(strip=True)} {given_names.get_text(strip=True)}")

          # Extract other details
          article_title = citation.find('div', class_='article-title').get_text(strip=True) if citation.find('div', class_='article-title') else ''
          journal_name = citation.find('div', class_='source').get_text(strip=True) if citation.find('div', class_='source') else ''
          year = citation.find('div', class_='year').get_text(strip=True) if citation.find('div', class_='year') else ''
          volume = citation.find('div', class_='volume').get_text(strip=True) if citation.find('div', class_='volume') else ''
          fpage = citation.find('div', class_='fpage').get_text(strip=True) if citation.find('div', class_='fpage') else ''
          
          # Combine citation information
          citation_info = f"{i}. {', '.join(authors)}. {article_title}. {journal_name}. {year}; {volume}:{fpage}."
          citation_list.append(citation_info)
          references = citation_list
    except Exception as e:
       logger.info(f'Error on get_article_references', e)
       return []
    return references
  
  # def get_soup_by_selenium(self):
  #   driver = get_selenium_driver()
  #   # Open the URL
  #   driver.get(self.url)
  #   # Optional: Wait for a specific element or condition (can be adjusted)
  #   driver.implicitly_wait(20)  # Wait for up to 10 seconds for the page to load
  #   print('step 2 -> selenium')
  #   # Get the fully loaded page's HTML
  #   html = driver.page_source
  #   with open('draft/selenium_html.html', 'w') as f:
  #      f.write(html)
  #   f.close()
    
  #   soup = BeautifulSoup(html, 'html.parser')
  #   # Close the browser
  #   driver.quit()

  #   return soup
