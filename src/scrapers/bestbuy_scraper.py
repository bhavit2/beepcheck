import requests
import random
import time
from .abstract_scraper import Scraper
from logger_config import get_logger

# Initialize logger
logger = get_logger(__name__)

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

        Args:
            search_term (str): The search term to query BestBuy.

        Returns:
            list: A list of dictionaries containing product details.
        """
        query = search_term.replace(" ", "+")
        params = {
            "query": query,
            "sortBy": "relevance",
            "page": 1,
            "pageSize": 24,
        }

        all_results = []

        while True:
            headers = {
                "User-Agent": random.choice(self.USER_AGENTS),
                "Accept": "application/json",
                "Referer": f"https://www.bestbuy.ca/en-ca/search?search={query}",
            }

            logger.info(f"Fetching BestBuy results for: {search_term}, Page: {params['page']}")
            logger.debug(f"Using headers: {headers}")

            try:
                response = requests.get(
                    self.BASE_API_URL,
                    headers=headers,
                    params=params,
                    timeout=10
                )

                if response.status_code == 200:
                    data = response.json()
                    products = self._parse_results(data)

                    if not products:
                        logger.info(f"No more products found on page {params['page']}. Stopping.")
                        break

                    all_results.extend(products)
                    logger.info(f"Page {params['page']} fetched successfully. Total products so far: {len(all_results)}")

                    # Increment the page for pagination
                    params["page"] += 1

                    # Random delay between 1 and 3 seconds
                    time.sleep(random.uniform(1, 3))
                else:
                    logger.warning(f"Failed to fetch data. Status code: {response.status_code}")
                    break

            except requests.exceptions.RequestException as e:
                logger.error(f"Request failed: {e}", exc_info=True)
                break

        logger.info(f"Total products fetched: {len(all_results)}")
        return all_results

    def _parse_results(self, data: dict) -> list:
        """
        Parse the JSON response and extract product data.

        Args:
            data (dict): The JSON response from the BestBuy API.

        Returns:
            list: A list of dictionaries containing product details.
        """
        product_list = []

        try:
            products = data.get("products", [])
            for product in products:
                name = product.get("name")
                price = product.get("salePrice", "N/A")
                sku = product.get("sku")
                rating = product.get("customerRating", "N/A")

                if not name or not sku:
                    logger.debug(f"Skipping product due to missing name or SKU: {product}")
                    continue

                url = f"https://www.bestbuy.ca/en-ca/product/{sku}"

                product_details = {
                    "Name": name,
                    "Price": price,
                    "URL": url,
                    "Rating": rating,
                }

                logger.debug(f"Product parsed: {product_details}")
                product_list.append(product_details)

            logger.info(f"Parsed {len(product_list)} products.")
        except Exception as e:
            logger.error(f"Error during parsing: {e}", exc_info=True)

        return product_list
