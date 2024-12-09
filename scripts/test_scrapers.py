import pandas as pd
import os
from scraper_manager import ScraperManager
from scrapers.amazon_scraper import AmazonScraper
from scrapers.bestbuy_scraper import BestBuyScraper

if __name__ == "__main__":
    # Initialize the Scraper Manager
    manager = ScraperManager()

    # Register the Amazon Scraper
    #amazon_scraper = AmazonScraper()
    #manager.register_scraper(amazon_scraper)
    # Register the BestBuy Scraper
    bestbuy_scraper = BestBuyScraper()
    manager.register_scraper(bestbuy_scraper)

    # Fetch results
    search_term = input("Enter a product to search for: ")
    results = manager.fetch_all_results(search_term)

    # Display the results
    if results:
        for product in results[:5]:  # Show the top 5 results
            print(product)

        # Save results to a CSV file
        
        # Define the data directory
        data_dir = '/mnt/SSD500GB/Work/project_claude_scraping/data'

        # Ensure the directory exists
        os.makedirs(data_dir, exist_ok=True)

        # Create the output file path
        output_file = os.path.join(data_dir, f"{search_term.replace(' ', '_')}_results.csv")
        df = pd.DataFrame(results)
        df.to_csv(output_file, index=False)
        print(f"Results saved to {output_file}")
    else:
        print("No results found.")
