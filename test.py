import joblib
import pandas as pd
import numpy as np
import os
from haversine import haversine
from datetime import datetime


# Define base path
base_path = r"C:\Users\p08pi\Desktop\Project\Packages"
base_path2 = r"C:\Users\p08pi\Desktop\Project\Dictionary"

# Load Transformers
print("\n Loading Transformers...")

# Load and check Input Transformer
pt_input_loaded = joblib.load(os.path.join(base_path, "pt_inputf.pkl"))
print("\n Input Transformer Loaded")

# Check if feature names exist before accessing them
if hasattr(pt_input_loaded, "feature_names_in_"):
    print("Feature Names:", pt_input_loaded.feature_names_in_)
else:
    print("Feature Names: Not available (PowerTransformer does not store them).")

print("Transformer Details:\n", pt_input_loaded)

# ✅ Load the correctly saved & fitted PowerTransformer
pt_target_loaded = joblib.load(os.path.join(base_path, "pt_targetf.pkl"))
print("power transformer target loaded")

if hasattr(pt_target_loaded, "feature_names_in_"):
    print("Feature Names:", pt_target_loaded.feature_names_in_)
else:
    print("Feature Names: Not available.")

print("Transformer Details:\n", pt_target_loaded)

#  Load Target Encoder
target_encf_loaded = joblib.load(os.path.join(base_path, "target_encf.pkl"))
# ✅ Check if encoder is correctly loaded
print("\n✅ Target Encoder Loaded Successfully!")
print("Encoder Columns:", target_encf_loaded.cols)

#LOADING THE DICTIONARIES
location_dict_loaded = joblib.load(os.path.join(base_path2, "location_dict.pkl"))
location_cat_dict_loaded = joblib.load(os.path.join(base_path2, "location_cat_dict.pkl"))
distance_look_loaded = joblib.load(os.path.join(base_path2, "distance_look.pkl"))
print("dictionaries loading success")

#  Load Model
print("\n🔹 Loading Model...")

model_loaded = joblib.load(os.path.join(base_path, "modelf.pkl"))
print("\n Model Loaded Successfully.")
print("Model Details:\n", model_loaded)

print("\n All model components are loaded properly and displayed!")

# Simulating user input (for testing)
pickup_location = "Dhaula Kuan"
drop_location = "Dwarka Sector 21 Metro Station"
weather_input = "Sunny"
special_event = "No"

# Validate locations
if pickup_location not in location_dict_loaded or drop_location not in location_dict_loaded:
    raise ValueError("Invalid Pickup or Drop Location")

# Fetch distance
if (pickup_location, drop_location) in distance_look_loaded:
    distance_km = distance_look_loaded[(pickup_location, drop_location)]
elif (drop_location, pickup_location) in distance_look_loaded:
    distance_km = distance_look_loaded[(drop_location, pickup_location)]
else:
    distance_km = 0
print(distance_km)

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
print("Weekend:", weekend)

# Traffic Index Logic
if weekend:
    traffic_index = np.random.randint(10, 40)  # Lower traffic on weekends
else:
    traffic_index = np.random.randint(60, 100) if hour in [8, 9, 18, 19] else np.random.randint(20, 50)

# Demand Index Logic
if weekend:
    demand_index = np.random.randint(10, 40)  # Lower demand on weekends
else:
    demand_index = np.random.randint(40, 80) if hour in [8, 9, 18, 19] else np.random.randint(10, 50)

#pickup_type = location_cat_dict_loaded.get(pickup_location, "Unknown")
#if pickup_type == "Commercial" and hour in [8, 9, 10]:
    ##demand_index = np.random.randint(60, 100)
#elif pickup_type == "Residential" and hour in [18, 19, 20]:
    #demand_index = np.random.randint(60, 100)
#else:
    #demand_index = np.random.randint(30, 80)

# Surge Multiplier Logic
surge_multiplier = 1.0
if demand_index > 60 and traffic_index > 80:
    surge_multiplier = np.random.uniform(1.5, 2.5)
if special_events == 1:
    surge_multiplier *= 1.5

# Apply Transformations
pickup_drop_df = pd.DataFrame({
    'pickup_location': [pickup_location],
    'drop_location': [drop_location]
})
encoded = target_encf_loaded.transform(pickup_drop_df)

pickup_location = encoded['pickup_location'].iloc[0]

drop_location = encoded['drop_location'].iloc[0]
print("encoding done")

# Correct numerical features as per your training:
numerical_features = pd.DataFrame(np.array([[distance_km, demand_index, traffic_index]]))
print("array df created", numerical_features)

# Transform numerical features
numerical_transformed = pt_input_loaded.transform(numerical_features)
print("half transformation done")
# Unpack transformed features
distance_km, demand_index, traffic_index = numerical_transformed[0]
print("transformation done")

feature_names = [
    'pickup_location', 'drop_location', 'distance_km', 'surge_multiplier', 
    'traffic_index', 'demand_index', 'weekend', 'special_events', 
    'hour', 'weather_Fog', 'weather_Humid', 'weather_Rain'
]
# Predict ETA
feauture_input = np.array([[pickup_location, drop_location, distance_km, surge_multiplier, traffic_index, demand_index, 
                                      weekend, special_events, hour, weather_Fog, weather_Humid, weather_Rain]])

sample_data = pd.DataFrame(feauture_input, columns=feature_names)


# ✅ Step 2: Make Prediction
predicted_eta = model_loaded.predict(sample_data)
print("\n✅ Prediction Success!")

# ✅ Step 3: Apply Inverse Transform (Convert ETA Back to Minutes)
if hasattr(pt_target_loaded, "lambdas_"):
    predicted_eta_original = pt_target_loaded.inverse_transform(predicted_eta.reshape(-1, 1))
    
    # Balanced correction: always subtract exactly 5 mins
    corrected_eta = max(predicted_eta_original[0][0], 1)  # ensure ETA is never negative
    
    print(f"🚀 Final Corrected ETA (Minutes): {corrected_eta:.2f}")
else:
    print("⚠️ Warning: PowerTransformer is not fitted. Showing raw prediction.")
    print(f"Predicted ETA (Raw Output): {predicted_eta[0]:.2f} (log-scale, not minutes)")






