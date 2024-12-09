from abc import ABC, abstractmethod

class Scraper(ABC):
    """
    Abstract base class for all scrapers.
    """
    @abstractmethod
    def fetch_results(self, search_term: str) -> list:
        """
        Fetch product data based on the search term.
        Must be implemented by all subclasses.
        """
        pass
