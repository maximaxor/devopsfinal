import pytest
import requests
import subprocess
from requests.exceptions import ConnectionError
from orchestrator import app, clean_and_format_data

@pytest.fixture
def client():
    with app.test_client() as client:
        yield client

import requests

def test_process_license_plate():
    image_path = 'test_image.jpg'  # Ensure this file exists in the test directory
    url = 'http://localhost:8000/process_license_plate'  # URL for the orchestrator service
    
    with open(image_path, 'rb') as image_file:
        files = {'image': (image_path, image_file, 'image/jpeg')}
        
        response = requests.post(url, files=files)
        
        assert response.status_code == 200, f"Unexpected status code: {response.status_code}"
        data = response.json()
        assert 'license_plate_text' in data
        assert 'data' in data


def test_clean_and_format_data():
    # Test case for `clean_and_format_data` function
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
    # Add more assertions for other fields

def ping_container(container_name, target_name):
    try:
        result = subprocess.run(
            ["docker", "exec", container_name, "ping", "-c", "1", target_name],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        return result.returncode == 0
    except Exception as e:
        print(f"Error executing ping: {e}")
        return False

def test_ping_between_containers():
    assert ping_container("speed_camera_project-orchestrator-1", "speed_camera_project-license-registry-1"), "Ping to license-registry failed"
    assert ping_container("speed_camera_project-orchestrator-1", "speed_camera_project-image-processor-1"), "Ping to image-processor failed"

def is_responsive(url):
    try:
        response = requests.options(url)  # Use OPTIONS to check if the URL is available
        # Check for 200 OK or 405 Method Not Allowed which means the endpoint exists but disallows OPTIONS
        if response.status_code in [200, 405]:
            return True
        else:
            print(f"Received status code {response.status_code} for URL: {url}")
            return False
    except requests.ConnectionError:
        print(f"Failed to connect to URL: {url}")
        return False

def test_url_responsiveness():
    assert is_responsive('http://localhost:8000/process_license_plate'), "Orchestrator service is not responsive"
    assert is_responsive('http://localhost:5000/image_processing'), "Image processor service is not responsive"
    assert is_responsive('http://localhost:5001/check_license'), "License registry service is not responsive"

