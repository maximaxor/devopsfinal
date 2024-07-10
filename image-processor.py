import os
import cv2
from flask import Flask, request, jsonify
import numpy as np
import imutils
import easyocr
from logging_config import setup_logger

# Initialize the Flask app
app = Flask(__name__)

logger = setup_logger()

@app.route('/image_processing', methods=['POST'])
def image_processing():
    try:
        if 'image' not in request.files:
            logger.error("No image file provided")
            return jsonify({"error": "No image file provided"}), 400

        file = request.files['image']
        file_path = 'uploaded_image.jpg'
        file.save(file_path)
        logger.info("Image file saved successfully")

        img = cv2.imread(file_path)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) # Gray image
        bfilter = cv2.bilateralFilter(gray, 11, 17, 17)  # Noise reduction
        edged = cv2.Canny(bfilter, 30, 200)  # Edge detection

        # Apply morphological operations to clean up the edges
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
        morph = cv2.morphologyEx(edged, cv2.MORPH_CLOSE, kernel)

        keypoints = cv2.findContours(morph.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        contours = imutils.grab_contours(keypoints)
        contours = sorted(contours, key=cv2.contourArea, reverse=True)[:10]

        img_area = img.shape[0] * img.shape[1]
        min_area = img_area * 0.01  # Minimum area as 1% of image area
        max_area = img_area * 0.9   # Maximum area as 90% of image area

        location = None
        for contour in contours:
            approx = cv2.approxPolyDP(contour, 21, True)
            if len(approx) == 4:
                area = cv2.contourArea(approx)
                if min_area < area < max_area:
                    # Aspect ratio check
                    x, y, w, h = cv2.boundingRect(approx)
                    aspect_ratio = w / float(h)
                    if 2 < aspect_ratio < 5:  # Common aspect ratio range for license plates
                        location = approx
                        break

        if location is None:
            logger.error("No license plate found")
            return jsonify({"error": "No license plate found"}), 400

        # Create mask
        mask = np.zeros(gray.shape, np.uint8)
        new_image = cv2.drawContours(mask, [location], 0, 255, -1)
        new_image = cv2.bitwise_and(img, img, mask=mask)

        (x, y) = np.where(mask == 255)
        (x1, y1) = (np.min(x), np.min(y))
        (x2, y2) = (np.max(x), np.max(y))
        cropped_image = gray[x1:x2+1, y1:y2+1]

        # Enhance the cropped image for better OCR
        cropped_image = cv2.resize(cropped_image, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
        _, cropped_image = cv2.threshold(cropped_image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        # Use EasyOCR to read text from the processed image
        reader = easyocr.Reader(['en'])
        result = reader.readtext(cropped_image, detail=0, allowlist='0123456789')
        
        # Convert result to list if it's a set
        if isinstance(result, set):
            result = list(result)

        text = " ".join(result)
        logger.info(f"Extracted text: {text}")
        return jsonify([{"text": text}])
    
    except Exception as e:
        logger.error(f"Error processing image: {e}")
        return jsonify({"error": "Failed to process image"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
