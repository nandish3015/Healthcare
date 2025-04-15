import pytesseract
from PIL import Image
import json
import re
from flask import Flask, request, jsonify
from flask_cors import CORS  # Add this import

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend-backend communication

# Simulated user profile (loaded from JSON or DB in production)
user_profile = {
    "dietary_goals": {"max_calories": 2000, "max_sugar": 50, "allergens": ["peanuts", "gluten"]},
    "diet_type": "low-carb"
}

# Simulated food database (replace with real DB in production)
food_db = {
    "alternative_products": [
        {"name": "Low-Sugar Granola", "calories": 150, "sugar": 5, "allergens": []},
        {"name": "Keto Bread", "calories": 100, "sugar": 2, "allergens": ["nuts"]}
    ]
}

def process_label_image(image_path):
    """Extract text from a nutrition label image using OCR."""
    try:
        image = Image.open(image_path)
        text = pytesseract.image_to_string(image)
        return text
    except Exception as e:
        return f"Error processing image: {str(e)}"

def parse_nutrition_data(text):
    """Parse nutrition data and ingredients from OCR text."""
    nutrition = {"calories": 0, "sugar": 0, "protein": 0, "allergens": []}
    ingredients = []

    # Basic regex patterns for parsing (improve with NLP in production)
    calorie_match = re.search(r"Calories[:\s]*(\d+)", text, re.IGNORECASE)
    sugar_match = re.search(r"Sugars?[:\s]*(\d+\.?\d*)g", text, re.IGNORECASE)
    ingredient_match = re.search(r"Ingredients[:\s]*(.+)", text, re.IGNORECASE)

    if calorie_match:
        nutrition["calories"] = int(calorie_match.group(1))
    if sugar_match:
        nutrition["sugar"] = float(sugar_match.group(1))
    if ingredient_match:
        ingredients = [i.strip().lower() for i in ingredient_match.group(1).split(",")]
        # Check for allergens
        for allergen in user_profile["dietary_goals"]["allergens"]:
            if allergen in ingredients:
                nutrition["allergens"].append(allergen)

    return nutrition, ingredients

def analyze_nutrition(nutrition, ingredients):
    """Analyze nutrition data against user goals."""
    result = {"score": "Green", "warnings": [], "suggestions": []}

    # Check calories
    if nutrition["calories"] > user_profile["dietary_goals"]["max_calories"] / 8:  # Per serving estimate
        result["score"] = "Yellow"
        result["warnings"].append("High calories for your daily goal.")

    # Check sugar
    if nutrition["sugar"] > user_profile["dietary_goals"]["max_sugar"] / 8:
        result["score"] = "Yellow"
        result["warnings"].append("High sugar content.")

    # Check allergens
    if nutrition["allergens"]:
        result["score"] = "Red"
        result["warnings"].append(f"Allergens detected: {', '.join(nutrition['allergens'])}")

    # Suggest alternatives
    for alt in food_db["alternative_products"]:
        if not any(a in alt["allergens"] for a in user_profile["dietary_goals"]["allergens"]):
            result["suggestions"].append(f"Try {alt['name']} (Calories: {alt['calories']}, Sugar: {alt['sugar']}g)")

    return result

@app.route('/')
def index():
    """Serve the frontend HTML file."""
    return app.send_static_file('index.html')  # Ensure index.html is in the static folder

@app.route('/scan', methods=['POST'])
def scan_label():
    """API endpoint to process uploaded label image."""
    if 'image' not in request.files:
        return jsonify({"error": "No image uploaded"}), 400

    image_file = request.files['image']
    image_path = f"temp_{image_file.filename}"
    image_file.save(image_path)

    # Process image
    text = process_label_image(image_path)
    nutrition, ingredients = parse_nutrition_data(text)
    analysis = analyze_nutrition(nutrition, ingredients)

    # Return results
    return jsonify({
        "nutrition": nutrition,
        "ingredients": ingredients,
        "analysis": analysis
    })

if __name__ == "__main__":
    app.run(debug=True)