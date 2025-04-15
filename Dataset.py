import numpy as np
import pandas as pd
import random
from datetime import datetime, timedelta
from haversine import haversine

#  Load Predefined Locations and Categories
location_data = pd.read_csv("location_data.csv")  # Contains 'location_name', 'latitude', 'longitude', 'category'

#  Convert Locations to Dictionary
location_coords = {
    row['location_name']: (row['latitude'], row['longitude']) 
    for _, row in location_data.iterrows()
}
location_categories = {
    row['location_name']: row['category'] 
    for _, row in location_data.iterrows()
}

#  Define Timeframe for Dataset (4 Months of Rides)
start_date = datetime(2024, 1, 1)
end_date = datetime(2024, 5, 1)
num_rides = 50000  # Total rides to generate

#  Initialize Empty List for Ride Data
ride_data = []

#  **Generate Ride Data**
for _ in range(num_rides):
    #  Generate Timestamp
    timestamp = start_date + timedelta(
        seconds=random.randint(0, int((end_date - start_date).total_seconds()))
    )
    hour = timestamp.hour
    weekend = 1 if timestamp.weekday() >= 5 else 0

    # Select Pickup & Drop Locations
    pickup_location = random.choice(list(location_coords.keys()))
    drop_location = random.choice([loc for loc in location_coords.keys() if loc != pickup_location])
    
    # Get Coordinates
    pickup_coords = location_coords[pickup_location]
    drop_coords = location_coords[drop_location]
    
    # Calculate Haversine Distance (with correction factor)
    distance_km = haversine(pickup_coords, drop_coords)
    distance_km = round(max(1.1 * distance_km + 2, 1), 2)  # Adjusted correction

    # Define Traffic & Demand Index
    if weekend:
        demand_index = np.random.randint(10, 40)  # Lower on weekends
        traffic_index = np.random.randint(10, 40)
    else:
        demand_index = np.random.randint(40, 80) if hour in [8, 9, 18, 19] else np.random.randint(10, 50)
        traffic_index = np.random.randint(60, 100) if hour in [8, 9, 18, 19] else np.random.randint(20, 50)
    
    # Calculate ETA (Estimated Time of Arrival)
    base_speed = np.random.uniform(20, 40)  # Average speed in km/h
    eta_minutes = (distance_km / base_speed) * 60 + (traffic_index / 10)
    eta_minutes = round(eta_minutes, 2)  # Round to 2 decimal places

    # Surge Multiplier (Higher when demand & traffic are high)
    surge_multiplier = 1.0
    if demand_index > 60 and traffic_index > 80:
        surge_multiplier = np.random.uniform(1.5, 2.5)

    # Special Events Handling
    special_events = 0
    special_dates = [datetime(2024, 1, 1), datetime(2024, 2, 14), datetime(2024, 3, 8)]
    if any(abs((timestamp - event).days) < 2 for event in special_dates):
        special_events = 1
        surge_multiplier *= 1.5  # Increase surge during events

    # Weather Conditions
    weather = np.random.choice(["Clear", "Fog", "Rain", "Humid"], p=[0.65, 0.15, 0.10, 0.10])

    # Store Ride Data
    ride_data.append([
        timestamp, pickup_location, drop_location, distance_km, surge_multiplier,
        traffic_index, demand_index, weekend, special_events, hour, weather
    ])

# Convert Ride Data to DataFrame
columns = [
    "datetime", "pickup_location", "drop_location", "distance_km", "surge_multiplier",
    "traffic_index", "demand_index", "weekend", "special_events", "hour", "weather"
]
df = pd.DataFrame(ride_data, columns=columns)

#  Save Final Dataset
df.to_csv("final_ride_dataset.csv", index=False)
print("Dataset Created & Saved Successfully!")
