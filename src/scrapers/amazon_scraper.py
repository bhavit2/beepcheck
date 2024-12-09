import requests
from bs4 import BeautifulSoup
import random
import time
from fake_useragent import UserAgent
from .abstract_scraper import Scraper
from logger_config import get_logger

# Initialize logger
logger = get_logger(__name__)

class AmazonScraper(Scraper):
    BASE_URL = "https://www.amazon.ca/s?k="

    def fetch_results(self, search_term: str) -> list:
        """
        Fetch search results from Amazon for a given search term.

        Args:
            search_term (str): The search term to query Amazon.

        Returns:
            list: A list of dictionaries containing product details.
        """
        query = search_term.replace(" ", "+")
        url = self.BASE_URL + query
        
        # Initialize user agent
        try:
            ua = UserAgent()
        except Exception as e:
            logger.warning(f"Failed to initialize UserAgent. Using a default User-Agent. Error: {e}")
            ua = {"random": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"}
        
        max_retries = 5
        retry_delay = 2

        for attempt in range(max_retries):
            try:
                headers = {
                    "User-Agent": ua.random,
                    "Accept-Language": "en-US, en;q=0.5",
                }

                logger.info(f"Attempting to fetch URL: {url} (Attempt {attempt + 1})")
                logger.debug(f"User-Agent details: {headers}")
                response = requests.get(url, headers=headers, timeout=10)

                if response.status_code == 200:
                    logger.info(f"Successfully fetched data from URL: {url}")
                    soup = BeautifulSoup(response.content, "lxml")
                    return self._parse_results(soup)
                elif response.status_code == 503:
                    logger.warning(f"503 error detected. Retrying... (Attempt {attempt + 1})")
                else:
                    logger.error(f"Unexpected status code {response.status_code}. Retrying...")

                time.sleep(retry_delay * (2 ** attempt))

            except requests.exceptions.RequestException as e:
                logger.error(f"Request failed: {e}. Retrying... (Attempt {attempt + 1})")

        logger.error(f"Failed to fetch data after {max_retries} attempts.")
        return []
    
    def _parse_results(self, soup: BeautifulSoup) -> list:
        """
        Parse the HTML content to extract product details.

        Args:
            soup (BeautifulSoup): The BeautifulSoup object containing the HTML content.

        Returns:
            list: A list of dictionaries containing product details.
        """
        product_list = []
        try:
            for item in soup.find_all("div", {"data-component-type": "s-search-result"}):
                # Extract product name
                name = "N/A"
                name_tag = item.find("span", {"class": "a-size-base-plus"})
                if not name_tag:
                    name_tag = item.find("span", {"class": "a-text-normal"})
                name = name_tag.text.strip() if name_tag else "N/A"

                # Extract product description
                description_tag = item.find("span", {"class": "a-size-base-plus a-color-base"})
                description = description_tag.text.strip() if description_tag else "N/A"

                # Extract product link
                link_tag = item.find("a", {"class": "a-link-normal"}, href=True)
                full_link = f"https://www.amazon.ca{link_tag['href']}" if link_tag else "N/A"

                # Extract product price
                price_whole = item.find("span", {"class": "a-price-whole"})
                price_fraction = item.find("span", {"class": "a-price-fraction"})
                price = f"{price_whole.text.strip()}.{price_fraction.text.strip()}" if price_whole and price_fraction else "N/A"

                # Extract product rating
                rating_tag = item.find("span", {"class": "a-icon-alt"})
                rating = rating_tag.text.split(" ")[0] if rating_tag else "N/A"

                # Add product details to the list
                product_list.append({
                    "Name": name,
                    "Description": description,
                    "Price": price,
                    "URL": full_link,
                    "Rating": rating,
                })

            logger.info(f"Successfully parsed {len(product_list)} products.")
        except Exception as e:
            logger.error(f"Error during parsing: {e}", exc_info=True)

        return product_list
