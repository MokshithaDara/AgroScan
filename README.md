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
Backend preprocesses the image
Hybrid CNN model predicts the disease
System fetches:
Treatment recommendations
Weather data
Alerts
Results are displayed on UI with optional voice output

🏗️ System Architecture

Frontend (HTML/CSS/JS)
⬇
FastAPI Backend
⬇
Hybrid CNN Model (TensorFlow/Keras)
⬇
Services (Weather API, Database, Voice)
⬇
Response to Frontend

📂 Dataset Used
Multi-Crop Disease Dataset (Mendeley Data)
🔗 https://data.mendeley.com/datasets/6243z8r6t6/1
Contains images of multiple crops and diseases
Includes both healthy and diseased leaf samples
Covers crops like Banana, Chilli, Groundnut, Radish, Cauliflower
Used for training and validation of the CNN model

⚠️ Dataset is not included in the repository due to large size

🤖 CNN Model Methodology

AgroScan uses a Hybrid CNN Architecture combining:

ResNet50
DenseNet121
EfficientNet
🔍 Approach:
Input images resized and normalized
Passed through multiple pre-trained CNN models
Feature extraction from each model
Features combined using concatenation
Fully connected layers for classification
Output layer predicts disease class

📊 Algorithm Steps:
Load and preprocess image
Apply data augmentation
Extract features using CNN backbones
Combine features
Train classifier using labeled dataset
Predict disease with probability score

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

▶️ Setup & Run
1. Clone the Repository
git clone https://github.com/MokshithaDara/AgroScan.git
2. Setup Backend
cd AgroScan
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
3. Run Backend
uvicorn app:app --reload
4. Run Frontend
cd ../frontend
python -m http.server 5500

👉 Open in browser:
http://localhost:5500

🎯 Use Case

AgroScan helps farmers and agricultural stakeholders quickly identify plant diseases and take preventive action, reducing crop loss and improving productivity.

🔮 Future Scope
📱 Mobile application (Android/iOS)
🌐 Multi-language support
☁️ Cloud deployment
🤖 AI chatbot integration
