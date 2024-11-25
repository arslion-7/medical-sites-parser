from datetime import datetime
import logging
import os
import re
from typing import Dict
from bs4 import BeautifulSoup
import requests

from class_parsers.pubmed_doi.sub_parser import SubParser

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s')


class MdpiParser(SubParser):
  def __init__(self, url, main_url, is_selenium=False):
     super().__init__(url, main_url, is_selenium)

  def get_article_page_date(self, soup: BeautifulSoup):
      # pdf_text, references = self.get_article_page_pdf_text(soup)
      # with open('draft/mdpi_pdf.md', 'w') as f:
      #    f.write(pdf_text)
     # Find the element with the 'Published' date
      pubhistory_div = soup.find('div', class_='pubhistory')
      if pubhistory_div:
          # Look for the 'Published' span text
          published_span = pubhistory_div.find('span', text=re.compile('Published:'))
          if published_span:
              # Extract the date after 'Published:'
              date_text = published_span.text.strip().replace('Published:', '').strip()

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
    title_tag = soup.find('h1', class_='title hypothesis_container')
    if title_tag:
        return title_tag.text.strip()
    return ''
  
  # def extract_text_from_pdf(self, file_name):
  #   print('file_name', file_name)
  #   import fitz  # PyMuPDF

  #   text = ""

  #   with fitz.open(file_name) as doc:
  #     for page in doc:
  #         text += page.get_text()

  #   return text
  
  # def get_article_page_pdf_text(self, soup: BeautifulSoup):
  #   import re

  #   pdf_url = self.extract_pdf_url(soup)
  #   file_name = self.download_pdf(pdf_url)
  #   text  = self.extract_text_from_pdf(file_name)

  #   # references
  #   references = re.findall(r'\n\s*\d+\.\s+(.+?)(?=\n\s*\d+\.|\Z)', text, re.DOTALL)

  #   from markdownify import markdownify
  #   # Convert the text to Markdown
  #   markdown_text = markdownify(text)
  #   return markdown_text, references
  
  # def download_pdf(self, pdf_url):
  #   # Download the PDF file
  #   pdf_response = requests.get(pdf_url)

  #   # Extract the file name from the URL
  #   pdf_filename = os.path.basename(pdf_url)

  #   # Define the directory to save the PDF
  #   pdf_directory = 'pdf/mdpi'

  #   # Ensure the directory exists
  #   os.makedirs(pdf_directory, exist_ok=True)

  #   # Full path for the PDF file
  #   pdf_filepath = os.path.join(pdf_directory, pdf_filename)

  #   # Save the PDF file locally
  #   with open(pdf_filepath, 'wb') as file:
  #       file.write(pdf_response.content)

  #   return pdf_filepath

  # def extract_pdf_url(self, soup: BeautifulSoup):
  #   drop_down = soup.find('div', {'id': 'drop-download-1440832'})
  #   print('ddd', drop_down)
  #   pdf_a = drop_down.find('a', class_='UD_ArticlePDF')
  #   print('aaa', pdf_a)
  #   pdf_url = pdf_a['href']

  #   # Ensure the URL is absolute
  #   if not pdf_url.startswith("http"):
  #       pdf_url = requests.compat.urljoin(self.get_origin(self.url), pdf_url)      

  #   return pdf_url
  
  # def download_pdf(self, pdf_url):
  #   # Download the PDF file
  #   pdf_response = requests.get(pdf_url)

  #   # Extract the file name from the URL
  #   pdf_filename = os.path.basename(pdf_url)

  #   # Define the directory to save the PDF
  #   pdf_directory = 'pdf'

  #   # Ensure the directory exists
  #   os.makedirs(pdf_directory, exist_ok=True)

  #   # Full path for the PDF file
  #   pdf_filepath = os.path.join(pdf_directory, pdf_filename)

  #   # Save the PDF file locally
  #   with open(pdf_filepath, 'wb') as file:
  #       file.write(pdf_response.content)

  #   return pdf_filepath
  
  def convert_html_to_markdown_with_origin_pre(self, html: BeautifulSoup):
    origin = self.get_origin(self.url) + '/'
     # Process <a> tags
    for a_tag in html.find_all("a", href=True):
        href = a_tag["href"]
        if href.startswith("#"):
            a_tag.decompose()  # Remove the <a> tag if href starts with "#"
        elif not href.startswith(origin):
            a_tag["href"] = origin + href
    
    # Process <img> tags
    for img_tag in html.find_all("img", src=True):
      src = img_tag["src"]
      if not src.startswith("http"):
          img_tag["src"] = origin + src
        
    
    # Convert modified HTML back to string
    modified_html = str(html)
    preprocessed_html = self.preprocess_html(modified_html)

    import markdownify as md
    # Convert to markdown
    markdown = md.markdownify(preprocessed_html, heading_style="ATX")
    return markdown

  def get_article_page_content(self, soup: BeautifulSoup):
    try:
       # Find all description divs
      description_divs = soup.find_all('div', class_='html-table_wrap_discription')

      # Find all captions and tables (they appear after the descriptions)
      captions = soup.find_all('div', class_='html-caption')
      # Create a map to match table captions with tables (assuming correct order)
      # Create a map to match table captions with tables (only matching "Table n")
      # Create a map to match table captions with tables (only matching "Table n.")
      table_map = {}
      for caption in captions:
          b_tag_text = caption.find('b').text.strip()  # Get the text inside the <b>
      
        # Use a regex to match the pattern "Table n." where n is a number
          match = re.match(r'^Table \d+\.$', b_tag_text)
          
          if match:
              table_number = b_tag_text  # Get the matched "Table n." string
              
              # Find the next sibling of the caption div that is a table
              next_sibling = caption.find_next_sibling('table')
              
              # If the next sibling is a table, map it to the caption
              if next_sibling:
                  table_map[table_number] = next_sibling

      # Output the matched table numbers and corresponding tables
      for table_number, table in table_map.items():
          print(f"{table_number}:")
          print(table.prettify())
          print()

        # Loop through description divs in the HTML
      for description_div in description_divs:
          table_number = description_div.find('b').text.strip()  # Extract the table number

          # Check if a corresponding table exists after the descriptions
          if table_number in table_map:
              # Append the corresponding table after the description
              description_div.append(table_map[table_number])

      content_div = soup.find('div', class_='html-dynamic')
      html_p_s = soup.find('div', class_='html-body')

      # finding tag whose child to be deleted 
      img_tables = soup.find_all('div', class_='html-table_wrap_td') 
        
      # delete the child element 
      for img_table in img_tables:
        img_table.decompose()

      # content_div.append(html_p_s)
      # Get the remaining content
      # return self.convert_html_to_markdown_with_origin_pre(description_divs)
      remaining_content =  f'{self.convert_html_to_markdown_with_origin_pre(content_div)} {self.convert_html_to_markdown_with_origin_pre(html_p_s)}'
      # remaining_content = content_div.find_all() + html_p_s.find_all()
      # remaining_content = html_p_s.find_all()
      remaining_content = re.sub(r'\[\,+\]|\[\]', '', remaining_content) # clean up [], [,] ...

    except Exception as e:
       logger.info(f'Error on get_article_page_content', e)

    return remaining_content

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
    # references = []
    # Find the section with id="html-references_list"
    references_section = soup.find('section', id='html-references_list')

    # Extract the references within that section
    try:
      references = []
      if references_section:
          for li in references_section.find_all('li'):
              reference_text = li.get_text(separator=" ", strip=True)
              references.append(reference_text)
      references_list = []
    # Print the references
      for i, ref in enumerate(references, 1):
        references_list.append(f"{i}. {ref}")
    except Exception as e:
       logger.info(f'Error on get_article_references', e)
       return []

    return references_list
  