def get_product_links(disease):

    search_map = {

        "Anthracnose": "mancozeb fungicide anthracnose",
        "Sigatoka": "propiconazole fungicide leaf spot",
        "Cordana": "copper fungicide leaf spot",
        "Pestalotiopsis": "carbendazim fungicide leaf disease",
        "Bacterial_Spot": "copper oxychloride bactericide",
        "Black_Rot": "streptomycin bactericide plant disease",
        "Downy_Mildew": "metalaxyl fungicide downy mildew",
        "Leaf_Spot": "chlorothalonil fungicide leaf spot",
        "Rust": "propiconazole fungicide rust",
        "Whitefly": "neem oil insecticide whitefly",
        "Insect_Pest": "organic insecticide pest control",
        "Flea_Beetle": "imidacloprid insecticide beetle",

        "Healthy": "organic plant fertilizer"
    }

    # extract disease name (remove crop prefix)
    disease_name = disease.split("_", 1)[-1]

    query = search_map.get(disease_name, disease_name + " pesticide")

    amazon = f"https://www.amazon.in/s?k={query.replace(' ','+')}"
    flipkart = f"https://www.flipkart.com/search?q={query.replace(' ','+')}"
    agri = f"https://www.google.com/search?q={query.replace(' ','+')}+agriculture+pesticide"

    return [
        {
            "platform": "Amazon",
            "link": amazon
        },
        {
            "platform": "Flipkart",
            "link": flipkart
        },
        {
            "platform": "Agri Stores",
            "link": agri
        }
    ]