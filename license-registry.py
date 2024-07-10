from flask import Flask, request, jsonify
import urllib.request
import json
from logging_config import setup_logger


app = Flask(__name__)

logger = setup_logger()

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "UP"}), 200

#add logging
@app.route('/check_license', methods=['GET'])
def check_license():
    license_number = request.args.get('number')
    if not license_number:
        logger.error(f"No license number provided:")
        return jsonify({"error": "No license number provided"}), 400

    url = f'https://data.gov.il/api/3/action/datastore_search?resource_id=053cea08-09bc-40ec-8f7a-156f0677aff3&q={license_number}'
    
    try:
        with urllib.request.urlopen(url) as response:
            data = json.loads(response.read().decode())
            return jsonify(data), 200
    except Exception as e:
        logger.error(f"Error processing license plate: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)