from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from pathlib import Path
from uuid import uuid4

PROJECT_ROOT = Path(__file__).resolve().parent.parent
FRONTEND_DIR = PROJECT_ROOT / "frontend"

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

FOOD_BASELINES = {
    "chicken breast": {"label": "Chicken breast", "calories": 1.65, "protein": 0.31, "carbs": 0.0, "fat": 0.036},
    "brown rice": {"label": "Brown rice", "calories": 1.23, "protein": 0.027, "carbs": 0.256, "fat": 0.01},
    "banana": {"label": "Banana", "calories": 0.89, "protein": 0.011, "carbs": 0.228, "fat": 0.003},
    "greek yogurt": {"label": "Greek yogurt", "calories": 0.73, "protein": 0.1, "carbs": 0.039, "fat": 0.02},
    "avocado": {"label": "Avocado", "calories": 1.6, "protein": 0.02, "carbs": 0.085, "fat": 0.147},
    "oatmeal": {"label": "Oatmeal", "calories": 0.68, "protein": 0.024, "carbs": 0.12, "fat": 0.012},
}

GOALS = {
    "balanced": {"label": "Balanced", "calories": 2000, "protein": 150, "carbs": 220, "fat": 70},
    "fitness": {"label": "Fitness", "calories": 2400, "protein": 190, "carbs": 260, "fat": 80},
}

session_state = {"goal": "balanced", "vibeCheck": False, "meals": []}


def build_state():
    goal = GOALS[session_state["goal"]]
    totals = {"calories": 0, "protein": 0, "carbs": 0, "fat": 0}
    for meal in session_state["meals"]:
        for nutrient in totals:
            totals[nutrient] += meal[nutrient]

    totals = {nutrient: round(value, 1) for nutrient, value in totals.items()}
    progress = {
        nutrient: round((totals[nutrient] / goal[nutrient]) * 100, 1)
        for nutrient in totals
    }
    return {
        "goal": {"id": session_state["goal"], **goal},
        "vibeCheck": session_state["vibeCheck"],
        "totals": totals,
        "targets": {nutrient: goal[nutrient] for nutrient in totals},
        "progress": progress,
        "isOverBudget": totals["calories"] > goal["calories"],
        "meals": session_state["meals"],
    }


def error_response(message, status=400):
    return jsonify({"error": message}), status


@app.get("/api/health")
def health_check():
    return jsonify({"status": "ok", "service": "health-tracker-api"})


@app.get("/api/state")
def get_state():
    return jsonify(build_state())


@app.post("/api/log-meal")
def log_meal():
    payload = request.get_json(silent=True) or {}
    food_key = str(payload.get("food", "")).strip().lower()
    try:
        grams = float(payload.get("grams", 0))
    except (TypeError, ValueError):
        return error_response("Portion must be a number.")

    if food_key not in FOOD_BASELINES:
        return error_response("Choose a food from the available list.")
    if grams <= 0 or grams > 5000:
        return error_response("Portion must be between 1 and 5000 grams.")

    baseline = FOOD_BASELINES[food_key]
    meal = {
        "id": str(uuid4()),
        "food": baseline["label"],
        "foodKey": food_key,
        "grams": round(grams, 1),
    }
    for nutrient in ("calories", "protein", "carbs", "fat"):
        meal[nutrient] = round(baseline[nutrient] * grams, 1)

    session_state["meals"].insert(0, meal)
    return jsonify(build_state()), 201


@app.delete("/api/log-meal/<meal_id>")
def delete_meal(meal_id):
    original_count = len(session_state["meals"])
    session_state["meals"] = [meal for meal in session_state["meals"] if meal["id"] != meal_id]
    if len(session_state["meals"]) == original_count:
        return error_response("Meal not found.", 404)
    return jsonify(build_state())


@app.put("/api/fitness-goal")
def update_goal():
    payload = request.get_json(silent=True) or {}
    goal = str(payload.get("goal", "")).strip().lower()
    if goal not in GOALS:
        return error_response("Goal must be balanced or fitness.")
    session_state["goal"] = goal
    return jsonify(build_state())


@app.put("/api/vibe-check")
def update_vibe_check():
    payload = request.get_json(silent=True) or {}
    value = payload.get("enabled")
    if not isinstance(value, bool):
        return error_response("Vibe Check enabled must be true or false.")
    session_state["vibeCheck"] = value
    return jsonify(build_state())


@app.get("/api/mock-scan")
def mock_scan():
    return jsonify({"food": "greek yogurt", "grams": 170, "confidence": 0.94})


@app.get("/")
def frontend_index():
    return send_from_directory(FRONTEND_DIR, "index.html")


@app.get("/<path:filename>")
def frontend_asset(filename):
    return send_from_directory(FRONTEND_DIR, filename)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
