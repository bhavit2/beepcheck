from flask import Flask, request, jsonify, send_from_directory
from scraper_manager import ScraperManager
from category_classifier import CategoryClassifier
import os
import json
import logging

# Initialize Flask app
app = Flask(__name__)

# Initialize ScraperManager
scraper_manager = ScraperManager()

# Set up directories for data and logs
DATA_DIR = os.path.join(os.getcwd(), "data")
os.makedirs(DATA_DIR, exist_ok=True)

LOGS_DIR = os.path.join(os.getcwd(), "logs")
os.makedirs(LOGS_DIR, exist_ok=True)

# Configure logging
logging.basicConfig(
    filename=os.path.join(LOGS_DIR, "flask_app.log"),
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

# Endpoint 1: Welcome
@app.route("/")
def index():
    return jsonify({"message": "Welcome to the Enhanced Scraper API!"})

# Endpoint 2: Classify without scraping
@app.route("/classify", methods=["POST"])
def classify():
    try:
        data = request.get_json()
        search_term = data.get("search_term")
        if not search_term:
            return jsonify({"error": "Missing 'search_term' in request"}), 400
        
        # Classify category
        category = scraper_manager.classifier.classify(search_term)
        logging.info(f"Search term '{search_term}' classified as category '{category}'")
        return jsonify({"search_term": search_term, "category": category})
    except Exception as e:
        logging.error(f"Error in /classify endpoint: {str(e)}")
        return jsonify({"error": str(e)}), 500

# Endpoint 3: Scrape data
@app.route("/scrape", methods=["POST"])
def scrape():
    try:
        data = request.get_json()
        search_term = data.get("search_term")
        if not search_term:
            return jsonify({"error": "Missing 'search_term' in request"}), 400

        # Fetch data using ScraperManager
        results = scraper_manager.fetch_data(search_term)
        
        # Save results to Excel file
        output_file = os.path.join(DATA_DIR, f"{search_term.replace(' ', '_')}_results.xlsx")
        scraper_manager.save_results_to_excel(results, output_file)

        logging.info(f"Scraping completed for term '{search_term}', saved to {output_file}")
        return jsonify({"message": "Scraping completed successfully!", "file": output_file, "results": results})
    except Exception as e:
        logging.error(f"Error in /scrape endpoint: {str(e)}")
        return jsonify({"error": str(e)}), 500

# Endpoint 4: Bulk search using file upload
@app.route("/bulk_scrape", methods=["POST"])
def bulk_scrape():
    try:
        file = request.files.get("file")
        if not file:
            return jsonify({"error": "No file uploaded"}), 400
        
        # Read search terms from uploaded file
        file_path = os.path.join(DATA_DIR, file.filename)
        file.save(file_path)
        
        with open(file_path, "r") as f:
            search_terms = [line.strip() for line in f.readlines()]
        
        results = []
        for term in search_terms:
            results.extend(scraper_manager.fetch_data(term))
        
        # Save results to Excel
        output_file = os.path.join(DATA_DIR, "bulk_results.xlsx")
        scraper_manager.save_results_to_excel(results, output_file)

        logging.info(f"Bulk scraping completed, results saved to {output_file}")
        return jsonify({"message": "Bulk scraping completed!", "file": output_file, "results_count": len(results)})
    except Exception as e:
        logging.error(f"Error in /bulk_scrape endpoint: {str(e)}")
        return jsonify({"error": str(e)}), 500

# Endpoint 5: List available data files
@app.route("/data_files", methods=["GET"])
def list_data_files():
    try:
        files = [f for f in os.listdir(DATA_DIR) if f.endswith(".xlsx")]
        return jsonify({"files": files})
    except Exception as e:
        logging.error(f"Error in /data_files endpoint: {str(e)}")
        return jsonify({"error": str(e)}), 500

# Endpoint 6: Download a specific data file
@app.route("/download/<filename>", methods=["GET"])
def download_file(filename):
    try:
        return send_from_directory(DATA_DIR, filename, as_attachment=True)
    except Exception as e:
        logging.error(f"Error in /download/{filename} endpoint: {str(e)}")
        return jsonify({"error": str(e)}), 500

# Run the Flask app
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
