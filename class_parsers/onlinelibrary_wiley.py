from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta
import logging
import random
import re
import time
import traceback
from typing import Dict, List
from urllib.parse import urljoin
from bs4 import BeautifulSoup
import requests
from markdownify import markdownify as md
from seleniumbase import SB
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException



from blog_parser import BlogParser
from db.mongodb_local import test_save_article
from helper import get_selenium_driver, selenium_base, write_to_file

logging.basicConfig(filename='draft/onlinelibrary_wiley_pages.log',
                    filemode='a',
                    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                    datefmt='%H:%M:%S',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


class OnlinelibraryWileyParser(BlogParser):
  def __init__(self, main_url, pagination, parse_weeks_count = 1, save_action=test_save_article, 
               certain_article_urls=[], category='', subcategory=''):
    super().__init__(main_url, pagination, parse_weeks_count, save_action)
    self.domain = "https://onlinelibrary.wiley.com"
    self.certain_article_urls = certain_article_urls
    self.category = category
    self.subcategory = subcategory

  def parse_willey(self, driver, articleUrl):
      h1 = 'h1.citation__title'

      driver.wait_for_element(h1, timeout=20)  # Example: Wait for the main heading

      html = driver.get_page_source()
      soup = BeautifulSoup(html, 'lxml')

      pub_date = self.get_article_page_date(soup)
      title_text = self.get_article_page_title(soup)
      references_content =  self.get_article_references(soup)
      authors = self.get_authors(soup)
      pdf_text = self.get_article_page_content(driver)
      print(f"Title: {title_text}")          

      # Optionally, wait for some content on the new page to load

      self.save_article_in_db(
        mainUrl=self.domain,
        articleUrl=articleUrl,
        title=title_text,
        date=pub_date,
        content='',
        authors=authors,
        pdf_text=pdf_text,
        references=references_content,
        doi_url='',
      )

      # self.save_action(mainUrl=self.domain,
      #               articleUrl=articleUrl,
      #               title=title_text,
      #               date=pub_date,
      #               content='',
      #               authors=authors,
      #               pdf_text=pdf_text,
      #               references=references_content,
      #               doi_url='',
      #               )

  def parse_certain_articles(self, driver):
     for articleUrl in self.certain_article_urls:
        driver.get(articleUrl)
        self.parse_willey(driver, articleUrl)


  def get_soup_by_selenium(self, url):
    # from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.common.by import By

    try:
      # driver = selenium_base(headless=False)
      
      with SB(uc=True, headless=True) as sb:
        sb.get(url)
        # Wait for the button to be visible and click it
        accept_cookies = "button.osano-cm-accept-all"
        sb.click(accept_cookies)

        print('len(self.certain_article_urls)', len(self.certain_article_urls))

        if len(self.certain_article_urls) > 0:
            print('Processing specific articles...')
            self.parse_certain_articles(sb)
        else:
            for page in range(0, 1):
                logger.info(f'Processing page {page}')
                sb.get(f'https://onlinelibrary.wiley.com/action/doSearch?SeriesKey=15251470&sortBy=Earliest&startPage={page}&pageSize=20')
                sb.wait_for_element("a.publication_title.visitable", timeout=10)  # Wait until elements are present

                links = sb.find_elements("a.publication_title.visitable")
                print('Number of links found:', len(links))

                # Loop through the links
                for i in range(len(links)):
                    try:
                        # Re-find the elements to avoid stale element reference
                        links = sb.find_elements("a.publication_title.visitable")
                        href = links[i].get_attribute("href")
                        print(f"Processing Link {i+1}: {href}")

                        # Click on the current link
                        links[i].click()

                        # Parse the article
                        self.parse_willey(sb, articleUrl=href)

                        # Navigate back to the previous page
                        sb.go_back()

                        # Wait for the elements to be present again after navigation
                        sb.wait_for_element("a.publication_title.visitable", timeout=10)

                    except Exception as e:
                        logger.error('Error on parse inline wiley', exc_info=True)

            # sb.sleep(10)  # Pause to avoid overwhelming the server
    except Exception as e:
       logger.info('Error on parse inline willey', e)
    #    driver.quit()
    # finally:
    #    driver.quit()
    # return soup

  # def fetch_url_with_selenium_base(url):

  def fetch_url(self, session: requests.Session, url: str) -> str:
    print('begin fetch_url')
    response = session.get(url, verify=False)
    # Regular expression to find the URL between <!-- and -->
    pattern = r'<!--\s*(https?://[^\s]+)\s*-->'
    # Search for the URL
    match = re.search(pattern, response.text)

    if match:
        second_url = match.group(1)
        print("Extracted URL:", second_url)
        soup = self.get_soup_by_selenium(second_url)
        # get_by_playwright(second_url)
        with open('draft/iii.html', 'w') as f:
          f.write(str(soup))
      
        f.close()
        r = session.get(second_url)
    else:
        print("No URL found between <!-- and -->")

    return response.text

  def get_article_page_date(self, soup: BeautifulSoup):
    date_span = soup.find('span', class_='epub-date')
    if date_span:
        date_str = date_span.get_text(strip=True)
        # Parse the date string
        try:
            date = datetime.strptime(date_str, "%d %B %Y")
            return date
        except ValueError:
            return 'No date'
    return 'No date'

  def get_article_page_title(self, soup: BeautifulSoup):
    title_text = ''
    h1 = soup.find('h1', class_='citation__title')
    try:
      title_text = h1.text
    except Exception as e:
      print('Couldnt get title text', e)   
    return title_text

  def main(self):
    logger.info(f">>> Started parsing {self.main_url}")
    page = self.page_start
    # logger.info(f"{self.main_url}: {page}")
    self.fetch_url(self.session, self.get_paginated_url(page))

  def get_article_references(self, soup: BeautifulSoup):
    refs = []
    try:
      ref_soup = soup.find('section', class_='article-section__references')
      ul = ref_soup.find('ul')
      reference_list = ul.find_all('li')
      for reference in reference_list:
          refs.append(reference.text.strip())
    except Exception as e:
       print('Error on refs', e)
    return refs
  
  def get_authors(self, soup: BeautifulSoup):
    # authors_div = soup.find('div', class_='loa-wrapper loa-authors')
    try:
      # Find all elements that contain author names
      authors = []
      for author_span in soup.find_all('a', class_='author-name'):
          # Extract and clean the author's name text
          author_name = author_span.get_text(strip=True)
          # Remove any email icons or other non-name elements
          author_name = author_name.split(' ')[0]
          authors.append(author_name)
      
      return authors

    except Exception as e:
      logger.info(f'Error on get_authors', e)
      return []

  def update_asset_urls(self, html):
    # updated_html = re.sub(r'(?<!https://onlinelibrary\.wiley\.com)(/cms/asset/[^"]+)', fr'{self.domain}\1', html)
    updated_html = re.sub(r'(?<!https://onlinelibrary\.wiley\.com)(/(cms/asset|action)/[^"]+)', fr'{self.domain}\1', html)

    return updated_html

  def get_article_page_content(self, driver):
      content = ''
      # section_html = soup.find('section', class_='article-section.article-section__full')
      try:
         abstract_div = driver.get_attribute("div.abstract-group ", "outerHTML")
         content += md(abstract_div)
        #  content += md(abstract_div, heading_style="ATX")
        #  abstract_div_soup = BeautifulSoup(abstract_div, 'lxml')
        #  content += self.convert_html_to_markdownify('', abstract_div_soup, self.domain)
      except Exception as e:
         logger.info(f'Error on abstract', e)

      try:
        # Extract the HTML content of the section tag
        section_html = driver.get_attribute("section.article-section.article-section__full", "outerHTML")
        # Remove the references section from section_html using regex
        section_html = re.sub(
        r'<section[^>]*class="article-section article-section__references"[^>]*>.*?</section>',
        '',
        section_html,
        flags=re.DOTALL
    )
        section_html = self.update_asset_urls(section_html)
        write_to_file('uuu.html', section_html)
        # Convert the HTML to Markdown
        content += md(section_html)
        # content += md(section_html, heading_style="ATX")
        # section_html_soup = BeautifulSoup(section_html, 'lxml')
        # content += self.convert_html_to_markdownify('', section_html_soup, self.domain)
      except Exception as e:
          print('Couldnt get content text', e)   

      return content
  
