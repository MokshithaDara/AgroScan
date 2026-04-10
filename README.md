🌱 AgroScan – AI Crop Disease Detection System

AgroScan is a full-stack AI application that detects crop diseases from leaf images and provides actionable insights such as treatment recommendations, weather alerts, and voice-based advisory.

🚀 Key Features
🌿 Crop disease detection using Deep Learning (CNN)
📸 Image upload for real-time prediction
💊 Treatment and prevention suggestions
🌦 Weather-based insights and alerts
🔊 Voice-based advisory system
📊 Dashboard with scan history
📚 Knowledge base for crops and diseases
🧠 System Workflow
User uploads a crop leaf image
Backend processes the image
CNN model predicts the disease
System fetches:
Treatment recommendations
Weather data
Alerts
Results are displayed on UI with optional voice output
🏗️ System Architecture

Frontend (HTML/CSS/JS)
→ FastAPI Backend
→ CNN Model (TensorFlow/Keras)
→ Services (Weather API, Database, Voice)
→ Response to Frontend

🛠️ Tech Stack

Frontend

HTML, CSS, JavaScript

Backend

FastAPI (Python)

Machine Learning

TensorFlow / Keras (CNN Model)

Utilities & APIs

Weather API
gTTS (Text-to-Speech)
📂 Project Structure
AgroScan/
│
├── backend/
│   ├── app.py
│   ├── database.py
│   ├── model/
│   ├── utils/
│
├── frontend/
│   ├── index.html
│   ├── dashboard.html
│   ├── scan.js
│   ├── style.css
│
├── README.md
├── .gitignore
▶️ Setup & Run
1. Clone the Repository
git clone https://github.com/MokshithaDara/AgroScan.git
cd AgroScan
2. Setup Backend
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
3. Run Backend
uvicorn app:app --reload
4. Run Frontend
cd ../frontend
python -m http.server 5500

Open in browser:
http://localhost:5500


🎯 Use Case

AgroScan helps farmers and agricultural stakeholders quickly identify plant diseases and take preventive action, reducing crop loss and improving productivity.

🔮 Future Scope
Mobile application (Android/iOS)
Multi-language support
Cloud deployment
AI chatbot integration
👩‍💻 Author

Mokshitha Lakshmi Dara

⭐ Support

If you found this project useful, please give it a ⭐ on GitHub.
