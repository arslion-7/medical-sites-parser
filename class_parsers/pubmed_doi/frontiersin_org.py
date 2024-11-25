from datetime import datetime
import logging
import re
from typing import Dict
from bs4 import BeautifulSoup
import requests

from class_parsers.pubmed_doi.sub_parser import SubParser

logger = logging.getLogger(__name__)


class FrontiersinOrgParser(SubParser):
  def __init__(self, url, main_url, is_selenium=False):
     super().__init__(url, main_url, is_selenium)

  def get_article_page_date(self, soup: BeautifulSoup):
        # Find all <span> elements and pick the second one for date
        # div class="ArticleLayoutHeader__info__journalDate">
        date_div = soup.find('div', class_='ArticleLayoutHeader__info__journalDate')
        spans = date_div.find_all('span')
        if len(spans) > 1:
            date_text = spans[1].text.strip()

            # Use regex to extract the day, month, and year
            full_date_match = re.search(r'(\d{1,2})\s+([A-Za-z]+)\s+(\d{4})', date_text)
            if full_date_match:
                day, month_abbr, year = full_date_match.groups()
                try:
                    # Convert month abbreviation to full date format (yyyy-mm-dd)
                    date_obj = datetime.strptime(f'{day} {month_abbr} {year}', '%d %B %Y')
                    return date_obj.strftime('%Y-%m-%d')
                except ValueError:
                    return 'No date'
        
        return 'No date'

  def get_article_page_title(self, soup):
    title_tag = soup.find('title')
    if title_tag:
        return title_tag.text.strip() 
    return ''
  
  def get_article_page_content(self, soup: BeautifulSoup):
    content_div = soup.find('div', class_='JournalFullText')
    references_to_remove = content_div.find_all('div', class_='References')
    authors_to_remove = content_div.find_all('span', class_='author-wrapper')

    for div in references_to_remove:
        div.extract()

    for span in authors_to_remove:
        span.extract()
    # Find all <p> tags
    p_tags = content_div.find_all('p')

    # Iterate over each <p> tag and check if it contains the specific <span> text
    for p in p_tags:
        span = p.find('span', text='*Correspondence:')
        if span:
            p.decompose()  # Remove the <p> tag containing the span
    
    references_word = content_div.find('h2', text='References')
    references_word.decompose()

    # Get the remaining content
    remaining_content = content_div
    if remaining_content:
        return self.convert_html_to_markdown(str(remaining_content))
    else:
        return "" 
    
  def get_authors(self, soup: BeautifulSoup):
    # authors_div = soup.find('div', class_='authors')
    author_spans = soup.find_all('span', class_='author-wrapper')
    # Extract the author names
    author_names = []
    for author_span in author_spans:
        if author_span.a:  # If the author is within an <a> tag
            author_names.append(author_span.a.text.strip())
        else:  # Otherwise, the author is just text within the span
            author_names.append(author_span.text.strip().split('<sup>')[0].strip())

    return author_names
  
  def get_article_references(self, soup):
    references = soup.find_all('p', class_='ReferencesCopy1')
    reference_list = [ref.text.strip() for ref in references]
    print('reference_list', reference_list)
    return reference_list