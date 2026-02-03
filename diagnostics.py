
import os
import requests
from flask import Flask, jsonify

app = Flask(__name__)

@app.route("/audit/env")
def audit_env():
    keys = ["GEMINI_API_KEY", "SUPABASE_URL", "SUPABASE_KEY", "GHL_API_TOKEN"]
    results = {}
    for k in keys:
        val = os.environ.get(k)
        results[k] = "EXISTS" if val else "MISSING"
    return jsonify(results)

if __name__ == "__main__":
    app.run(port=float(os.environ.get("PORT", 5000)))
