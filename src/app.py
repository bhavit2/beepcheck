from flask import Flask, request, jsonify, send_from_directory
from scraper_manager import ScraperManager
import os
from logger_config import get_logger

# Initialize Flask app
app = Flask(__name__)

# Initialize ScraperManager
scraper_manager = ScraperManager()

# Set up directories for data and logs
DATA_DIR = os.path.join(os.getcwd(), "data")
os.makedirs(DATA_DIR, exist_ok=True)

#LOGS_DIR = os.path.join(os.getcwd(), "logs")
#os.makedirs(LOGS_DIR, exist_ok=True)

# Get logger
logger = get_logger(__name__)

@app.route("/")
def index():
    """
    Index endpoint to confirm the API is running.
    """
    return jsonify({"message": "Welcome to the Enhanced Scraper API!"})

@app.route("/classify", methods=["POST"])
def classify():
    """
    Endpoint to classify a search term.
    Input JSON: {"search_term": "product name"}
    """
    try:
        data = request.get_json()
        search_term = data.get("search_term")
        if not search_term:
            return jsonify({"error": "Missing 'search_term' in request"}), 400
        
        # Classify category
        category = scraper_manager.classifier.classify(search_term)
        logger.info(f"Search term '{search_term}' classified as category '{category}'")
        return jsonify({"search_term": search_term, "category": category})
    except Exception as e:
        logger.error(f"Error in /classify endpoint: {str(e)}", exc_info=True)
        return jsonify({"error": "An error occurred while processing your request."}), 500

@app.route("/scrape", methods=["POST"])
def scrape():
    """
    Endpoint to scrape data based on a search term.
    Input JSON: {"search_term": "product name"}
    """
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

        logger.info(f"Scraping completed for term '{search_term}', saved to {output_file}")
        return jsonify({"message": "Scraping completed successfully!", "file": output_file, "results": results})
    except Exception as e:
        logger.error(f"Error in /scrape endpoint: {str(e)}", exc_info=True)
        return jsonify({"error": "An error occurred while processing your request."}), 500

@app.route("/data_files", methods=["GET"])
def list_data_files():
    """
    Endpoint to list all available data files in the 'data' directory.
    """
    try:
        files = [f for f in os.listdir(DATA_DIR) if f.endswith(".xlsx")]
        return jsonify({"files": files})
    except Exception as e:
        logger.error(f"Error in /data_files endpoint: {str(e)}", exc_info=True)
        return jsonify({"error": "An error occurred while retrieving the file list."}), 500

@app.route("/download/<filename>", methods=["GET"])
def download_file(filename):
    """
    Endpoint to download a specific data file from the 'data' directory.
    """
    try:
        # Ensure the file exists in the data directory
        if not os.path.isfile(os.path.join(DATA_DIR, filename)):
            return jsonify({"error": "File not found"}), 404

        return send_from_directory(DATA_DIR, filename, as_attachment=True)
    except Exception as e:
        logger.error(f"Error in /download/{filename} endpoint: {str(e)}", exc_info=True)
        return jsonify({"error": "An error occurred while attempting to download the file."}), 500

if __name__ == "__main__":
    # Run in development mode. Change `debug` to `False` in production.
    app.run(host="0.0.0.0", port=5001, debug=True)
