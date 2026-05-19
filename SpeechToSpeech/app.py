import os
from pathlib import Path

import requests
from dotenv import load_dotenv
from flask import Flask, Response, jsonify, send_from_directory


BASE_DIR = Path(__file__).resolve().parent
DIST_DIR = BASE_DIR / "dist"
OPENAI_REALTIME_TOKEN_URL = "https://api.openai.com/v1/realtime/client_secrets"


load_dotenv(BASE_DIR / ".env")

app = Flask(__name__, static_folder=str(DIST_DIR), static_url_path="")


def _token_request_body() -> dict:
    return {
        "session": {
            "type": "realtime",
            "model": "gpt-realtime",
        }
    }


@app.get("/")
def index() -> Response:
    return send_from_directory(DIST_DIR, "index.html")


@app.get("/token")
def create_token() -> Response:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return jsonify({"error": "OPENAI_API_KEY is not set."}), 500

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    body = _token_request_body()

    try:
        upstream = requests.post(
            OPENAI_REALTIME_TOKEN_URL,
            headers=headers,
            json=body,
            timeout=30,
        )
    except requests.RequestException as exc:
        return jsonify({"error": f"Failed to contact OpenAI: {exc}"}), 502

    if not upstream.ok:
        try:
            payload = upstream.json()
        except ValueError:
            payload = {"error": upstream.text}
        return jsonify(payload), upstream.status_code

    try:
        payload = upstream.json()
    except ValueError:
        return jsonify({"error": "OpenAI returned an invalid token response."}), 502

    token = payload.get("value")
    if not token:
        return jsonify({"error": "OpenAI token response did not include a client secret."}), 502

    return jsonify({"client_secret": token})


@app.get("/health")
def health() -> Response:
    return jsonify({"ok": True, "dist_exists": DIST_DIR.exists()})


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8000, debug=False)
