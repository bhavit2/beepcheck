from sentence_transformers import SentenceTransformer, util

class RelevanceChecker:
    def __init__(self):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.exclusion_keywords = ["case", "protector", "accessory", "cable"]

    def filter_relevant_results(self, search_term, results):
        """
        Filters results based on semantic similarity and exclusion keywords.
        
        Args:
            search_term (str): The user-provided search term.
            results (list): List of result dictionaries with at least a 'title' key.

        Returns:
            list: Filtered list of relevant results.
        """
        search_embedding = self.model.encode(search_term, convert_to_tensor=True)
        relevant_results = []

        for result in results:
            title = result.get('title', '')
            if not title:
                continue

            # Calculate similarity
            product_embedding = self.model.encode(title, convert_to_tensor=True)
            similarity = util.pytorch_cos_sim(search_embedding, product_embedding).item()

            # Check for relevance
            if similarity > 0.75 and not any(
                keyword.lower() in title.lower() for keyword in self.exclusion_keywords
            ):
                relevant_results.append(result)

        return relevant_results
