


import logging
import time
import traceback
from typing import Dict

from bs4 import BeautifulSoup
import html2text
import requests
from blog_parser import BlogParser
from helper import create_session, get_selenium_driver, selenium_base, write_to_file
from seleniumbase import SB


logger = logging.getLogger(__name__)


class SubParser(BlogParser):
  def __init__(self, url, main_url, is_selenium = False):
    self.url = url
    self.mainUrl = main_url
    self.isSelenium = is_selenium

  def process_article(self):
    try:
        article = self.parse_article_page(create_session(), self.url)
        # get by article
        cleaned_article = {
           'doi_url': self.url,
           'title': article['title'],
           'content': article['content'],
           'date': article['date'],
           'pdf_text': article['pdf_text'] if 'pdf_text' in article else '',
           'references': article['references'] if 'references' in article else [],
           'authors': article['authors'] if 'authors' in article else []   
        }

        # self.save_article_in_db(mainUrl=self.mainUrl, articleUrl=self.url, title=title, date=date, content=content, pdf_text=pdf_text, references=references)
        # print('cleaned_article.references', cleaned_article['references'])

        return cleaned_article
    
    except Exception as e:
      logger.error(f"Error processing article {self.url}: {e}")
      logger.info(traceback.format_exc())
      return None

  def stop_parsing(self):
    return False

  def get_article_page_date(self, soup: BeautifulSoup):      
      return 'No date'

  def get_article_page_title(self, soup: BeautifulSoup):
      title = ''
      try:
        title_tag = soup.find('title')
        if title_tag:
            return title_tag.text.strip() 
      except Exception as e:
        print('Error on get_article_page_title', e)

      return title

  def main(self):
    logger.info(f">>> Started parsing {self.url}")
    print('Started parsing')

    try:
        return self.process_article()
    except requests.exceptions.RequestException as e:
        logger.info(f"An error occurred while fetching the page: {e}")
         # Log the detailed traceback
        logger.info(traceback.format_exc())
        return {}
    except Exception as e:
        logger.info(f"An unexpected error occurred: {e}")
        # Log the detailed traceback
        logger.info(traceback.format_exc())
        return {}
    
  def remove_correspondence(self, html: BeautifulSoup):
     # Find all <br> tags
     try:
      br_tags = html.find_all('br')

      # Initialize a flag to track whether we're in the section to remove
      in_correspondence_section = False

      # Iterate through the <br> tags and remove text accordingly
      for br in br_tags:
          # Check the next sibling to see if it starts with "Correspondence from:"
          next_sibling = br.next_sibling
          if next_sibling and isinstance(next_sibling, str) and next_sibling.strip().startswith("Correspondence:"):
              in_correspondence_section = True

          # If we are in the correspondence section and the next sibling starts with "Abstract:", stop removing
          if in_correspondence_section:
              if next_sibling and isinstance(next_sibling, str) and next_sibling.strip().startswith("Abstract:"):
                  in_correspondence_section = False
              else:
                  # Remove the text in the next sibling if it is a string
                  if isinstance(next_sibling, str):
                      br.next_sibling.extract()
     except Exception as e:
        print('remove_correspondence error', e)
        return

  def convert_html_to_markdown_with_origin_pre(self, html: BeautifulSoup):
    self.remove_correspondence(html)

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
        if not src.startswith(origin):
            img_tag["src"] = origin + src
    
    # Convert modified HTML back to string
    modified_html = str(html)
    
    # Convert to markdown
    h = html2text.HTML2Text()
    h.ignore_links = False  # Keep links in the markdown
    return h.handle(modified_html)
  

  def get_soup_by_selenium(self):
    # driver = get_selenium_driver(headless=False)
    try:
      with SB(uc=True, headless=False) as sb:
        print('hhhhhhh')
        # driver = selenium_base(headless=False)
        # Open the URL
        sb.get(self.url)
        # Optional: Wait for a specific element or condition (can be adjusted)
        # sb.implicitly_wait(10)  # Wait for up to 10 seconds for the page to load
         # Scroll to the bottom of the page
        print('Waiting for 5 seconds...')
        time.sleep(5)
        # Scroll to the bottom of the page using JavaScript
        print('Scrolling to the bottom of the page...')
        last_height = sb.execute_script("return document.body.scrollHeight")
        
        while True:
            # Scroll down to the bottom
            sb.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            
            # Wait for content to load
            time.sleep(3)
            
            # Calculate new scroll height
            new_height = sb.execute_script("return document.body.scrollHeight")
            if new_height == last_height:  # Exit if no new content is loaded
                break
            last_height = new_height
        print('step 2 -> selenium')
        # Wait for 10 seconds before proceeding
        print('Waiting for 10 seconds...')
        time.sleep(10)
        # Get the fully loaded page's HTML
        html = sb.get_page_source()
        # write_to_file('cccccc.html', html)
        soup = BeautifulSoup(html, 'html.parser')
        return soup
    except Exception as e:
       logger.info('Error on pubmed sub', e)
  
  def parse_article_page(self, session: requests.Session, url: str) -> Dict[str, str]:
    if self.isSelenium:
       soup = self.get_soup_by_selenium()
       with open('draft/ssss.html', 'w') as f:
        f.write(str(soup))
    
       f.close()
    else:
       soup = self.get_parsed_soup(session, url)

    article = {}
    article['title'] = self.get_article_page_title(soup)
    article['date'] = self.get_article_page_date(soup)
    article['references'] = self.get_article_references(soup)
    article['authors'] = self.get_authors(soup)
    article['content'] = self.get_article_page_content(soup)
    
    return article