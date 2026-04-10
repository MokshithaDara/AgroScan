from fastapi import FastAPI, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse

import numpy as np
import cv2
import json
import io
import os
from PIL import Image

from tensorflow.keras.models import load_model
from tensorflow.keras.applications import ResNet50, DenseNet121, EfficientNetB5
from tensorflow.keras.layers import GlobalAveragePooling2D
from tensorflow.keras.models import Model
from tensorflow.keras.applications.resnet50 import preprocess_input as resnet_pre
from tensorflow.keras.applications.densenet import preprocess_input as dense_pre
from tensorflow.keras.applications.efficientnet import preprocess_input as eff_pre

from utils.location import get_coordinates
from utils.weather import get_weather
from utils.alerts import generate_alerts
from utils.treatment import get_treatment
from utils.severity import get_severity
from utils.voice import generate_voice
from utils.history import save_scan, get_history
from utils.products import get_product_links


# ---------------------------------------------------
# FASTAPI INITIALIZATION
# ---------------------------------------------------

app = FastAPI()

os.makedirs("static", exist_ok=True)

app.mount("/static", StaticFiles(directory="."), name="static")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------
# LOAD MODEL
# ---------------------------------------------------

model = load_model("model/model.h5")

with open("model/cropped_class_indices.json") as f:
    class_indices = json.load(f)

idx_to_class = {v: k for k, v in class_indices.items()}

IMG_SIZE = 224


# ---------------------------------------------------
# DISEASE NAME MAPPING
# ---------------------------------------------------

disease_full_names = {

    # -------- BANANA --------
    "Bract": "Banana – Bract Mosaic Virus",
    "Moko": "Banana – Moko",
    "Panama": "Banana – Panama",
    "Yellow": "Banana – Yellow and Black Sigatoka",
    "cordana": "Banana – Cordana",
    "pestalotiopsis": "Banana – Pestalotiopsis",
    "sigatoka": "Banana – Sigatoka",
    "Insect": "Banana – Insect Pest",

    # -------- CHILLI --------
    "Anthracnose": "Chilli – Anthracnose",
    "Leaf": "Chilli – Leaf Curl",
    "Whitefly": "Chilli – Whitefly",
    "yellowish": "Chilli – Yellowish",

    # -------- GROUNDNUT --------
    "Nutirtion": "Groundnut – Nutrition Deficiency",
    "Early": "Groundnut – Early Leaf Spot",
    "Late": "Groundnut – Late Leaf Spot",
    "Rust": "Groundnut – Rust",

    # -------- RADISH --------
    "Flea": "Radish – Flea Beetle",
    "Mosaic": "Radish – Mosaic Virus",
    "Downey": "Radish – Downy Mildew",

    # -------- CAULIFLOWER --------
    "Downy": "Cauliflower – Downy Mildew",
    "Black": "Cauliflower – Black Rot",
    "Bacterial": "Cauliflower – Bacterial Spot"
}


# ---------------------------------------------------
# FEATURE EXTRACTORS
# ---------------------------------------------------

resnet = ResNet50(weights="imagenet", include_top=False, input_shape=(224,224,3))
resnet = Model(resnet.input, GlobalAveragePooling2D()(resnet.output))

densenet = DenseNet121(weights="imagenet", include_top=False, input_shape=(224,224,3))
densenet = Model(densenet.input, GlobalAveragePooling2D()(densenet.output))

efficient = EfficientNetB5(weights="imagenet", include_top=False, input_shape=(224,224,3))
efficient = Model(efficient.input, GlobalAveragePooling2D()(efficient.output))


# ---------------------------------------------------
# LEAF VALIDATION
# ---------------------------------------------------

def is_leaf_image(image):

    img = np.array(image)

    hsv = cv2.cvtColor(img, cv2.COLOR_RGB2HSV)

    lower_green = np.array([25,40,40])
    upper_green = np.array([90,255,255])

    mask = cv2.inRange(hsv,lower_green,upper_green)

    green_ratio = np.sum(mask>0)/mask.size

    gray = cv2.cvtColor(img,cv2.COLOR_RGB2GRAY)
    edges = cv2.Canny(gray,50,150)

    edge_ratio = np.sum(edges>0)/edges.size

    return green_ratio>0.1 and edge_ratio>0.02


# ---------------------------------------------------
# IMAGE PREPROCESSING
# ---------------------------------------------------

def preprocess(img):

    img = img.convert("RGB")
    img = img.resize((IMG_SIZE,IMG_SIZE))

    arr = np.array(img)
    arr = np.expand_dims(arr,0)

    return arr


# ---------------------------------------------------
# FEATURE EXTRACTION
# ---------------------------------------------------

def extract_features(arr):

    f1 = resnet.predict(resnet_pre(arr),verbose=0)
    f2 = densenet.predict(dense_pre(arr),verbose=0)
    f3 = efficient.predict(eff_pre(arr),verbose=0)

    features = np.concatenate([f1,f2,f3],axis=1)

    return features


# ---------------------------------------------------
# HOME
# ---------------------------------------------------

@app.get("/")
def home():
    return {"message":"AgroScan API Running"}


# ---------------------------------------------------
# PREDICT API
# ---------------------------------------------------

@app.post("/predict")
async def predict(
    file: UploadFile = File(...),
    location: str = Form(...),
    language: str = Form("en"),
    user_id: str = Form(...)
):

    contents = await file.read()
    img = Image.open(io.BytesIO(contents))

    if not is_leaf_image(img):

        return JSONResponse({
            "scan":{
                "location":location,
                "disease":"Invalid Image",
                "confidence":0
            },
            "message":"Please upload a clear crop leaf image."
        })

    arr = preprocess(img)

    features = extract_features(arr)

    preds = model.predict(features)

    top = np.argmax(preds)

    disease_label = idx_to_class[top]

    confidence = float(preds[0][top]*100)


    # ---------------------------------------------------
    # HEALTHY CASE
    # ---------------------------------------------------

    if disease_label == "IMG":

        disease_name = "Healthy"
        disease_display = "Healthy Crop"

        treatment = "No disease detected. Maintain irrigation, fertilization and regular monitoring."
        alerts = []
        products = []

    else:

        disease_name = disease_full_names.get(disease_label, disease_label)
        disease_display = disease_name.replace("_"," ")

        alerts = []
        products = []


    # ---------------------------------------------------
    # SAVE HISTORY
    # ---------------------------------------------------

    save_scan(user_id,location,disease_display)


    # ---------------------------------------------------
    # WEATHER
    # ---------------------------------------------------

    try:
        lat,lon = get_coordinates(location)
        weather = get_weather(lat,lon)
    except:
        weather = {"temperature":"N/A","humidity":"N/A"}


    # ---------------------------------------------------
    # EXTRA FEATURES ONLY FOR DISEASE
    # ---------------------------------------------------

    if disease_name != "Healthy":

        alerts = generate_alerts(disease_name,weather)

        treatment = get_treatment(disease_name)

        severity,severity_recommendation = get_severity(confidence)

        products = get_product_links(disease_name)

    voice_file = generate_voice(disease_display,treatment,language)


    return {

        "scan":{
            "location":location,
            "disease":disease_display,
            "confidence":confidence
        },

        "treatment":treatment,

        "weather":weather,

        "alerts":alerts,

        "media":{
            "voice":voice_file,
            "heatmap":None
        },

        "products":products
    }


# ---------------------------------------------------
# HISTORY API
# ---------------------------------------------------

@app.get("/history/{user_id}")
def history(user_id:str):

    data = get_history(user_id)

    return {
        "total_scans":len(data),
        "history":data[:10]
    }


# ---------------------------------------------------
# WEATHER API
# ---------------------------------------------------

@app.get("/weather/{location}")
def weather_api(location:str):

    lat,lon = get_coordinates(location)

    weather = get_weather(lat,lon)

    return {

        "location":location,
        "temperature":weather.get("temperature","N/A"),
        "humidity":weather.get("humidity","N/A"),
        "condition":weather.get("condition","Unknown"),
        "advisory":"Monitor crop health during high humidity to prevent fungal diseases."
    }