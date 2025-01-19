from flask import Flask, jsonify, request
from flask_cors import CORS
import requests
import xgboost as xgb
import pandas as pd

app = Flask(__name__)

CORS(app, origins="*", supports_credentials=True)
# Load the pre-trained model
model = xgb.XGBClassifier()
model.load_model('xgb_model.json')

# Function to fetch drivers
def fetch_drivers():
    url = "http://ergast.com/api/f1/2024/drivers.json?limit=1000"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        drivers = data['MRData']['DriverTable']['Drivers']
        # Return a dictionary with driverId as the key and first + last name as the value
        driver_dict = {
            driver['familyName']: {
                'firstName': driver['givenName'],
                'lastName': driver['familyName']
            }
            for driver in drivers
        }
        return driver_dict
    else:
        print("Failed to fetch driver data")
        return {}

# Function to fetch circuits for the year 2024
def fetch_circuits():
    url = "http://ergast.com/api/f1/2024/circuits.json?limit=1000"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        circuits = data['MRData']['CircuitTable']['Circuits']
        return {circuit['circuitName']: idx + 1 for idx, circuit in enumerate(circuits)}
    else:
        print("Failed to fetch circuit data for 2024")
        return {}

# Fetch the 2024 mappings for drivers and circuits
driver_mapping = fetch_drivers()
circuit_mapping = fetch_circuits()

@app.route('/drivers', methods=['GET'])
def get_drivers():
    return jsonify(driver_mapping)

@app.route('/circuits', methods=['GET'])
def get_circuits():
    return jsonify(circuit_mapping)

@app.route('/predict', methods=['POST', 'OPTIONS'])
def predict():
    if request.method == 'OPTIONS':
        return jsonify({'message': 'Preflight check successful'}), 200
    
    # Handle the POST request
    if not request.is_json:
        return jsonify({'error': 'Request must be JSON'}), 400
    data = request.get_json()
    driver_name = data.get('Driver')
    circuit_name = data.get('Circuit')
    qualifying_position = data.get('Qualifying_Position')

    # Validate input data
    if not driver_name or not circuit_name or qualifying_position is None:
        return jsonify({'error': 'Driver, Circuit, and Qualifying_Position are required.'}), 400

    try:
        qualifying_position = int(qualifying_position)
    except ValueError:
        return jsonify({'error': 'Qualifying_Position must be an integer.'}), 400

    if qualifying_position < 1 or qualifying_position > 20:
        return jsonify({'error': 'Qualifying_Position must be between 1 and 20.'}), 400

    # Map driver and circuit to IDs
    driver_id = driver_mapping.get(driver_name, -1)
    circuit_id = circuit_mapping.get(circuit_name, -1)

    if driver_id == -1:
        return jsonify({'error': f"Driver '{driver_name}' not found in the dataset."}), 400
    if circuit_id == -1:
        return jsonify({'error': f"Circuit '{circuit_name}' not found in the dataset."}), 400

    # Create DataFrame for model prediction
    input_data = pd.DataFrame([[driver_id, circuit_id, qualifying_position]], 
                              columns=['Driver', 'Circuit', 'Qualifying_Position'])

    # Predict probability of winning
    prediction = model.predict_proba(input_data)[0][1] * 100 

    return jsonify({'win_probability': f'{prediction:.2f}'})

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)
