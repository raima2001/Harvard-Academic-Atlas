from flask import Flask, request, jsonify
from google.cloud import aiplatform
from google.oauth2 import service_account
from google.protobuf.json_format import MessageToDict
import json


# Authenticate with the service account
credentials = service_account.Credentials.from_service_account_file("../secrets/mega-pipeline.json")

app = Flask(__name__)

def log_request_details():
    """ Log the incoming JSON request details. """
    data = request.get_json()  # Using get_json() directly to parse JSON data
    print("Received Data:", data)

def predict_custom_trained_model(project, endpoint_id, instances, location="us-central1", api_endpoint="us-central1-aiplatform.googleapis.com"):
    """ Make a prediction using a custom-trained model on Google Cloud AI Platform. """
    client_options = {"api_endpoint": api_endpoint}
    client = aiplatform.gapic.PredictionServiceClient(client_options=client_options, credentials=credentials)
    endpoint = client.endpoint_path(project=project, location=location, endpoint=endpoint_id)
    
    try:
        response = client.predict(endpoint=endpoint, instances=instances)
        response_dict = {
        'deployed_model_id': response.deployed_model_id,
        'model': response.model,
        'model_display_name': response.model_display_name,
        'model_version_id': response.model_version_id
    }
        messages=[]
        for index, message in enumerate(response.predictions):
            messages.append(message)
        response_dict['messages']=messages
        return response_dict
    except Exception as e:
        raise e

@app.route('/predict', methods=['POST'])
def predict():
    """ Endpoint to handle prediction requests. """
    log_request_details()
    if not request.is_json:
        return jsonify({'error': 'Request must be JSON'}), 400
    
    data = request.get_json()
    project = data.get('project')
    endpoint_id = data.get('endpoint_id')
    instances = data.get('instances')
    
    if not project or not endpoint_id or not instances:
        return jsonify({'error': 'Missing required parameters'}), 400

    try:
        serialized_response = predict_custom_trained_model(project, endpoint_id, instances)
        return serialized_response
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/ping', methods=['GET'])
def ping():
    """ Health check route to ensure the service is running. """
    return jsonify({'message': 'Service is alive'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)