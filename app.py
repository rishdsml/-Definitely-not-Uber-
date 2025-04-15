from flask import Flask, request,send_file, jsonify, render_template
import joblib
import pandas as pd
import numpy as np
import os
from haversine import haversine
from datetime import datetime

app = Flask(__name__,template_folder="templates", static_folder="static")

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

# Define base path
#base_path = r"C:\Users\p08pi\Desktop\Project\Packages"
#base_path2 = r"C:\Users\p08pi\Desktop\Project\Dictionary"

#  **1. Load Locations from Excel File**
location_file = os.path.join(PROJECT_ROOT, "Dictionary", "final_categorized_locations.xlsx")
df_locations = pd.read_excel(location_file)  # Read the file
locations_list = df_locations["Location"].tolist()  # Extract location names

#Transformer Loading
pt_input_loaded = joblib.load(os.path.join(PROJECT_ROOT, "Packages", "pt_inputf.pkl"))
pt_target_loaded = joblib.load(os.path.join(PROJECT_ROOT, "Packages", "pt_targetf.pkl"))
target_encf_loaded = joblib.load(os.path.join(PROJECT_ROOT, "Packages", "target_encf.pkl"))
model_loaded = joblib.load(os.path.join(PROJECT_ROOT, "Packages", "modelf.pkl"))

#Dictionary Loading
location_dict_loaded = joblib.load(os.path.join(PROJECT_ROOT, "Dictionary", "location_dict.pkl"))
location_cat_dict_loaded = joblib.load(os.path.join(PROJECT_ROOT, "Dictionary", "location_cat_dict.pkl"))
distance_look_loaded = joblib.load(os.path.join(PROJECT_ROOT, "Dictionary", "distance_look.pkl"))

print("All things Loaded")

# Extract all locations before using them
locations_list = list(location_dict_loaded.keys())

#home page
@app.route('/')
def home():
    return render_template("index.html")

#location end point
@app.route('/get_locations')
def get_locations():
    locations_list = list(location_dict_loaded.keys())  # Convert dictionary keys to list
    return jsonify(locations_list)


#ETA Endpoint
@app.route('/predict_eta', methods=['POST'])
def predict_eta():
    data = request.get_json()
    pickup_location = data.get('pickup_location')
    drop_location = data.get('drop_location')
    weather_input = data.get('weather_input', 'Sunny')
    special_event = data.get('special_event', 'No')

    # Validate locations
    if pickup_location not in location_dict_loaded or drop_location not in location_dict_loaded:
        return jsonify({"error": "Invalid Pickup or Drop Location"}), 400

    # Fetch distance
    if (pickup_location, drop_location) in distance_look_loaded:
        distance_km = distance_look_loaded[(pickup_location, drop_location)]
    elif (drop_location, pickup_location) in distance_look_loaded:
        distance_km = distance_look_loaded[(drop_location, pickup_location)]
    else:
        distance_km = 0

    # Weather Matching
    weather_conditions = {"Sunny": "Clear", "Rainy": "Rain", "Foggy": "Fog", "Humid": "Humid"}
    weather = weather_conditions.get(weather_input, "Clear")

    # Weather One-Hot Encoding
    weather_Fog = 1 if weather == "Fog" else 0
    weather_Humid = 1 if weather == "Humid" else 0
    weather_Rain = 1 if weather == "Rain" else 0

    # Get current time details
    now = datetime.now()
    hour = now.hour
    weekend = 1 if now.weekday() >= 5 else 0
    special_events = 1 if special_event == "Yes" else 0

    # Traffic Index Logic
    if weekend:
        traffic_index = np.random.randint(10, 40)
    else:
        traffic_index = np.random.randint(60, 100) if hour in [8, 9, 18, 19] else np.random.randint(20, 50)

    # Demand Index Logic
    if weekend:
        demand_index = np.random.randint(10, 40)
    else:
        demand_index = np.random.randint(40, 80) if hour in [8, 9, 18, 19] else np.random.randint(10, 50)

    # Surge Multiplier Logic
    surge_multiplier = 1.0
    if demand_index > 60 and traffic_index > 80:
        surge_multiplier = np.random.uniform(1.5, 2.5)
    if special_events == 1:
        surge_multiplier *= 1.5

    # Apply Transformations
    pickup_drop_df = pd.DataFrame({'pickup_location': [pickup_location], 'drop_location': [drop_location]})
    encoded = target_encf_loaded.transform(pickup_drop_df)

    pickup_location = encoded['pickup_location'].iloc[0]
    drop_location = encoded['drop_location'].iloc[0]

    numerical_features = pd.DataFrame(np.array([[distance_km, demand_index, traffic_index]]))
    numerical_transformed = pt_input_loaded.transform(numerical_features)
    distance_km, demand_index, traffic_index = numerical_transformed[0]

    feature_names = [
        'pickup_location', 'drop_location', 'distance_km', 'surge_multiplier', 
        'traffic_index', 'demand_index', 'weekend', 'special_events', 
        'hour', 'weather_Fog', 'weather_Humid', 'weather_Rain'
    ]

    feature_input = np.array([[pickup_location, drop_location, distance_km, surge_multiplier, traffic_index, demand_index, 
                              weekend, special_events, hour, weather_Fog, weather_Humid, weather_Rain]])

    sample_data = pd.DataFrame(feature_input, columns=feature_names)

    # Make Prediction
    predicted_eta = model_loaded.predict(sample_data)

    # Apply Inverse Transform (Convert ETA Back to Minutes)
    if hasattr(pt_target_loaded, "lambdas_"):
        predicted_eta_original = pt_target_loaded.inverse_transform(predicted_eta.reshape(-1, 1))
        corrected_eta = max(predicted_eta_original[0][0] - 15, 1)
    else:
        corrected_eta = float(predicted_eta[0])

    return jsonify({
    "predicted_eta_minutes": round(float(corrected_eta), 2)
    })

import traceback

import traceback

#Surge Classifier Endpoint
@app.route('/predict_surge', methods=['POST'])
def predict_surge():
    try:
        data = request.get_json()


        # Required inputs (even if not used for now)
        pickup_location = data.get('pickup_location')
        drop_location = data.get('drop_location')
        weather_input = data.get('weather_input', 'Sunny')
        special_event = data.get('special_event', 'No')
        print("Step 1: Processing inputs...")

        # Process weather input into one-hot flags
        weather_conditions = {"Sunny": "Clear", "Rainy": "Rain", "Foggy": "Fog", "Humid": "Humid"}
        weather = weather_conditions.get(weather_input, "Clear")
        weather_Fog = 1 if weather == "Fog" else 0
        weather_Humid = 1 if weather == "Humid" else 0
        weather_Rain = 1 if weather == "Rain" else 0

        # Get current time, weekend flag, and event flag
        now = datetime.now()
        hour = now.hour
        weekend = 1 if now.weekday() >= 5 else 0
        special_events = 1 if special_event == "Yes" else 0

        # Generate traffic and demand indices (same logic as /predict_eta)
        if weekend:
            traffic_index = np.random.randint(10, 40)
            demand_index = np.random.randint(10, 40)
        else:
            traffic_index = np.random.randint(60, 100) if hour in [8, 9, 10, 18, 19,20] else np.random.randint(20, 50)
            demand_index = np.random.randint(40, 80) if hour in [8, 9, 10, 18, 19,20] else np.random.randint(10, 50)

        # Load and apply PowerTransformer for surge inputs
        try:
            print("Step 1.5: demand_index =", demand_index, "| traffic_index =", traffic_index)
            pt_surge_path = os.path.join(PROJECT_ROOT, "Packages", "pt_input_surge.pkl")
            pt_surge = joblib.load(pt_surge_path)
            scaled = pt_surge.transform(pd.DataFrame([[demand_index, traffic_index]], columns=["demand_index", "traffic_index"]))
            print("Step 1.6: Scaled values =", scaled)
            demand_index, traffic_index = scaled[0]
        except Exception as e:
            traceback.print_exc()
            return jsonify({"error": "PowerTransformer failed: " + str(e)})

        # Prepare final feature input for surge classifier
        surge_features = pd.DataFrame([[
            demand_index, traffic_index, weekend, special_events, hour,
            weather_Fog, weather_Humid, weather_Rain
        ]], columns=[
            'demand_index', 'traffic_index', 'weekend', 'special_events', 'hour',
            'weather_Fog', 'weather_Humid', 'weather_Rain'
        ])
        print("Step 2: Final surge features →\n", surge_features)
        print("Step 3: Loading model...")

        try:
            surge_model_path = os.path.join(PROJECT_ROOT, "Packages", "modelc.pkl")
            surge_model = joblib.load(surge_model_path)
            is_surge = int(surge_model.predict(surge_features)[0])
            proba = surge_model.predict_proba(surge_features)
            confidence = float(proba[0][1])

        except Exception as e:
            traceback.print_exc()
            is_surge = 0
            confidence = 0.0

        return jsonify({
            "is_surge": is_surge,
            "confidence": confidence
        })

    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)})

# Route to serve the interactive demand heatmap
@app.route('/heatmap')
def heatmap():
    absolute_path = os.path.join(PROJECT_ROOT, "maps", "button_heatmap_hiddenf.html")
    return send_file(absolute_path)

if __name__ == '__main__':
    app.run(debug=True)

