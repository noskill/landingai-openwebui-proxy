# LandingAI Wrapper for OpenWebUI

Tiny wrapper service that makes LandingAI ADE Parse compatible with OpenWebUI's `ExternalDocumentLoader`.

## What It Does
- Accepts OpenWebUI `PUT`/`POST` to `/process` (or `/`) with raw file bytes.
- Forwards the file to LandingAI ADE Parse (`/v1/ade/parse`).
- Returns a list of `{page_content, metadata}` documents OpenWebUI expects.

## Files
- `app.py`: Flask app.
- `Dockerfile`: Container image.
- `start.sh`: Build + run on Docker network `gitea_default`.
- `requirements.txt`: Python deps.

## Run
```bash
export LANDING_API_KEY="your_key"
export LANDING_API_URL="https://api.va.landing.ai/v1/ade/parse"   # optional (EU: https://api.va.eu-west-1.landing.ai/v1/ade/parse)
export LANDING_MODEL=""                                           # optional
export RETURN_CHUNKS="false"                                      # optional
export LANDING_TIMEOUT_SECONDS="120"                              # optional (LandingAI HTTP timeout)
export GUNICORN_TIMEOUT="600"                                     # optional (wrapper worker timeout)

./start.sh
```

By default it listens on container port `8080` and maps host `8088` -> `8080`.
Change the mapping in `start.sh` if needed.

## OpenWebUI Settings
Set External Document Loader URL to the container **network address** (not host port):
```
http://landing-ai-wrapper:8080/process
```

If you must use a different internal port, update the gunicorn bind and your OpenWebUI URL.

## Notes
- Reuse already-uploaded files via Knowledge Bases to avoid reprocessing.
- If you see `WORKER TIMEOUT`, increase `GUNICORN_TIMEOUT`.
