import requests
from flask import Flask, request, jsonify
from logging_config import setup_logger
from pymongo import MongoClient
import os
from bson import ObjectId

app = Flask(__name__)

logger = setup_logger()

# Initialize MongoDB connection
mongo_client = MongoClient(os.getenv('MONGODB_URL', 'mongodb://mongodb:27017'))
db = mongo_client.dbdata
collection = db.license_plates


# Function to clean and format the data
def clean_and_format_data(api_data):
    if 'result' in api_data and 'records' in api_data['result'] and len(api_data['result']['records']) > 0:
        record = api_data['result']['records'][0]
        return {
            "license_plate": record.get("mispar_rechev"),
            "owner": record.get("baalut"),
            "model": record.get("tozeret_nm"),
            "color": record.get("tzeva_rechev"),
            "engine_model": record.get("degem_manoa"),
            "manufacturing_date": record.get("shnat_yitzur"),
            "car_type": record.get("sug_delek_nm"),
            "fanciness": record.get("ramat_gimur"),
        }
    else:
        return None
    
# Function to convert ObjectId to string
def convert_objectid_to_str(document):
    if isinstance(document, dict):
        for key, value in document.items():
            if isinstance(value, ObjectId):
                document[key] = str(value)
            elif isinstance(value, dict):
                convert_objectid_to_str(value)
            elif isinstance(value, list):
                document[key] = [convert_objectid_to_str(item) if isinstance(item, (dict, ObjectId)) else item for item in value]
    elif isinstance(document, ObjectId):
        document = str(document)
    return document

@app.route('/process_license_plate', methods=['POST'])
def process_license_plate():
    try:
        if 'image' not in request.files:
            app.logger.info("No image file provided")
            return jsonify({"error": "No image file provided"}), 400

        file = request.files['image']
        files = {'image': (file.filename, file.stream, file.content_type)}

        # Process the image using the image processor service
        image_resp = requests.post('http://image_processor:5000/image_processing', files=files)

        if image_resp.status_code != 200:
            app.logger.error(f"Error from image_processor: {image_resp.text}")
            return jsonify({"error": "Failed to process image"}), image_resp.status_code

        result = image_resp.json()
        app.logger.info(f"Response from image_processor: {result}")

        # Check if the result is a list and extract the license text
        if isinstance(result, list) and len(result) > 0:
            license_text = result[0].get("text", "")
        else:
            return jsonify({"error": "Invalid response format from image processor"}), 400

        if not license_text:
            return jsonify({"error": "No license plate text found"}), 400

        # Check if the license plate number is already in the database
        license_plate = collection.find_one({"license_plate": license_text})
        if license_plate:
            return jsonify({"license_plate_text": license_text, "data": convert_objectid_to_str(license_plate)})

        # If not in the database, check with the external API
        try:
            api_resp = requests.get(f'http://license_registry:5001/check_license?number={license_text}')
            api_resp.raise_for_status()
        except requests.exceptions.RequestException as e:
            app.logger.error(f"Errdor from external API: {e}")
            return jsonify({"error": "Failed to check license with external API"}), 500

        api_data = api_resp.json()
        app.logger.info(f"Response from external API: {api_data}")

        # Ensure api_data is a dictionary
        if isinstance(api_data, list):
            app.logger.error(f"Expected dictionary but got list: {api_data}")
            return jsonify({"error": "Invalid data format from external API"}), 500

        # Clean and format the datad
        cleaned_data = clean_and_format_data(api_data)

        if not cleaned_data:
            return jsonify({"error": "No data found for the given license plate"}), 404


        # Insert the cleaned data into the database
        collection.insert_one(cleaned_data)

        return jsonify({"license_plate_text": license_text, "data": convert_objectid_to_str(cleaned_data)})

    except Exception as e:
        app.logger.error(f"Error processing license plate: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
