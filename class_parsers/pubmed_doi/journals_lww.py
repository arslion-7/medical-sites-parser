from datetime import datetime
import logging
import re
from typing import Dict
from bs4 import BeautifulSoup
import markdownify

from class_parsers.pubmed_doi.sub_parser import SubParser
from helper import write_to_file

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s')


class JournalsLwwParser(SubParser):
  def __init__(self, url, main_url, is_selenium=False):
     super().__init__(url, main_url, is_selenium)
  
  def get_article_references(self, soup: BeautifulSoup):
   # Extract all references as strings
    references = []
    ref_divs = soup.find_all('div', class_='article-references__item')
    
    try:
      for r in ref_divs:
       references.append(r.text.strip())
    except Exception as e:
       logger.info(f'Error on get_article_references', e)
       return []

    return references

  def get_authors(self, soup: BeautifulSoup):
    try:
     # Find the paragraph containing the authors
      authors_paragraph = soup.find('p', id='P7')

      # Extract the text from each author and their corresponding superscript
      authors_with_affiliations = []
      for author in authors_paragraph.find_all(text=True, recursive=False):
          sup_tag = author.next_sibling
          if sup_tag and sup_tag.name == 'sup':
              affiliation_ref = sup_tag.get_text(strip=True)
              authors_with_affiliations.append(f"{author.strip()} ({affiliation_ref})")
          else:
              authors_with_affiliations.append(author.strip())

      return authors_with_affiliations
    except Exception as e:
       logger.info(f'Error on get_authors', e)
       return []
    
  def clean_image_urls(self, text):
    # Fix improperly escaped characters in URLs
    text = re.sub(r'\\-', '-', text)
    return text

  def clean_image_urls(self, text):
    # Fix improperly escaped characters in URLs
    text = re.sub(r'\\-', '-', text)
    return text

  def remove_invalid_links(self, text):
    # Remove JavaScript links
    text = re.sub(r'\[.*?\]\(javascript:void\(0\)\)', '', text)
    return text

  import re

  def clean_escaped_characters(self, text):
      # Remove unwanted escaping
      text = re.sub(r'\\([>\-\[\]])', r'\1', text)
      return text

    
  def clean_markdown_output(self, text):
    text = self.clean_escaped_characters(text)
    text = self.remove_invalid_links(text)
    text = self.clean_image_urls(text)
    return text

  def get_article_page_content(self, soup: BeautifulSoup):
    try:
        result = ''

        # Extract abstract
        abstract = soup.find('section', {'id': 'abstractWrap'})
        if abstract:
            result += self.convert_html_to_markdownify(str(abstract))

        # Extract the main article body
        full_text = soup.find('section', {'id': 'ArticleBody'})
        if full_text:
            for img_section in full_text.find_all("section", {"class": "ejp-r-article-images"}):
                # Find the image
                img = img_section.find("img", {"srcset": True}) or img_section.find("img", {"src": True})
                if img:
                    # Extract the best resolution image URL
                    img_url = None
                    if img.get('srcset'):
                        img_url = img['srcset'].split(',')[-1].strip().split(' ')[0]
                    else:
                        img_url = img.get('src')

                    # Ensure the URL is valid
                    if img_url and not img_url.startswith("javascript"):
                        img_url = img_url.replace('\\', '')  # Clean backslashes

                    # Get alt text
                    alt_text = img.get('alt', 'Image')

                    # Extract caption text
                    figcaption = img_section.find("figcaption", {"class": "ejp-r-article-images__figcaption"})
                    figcaption_text = ""
                    if figcaption:
                        # Check for caption link and caption div
                        figcaption_link = figcaption.find("a", {"class": "ejp-r-article-images__figcaption-link"})
                        caption_div = figcaption.find("div", {"class": "ejp-r-article-images__figcaption-text"})

                        # Safely get the text content of each
                        if figcaption_link:
                            figcaption_text += figcaption_link.get_text(strip=True) + " "
                        if caption_div:
                            figcaption_text += caption_div.get_text(strip=True)

                    # Generate Markdown for the image
                    if img_url:
                        if figcaption_text:
                            img_markdown = f"![{alt_text}]({img_url})\n*{figcaption_text}*\n\n"
                        else:
                            img_markdown = f"![{alt_text}]({img_url})\n\n"

                        # Replace the entire section with the generated Markdown
                        img_section.replace_with(img_markdown)

            # Convert the processed HTML back to Markdown
            result += '\n' + self.convert_html_to_markdownify(str(full_text))

        # Clean up the final Markdown
        result = self.clean_markdown_output(result)

        return result

    except Exception as e:
        logger.exception("Error in get_article_page_content")
        return ''
  