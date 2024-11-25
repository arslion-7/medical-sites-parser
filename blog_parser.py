

from abc import abstractmethod
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta
import logging
import random
import re
from threading import Thread
import time
import traceback
from typing import Dict, List
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import html2text
from markdownify import markdownify as md

from db.mongodb_local import test_save_article
from helper import Pagination, create_session
from fake_useragent import UserAgent

logger = logging.getLogger(__name__)

class BlogParser():
  # extract datetime from article detail page
  def __init__(self, main_url, pagination: Pagination, parse_weeks_count = 1, save_action=test_save_article, 
               certain_article_urls=[], category='', subcategory=''):
    self.main_url = main_url
    self.session = create_session()
    self.domain = self.get_origin(main_url) # TODO:
    self.pagination = pagination
    self.parse_weeks_count = parse_weeks_count
    self.save_action = save_action
    self.stop_on_articles_not_found_on_page = True
    self.certain_article_urls = certain_article_urls
    self.category = category
    self.subcategory = subcategory

  @property
  def page_start(self):
    page_start = 1
    if self.pagination is not None:
       if self.pagination.page_start is not None:
          page_start = self.pagination.page_start
          
    return page_start
  
  @abstractmethod
  def find_articles(self, soup):
    return soup

  @abstractmethod
  def get_card_title_url(self, title_a_tag):
     pass
  
  @abstractmethod
  def get_article_page_title(self, soup):
     pass
  
  @abstractmethod
  def get_article_page_date(self, soup):
     pass
  
  @abstractmethod
  def get_article_references(self, soup):
     pass

  @abstractmethod
  def get_card_title_a_tag(self, card):
     pass
  
  @abstractmethod
  def get_article_page_content(self, soup):
     pass
  
  @staticmethod
  def clean_extra_newlines(input_str):
    # Split the string by newlines and filter out any empty lines
    lines = [line for line in input_str.splitlines() if line.strip() != '']
    # Join the non-empty lines with a single newline character
    cleaned_str = "\n".join(lines)
    return cleaned_str
  
  @staticmethod
  def remove_extra_newlines(self, markdown_content):
    # Remove multiple newlines
    cleaned_markdown = re.sub(r'\n+', '\n', markdown_content)
    return cleaned_markdown
  
  @staticmethod
  def html_to_clean_markdown(html_content):
    # Convert HTML to Markdown
    markdown_content = md(html_content)
    
    # Remove extra newlines from the Markdown content
    cleaned_markdown = BlogParser.remove_extra_newlines(markdown_content)
    
    return cleaned_markdown
  
  def clean_html(self, html_content):
    # Remove extra newlines
    cleaned_html = re.sub(r'\n+', '\n', html_content)
    return cleaned_html
  
  def parse_page(self, html_content: str) -> List[Dict[str, str]]:
    soup = BeautifulSoup(html_content, 'html.parser')
    articles = self.find_articles(soup)

    return [self.parse_news_card(article) for article in articles]

  def get_paginated_url(self, page):
    if self.pagination is None:
       return self.main_url
    
    prefix = self.pagination.pagination_format.split('{')[0]
    suffix = self.pagination.pagination_format.split('}')[1]

    paginated_url = f"{self.main_url}{prefix}{page}{suffix}"
    logger.info(f">>> Started parsing paginated_url {paginated_url}")
    return paginated_url
  
  def parse_certain_articles(self):
      threads = []

      chunk_size = 7
      for i in range(0, len(self.certain_article_urls), chunk_size):
        chunk = self.certain_article_urls[i:i + chunk_size]
        for url in chunk:
          thread = Thread(target=self.process_article, args=(self.main_url, self.session, dict(url=url)))
          threads.append(thread)
          thread.start()      

        for thread in threads:
          thread.join()
    #  for url in self.certain_article_urls:
    #     logger.info(f"parsing url in certain articles: {url}")
    #     # html_content = self.fetch_url(self.session, url)
    #     result = self.process_article(self.main_url, self.session, dict(url=url)) 
    #     if result == "Parsed":
    #           time.sleep(5)
    #           logger.info(f"Parsed all articles for last {self.parse_weeks_count} week(s)")
    #           return
    #     else:    
    #         logger.info(f"Added {result}")

  def main(self):
    logger.info(f">>> Started parsing {self.main_url}")

    page = self.page_start

    logger.info(f"{self.main_url}: {page}")
    logger.info(f'certain_article_urls {self.certain_article_urls}')

    try:
      if len(self.certain_article_urls) > 0:
        # parsing certain articles only 
        self.parse_certain_articles()
      else:
        while True:
            logger.info(f"parsing page: {self.page_start}")
            html_content = self.fetch_url(self.session, self.get_paginated_url(page))
            news_items = self.parse_page(html_content)
            
            if self.stop_on_articles_not_found_on_page:
              if not news_items:
                  logger.info(f"No more news items found on page {page}. Stopping.")
                  break
            
            with ThreadPoolExecutor(max_workers=10) as executor:  # Reduced max_workers to avoid overwhelming the server
              future_to_item = {executor.submit(self.process_article, self.main_url, self.session, item): item for item in news_items}
              for future in as_completed(future_to_item):
                  result = future.result()
                  if result == "Parsed":
                      time.sleep(5)
                      logger.info(f"Parsed all articles for last {self.parse_weeks_count} week(s)")
                      return
                  else:    
                      logger.info(f"Added {result}")

            if self.pagination is None:
               break
            page += 1
            
    except requests.exceptions.RequestException as e:
        logger.info(f"An error occurred while fetching the page: {e}")
         # Log the detailed traceback
        logger.info(traceback.format_exc())
    except Exception as e:
        logger.info(f"An unexpected error occurred: {e}")
        # Log the detailed traceback
        logger.info(traceback.format_exc())

  @staticmethod
  def get_origin(url):
    parsed_url = urlparse(url)
    protocol = parsed_url.scheme
    domain = parsed_url.netloc
    # Ensure the domain includes 'www.'
    if not domain.startswith('www.'):
        domain = 'www.' + domain
    return f"{protocol}://{domain}"
  
  def fetch_url(self, session: requests.Session, url: str) -> str:
    headers = self.get_random_headers()
    session.headers.update(headers)
    time.sleep(random.uniform(0, 2))
    response = session.get(url)
    response.raise_for_status()
    return response.text

  @staticmethod
  def get_random_headers() -> Dict[str, str]:
    ua = UserAgent()
    return {
        'User-Agent': ua.random,
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'
    }

  @staticmethod
  def create_session() -> requests.Session:
    session = requests.Session()
    retry = Retry(total=5, backoff_factor=0.1, status_forcelist=[500, 502, 503, 504])
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session
  
  @staticmethod
  def preprocess_html(html_content):
    # Convert BeautifulSoup object to string if needed
    if isinstance(html_content, BeautifulSoup):
        html_content = str(html_content)
    
    # Ensure that <h2> tags always start on a new line
    # Add a newline before every <h2> if it is not already preceded by a newline
    html_content = re.sub(r'(?<!\n)\s*<h2[^>]*>', r'\n<h2>', html_content)

    return html_content

  @staticmethod
  def convert_html_to_markdown(html: str, html_raw = '', domain = ''):
    if html_raw != '' and domain != '':
        # Find all images within this div
        images = html_raw.find_all('img')
        # Iterate over each image and modify the src attribute
        for img in images:
            # If the src is relative, prepend the domain
            if img['src'].startswith('/'):
                img['src'] = urljoin(domain, img['src']) 
        html = str(html_raw)

    h = html2text.HTML2Text()
    h.ignore_links = False  # Keep links in the markdown
    return h.handle(html)
  
  @staticmethod
  def convert_html_to_markdownify(html: str, soup='', domain=''):
    if soup != '' and domain != '':
        images = soup.find_all('img')
        for img in images:
            if img['src'].startswith('/'):
                img['src'] = urljoin(domain, img['src'])
            elif img['src'].startswith('article/fulltext_file/'):
               img['src'] = urljoin(domain, img['src'])
        html = str(soup)

    # Use markdownify to convert HTML to markdown
    return md(html)  # You can customize this behavior
  
  @staticmethod
  def convert_html_to_markdown_markdownify(html: str, html_raw='', domain=''):
    # if html_raw != '' and domain != '':
    #     soup = BeautifulSoup(html_raw, 'html.parser')
        
    #     # Process image sources (img src)
    #     for img in soup.find_all('img'):
    #         img_src = img.get('src')
    #         if img_src and not img_src.startswith('http'):
    #             # Add the domain to relative image paths
    #             img['src'] = urljoin(domain, img_src)
        
       # Process anchor hrefs (a href)
        # for a in soup.find_all('a'):
        #     href = a.get('href')
        #     if href and not href.startswith('http') and not href.startswith('#'):
        #         # Add the domain to relative href paths, but skip anchors (e.g., #section)
        #         a['href'] = urljoin(domain, href)
                
        # html = str(soup)
    
    markdown = md(html, heading_style="ATX")  # Customize options if necessary
    return markdown

  def stop_parsing(self, date):
    current_date = datetime.now(date.tzinfo)  # Ensures both dates have the same timezone
    one_week_ago = current_date - timedelta(weeks=self.parse_weeks_count)
    if date < one_week_ago:
        return True
    return False
  
  def get_parsed_soup(self, session: requests.Session, url: str):
    html_content = self.fetch_url(session, url)
    return BeautifulSoup(html_content, 'html.parser')
  
  def parse_article_page(self, session: requests.Session, url: str) -> Dict[str, str]:
    logger.info(f">>> Started parsing article page {url}")
    soup = self.get_parsed_soup(session, url)
    
    article = {}
    article['title'] = self.get_article_page_title(soup)
    article['date'] = self.get_article_page_date(soup)
    article['references'] = self.get_article_references(soup)
    article['content'] = self.get_article_page_content(soup)
    
    return article

  def parse_news_card(self, card: BeautifulSoup) -> Dict[str, str]:
    article_card = {}

    # Extract title
    title_a_tag = self.get_card_title_a_tag(card)
    # title_text = self.get_card_title_text(title_a_tag)
    title_url = self.get_card_title_url(title_a_tag)
    
   # Extract publish date
    # publish_date = self.get_publish_date_str(card)

    if title_a_tag:
        article_card['url'] = title_url
        # article_card['title'] = title_text
        # article_card['date'] = publish_date

    return article_card
  
  def check_for_images(self, content, pdf_text=None):
    """
    Checks if the provided content or PDF text contains URLs with common image formats,
    including Markdown-style nested image references.
    Returns True if any image URLs are found, otherwise False.
    """
    try:
        # Regular expression to match URLs ending with common image formats
        image_url_pattern = r'https?:\/\/\S+\.(?:png|jpg|jpeg|gif|bmp|webp|svg)(\?\S*)?'

        # Regular expression to match Markdown-style nested images
        markdown_image_pattern = r'!\[.*?\]\((https?:\/\/\S+\.(?:png|jpg|jpeg|gif|bmp|webp|svg)(\?\S*)?)\)'

        # Check for direct image URLs in content
        if content and (re.search(image_url_pattern, content, re.IGNORECASE) or
                        re.search(markdown_image_pattern, content, re.IGNORECASE)):
            return True

        # Check for direct image URLs in pdf_text
        if pdf_text and (re.search(image_url_pattern, pdf_text, re.IGNORECASE) or
                         re.search(markdown_image_pattern, pdf_text, re.IGNORECASE)):
            return True

        return False
    except Exception as e:
        # Log the exception if needed (optional)
        print(f"Error in check_for_images: {e}")
        return False


  def save_article_in_db(self, mainUrl, articleUrl, title, date, content, authors, pdf_text, references, doi_url):
      has_images = self.check_for_images(content, pdf_text)

      print('has_images', has_images)

      self.save_action(mainUrl=mainUrl,
                        articleUrl=articleUrl,
                        title=title,
                        date=date,
                        content=content,
                        authors=authors,
                        pdf_text=pdf_text,
                        references=references,
                        doi_url=doi_url,
                        has_images=has_images,
                        category=self.category,
                        subcategory=self.subcategory,
                        )

  def process_article(self, mainUrl, session: requests.Session, card: Dict[str, str]):
    try:
        # get by card
        articleUrl = card['url']
        # date = card['date']

        article = self.parse_article_page(session, articleUrl)
        # get by article
        title = article['title']
        logger.info(f"Title in process_article: {title}")
        content = article['content']
        date = article['date']
        pdf_text = article['pdf_text'] if 'pdf_text' in article else ''
        references = article['references'] if 'references' in article else []
        authors = article['authors'] if 'authors' in article else []
        doi_url = article['doi_url'] if 'doi_url' in article else ''
        
        if self.stop_parsing(date):
            print('stop parsing')
            return "Parsed"
        
        logger.info(f">>> Started saving to db {articleUrl}")
        self.save_article_in_db(mainUrl=mainUrl, 
                                articleUrl=articleUrl, 
                                title=title, date=date, 
                                content=content, 
                                authors=authors, 
                                pdf_text=pdf_text, 
                                references=references, 
                                doi_url=doi_url,)
        
        return article['title']
    
    except Exception as e:
        logger.error(f"Error processing article {card.get('url', 'Unknown URL')}: {e}")
        logger.info(traceback.format_exc())
        return None