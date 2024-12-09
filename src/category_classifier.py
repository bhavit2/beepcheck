from transformers import pipeline

class CategoryClassifier:
    def __init__(self):
        # Load a zero-shot classification pipeline
        self.classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")
        self.categories = {
            "Electronics": ["smartphone", "laptop", "tablet", "TV", "camera", "robot vacuum"],
            "Appliances": ["refrigerator", "microwave", "washing machine"],
            "Fashion": ["shoes", "clothing", "accessories"],
            "Groceries": ["food", "snacks", "beverages", "groceries"],
        }

    def classify(self, search_term: str) -> str:
        # Flatten category options
        category_labels = list(self.categories.keys())
        try:
            result = self.classifier(search_term, candidate_labels=category_labels)
            return result["labels"][0]  # Top predicted category
        except Exception as e:
            print(f"Error during classification: {e}")
            return "Unknown"

# Testing the classifier
if __name__ == "__main__":
    classifier = CategoryClassifier()
    search_term = input("Enter a search term: ")
    category = classifier.classify(search_term)
    print(f"Predicted category: {category}")
