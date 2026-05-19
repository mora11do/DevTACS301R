# Speech-to-Speech Demo

Classroom demo using a tiny Python token server plus a built browser client that follows the lecture demo's Realtime SDK/WebRTC approach.

## Run

1. Create a virtual environment and install `requirements.txt`.
2. In `frontend/`, run `npm install` and `npm run build` if `dist/` is missing or stale.
3. Copy `.env.example` to `.env` and set `OPENAI_API_KEY`.
4. Run `python app.py`.
5. Open `http://127.0.0.1:8000`.
6. Click `Connect` and allow microphone access.
