import requests
import logging
import random
import time
import os
from .abstract_scraper import Scraper

# Ensure necessary directories exist
logs_dir = '/mnt/SSD500GB/Work/project_claude_scraping/logs'
data_dir = '/mnt/SSD500GB/Work/project_claude_scraping/data'
os.makedirs(logs_dir, exist_ok=True)
os.makedirs(data_dir, exist_ok=True)

# Configure logging
logging.basicConfig(
    filename=os.path.join(logs_dir, 'bestbuy_scraper.log'),
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class BestBuyScraper(Scraper):
    BASE_API_URL = "https://www.bestbuy.ca/api/v2/json/search"

    # List of User-Agent strings
    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15A372 Safari/604.1",
        "Mozilla/5.0 (iPad; CPU OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15A372 Safari/604.1",
    ]

    def fetch_results(self, search_term: str) -> list:
        """
        Fetch product data from BestBuy API based on the search term.
        """
        query = search_term.replace(" ", "+")
        params = {
            "query": query,
            "sortBy": "relevance",
            "page": 1,
            "pageSize": 24,
        }

        headers = {
            "User-Agent": random.choice(self.USER_AGENTS),
            "Accept": "application/json",
            "Referer": f"https://www.bestbuy.ca/en-ca/search?search={query}",
        }

        all_results = []
        while params["page"] <= 5:  # Limit to 5 pages to avoid excessive requests
            try:
                logging.info(f"Fetching BestBuy results for: {search_term}, Page: {params['page']}")
                response = requests.get(self.BASE_API_URL, headers=headers, params=params, timeout=10)

                if response.status_code == 200:
                    data = response.json()
                    products = self._parse_results(data)

                    if not products:
                        logging.info(f"No more products found on page {params['page']}. Stopping.")
                        break

                    all_results.extend(products)
                    logging.info(f"Page {params['page']} fetched successfully.")

                    # Increment the page for pagination
                    params["page"] += 1

                    # Random delay between 1 and 3 seconds
                    time.sleep(random.uniform(1, 3))
                else:
                    logging.warning(f"Failed to fetch data. Status code: {response.status_code}")
                    break
            except requests.exceptions.RequestException as e:
                logging.error(f"Request failed: {e}")
                break

        logging.info(f"Total products fetched: {len(all_results)}")
        return all_results

    def _parse_results(self, data: dict) -> list:
        """
        Parse the JSON response and extract product data.
        """
        product_list = []

        try:
            products = data.get("products", [])
            for product in products:
                name = product.get("name")
                price = product.get("salePrice")
                sku = product.get("sku")
                rating = product.get("customerRating")

                if not name or not sku:
                    logging.warning(f"Skipping product due to missing name or SKU: {product}")
                    continue

                url = f"https://www.bestbuy.ca/en-ca/product/{sku}"

                product_details = {
                    "Name": name,
                    "Price": price if price else "N/A",
                    "URL": url,
                    "Rating": rating if rating else "N/A",
                }

                logging.info(f"Product parsed: {product_details}")
                product_list.append(product_details)

            logging.info(f"Parsed {len(product_list)} products.")
        except Exception as e:
            logging.error(f"Error during parsing: {e}")

        return product_list
