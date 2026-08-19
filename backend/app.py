from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
FRONTEND_DIR = PROJECT_ROOT / "frontend"

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})


@app.get("/api/health")
def health_check():
    return jsonify({"status": "ok", "service": "health-tracker-api"})


@app.get("/")
def frontend_index():
    return send_from_directory(FRONTEND_DIR, "index.html")


@app.get("/<path:filename>")
def frontend_asset(filename):
    return send_from_directory(FRONTEND_DIR, filename)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
