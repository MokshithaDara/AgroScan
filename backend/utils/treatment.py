def get_treatment(disease):

    # remove crop name (Banana – Moko → Moko)
    if "–" in disease:
        disease = disease.split("–")[1].strip()

    # convert spaces to underscores to match dictionary keys
    disease = disease.replace(" ", "_")

    treatments = {

        "Yellow_and_Black_Sigatoka":
        "Apply systemic fungicides such as propiconazole or triazole sprays.",

        "Cordana":
        "Remove infected leaves and apply copper fungicide spray.",

        "Pestalotiopsis":
        "Improve field sanitation and spray carbendazim or mancozeb fungicide.",

        "Sigatoka":
        "Apply systemic fungicides like propiconazole.",

        "Yellowish":
        "Apply balanced fertilizers including nitrogen and micronutrients.",

        "Anthracnose":
        "Remove infected fruits and spray fungicides such as mancozeb.",

        "Leaf_Curl":
        "Control whiteflies using neem oil or imidacloprid.",

        "Mosaic_Virus":
        "Remove infected plants and control insect vectors.",

        "Nutrition_Deficiency":
        "Apply balanced NPK fertilizer.",

        "Whitefly":
        "Use neem oil spray or imidacloprid.",

        "Black_Rot":
        "Apply copper-based bactericides.",

        "Early_Leaf_Spot":
        "Apply fungicides such as mancozeb.",

        "Late_Leaf_Spot":
        "Apply carbendazim fungicide.",

        "Rust":
        "Use rust control fungicides.",

        "Downy_Mildew":
        "Apply metalaxyl fungicide.",

        "Flea_Beetle":
        "Apply neem oil spray.",

        "Insect_Pest":
        "Use biological pest control.",

        "Bacterial_Spot":
        "Apply copper oxychloride spray.",

        "Moko":
        "Remove infected plants immediately and disinfect tools to prevent spread.",

        "Panama":
        "Use disease resistant banana varieties and improve soil drainage.",

        "Bract_Mosaic_Virus":
        "Control aphids and remove infected plants to stop virus spread.",

        "Downey_Mildew":
        "Apply metalaxyl fungicide and maintain proper field ventilation."
    }

    return treatments.get(disease, "No treatment information available.")