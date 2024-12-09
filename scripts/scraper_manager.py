from category_classifier import CategoryClassifier
from scrapers.amazon_scraper import AmazonScraper
from scrapers.bestbuy_scraper import BestBuyScraper
from logger_config import scraper_logger
import pandas as pd
import os


class ScraperManager:
    def __init__(self):
        self.scrapers = {
            "Electronics": [AmazonScraper(), BestBuyScraper()],
            "Appliances": [BestBuyScraper()],
            "Fashion": [],  # Add scrapers for fashion retailers
            "Groceries": [],  # Add scrapers for grocery retailers
        }
        self.classifier = CategoryClassifier()

    def fetch_data(self, search_term: str) -> list:
        """
        Fetch data from the appropriate scrapers based on the search term.
        """
        # Classify the search term
        category = self.classifier.classify(search_term)
        selected_scrapers = self.scrapers.get(category, [])

        scraper_logger.info(f"Search term classified as category: {category}")
        scraper_logger.info(
            f"Selected scrapers: {', '.join(scraper.__class__.__name__ for scraper in selected_scrapers)}"
        )

        results = []
        for scraper in selected_scrapers:
            try:
                scraper_logger.info(f"Starting scrape with {scraper.__class__.__name__}")
                results.extend(scraper.fetch_results(search_term))
            except Exception as e:
                scraper_logger.error(
                    f"Error while scraping with {scraper.__class__.__name__}: {str(e)}"
                )

        if results:
            scraper_logger.info(f"Scraping completed. Total results fetched: {len(results)}")
            self.save_results_to_excel(results, search_term)
        else:
            scraper_logger.warning(f"No results found for search term: '{search_term}'")

        return results

    def get_scrapers_for_category(self, category: str):
        """
        Return a list of scraper instances for the given category.
        """
        scrapers = self.scrapers.get(category, [])
        scraper_logger.info(f"Retrieved {len(scrapers)} scrapers for category: {category}")
        return scrapers

    def save_results_to_excel(self, results: list, search_term: str):
        """
        Save the scraped results to an Excel file in the 'data' directory.
        """
        data_dir = os.path.join(os.getcwd(), "data")
        os.makedirs(data_dir, exist_ok=True)
        output_file = os.path.join(data_dir, f"{search_term.replace(' ', '_')}_results.xlsx")

        try:
            df = pd.DataFrame(results)
            df.to_excel(output_file, index=False)
            scraper_logger.info(f"Results saved to {output_file}")
        except Exception as e:
            scraper_logger.error(f"Failed to save results to Excel: {str(e)}")


# Testing ScraperManager
if __name__ == "__main__":
    search_term = input("Enter a product to search for: ")
    manager = ScraperManager()
    results = manager.fetch_data(search_term)

    if results:
        for result in results:
            print(result)
    else:
        print("No results found.")
