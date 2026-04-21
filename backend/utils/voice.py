import base64
import io
import os
import re

from gtts import gTTS
from deep_translator import GoogleTranslator


def _normalize_label(text: str) -> str:
    value = str(text or "").strip()
    value = value.replace("_", " ").replace("  ", " ")
    value = value.replace(" - ", " – ")
    return value


def _build_advisory_script(disease: str, treatment: str) -> str:
    disease_clean = _normalize_label(disease)
    treatment_clean = _normalize_label(treatment)

    if disease_clean.lower() in ["healthy", "healthy crop"]:
        return (
            "Good news. Your crop appears healthy. "
            "Please continue regular irrigation, balanced nutrition, and field monitoring. "
            "Keep checking the leaves every two days for early symptoms."
        )

    return (
        f"We detected {disease_clean}. "
        f"Recommended treatment: {treatment_clean}. "
        "Please apply the treatment at the right dosage and follow safety instructions. "
        "Monitor the crop after application and repeat only if needed."
    )


def _prepare_tts_text(text: str) -> str:
    # Keep sentence rhythm clear so gTTS sounds less abrupt.
    value = re.sub(r"\s+", " ", str(text or "")).strip()
    value = value.replace(";", ". ")
    value = value.replace(":", ". ")
    value = value.replace("..", ".")
    return value


def generate_voice(disease, treatment, language, user_id=None):
    # Ensure supported language code.
    lang = str(language or "en").lower().strip()
    if lang not in {"en", "te", "hi"}:
        lang = "en"

    base_text = _build_advisory_script(disease, treatment)

    # Translate if needed (gTTS expects language codes).
    try:
        if lang != "en":
            translated_text = GoogleTranslator(source="auto", target=lang).translate(base_text)
        else:
            translated_text = base_text
    except Exception:
        translated_text = base_text

    spoken_text = _prepare_tts_text(translated_text)

    # Slightly better accents for a farmer-focused India audience.
    tld_map = {
        "en": "co.in",
        "hi": "co.in",
        "te": "co.in",
    }
    tts = gTTS(text=spoken_text, lang=lang, tld=tld_map.get(lang, "co.in"), slow=False)

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
