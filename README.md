# Nexhacks2026 project --- ADaptiv

Frontend (Next.js) + backend (Flask) for a video + image prompt interface.

## Structure

```
frontend/   # Next.js app
backend/    # Flask API + prompt logic
```

## Development

Frontend:

```
cd frontend
npm install
npm run dev
```

Backend:

```
cd backend
pip install -r requirements.txt
python main.py
```

## Backend API

The Flask server listens on `http://localhost:8000` by default and exposes three endpoints:

### `GET /health`
- Returns `200` with `{"status":"healthy"}` when the API is up.
- `500` on internal errors.

### `POST /analyze`
- Targeted by the frontend “Process items” button.
- Request: `multipart/form-data` with
  - `video`: required video file (`mp4`, `avi`, `mov`, `mkv`).
  - `image`: required reference image (`png`, `jpg`, `jpeg`, `webp`).
  - `text`: optional textual instructions/prompts.
- Response: binary stream of the generated video (`Content-Type` inferred from the file). The Gemini summary is echoed in the `X-Generated-Text` header when available. Errors return JSON `{"error": "..."}`
  with status `400` (bad input) or `500` (processing failure).

Example:
```bash
curl -o output.mp4 \
  -H "Accept: video/mp4" \
  -F "video=@/path/input.mp4" \
  -F "image=@/path/reference.jpg" \
  -F "text=Swap the soda can for sparkling water" \
  http://localhost:8000/analyze
```

### `POST /process-video`
- Same payload as `/analyze`.
- Response JSON:
  ```json
  {
    "video": "<base64-encoded binary>",
    "text": "<Gemini narrative>",
    "filename": "processed_<uuid>.mp4"
  }
  ```
- Errors mirror `/analyze` (`400`/`500` with `{"error": "..."}`).

Temporary uploads and generated outputs are deleted automatically once the response is sent, so callers should persist the response locally if needed.

## Cloudglue utility (backend)

`backend/cloudglue/cloudglue.py` uploads a local video and returns replaceable
object intervals. It expects:

- `CLOUDGLUE_API` in your `.env`
- `backend/cloudglue/input.mp4` as the input video

It writes `backend/cloudglue/replaceable_objects.json` (ignored by git).
