import os
import logging
from typing import Any, Dict, List

import requests
from flask import Flask, jsonify, request

app = Flask(__name__)

logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
log = logging.getLogger("landing-wrapper")

LANDING_API_URL = os.getenv("LANDING_API_URL", "https://api.va.landing.ai/v1/ade/parse")
LANDING_API_KEY = os.getenv("LANDING_API_KEY")
LANDING_MODEL = os.getenv("LANDING_MODEL", "")
RETURN_CHUNKS = os.getenv("RETURN_CHUNKS", "false").lower() in {"1", "true", "yes"}
TIMEOUT_SECONDS = float(os.getenv("LANDING_TIMEOUT_SECONDS", "120"))


def _bool_str(value: bool) -> str:
    return "true" if value else "false"


def _build_documents(parse_response: Dict[str, Any]) -> List[Dict[str, Any]]:
    metadata = parse_response.get("metadata") or {}

    if RETURN_CHUNKS:
        documents = []
        for chunk in parse_response.get("chunks", []) or []:
            documents.append(
                {
                    "page_content": chunk.get("markdown") or "",
                    "metadata": {
                        "landing": {
                            "metadata": metadata,
                            "chunk": {
                                "id": chunk.get("id"),
                                "type": chunk.get("type"),
                                "grounding": chunk.get("grounding"),
                            },
                        }
                    },
                }
            )
        return documents

    return [
        {
            "page_content": parse_response.get("markdown") or "",
            "metadata": {"landing": {"metadata": metadata}},
        }
    ]


@app.route("/health", methods=["GET"])
def health() -> Any:
    return jsonify({"status": "ok"})


@app.route("/", methods=["PUT", "POST"])
@app.route("/process", methods=["PUT", "POST"])
def parse_document() -> Any:
    data = request.get_data()
    if not data:
        return jsonify({"error": "Empty request body"}), 400

    filename = request.headers.get("X-Filename", "document")
    content_type = request.headers.get("Content-Type", "application/octet-stream")

    api_key = LANDING_API_KEY
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.lower().startswith("bearer "):
        api_key = auth_header.split(" ", 1)[1].strip()

    if not api_key:
        return jsonify({"error": "Missing API key"}), 401

    headers = {"Authorization": f"Bearer {api_key}"}

    files = {"document": (filename, data, content_type)}
    form = {}

    model = request.args.get("model") or LANDING_MODEL
    if model:
        form["model"] = model

    split = request.args.get("split")
    if split:
        form["split"] = split

    try:
        response = requests.post(
            LANDING_API_URL,
            headers=headers,
            files=files,
            data=form,
            timeout=TIMEOUT_SECONDS,
        )
    except Exception as exc:
        log.exception("LandingAI request failed")
        return jsonify({"error": f"LandingAI request failed: {exc}"}), 502

    if not response.ok:
        return (
            jsonify({"error": f"LandingAI error: {response.status_code}", "details": response.text}),
            502,
        )

    try:
        parse_response = response.json()
    except Exception as exc:
        return jsonify({"error": f"Invalid JSON from LandingAI: {exc}"}), 502

    documents = _build_documents(parse_response)
    return jsonify(documents)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "8080")))
