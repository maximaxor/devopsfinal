import pytest
import requests
from pymongo import MongoClient
from orchestrator import app, clean_and_format_data
import time

@pytest.fixture
def client():
    with app.test_client() as client:
        yield client

@pytest.fixture(scope="module")
def mongo_client():
    client = MongoClient('mongodb://mongodb:27017')
    yield client
    client.close()

@pytest.fixture(scope="module")
def db(mongo_client):
    return mongo_client["dbdata"]

def wait_for_record(db, license_plate_text, timeout=10):
    start_time = time.time()
    while time.time() - start_time < timeout:
        record = db.license_plates.find_one({"license_plate": license_plate_text})
        if record:
            return record
        time.sleep(1)
    return None

def test_process_license_plate(db):
    image_path = 'test_image.jpg'  # Ensure this file exists in the test directory
    url = 'http://orchestrator.default.svc.cluster.local:8000/process_license_plate'  # URL for the orchestrator service

    with open(image_path, 'rb') as image_file:
        files = {'image': (image_path, image_file, 'image/jpeg')}
        
        response = requests.post(url, files=files)
        assert response.status_code == 200, f"Unexpected status code: {response.status_code}"
        data = response.json()
        assert 'license_plate_text' in data
        assert 'data' in data

    # Debug: Print response data
    print("Response data:", data)

    # Wait for the data to be inserted into MongoDB
    license_plate_text = data['license_plate_text']
    record = wait_for_record(db, license_plate_text, timeout=10)

    # Verify information in MongoDB
    # Query with license plate as a string
    record = db.license_plates.find_one({"license_plate": license_plate_text})

    # Debug: Print the record found
    print("Record found in MongoDB:", record)

    assert record is not None, "Record not found in MongoDB"

    # Cleanup: Delete the record from MongoDB
    delete_result = db.license_plates.delete_one({"license_plate": license_plate_text})
    assert delete_result.deleted_count == 1, "Record deletion failed"

def test_clean_and_format_data():
    # Test case for clean_and_format_data function
    api_data = {
        'result': {
            'records': [
                {
                    'mispar_rechev': '1234567',
                    'baalut': 'Owner Name',
                    'tozeret_nm': 'Car Model',
                    'tzeva_rechev': 'Red',
                    'degem_manoa': 'Engine Model',
                    'shnat_yitzur': '2020',
                    'sug_delek_nm': 'Gasoline',
                    'ramat_gimur': 'High'
                }
            ]
        }
    }

    cleaned_data = clean_and_format_data(api_data)
    assert cleaned_data['license_plate'] == '1234567'
    assert cleaned_data['owner'] == 'Owner Name'