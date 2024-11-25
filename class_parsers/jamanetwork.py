from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta
import logging
import random
import time
from typing import Dict, List
from urllib.parse import urljoin
from bs4 import BeautifulSoup
import requests

from blog_parser import BlogParser
from db.mongodb_local import test_save_article
from fake_useragent import UserAgent

logger = logging.getLogger(__name__)


class JamanetworkParser(BlogParser):
  def __init__(self, main_url, pagination, parse_weeks_count = 1, save_action=test_save_article):
    super().__init__(main_url, pagination, parse_weeks_count, save_action)

  def find_articles(self, soup: BeautifulSoup):
    articles = soup.find_all('li', class_='article') 
    print('find_articles len', len(articles))
    return articles

  def get_card_title_a_tag(self, card):
    return card.find('a', class_='article--title')
  
  def get_card_title_url(self, title_a_tag):
    url = title_a_tag['href']
    return url

  def get_article_page_date(self, soup: BeautifulSoup):
    # Find the div with class "meta-date"
    print('soupppp', soup)
    try:
      meta_date_div = soup.find('div', {'class': 'meta-date'})
      # Extract the date text
      date_str = meta_date_div.get_text(strip=True)
      # Convert to datetime object
      date_format = "%B %d, %Y"  # Format matching "March 30, 2022"
      return datetime.strptime(date_str, date_format)
    except Exception as e:
       logger.info(f"Error processing pub date")
       return None

  def get_article_page_title(self, soup):
    title_tag = soup.find('h1', class_='meta-article-title')
    if title_tag:
        return title_tag.text.strip() 
    return ''
  
  def get_article_page_content(self, soup):
    content_div = soup.find('div', class_='article-full-text')
    if content_div:
        return self.convert_html_to_markdown(str(content_div))
    else:
        return "NO content" 

      
  def get_main_page_header(self):
    headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Accept-Language': 'en-US,en;q=0.9',
    'Cache-Control': 'max-age=0',
    'Connection': 'keep-alive',
    'Cookie': 'JAMA_NetworkMachineID=638577038911184618; AMA_SessionId=0hca1poyybt1mj1ihzbaobax; persistentSearchFilters=; gaCustomerId=Unknown; gaInstitutionId=Unknown; gaTAMId=Unknown; __gads=ID=990789dfb0405eb4:T=1722107100:RT=1722107100:S=ALNI_MZ7dEgu3hAqoKYCOwIiCWTh-tZf4w; __gpi=UID=00000e80b59619b8:T=1722107100:RT=1722107100:S=ALNI_MbYwCNswT9BhM7V-jd_tufQuiZgmg; __eoi=ID=112be1648ae1084f:T=1722107100:RT=1722107100:S=AA-AfjaNtXGFZQvNY6BPfPuLvhDp; _xdClientId=625091390.1722107098; gaPrevTAMId=Unknown; _ngyqd_ga=GA1.2.625091390.1722107098; BCSessionID=5a27c5ff-4100-49db-958f-c67eb9ea9469; QuantumMetricUserID=88e6fe08bf774fa28fd67313abdd99ea; OptanonAlertBoxClosed=2024-07-27T19:05:06.817Z; OptanonConsent=isGpcEnabled=0&datestamp=Sun+Jul+28+2024+00%3A05%3A06+GMT%2B0500+(Turkmenistan+Standard+Time)&version=202307.1.0&browserGpcFlag=0&isIABGlobal=false&hosts=&consentId=f78676e3-aa65-4393-913d-51afd3168c77&interactionCount=1&landingPath=NotLandingPage&groups=C0004%3A1%2CCOSPDTA_BG%3A1%2CC0003%3A1%2CC0002%3A1%2CC0001%3A1; _gaCorpUserId=1722107106945.128513; _gaCorp=GA1.2.1063611774.1722107107; _ga=GA1.2.625091390.1722107098; _ga_7YZKB5MSZN=GS1.1.1722107103.1.1.1722107168.0.0.0; _ga_CXRFQ9PGSH=GS1.1.1722107103.1.1.1722107168.0.0.0; _ga_B4FWHWKMEB=GS1.1.1722107103.1.1.1722107168.60.0.0; _ngyqd_ga_NGYQD9R7ZM=GS1.2.1722107103.1.1.1722107168.60.0.0; AMA_Store_SessionId=kkcr5wxlpxptjyucrava2sq4; JAMA_Network=UserName=FC14A0FF-55DA-4F38-98EA-5F5C731C4A46&UserPwd=B84C8B5120A669A7566E1F6ABBA4EC9FFC75BCDB; ForceAutoLogin=AutoLogin=JAMA_Network; Cart=958bfc67-9e27-437f-9562-e102062b9494; CookieBanner_Closed=true; KEY=1388161*2271767:1467654327:1039236888:1',
    'DNT': '1',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'none',
    'Sec-Fetch-User': '?1',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
    'sec-ch-ua': '"Not/A)Brand";v="8", "Chromium";v="126", "Google Chrome";v="126"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"macOS"',
    }

    return headers

  def fetch_url(self, session: requests.Session, url: str) -> str:
    headers = self.get_main_page_header()

    logger.info(f"parsing url: {url}")
    logger.info(f"parsing headers: {headers}")

    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.text

  def main(self):
    logger.info(f">>> Started parsing {self.main_url}")

    page = self.page_start

    try:
        while True:
            logger.info(f"parsing page: {self.page_start}")
            html_content = self.fetch_url(self.session, self.get_paginated_url(page))
            news_items = self.parse_page(html_content)
            
            if not news_items:
                logger.info(f"No more news items found on page {page}. Stopping.")
                break
            for item in news_items:
               self.process_article(self.main_url, self.session, item)
               time.sleep(random.uniform(7, 15))

            if self.pagination is None:
               break
            page += 1
            
    except requests.exceptions.RequestException as e:
        logger.info(f"An error occurred while fetching the page: {e}")
    except Exception as e:
        logger.info(f"An unexpected error occurred: {e}")