from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta
import logging
from threading import Thread
import traceback
import random
import re
import time
from typing import Dict, List
from urllib.parse import urljoin
from bs4 import BeautifulSoup
import requests

from blog_parser import BlogParser
from class_parsers.pubmed_doi.academic_oup import AcademicOupParser
from class_parsers.pubmed_doi.anndermatol_org import AnndermatolOrgParser
from class_parsers.pubmed_doi.cureus import CureusParser
from class_parsers.pubmed_doi.dovepress import DovepressParser
from class_parsers.pubmed_doi.dpcj import DpcjParser
from class_parsers.pubmed_doi.ejcrim import EjcrimParser
from class_parsers.pubmed_doi.frontiersin_org import FrontiersinOrgParser
from class_parsers.pubmed_doi.ijdvl import IjdvlParser
from class_parsers.pubmed_doi.journals_lww import JournalsLwwParser
from class_parsers.pubmed_doi.mdpi import MdpiParser
from class_parsers.pubmed_doi.science_org import ScienceOrgParser
from class_parsers.pubmed_doi.wjgnet import WjgnetParser
from db.mongodb_local import test_save_article
from helper import get_domain, get_origin, write_to_file

logger = logging.getLogger(__name__)

frontiersin_org_origin = 'https://www.frontiersin.org'
academic_oup_origin = 'https://academic.oup.com'
journals_viamedica_origin = 'https://journals.viamedica.pl'
mdpi_origin = 'https://www.mdpi.com'
cureus_origin = 'https://www.cureus.com'
journals_lww_origin = 'https://journals.lww.com'
dovepress_origin = 'https://www.dovepress.com'
dpcj_origin = 'https://dpcj.org'
ijdvl_origin = 'https://ijdvl.com'
wjgnet_origin = 'https://www.wjgnet.com'
anndermatol_org_origin = 'https://anndermatol.org'
ejcrim_origin = 'https://www.ejcrim.com'
science_org = 'https://www.science.org' # https://www.science.org/doi/10.1126/sciadv.ado5545

# https://www.techscience.com/  https://www.techscience.com/or/v29n5/50095 by adding /html to the end 
# https://rmdopen.bmj.com/content/10/3/e004464


url_dict = {}


class PubmedParser(BlogParser):
  def __init__(self, main_url, pagination, parse_weeks_count = 1, save_action=test_save_article, certain_article_urls=[], category='', subcategory=''):
    super().__init__(main_url, pagination, parse_weeks_count, save_action)
    self.stop_on_articles_not_found_on_page = False
    self.certain_article_urls = certain_article_urls
    self.category = category
    self.subcategory = subcategory

  def find_articles(self, soup: BeautifulSoup):
    # return soup.find_all('div', class_='docsum-content')
    return [div for div in soup.find_all('div', class_='docsum-content') if div.find('span', class_='free-resources')]

  def get_card_title_a_tag(self, card):
    return card.find('a', class_='docsum-title')
  
  def get_card_title_url(self, title_a_tag):
    url = title_a_tag['href']

    return urljoin(self.domain, url)

  def get_article_page_date(self, soup: BeautifulSoup):
   # Find the date string within the specific tag
    try:
        date_str = soup.find('span', class_='cit').get_text(strip=True)
        # Define regex pattern for the "Year Month Day" format
        pattern = re.compile(r'(\d{4})\s([A-Za-z]{3})(?:\s(\d{1,2}))?')

        # Search for the date
        match = pattern.search(date_str)

        if match:
            year, month_str, day = match.groups()
            if not day:
                day = '1'  # Default to first day of the month if day is missing
            date_format = f"{year} {month_str} {day}"
            parsed_date = datetime.strptime(date_format, "%Y %b %d")
            return parsed_date
        else:
          return 'No date'
    except Exception as e:
       logger.info(f'Cant get pub date')
       return 'No date'

  def get_article_page_title(self, soup):
    title_tag = soup.find('title')
    if title_tag:
        print('title of article is', title_tag.text.strip())
        return title_tag.text.strip() 
    return ''

  def sub_get_random_headers(self) -> Dict[str, str]:
    headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Cache-Control': 'max-age=0',
    'Content-Type': 'application/x-www-form-urlencoded',
    'Cookie': '__cf_bm=BYJ5hnCOuSWbnZm83LUi0PS98xdMNG3tdsDKE.tQP7U-1723614894-1.0.1.1-loX3tqTyRGUopKRN3keq_sQxh7czSqfaiiI0B5CVLSoSFv.cDdfbxtu1k0bWW8gruS2jIDx_jCjvuMY7tIGDTA; MAID=Bg+3Wc6aqD153YwPF/7J3w==; ...',
    'DNT': '1',
    'Origin': 'https://www.thelancet.com',
    'Priority': 'u=0, i',
    'Referer': 'https://www.thelancet.com/journals/lanwpc/article/PIIS2666-6065(24)00138-X/fulltext?__cf_chl_tk=_BTgYn8P82FznmgeJG0zA7uqSGymQfupuqGdkTrF5Jk-1723614895-0.0.1.1-4393',
    'Sec-CH-UA': '"Not)A;Brand";v="99", "Google Chrome";v="127", "Chromium";v="127"',
    'Sec-CH-UA-Arch': '"arm"',
    'Sec-CH-UA-Bitness': '"64"',
    'Sec-CH-UA-Full-Version': '"127.0.6533.90"',
    'Sec-CH-UA-Full-Version-List': '"Not)A;Brand";v="99.0.0.0", "Google Chrome";v="127.0.6533.90", "Chromium";v="127.0.6533.90"',
    'Sec-CH-UA-Mobile': '?0',
    'Sec-CH-UA-Model': '""',
    'Sec-CH-UA-Platform': '"macOS"',
    'Sec-CH-UA-Platform-Version': '"14.5.0"',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'same-origin',
    'Sec-Fetch-User': '?1',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36',
    }

    return headers

  def get_sub_origin(self, session: requests.Session, url: str) -> str:
    headers = self.sub_get_random_headers()
    session.headers.update(headers)
    time.sleep(random.uniform(0, 2))
    response = session.get(url)
    origin = None
    final_destination = None
    if response.history:
        print(f"URL was redirected. Full redirection path:")
        final_destination = response.url
        print(f"Final destination: {final_destination}")

        for resp in response.history:
            print(f"{resp.status_code} -> {resp.url}")

        origin = get_origin(final_destination)
        print('origin', origin)
    else:
        print("URL was not redirected.")
    # response.raise_for_status()
    return origin, final_destination

  def parse_sub_soup(self, session: requests.Session, url: str, parent_url):
    try: 
       origin, final_destination = self.get_sub_origin(session, url)
    except Exception as e:
       logger.error("Error on get_sub_origin", e)
       return None
    print('sub origin', origin)
    if origin in url_dict:
        url_dict[origin] += 1  # If URL exists, increment count
    else:
        url_dict[origin] = 1   # If URL does not exist, add it with count 1
    if origin == frontiersin_org_origin:
        # pass
        try: 
          return FrontiersinOrgParser(url=final_destination, main_url=origin).main()
        except Exception as e:
         print('Exception on frontiersin_org_origin', e)
         return None    
    elif origin == academic_oup_origin:
      try:
      #  AcademicOupParser(url=final_destination, main_url=origin, is_selenium=True).main()
       return AcademicOupParser(url=final_destination, main_url=origin, is_selenium=True).main()
      except Exception as e:
         print('Exception on academic_oup_origin', e)
         return None
    elif origin == mdpi_origin:
       try:
          logger.info('mdpi_parser')
          return MdpiParser(url=final_destination, main_url=origin, is_selenium=True).main()
       except Exception as e:
         print('Exception on mdpi_parser', e)
         return None
    elif origin == cureus_origin:
      try:
        cureus = CureusParser(url=final_destination, main_url=origin, is_selenium=True).main()
        return cureus
      except Exception as e:
        print('Exception on cureus_parser', e)
        return None
    elif origin == journals_lww_origin:
       try:
          journals_lww = JournalsLwwParser(url=final_destination, main_url=origin, is_selenium=True).main()
          return journals_lww
       except Exception as e:
          print('Exception on journals_lww', e)
          return None
    elif origin == dovepress_origin:
       try:
          dovepress = DovepressParser(url=final_destination, main_url=origin, is_selenium=True).main()
          return dovepress
       except Exception as e:
          print('Exception on dovepress', e)
          return None
    elif origin == dpcj_origin:
       try:
          dpcj = DpcjParser(url=final_destination, main_url=origin, is_selenium=True).main()
          return dpcj
       except Exception as e:
          print('Exception on dpcj', e)
          return None
    elif origin == ijdvl_origin:
       try:
          ijdvl = IjdvlParser(url=final_destination, main_url=origin, is_selenium=True).main()
          return ijdvl
       except Exception as e:
          print('Exception on ijdvl', e)
          return None
    elif origin == wjgnet_origin:
       try:
          wjgnet = WjgnetParser(url=final_destination, main_url=origin, is_selenium=True).main()
          return wjgnet
       except Exception as e:
          print('Exception on wjgnet', e)
          return None
    elif origin == anndermatol_org_origin:
       try:
          anndermatol = AnndermatolOrgParser(url=final_destination, main_url=origin, is_selenium=True).main()
          return anndermatol
       except Exception as e:
          print('Exception on anndermatol', e)
          return None
    elif origin == ejcrim_origin:
       try:
          ejcrim = EjcrimParser(url=final_destination, main_url=origin, is_selenium=True).main()
          print('ejcrim', ejcrim)
          return ejcrim
       except Exception as e:
          print('Exception on ejcrim', e)
          return None
    elif origin == science_org:
       print('in science_org')
       try:
          science = ScienceOrgParser(url=final_destination, main_url=origin, is_selenium=True).main()
          print('science content', science['content'])
          return science
       except Exception as e:
          return None
    
    else:
       with open('draft/sub_origins.txt', 'a+') as f:
          f.write(f'{final_destination}\n')
       f.close()
    
    return None

  def get_DOI(self, soup: BeautifulSoup, parent_url):
      # write_to_file('doi.html', str(soup))
      try:
        doi_url = soup.find('span', class_='identifier doi')
        a_tag = doi_url.find('a', class_='id-link')
        doi_url = a_tag['href']
        return self.parse_sub_soup(self.session, doi_url, parent_url)
      except Exception as e:
        logger.info('Article dont has doi', e)
        return None
     
  
  def parse_article_page(self, session: requests.Session, url: str) -> Dict[str, str]:
    logger.info(f">>> Started parsing article page {url}")
    soup = self.get_parsed_soup(session, url)
    doi = self.get_DOI(soup, parent_url=url)

    # print('doi', doi)
    
    article = {}

    if doi: 
      article['references'] = doi['references'] if doi['references'] else []
      article['pdf_text'] = doi['content'] if doi['content'] else None
      article['authors'] = doi['authors'] if doi['authors'] else []
      article['doi_url'] = doi['doi_url'] if doi['doi_url'] else None
      
    else:
      article['references'] = self.get_article_references(soup)

    article['title'] = self.get_article_page_title(soup)
    article['content'] = self.get_article_page_content(soup)
    article['date'] = self.get_article_page_date(soup)
    
    return article
  
  def get_article_page_content(self, soup):
    from markdownify import markdownify

    # Initialize an empty string for markdown content
    markdown_content = ""

    # Extract the 'abstract' div if it exists
    abstract_div = soup.find('div', id='abstract')
    if abstract_div:
        markdown_content += markdownify(str(abstract_div), heading_style="ATX") + "\n\n"

    # Extract the 'conflict-of-interest' div if it exists
    # conflict_of_interest_div = soup.find('div', id='conflict-of-interest')
    # if conflict_of_interest_div:
    #     markdown_content += markdownify(str(conflict_of_interest_div), heading_style="ATX") + "\n\n"
        
    # 'markdown_content' now contains the markdown version of the selected HTML parts
    if markdown_content:
        return BlogParser.clean_extra_newlines(markdown_content)
    else:
        return "NO content" 

  def get_article_references(self, soup):
    references_list = []

    # Check if the references section exists
    refs_div = soup.find('div', class_='refs-list')
    if refs_div:
        # Find all the reference items
        references = refs_div.find_all('li', class_='skip-numbering')
        for ref in references:
            # Get the text of each reference and strip any extra whitespace
            reference_text = ref.get_text(strip=True)
            references_list.append(reference_text)
    
    return references_list

  def stop_parsing(self, date):
    # current_date = datetime.now(date.tzinfo)  # Ensures both dates have the same timezone
    # one_week_ago = current_date - timedelta(weeks=self.parse_weeks_count)
    # if date < one_week_ago:
    #     print('url_dict', sorted(url_dict.items(), key=lambda item: item[1], reverse=True))
    #     return True
    return False     

  def main(self):
    logger.info(f">>> Started parsing {self.main_url}")

    page = self.page_start

    logger.error(f"{self.main_url}: {page}")

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
              
              # threads = []

              for item in news_items:
                self.process_article(self.main_url, self.session, item)
                # thread = Thread(target=self.process_article, args=(self.main_url, self.session, item,))
                # threads.append(thread)
                # thread.start()

              # for thread in threads:
              #   thread.join()

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