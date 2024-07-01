import requests
from flask import Flask, request, jsonify
from logging_config import setup_logger

app = Flask(__name__)

logger = setup_logger()

@app.route('/process_license_plate', methods=['POST'])
def process_license_plate():
    try:
        if 'image' not in request.files:
            app.logger.info(f"Response from image_processor: {result}")
            return jsonify({"error": "No image file provided"}), 400

        file = request.files['image']
        files = {'image': (file.filename, file.stream, file.content_type)}

        # Ensure this URL matches the endpoint in image_processor.py
        image_resp = requests.post('http://image_processor:5000/image_processing', files=files)

        if image_resp.status_code != 200:
            app.logger.error(f"Error from image_processor: {image_resp.text}")
            return jsonify({"error": "Failed to process image"}), image_resp.status_code

        result = image_resp.json()
        app.logger.info(f"Response from image_processor: {result}")

        license_text = result.get("text", "")
        if not license_text:
            return jsonify({"error": "No license plate text found"}), 400

        return jsonify({"license_plate_text": license_text})

    except Exception as e:
        app.logger.error(f"Error processing license plate: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
