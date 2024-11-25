from datetime import datetime
import logging
import random
import re
import time
from typing import Dict, List
from bs4 import BeautifulSoup
import requests

from class_parsers.pubmed_doi.sub_parser import SubParser

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s')


import requests

cookies = {
    'PHPSESSID': '31u5fa79dnkivoa59ba5dhne2d',
    '_rspkrLoadCore': '1',
    '__cf_bm': 'JraymNspfZUrB9LAKGTjZoviuwEgRPyeMEd1UF6aEdw-1724241747-1.0.1.1-H1YAK6UDn6BpUqPC2H5aXusaGk6Ru_p24pTbjOmrg7oX7oYcxtzyTfPodfQdQ2rzAgkCicxAZnlTBgCRYjQvkM6rJ6IoGR39CG5Erb83JBQ',
    'OptanonAlertBoxClosed': '2024-08-21T12:05:07.147Z',
    'OptanonConsent': 'isGpcEnabled=0&datestamp=Wed+Aug+21+2024+17%3A05%3A08+GMT%2B0500+(Turkmenistan+Standard+Time)&version=202404.1.0&browserGpcFlag=0&isIABGlobal=false&hosts=&consentId=2301641d-1ffa-429c-a920-4b16072ac755&interactionCount=1&isAnonUser=1&landingPath=NotLandingPage&groups=C0001%3A1%2CC0002%3A1%2CC0003%3A1%2CC0004%3A1&intType=1&geolocation=US%3BIL&AwaitingReconsent=false',
    'ps_rvm_BuTp': '%7B%22pssid%22%3A%22CZxn7s5DExyhNFes-1724241909320%22%2C%22last-visit%22%3A%221724241907082%22%7D',
}

headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'en-US,en;q=0.9',
    'cache-control': 'max-age=0',
    # 'cookie': 'PHPSESSID=31u5fa79dnkivoa59ba5dhne2d; _rspkrLoadCore=1; __cf_bm=JraymNspfZUrB9LAKGTjZoviuwEgRPyeMEd1UF6aEdw-1724241747-1.0.1.1-H1YAK6UDn6BpUqPC2H5aXusaGk6Ru_p24pTbjOmrg7oX7oYcxtzyTfPodfQdQ2rzAgkCicxAZnlTBgCRYjQvkM6rJ6IoGR39CG5Erb83JBQ; OptanonAlertBoxClosed=2024-08-21T12:05:07.147Z; OptanonConsent=isGpcEnabled=0&datestamp=Wed+Aug+21+2024+17%3A05%3A08+GMT%2B0500+(Turkmenistan+Standard+Time)&version=202404.1.0&browserGpcFlag=0&isIABGlobal=false&hosts=&consentId=2301641d-1ffa-429c-a920-4b16072ac755&interactionCount=1&isAnonUser=1&landingPath=NotLandingPage&groups=C0001%3A1%2CC0002%3A1%2CC0003%3A1%2CC0004%3A1&intType=1&geolocation=US%3BIL&AwaitingReconsent=false; ps_rvm_BuTp=%7B%22pssid%22%3A%22CZxn7s5DExyhNFes-1724241909320%22%2C%22last-visit%22%3A%221724241907082%22%7D',
    'dnt': '1',
    'priority': 'u=0, i',
    'sec-ch-ua': '"Not)A;Brand";v="99", "Google Chrome";v="127", "Chromium";v="127"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"macOS"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'none',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36',
}

class DovepressParser(SubParser):
  def __init__(self, url, main_url, is_selenium=False):
     super().__init__(url, main_url, is_selenium)
     self.domain = 'https://www.dovepress.com/'
  
  # def fetch_url(self, session: requests.Session, url: str) -> str:
  #   session.headers.update(headers)
  #   session.cookies.update(cookies)
  #   time.sleep(random.uniform(0, 2))
  #   response = session.get(url)
  #   response.encoding = 'utf-8'
  #   response.raise_for_status()
  #   return response.text

  # def get_parsed_soup(self, session: requests.Session, url: str):
  #     html_content = self.fetch_url(session, url)
  #     soup = BeautifulSoup(html_content, 'lxml')
  #     return soup

  def get_article_references(self, soup: BeautifulSoup):
   # Extract all references as strings
    references = []
    ref_divs = soup.find_all('p', class_='$reftext')
    
    try:
      for r in ref_divs:
       references.append(r.text.strip())
    except Exception as e:
       logger.info(f'Error on get_article_references', e)
       return []

    return references

  def get_authors(self, soup: BeautifulSoup):
    try:
      intro_intro_rs_skip = soup.find('div', class_='intro rs_skip')
      # Find the paragraph containing the authors
      authors_paragraph = intro_intro_rs_skip.find('p', text=lambda t: t and 'Authors' in t)
      authors = []
      for a in authors_paragraph.find_all('a'):
          author_name = a.get_text(strip=True)
          authors.append(author_name)

      return authors
    except Exception as e:
       logger.info(f'Error on get_authors', e)
       return []

  def get_article_page_content(self, soup: BeautifulSoup):
    try:
      ref_divs = soup.find_all('p', class_='$reftext')
      for r in ref_divs:
         r.extract()
      
      inner_html = soup.find('div', class_='article-inner_html')

      # remaining_content = inner_html.find_all()

      if inner_html:
          # return self.convert_html_to_markdownify(str(inner_html), inner_html, self.domain)    
          return self.convert_html_to_markdown_with_origin_pre(inner_html)
      
      else:
          return "" 
    except Exception as e:
       logger.info(f'Error on get_article_page_content', e)
       return ''
    
  
  