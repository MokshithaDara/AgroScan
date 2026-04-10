from gtts import gTTS
from deep_translator import GoogleTranslator


def generate_voice(disease, treatment, language):

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

    except:
        translated_text = text

    # ---------------------------------------
    # Save audio (overwrite same file)
    # ---------------------------------------
    filename = "voice.mp3"

    tts = gTTS(text=translated_text, lang=language)
    tts.save(filename)

    return filename