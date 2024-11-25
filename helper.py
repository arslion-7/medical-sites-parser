import re

from datetime import datetime
from urllib.parse import urlparse
import requests
from typing import Dict
import time
import random
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from fake_useragent import UserAgent
from seleniumbase import Driver

from markdownify import MarkdownConverter, markdownify as md


class CustomMarkdownConverter(MarkdownConverter):
    def convert_table(self, el, text, convert_as_inline):
        rows = []
        header_row = []
        for i, row in enumerate(el.find_all('tr')):
            columns = [col.get_text(strip=True) for col in row.find_all(['td', 'th'])]
            if i == 0:
                # Treat first row as header
                header_row = columns
                rows.append(' | '.join(header_row))
                rows.append(' | '.join(['---'] * len(columns)))  # Markdown separator
            else:
                rows.append(' | '.join(columns))
        return '\n'.join(rows) + '\n'

def custom_markdownify(html):
    return md(html, convert=['img','table'], converter=CustomMarkdownConverter())


class Pagination:
    def __init__(self, pagination_format: str, page_start: int):
        self.pagination_format = pagination_format
        self.page_start = page_start

def parse_date(date_str):
    try:
        # Attempt to parse the date string in different formats
        try:
            parsed_date = datetime.strptime(date_str, "%B %d, %Y")  # Example format: "June 20, 2024"
        except ValueError:
            try:
                parsed_date = datetime.strptime(date_str, "%m/%d/%Y")  # Example format: "11/03/2023"
            except ValueError:
                parsed_date = datetime.strptime(date_str, "%b %d %Y")  # Example format: "Jun 10 2024"
        
        # Combine parsed date with time string into a datetime object
        return parsed_date
    
    except ValueError:
        return None

def parse_curl_headers(curl_text):
    """
    Parses the cURL headers from a multi-line string and returns them as a Python dictionary.
    
    Args:
    - curl_text (str): The cURL command text containing headers.
    
    Returns:
    - dict: A dictionary of headers.
    """
    headers = {}
    lines = curl_text.splitlines()
    
    for line in lines:
        line = line.strip()
        if line.startswith('-H '):
            header = line[3:].strip(" '")  # Remove "-H" and extra quotes
            key, value = header.split(": ", 1)  # Split the header into key and value
            headers[key] = value
    
    return headers

def get_origin(url):
    """
    Extract the origin (scheme + netloc) from the given URL.

    :param url: The URL from which to extract the origin.
    :return: The origin part of the URL.
    """
    parsed_url = urlparse(url)
    origin = f"{parsed_url.scheme}://{parsed_url.netloc}"
    return origin

def get_domain(url):
    # Parse the URL
    parsed_url = urlparse(url)
    
    # Extract and return the domain (netloc)
    return parsed_url.netloc
    


def selenium_base(headless=True):
    # service = Service('/usr/local/bin/chromedriver')
    driver = Driver(headless=headless, uc=True)
    # driver = Driver(uc=True)
    return driver
    

def get_selenium_driver(headless=True):
    # from selenium import webdriver
    # from selenium.webdriver.chrome.service import Service
    # from selenium.webdriver.common.by import By
    # from selenium.webdriver.chrome.options import Options

    # # Set up Chrome WebDriver options
    # chrome_options = Options()
    # if headless:
    #     chrome_options.add_argument("--headless")  # Runs Chrome in headless mode (no UI)

    # # Path to your Chrome WebDriver
    # service = Service('/usr/local/bin/chromedriver')  # Adjust the path to your WebDriver
    # print('begin selenium')
    # # Initialize the WebDriver
    # driver = webdriver.Chrome(service=service, options=chrome_options)

    driver = selenium_base(headless=headless)

    return driver


# def write_file(file_name: str, text: str):
#     with open(file_name, 'a')


def write_to_file(file_name: str, text: str, mode = 'w'):
    with open(f'draft/write_files/{file_name}', mode) as f:
        f.write(text)
    f.close()


def create_session() -> requests.Session:
    session = requests.Session()
    retry = Retry(total=5, backoff_factor=0.1, status_forcelist=[500, 502, 503, 504])
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session

def get_random_headers() -> Dict[str, str]:
    ua = UserAgent()
    return {
        'User-Agent': ua.random,
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'
    }

def fetch_url(session: requests.Session, url: str) -> str:
    headers = get_random_headers()
    session.headers.update(headers)
    time.sleep(random.uniform(0, 2))
    response = session.get(url)
    response.raise_for_status()
    return response.text

def get_article_page_title(self, soup):
    title_tag = soup.find('h1', class_='citation__title')
    if title_tag:
        return title_tag.text.strip() 
    return ''
  
def get_article_page_content(self, soup):
    content_div = soup.find('section', class_='article-section.article-section__full')
    if content_div:
        return re.sub(r'src="(/[^"]+)"', f'src="{self.domain}\\1"', content_div)
    else:
        return "" 
    
def get_article_references(self, soup):
   # Extract all references as strings
    # references = []
    # Find the section with id="html-references_list"
    references_section = soup.find('section', id='html-references_list')

    # Extract the references within that section
    try:
      references_list = []
      # Find the section with class "item references"
      references_section = soup.find('section', class_='item references')

      # Extract the references within that section
      references = []
      if references_section:
          for p in references_section.find_all('p'):
              reference_text = p.get_text(separator=" ", strip=True)
              references.append(reference_text)

      # Print the references
      for i, ref in enumerate(references, 1):
          references_list.append(f"{i}. {ref}")
    except Exception as e:
    #    logger.info(f'Error on get_article_references', e)
       return []

    return references_list
