
import pytest
import requests
import json

@pytest.fixture
def test_predict_endpoint():
    url = "http://34.71.165.181:8080/predict"
    headers = {
        "Content-Type": "application/json"
    }
    data = {
        "project": "827611166741",
        "endpoint_id": "7390671970817277952",
        "instances": [
            {
                "inputs": "Hello World!!",
                "parameters": {
                    "max_new_tokens": 128,
                    "temperature": 1.0,
                    "top_p": 0.9,
                    "top_k": 10
                }
            }
        ]
    }
    return url, headers, data

def test_predict_api(test_predict_endpoint):
    url, headers, data = test_predict_endpoint
    response = requests.post(url, headers=headers, json=data)

    # Assert the status code
    assert response.status_code == 200, f"Expected status code 200, but got {response.status_code}"

    # Parse and log the response data
    response_data = response.json()
    print("Full response:", json.dumps(response_data, indent=2)) 

    # Updated assertions based on the actual response structure
    assert 'messages' in response_data, "Response JSON should include a 'messages' key"
    assert isinstance(response_data['messages'], list), "'messages' key should contain a list"
    assert len(response_data['messages']) > 0, "'messages' list should not be empty"

    # Check additional keys if needed
    assert 'deployed_model_id' in response_data, "Response JSON should include 'deployed_model_id'"
    assert 'model' in response_data, "Response JSON should include 'model'"

