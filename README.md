# Definitely Not Uber 🚖  
*I wanted to build Uber — without Uber’s data.*

I wanted to understand how ride-hailing apps really work —  
not just the product, but the entire **system** behind it.  
With no datasets, no APIs — just logic, math, and questions.  
So I built something.  
Something that’s... "Definitely Not" Uber 😄

> 📝 P.S. If I worked at a ride-hailing company, I wouldn’t generate my own data — I’d use theirs. 🤝

---

## 🧪 How I Made My Own Dataset
- Simulated **ride demand, traffic, surge, weather** using logic & probability distributions  
- Used the **Haversine formula** to calculate distances between 128 real Delhi zones  
- Each feature was handcrafted, tested, and tuned for **realistic, dynamic behavior**

---

## ✅ ETA Prediction
- Trained using `XGBoostRegressor`  
- R² Score: **0.88**, MAE: **0.17 minutes**  
- Optimized with **Optuna**: tree depth, regularization, learning rate  
- Feature engineered for **time, traffic, weather, distance, zone**

---

## ✅ Surge Classification
- Modeled as a **binary classification** problem using `XGBoostClassifier`  
- Predicted `surge_flag` with confidence scoring  
- Built for **high recall** during pressure zones

---

## ✅ Demand Forecasting (Heuristic)
- Used **clustering and behavioral logic** instead of time series  
- Simulated realistic flow: morning exits, evening returns, sudden spikes  
- Visualized demand trends across 24 hours via **Folium heatmap**

---

## ⚙️ System Design & Deployment
- Built a **full-stack simulation system**
- **Backend:** Flask API serving real-time ETA/surge/location endpoints  
- **Frontend:** HTML, CSS, JS for interactive UI  
- **Deployment:** Hosted on **Render**

https://www.linkedin.com/feed/update/urn:li:activity:7318368337447526401/


---

## 🧰 Tech Stack  
Python, Flask, XGBoost, Optuna, Pandas, NumPy, Joblib, Folium, HTML, CSS, JavaScript, Render

---

## 🚀 If Scaled Further  
- Dynamic **driver allocation** logic  
- Predictive **surge triggering**  
- Accurate ETA → fewer cancellations  
- **Simulation Sandbox** for pricing or fleet testing


---

