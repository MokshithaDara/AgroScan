from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

import numpy as np
import cv2
import json
import io
import os
import re
import logging
import shutil
import tempfile
from typing import List, Optional
from PIL import Image, UnidentifiedImageError
from dotenv import load_dotenv
from pydantic import BaseModel, Field
import h5py

from tensorflow.keras.models import load_model
from tensorflow.keras.applications import ResNet50, DenseNet121, EfficientNetB5
from tensorflow.keras.layers import GlobalAveragePooling2D, Dense, Dropout, Input
from tensorflow.keras.models import Model
from tensorflow.keras.applications.resnet50 import preprocess_input as resnet_pre
from tensorflow.keras.applications.densenet import preprocess_input as dense_pre
from tensorflow.keras.applications.efficientnet import preprocess_input as eff_pre

from utils.location import get_coordinates, get_city_from_coordinates
from utils.weather import get_weather
from utils.alerts import generate_alerts
from utils.treatment import get_treatment, get_treatment_plan
from utils.voice import generate_voice
from utils.history import save_scan, get_history, get_total_scans
from utils.products import get_product_links
from utils.forecast import get_forecast_risk
from utils.analytics import get_hotspot_analytics

# ---------------------------------------------------
# FASTAPI INITIALIZATION
# ---------------------------------------------------

app = FastAPI()
load_dotenv()
logger = logging.getLogger("agroscan")
if not logger.handlers:
    logging.basicConfig(level=logging.INFO)

os.makedirs("static", exist_ok=True)

app.mount("/static", StaticFiles(directory="static"), name="static")

origins_env = os.getenv(
    "CORS_ORIGINS",
    "http://127.0.0.1:5500,http://localhost:5500,http://127.0.0.1:3000,http://localhost:3000,null",
)
allowed_origins = [origin.strip() for origin in origins_env.split(",") if origin.strip()]
allow_credentials = "*" not in allowed_origins

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_origin_regex=r"^https?://(localhost|127\.0\.0\.1)(:\d+)?$|^null$",
    allow_credentials=allow_credentials,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)


class ProductLink(BaseModel):
    product: Optional[str] = None
    platform: str
    link: str
    reason: Optional[str] = None
    when_to_use: Optional[str] = None
    when_not_to_use: Optional[str] = None
    dose_guidance: Optional[str] = None
    weather_note: Optional[str] = None


class MediaInfo(BaseModel):
    voice: Optional[str] = None
    heatmap: Optional[str] = None


class ScanInfo(BaseModel):
    location: str
    disease: str
    confidence: float


class WeatherInfo(BaseModel):
    temperature: str | float
    humidity: str | float
    condition: str = "Unknown"


class PredictResponse(BaseModel):
    scan: ScanInfo
    treatment: str
    treatment_steps: List[str] = Field(default_factory=list)
    weather_cautions: List[str] = Field(default_factory=list)
    weather: WeatherInfo
    alerts: List[str]
    products: List[ProductLink]
    media: MediaInfo


class HistoryItem(BaseModel):
    user_id: str
    date: str
    location: str
    disease: str
    treatment: str = ""
    treatment_steps: List[str] = Field(default_factory=list)
    products_recommended: List[str] = Field(default_factory=list)


class HistoryResponse(BaseModel):
    total_scans: int
    current_page: int
    page_size: int
    total_pages: int
    history: List[HistoryItem]


class WeatherResponse(BaseModel):
    location: str
    temperature: str | float
    humidity: str | float
    condition: str
    advisory: str


class DetectLocationResponse(BaseModel):
    city: str
    lat: float
    lon: float


class SprayWindow(BaseModel):
    start: str
    wind_kmh: float
    rain_mm_3h: float
    suitable: bool


class DailyRiskItem(BaseModel):
    date: str
    temp_avg_c: float
    humidity_avg_pct: float
    rain_total_mm: float
    wind_max_kmh: float
    risk_level: str
    alerts: List[str]
    preventive_recommendations: List[str]


class ForecastRiskResponse(BaseModel):
    location: str
    days_requested: int
    days_available: int
    generated_at_utc: str
    daily_risk: List[DailyRiskItem]
    spray_windows: List[SprayWindow]
    spray_window_note: str


class HotspotItem(BaseModel):
    location: str
    lat: Optional[float] = None
    lon: Optional[float] = None
    scan_count: int
    top_disease: str
    top_disease_count: int


class ClusterItem(BaseModel):
    grid_lat: float
    grid_lon: float
    scan_count: int


class DistrictTrendItem(BaseModel):
    location: str
    scan_count: int
    top_disease: str
    recent_count: int = 0
    previous_count: int = 0
    trend_delta: int = 0
    trend_direction: str = "stable"


class DiseaseCountItem(BaseModel):
    disease: str
    count: int


class WeeklyTrendItem(BaseModel):
    week: str
    count: int


class HotspotAnalyticsResponse(BaseModel):
    total_scans: int
    hotspots: List[HotspotItem]
    clusters: List[ClusterItem]
    district_trends: List[DistrictTrendItem]
    top_diseases: List[DiseaseCountItem]
    weekly_trend: List[WeeklyTrendItem]

# ---------------------------------------------------
# LOAD MODEL
# ---------------------------------------------------

model = None
class_indices = {}
idx_to_class = {}
MODEL_READY = False


def _build_classifier_from_weights(weights_path: str, num_classes: int = 23):
    """Rebuild classifier head and load weights by layer name (cross-version safe)."""
    inp = Input(shape=(5120,), name="input_layer_3")
    x = Dense(512, activation="relu", name="dense")(inp)
    x = Dropout(0.5, name="dropout")(x)
    x = Dense(256, activation="relu", name="dense_1")(x)
    x = Dropout(0.4, name="dropout_1")(x)
    out = Dense(num_classes, activation="softmax", name="dense_2")(x)
    classifier = Model(inp, out, name="hybrid_classifier_head")
    classifier.load_weights(weights_path, by_name=True)
    return classifier


def _load_model_with_h5_compat(model_path: str):
    """Load H5 model and patch known Keras config key mismatches when needed."""
    try:
        return load_model(model_path, compile=False)
    except Exception as exc:
        msg = str(exc)
        if "Unrecognized keyword arguments: ['batch_shape']" not in msg:
            raise

        logger.warning(
            "Detected legacy/new Keras config mismatch for '%s'. Applying compatibility patch for InputLayer batch_shape.",
            model_path,
        )

        tmp_file = tempfile.NamedTemporaryFile(suffix=".h5", delete=False)
        tmp_path = tmp_file.name
        tmp_file.close()

        try:
            shutil.copyfile(model_path, tmp_path)
            with h5py.File(tmp_path, "r+") as h5f:
                model_config = h5f.attrs.get("model_config")
                if model_config is None:
                    raise RuntimeError("model_config attribute not found in H5 file.")

                config_text = (
                    model_config.decode("utf-8")
                    if isinstance(model_config, (bytes, bytearray))
                    else str(model_config)
                )
                patched_text = config_text.replace('"batch_shape"', '"batch_input_shape"')
                if patched_text == config_text:
                    raise RuntimeError(
                        "No batch_shape key found in model_config; cannot apply compatibility patch."
                    )

                if isinstance(model_config, (bytes, bytearray)):
                    h5f.attrs["model_config"] = patched_text.encode("utf-8")
                else:
                    h5f.attrs["model_config"] = patched_text

            try:
                return load_model(tmp_path, compile=False)
            except Exception as patched_exc:
                patched_msg = str(patched_exc)
                if "Unknown dtype policy: 'DTypePolicy'" in patched_msg:
                    logger.warning(
                        "Falling back to manual classifier reconstruction for '%s' due to Keras dtype policy mismatch.",
                        model_path,
                    )
                    return _build_classifier_from_weights(model_path, num_classes=23)
                raise
        finally:
            try:
                os.remove(tmp_path)
            except OSError:
                pass

try:
    model = _load_model_with_h5_compat("model/model.h5")
    with open("model/cropped_class_indices.json") as f:
        class_indices = json.load(f)
    idx_to_class = {v: k for k, v in class_indices.items()}
    MODEL_READY = True
except Exception as e:
    logger.error(
        "ML model initialization failed. /predict will be unavailable until fixed: %s",
        e,
    )

IMG_SIZE = 224
MAX_UPLOAD_BYTES = 5 * 1024 * 1024
MAX_LOCATION_LENGTH = 120
USER_ID_PATTERN = re.compile(r"^farmer_[a-zA-Z0-9]{8,}$")
ALLOWED_LANGUAGES = {"en", "te", "hi"}


def disease_key_from_display(disease_display: str) -> str:
    normalized = str(disease_display or "")
    for token in ("Ã¢â‚¬â€œ", "â€“", "–", "—"):
        normalized = normalized.replace(token, "-")
    if "-" in normalized:
        return normalized.split("-", 1)[-1].strip()
    return normalized.strip()

# ---------------------------------------------------
# FEATURE EXTRACTORS
# ---------------------------------------------------

resnet = None
densenet = None
efficient = None

if MODEL_READY:
    try:
        resnet_base = ResNet50(weights="imagenet", include_top=False, input_shape=(224,224,3))
        resnet = Model(resnet_base.input, GlobalAveragePooling2D()(resnet_base.output))

        densenet_base = DenseNet121(weights="imagenet", include_top=False, input_shape=(224,224,3))
        densenet = Model(densenet_base.input, GlobalAveragePooling2D()(densenet_base.output))

        efficient_base = EfficientNetB5(weights="imagenet", include_top=False, input_shape=(224,224,3))
        efficient = Model(efficient_base.input, GlobalAveragePooling2D()(efficient_base.output))
    except Exception as e:
        MODEL_READY = False
        logger.error(
            "Feature extractor initialization failed. /predict unavailable: %s",
            e,
        )

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
# PREPROCESS
# ---------------------------------------------------

def preprocess(img):
    img = img.convert("RGB")
    img = img.resize((IMG_SIZE,IMG_SIZE))
    arr = np.array(img)
    return np.expand_dims(arr,0)

# ---------------------------------------------------
# FEATURE EXTRACTION
# ---------------------------------------------------

def extract_features(arr):
    if not MODEL_READY or not all([resnet, densenet, efficient]):
        raise RuntimeError("ML stack is not ready.")
    f1 = resnet.predict(resnet_pre(arr),verbose=0)
    f2 = densenet.predict(dense_pre(arr),verbose=0)
    f3 = efficient.predict(eff_pre(arr),verbose=0)
    return np.concatenate([f1,f2,f3],axis=1)


disease_full_names = {

    # -------- BANANA --------
    "Bract": "Banana - Bract Mosaic Virus",
    "Moko": "Banana - Moko",
    "Panama": "Banana - Panama",
    "Yellow": "Banana - Yellow and Black Sigatoka",
    "cordana": "Banana - Cordana",
    "pestalotiopsis": "Banana - Pestalotiopsis",
    "sigatoka": "Banana - Sigatoka",
    "Insect": "Banana - Insect Pest",

    # -------- CHILLI --------
    "Anthracnose": "Chilli - Anthracnose",
    "Leaf": "Chilli - Leaf Curl",
    "Whitefly": "Chilli - Whitefly",
    "yellowish": "Chilli - Yellowish",

    # -------- GROUNDNUT --------
    "Nutirtion": "Groundnut - Nutrition Deficiency",
    "Early": "Groundnut - Early Leaf Spot",
    "Late": "Groundnut - Late Leaf Spot",
    "Rust": "Groundnut - Rust",

    # -------- RADISH --------
    "Flea": "Radish - Flea Beetle",
    "Mosaic": "Radish - Mosaic Virus",
    "Downey": "Radish - Downy Mildew",

    # -------- CAULIFLOWER --------
    "Downy": "Cauliflower - Downy Mildew",
    "Black": "Cauliflower - Black Rot",
    "Bacterial": "Cauliflower - Bacterial Spot"
}


# ---------------------------------------------------
# HOME
# ---------------------------------------------------

@app.get("/")
def home():
    return {"message":"AgroScan API Running"}

# ---------------------------------------------------
# PREDICT
# ---------------------------------------------------

@app.post("/predict", response_model=PredictResponse)
async def predict(
    file: UploadFile = File(...),
    location: str = Form(...),
    language: str = Form("en"),
    user_id: str = Form(...)
):
    if not MODEL_READY or model is None or not idx_to_class:
        raise HTTPException(
            status_code=503,
            detail="Prediction service is temporarily unavailable. Model failed to initialize.",
        )

    location = location.strip()
    if not location:
        raise HTTPException(status_code=400, detail="Location is required.")
    if len(location) > MAX_LOCATION_LENGTH:
        raise HTTPException(
            status_code=400,
            detail=f"Location must be {MAX_LOCATION_LENGTH} characters or less.",
        )
    if not USER_ID_PATTERN.match(user_id):
        raise HTTPException(status_code=400, detail="Invalid user_id format.")
    if language not in ALLOWED_LANGUAGES:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported language. Allowed values: {', '.join(sorted(ALLOWED_LANGUAGES))}.",
        )

    if file.content_type and not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Only image uploads are supported.")

    contents = await file.read()
    if not contents:
        raise HTTPException(status_code=400, detail="Empty file uploaded.")
    if len(contents) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail="Image size must be 5MB or less.")

    try:
        img = Image.open(io.BytesIO(contents))
    except UnidentifiedImageError:
        raise HTTPException(status_code=400, detail="Invalid image file.")

    if not is_leaf_image(img):
        raise HTTPException(
            status_code=400,
            detail="Please upload a clear crop leaf image."
        )

    arr = preprocess(img)
    features = extract_features(arr)
    preds = model.predict(features)

    top = np.argmax(preds)
    confidence = float(preds[0][top]*100)

# Low-confidence filter intentionally disabled per current product requirement.

    disease_label = idx_to_class[top]

    # ---------------------------------------------------
    # WEATHER
    # ---------------------------------------------------

    try:
        lat, lon = get_coordinates(location)
        weather = get_weather(lat, lon)
    except Exception as e:
        logger.warning("Failed to fetch weather for '%s': %s", location, e)
        weather = {"temperature": "N/A", "humidity": "N/A", "condition": "Unknown"}

    # ---------------------------------------------------
    # HEALTHY / DISEASE LOGIC
    # ---------------------------------------------------

    if disease_label == "IMG":
        disease_display = "Healthy Crop"
        treatment = "No disease detected. Maintain irrigation and routine monitoring."
        treatment_steps = [
            "Continue regular scouting every 48 hours.",
            "Maintain balanced irrigation and nutrition.",
            "Keep field sanitation and remove stressed debris."
        ]
        weather_cautions = []
        alerts = []
        products = []
    else:
        disease_display = disease_full_names.get(disease_label, disease_label)
        disease_key = disease_key_from_display(disease_display)

        treatment_plan = get_treatment_plan(disease_key, weather=weather)
        treatment = get_treatment(disease_key, weather=weather)
        treatment_steps = treatment_plan.get("steps", [])
        weather_cautions = treatment_plan.get("weather_cautions", [])
        alerts = generate_alerts(disease_display, weather)
        products = get_product_links(disease_display, weather=weather)

    # ---------------------------------------------------
    # SAVE HISTORY (SAFE)
    # ---------------------------------------------------

    products_recommended = []
    seen_products = set()
    for item in (products or []):
        if not isinstance(item, dict):
            continue
        name = (item.get("product") or "").strip()
        if not name or name in seen_products:
            continue
        seen_products.add(name)
        products_recommended.append(name)

    try:
        save_scan(
            user_id,
            location,
            disease_display,
            treatment,
            treatment_steps=treatment_steps,
            products_recommended=products_recommended,
        )
    except Exception as e:
        logger.warning("Failed to save scan history: %s", e)

    # ---------------------------------------------------
    # VOICE
    # ---------------------------------------------------

    try:
        voice_file = generate_voice(disease_display, treatment, language, user_id=user_id)
    except Exception as e:
        logger.warning("Failed to generate voice advice: %s", e)
        voice_file = None

    return {
        "scan":{
            "location":location,
            "disease":disease_display,
            "confidence":confidence
        },
        "treatment":treatment,
        "treatment_steps": treatment_steps,
        "weather_cautions": weather_cautions,
        "weather":weather,
        "alerts":alerts,
        "products":products,
        "media":{
            "voice":voice_file,
            "heatmap":None
        }
    }

# ---------------------------------------------------
# HISTORY
# ---------------------------------------------------

@app.get("/history/{user_id}", response_model=HistoryResponse)
def history(user_id:str, page: int = 1, page_size: int = 9):
    if not USER_ID_PATTERN.match(user_id):
        raise HTTPException(status_code=400, detail="Invalid user_id format.")
    if page < 1:
        raise HTTPException(status_code=400, detail="Page must be 1 or greater.")
    if page_size < 1 or page_size > 50:
        raise HTTPException(status_code=400, detail="page_size must be between 1 and 50.")
    try:
        total = get_total_scans(user_id)
        total_pages = max(1, (total + page_size - 1) // page_size)
        if page > total_pages and total > 0:
            page = total_pages

        skip = (page - 1) * page_size
        data = get_history(user_id, limit=page_size, skip=skip)
    except Exception as e:
        logger.error("History read failed for user_id=%s: %s", user_id, e)
        raise HTTPException(
            status_code=503,
            detail="History service temporarily unavailable. Please try again.",
        )
    return {
        "total_scans": total,
        "current_page": page,
        "page_size": page_size,
        "total_pages": total_pages,
        "history": data
    }

# ---------------------------------------------------
# WEATHER API
# ---------------------------------------------------

@app.get("/weather/{location}", response_model=WeatherResponse)
def weather_api(location:str):
    location = location.strip()
    if not location:
        raise HTTPException(status_code=400, detail="Location is required.")

    try:
        lat, lon = get_coordinates(location)
        weather = get_weather(lat, lon)
    except ValueError as e:
        msg = str(e)
        if "not configured" in msg.lower():
            raise HTTPException(status_code=500, detail=msg)
        raise HTTPException(status_code=404, detail=msg)
    except Exception:
        raise HTTPException(status_code=502, detail="Unable to fetch weather data.")

    return {
        "location":location,
        "temperature":weather.get("temperature","N/A"),
        "humidity":weather.get("humidity","N/A"),
        "condition":weather.get("condition","Unknown"),
        "advisory":"Monitor crop health during high humidity to prevent fungal diseases."
    }


@app.get("/weather", response_model=WeatherResponse)
def weather_query_api(location: str):
    return weather_api(location)


@app.get("/forecast-risk/{location}", response_model=ForecastRiskResponse)
def forecast_risk_api(location: str, days: int = 3):
    location = location.strip()
    if not location:
        raise HTTPException(status_code=400, detail="Location is required.")
    if days < 1 or days > 7:
        raise HTTPException(status_code=400, detail="Days must be between 1 and 7.")

    try:
        lat, lon = get_coordinates(location)
        forecast = get_forecast_risk(lat, lon, days=days)
    except ValueError as e:
        msg = str(e)
        if "not configured" in msg.lower():
            raise HTTPException(status_code=500, detail=msg)
        raise HTTPException(status_code=404, detail=msg)
    except Exception:
        raise HTTPException(status_code=502, detail="Unable to fetch forecast risk data.")

    return {"location": location, **forecast}


@app.get("/analytics/hotspots/{user_id}", response_model=HotspotAnalyticsResponse)
def hotspots_api(user_id: str):
    if not USER_ID_PATTERN.match(user_id):
        raise HTTPException(status_code=400, detail="Invalid user_id format.")
    try:
        return get_hotspot_analytics(user_id)
    except Exception:
        raise HTTPException(status_code=500, detail="Unable to generate hotspot analytics.")


# ---------------------------------------------------
# LOCATION DETECTION API (REVERSE GEOCODING)
# ---------------------------------------------------

@app.get("/detect-location", response_model=DetectLocationResponse)
def detect_location_api(lat: float, lon: float):
    """Reverse geocoding: Get city name from latitude and longitude"""
    if not (-90 <= lat <= 90):
        raise HTTPException(status_code=400, detail="Latitude must be between -90 and 90.")
    if not (-180 <= lon <= 180):
        raise HTTPException(status_code=400, detail="Longitude must be between -180 and 180.")

    try:
        city = get_city_from_coordinates(lat, lon)
        return {"city": city, "lat": lat, "lon": lon}
    except ValueError as e:
        msg = str(e)
        if "not configured" in msg.lower():
            raise HTTPException(status_code=500, detail=msg)
        raise HTTPException(status_code=404, detail=msg)
    except Exception:
        raise HTTPException(status_code=502, detail="Unable to detect location.")



