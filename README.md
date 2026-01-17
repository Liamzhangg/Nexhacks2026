# Nexhacks2026

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

## Cloudglue utility (backend)

`backend/cloudglue/cloudglue.py` uploads a local video and returns replaceable
object intervals. It expects:

- `CLOUDGLUE_API` in your `.env`
- `backend/cloudglue/input.mp4` as the input video

It writes `backend/cloudglue/replaceable_objects.json` (ignored by git).
