import base64
import io
import os
import re

from gtts import gTTS
from deep_translator import GoogleTranslator


def generate_voice(disease, treatment, language, user_id=None):

    # ---------------------------------------
    # Healthy crop message
    # ---------------------------------------
    if disease.lower() in ["healthy", "healthy crop"]:

        text = (
            "Good news! The crop appears healthy. "
            "Continue proper irrigation, fertilization, and regular monitoring "
            "to maintain plant health."
        )

    # ---------------------------------------
    # Disease detected message
    # ---------------------------------------
    else:

        text = (
            f"This plant is affected by {disease}. "
            f"Recommended treatment is {treatment}. "
            "Please apply the treatment as soon as possible."
        )

    # ---------------------------------------
    # Language mapping
    # ---------------------------------------
    language_map = {
        "en": "english",
        "te": "telugu",
        "hi": "hindi"
    }

    # ---------------------------------------
    # Translate if needed
    # ---------------------------------------
    try:
        if language != "en":

            translated_text = GoogleTranslator(
                source="auto",
                target=language_map.get(language, "english")
            ).translate(text)

        else:
            translated_text = text

    except Exception:
        translated_text = text

    # ---------------------------------------
    # Generate in-memory audio data URL (no static file creation)
    # ---------------------------------------
    tts = gTTS(text=translated_text, lang=language)

    # Preferred path: in-memory data URL (no file writes).
    try:
        buffer = io.BytesIO()
        tts.write_to_fp(buffer)
        audio_b64 = base64.b64encode(buffer.getvalue()).decode("ascii")
        return f"data:audio/mpeg;base64,{audio_b64}"
    except Exception:
        # Fallback path: overwrite one stable file (no accumulation).
        os.makedirs("static", exist_ok=True)
        safe_user = re.sub(r"[^a-zA-Z0-9_-]", "_", str(user_id or "global"))
        filename = f"voice_{safe_user}.mp3"
        filepath = os.path.join("static", filename)
        tts.save(filepath)
        return filename
