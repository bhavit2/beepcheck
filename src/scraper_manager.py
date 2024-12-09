from category_classifier import CategoryClassifier
from scrapers.amazon_scraper import AmazonScraper
from scrapers.bestbuy_scraper import BestBuyScraper
from sentence_transformers import SentenceTransformer, util
from logger_config import get_logger
import pandas as pd
import os


class RelevanceChecker:
    """
    Filters search results based on semantic similarity to the search term.
    """
    def __init__(self, similarity_threshold=0.55, exclusion_keywords=None, logger=None):
        self.model = SentenceTransformer('all-MiniLM-L12-v2')
        self.similarity_threshold = similarity_threshold
        self.exclusion_keywords = exclusion_keywords or ["case", "protector", "accessory", "cable", "replacement"]
        self.logger = logger or get_logger(__name__)  # Default to module logger

    def filter_relevant_results(self, search_term, results):
        """
        Filter results based on semantic similarity of both Name and Description.

        Args:
            search_term (str): The search term to compare against.
            results (list): List of product results to filter.

        Returns:
            list: Filtered list of relevant results.
        """
        search_embedding = self.model.encode(search_term, convert_to_tensor=True)
        relevant_results = []

        for result in results:
            # Get Name and Description
            product_name = result.get('Name', '')
            product_description = result.get('Description', '')

            if not product_name and not product_description:
                continue  # Skip if both Name and Description are missing

            # Combine Name and Description into a single text
            combined_text = f"{product_name} {product_description}".strip()

            # Compute semantic similarity
            product_embedding = self.model.encode(combined_text, convert_to_tensor=True)
            similarity = util.pytorch_cos_sim(search_embedding, product_embedding).item()
            self.logger.debug(
                f"Product: {product_name}, Similarity: {similarity:.4f}, Combined Text: {combined_text}"
            )
            # Check for exclusion keywords and filter based on similarity threshold
            if similarity > self.similarity_threshold and not any(
                keyword.lower() in combined_text.lower() for keyword in self.exclusion_keywords
            ):
                relevant_results.append(result)

        self.logger.info(f"Filtered {len(relevant_results)} relevant results from {len(results)} total.")
        return relevant_results


class ScraperManager:
    def __init__(self, data_dir=None):
        self.scrapers = {
            "Electronics": [AmazonScraper(), BestBuyScraper()],
            "Appliances": [BestBuyScraper()],
            "Fashion": [],  # Add scrapers for fashion retailers
            "Groceries": [],  # Add scrapers for grocery retailers
        }
        self.classifier = CategoryClassifier()
        self.data_dir = data_dir or os.path.join(os.getcwd(), "data")  # Default data directory
        os.makedirs(self.data_dir, exist_ok=True)

        # Initialize logger
        self.logger = get_logger(__name__)

        # Initialize RelevanceChecker with logger
        self.relevance_checker = RelevanceChecker(logger=self.logger)

    def fetch_data(self, search_term: str) -> list:
        """
        Fetch data from the appropriate scrapers based on the search term.

        Args:
            search_term (str): The term to search for.

        Returns:
            list: Filtered list of relevant results.
        """
        category = self.classifier.classify(search_term)
        selected_scrapers = self.scrapers.get(category, [])

        self.logger.info(f"Search term '{search_term}' classified as category: {category}")
        if not selected_scrapers:
            self.logger.info(f"No scrapers configured for category: {category}")
            return []

        self.logger.debug(f"Selected scrapers: {', '.join(scraper.__class__.__name__ for scraper in selected_scrapers)}")

        results = []
        for scraper in selected_scrapers:
            try:
                self.logger.info(f"Starting scrape for '{search_term}' with {scraper.__class__.__name__}")
                results.extend(scraper.fetch_results(search_term))
            except Exception as e:
                self.logger.error(f"Error while scraping with {scraper.__class__.__name__}: {str(e)}", exc_info=True)

        if results:
            self.logger.info(f"Scraping completed for '{search_term}'. Total results fetched: {len(results)}")

            # Filter results for relevance
            filtered_results = self.relevance_checker.filter_relevant_results(search_term, results)
            self.logger.info(f"Results after filtering: {len(filtered_results)}")
            return filtered_results
        else:
            self.logger.info(f"No results found for search term: '{search_term}'")
            return []

    def save_results_to_excel(self, results: list, search_term: str, data_dir=None):
        """
        Save the scraped results to an Excel file.

        Args:
            results (list): List of results to save.
            search_term (str): Search term for naming the file.
            data_dir (str): Directory to save the file. Defaults to `self.data_dir`.
        """
        data_dir = data_dir or self.data_dir
        output_file = os.path.join(data_dir, f"{search_term.replace(' ', '_')}_results.xlsx")

        try:
            df = pd.DataFrame(results)
            df.to_excel(output_file, index=False)
            self.logger.info(f"Results saved to {output_file}")
        except Exception as e:
            self.logger.error(f"Failed to save results to Excel: {str(e)}", exc_info=True)
