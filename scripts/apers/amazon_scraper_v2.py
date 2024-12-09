import requests
from bs4 import BeautifulSoup
import random
import time
from fake_useragent import UserAgent
from .abstract_scraper import Scraper
import logging
import os

# Ensure necessary directories exist
logs_dir = '/mnt/SSD500GB/Work/project_claude_scraping/logs'
data_dir = '/mnt/SSD500GB/Work/project_claude_scraping/data'
os.makedirs(logs_dir, exist_ok=True)
os.makedirs(data_dir, exist_ok=True)

# Configure logging
logging.basicConfig(
    filename=os.path.join(logs_dir, 'amazon_scraper.log'),
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class AmazonScraper(Scraper):
    BASE_URL = "https://www.amazon.ca/s?k="

    def fetch_results(self, search_term: str) -> list:
        query = search_term.replace(" ", "+")
        url = self.BASE_URL + query
        
        ua = UserAgent()
        max_retries = 5
        retry_delay = 2

        for attempt in range(max_retries):
            try:
                headers = {
                    "User-Agent": ua.random,
                    "Accept-Language": "en-US, en;q=0.5",
                }

                logging.info(f"Attempting to fetch URL: {url} (Attempt {attempt + 1})")
                response = requests.get(url, headers=headers, timeout=10)

                if response.status_code == 200:
                    logging.info(f"Successfully fetched data from URL: {url}")
                    soup = BeautifulSoup(response.content, "lxml")
                    return self._parse_results(soup)
                elif response.status_code == 503:
                    logging.warning(f"503 error detected. Retrying... (Attempt {attempt + 1})")
                else:
                    logging.error(f"Unexpected status code {response.status_code}. Retrying...")

                time.sleep(retry_delay * (2 ** attempt))

            except requests.exceptions.RequestException as e:
                logging.error(f"Request failed: {e}. Retrying... (Attempt {attempt + 1})")

        logging.error(f"Failed to fetch data after {max_retries} attempts.")
        return []

    def _parse_results(self, soup: BeautifulSoup) -> list:
        product_list = []
        try:
            for item in soup.find_all("div", {"data-component-type": "s-search-result"}):
                # Extract product name
                name = "N/A"
                name_tag = item.find("span", {"class": "a-size-base-plus"})
                if name_tag:
                    name = name_tag.text.strip()
                else:
                    # Fallback for alternate name structures
                    name_tag_alt = item.find("span", {"class": "a-text-normal"})
                    if name_tag_alt:
                        name = name_tag_alt.text.strip()

                # Extract product description (if available)
                description = item.find("span", {"class": "a-size-base-plus a-color-base"})
                description = description.text.strip() if description else "N/A"

                # Extract product link
                link_tag = item.h2.a if item.h2 and item.h2.a else None
                full_link = f"https://www.amazon.ca{link_tag['href']}" if link_tag and 'href' in link_tag.attrs else "N/A"

                # Extract product price
                price_whole = item.find("span", {"class": "a-price-whole"})
                price_fraction = item.find("span", {"class": "a-price-fraction"})
                price = None
                if price_whole and price_fraction:
                    price = f"{price_whole.text.strip()}.{price_fraction.text.strip()}"
                else:
                    # Fallback for alternate price structure
                    price_tag_alt = item.find("span", {"class": "a-offscreen"})
                    price = price_tag_alt.text.strip() if price_tag_alt else "N/A"

                # Extract product rating
                rating = item.find("span", {"class": "a-icon-alt"})
                rating = rating.text.split(" ")[0] if rating else "N/A"

                # Skip if no name or description is found
                if name == "N/A" and description == "N/A":
                    logging.info("Skipping result due to missing title and description.")
                    continue

                product_list.append({
                    "Name": name,
                    "Description": description,
                    "Price": price,
                    "URL": full_link,
                    "Rating": rating,
                })
            
            logging.info(f"Successfully parsed {len(product_list)} products.")
        except Exception as e:
            logging.error(f"Error during parsing: {e}")

        return product_list
