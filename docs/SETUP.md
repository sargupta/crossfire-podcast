# Setup Guide

## Prerequisites
- **Node.js**: v18+
- **Python**: v3.10+
- **Google Cloud Platform (GCP) Account** with:
    - Vertex AI API Enabled
    - Cloud Text-to-Speech API Enabled
    - Cloud Storage API Enabled

## 1. Backend Setup

The backend handles AI generation and audio synthesis.

```bash
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Environment Variables
Create a `.env.local` file in the root directory:
```bash
GCP_PROJECT_ID=your-project-id
```

### Authentication
Ensure your terminal is authenticated to GCP:
```bash
gcloud auth application-default login
```

### Run Server
```bash
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```
*The API will be available at `http://localhost:8000`.*

---

## 2. Frontend Setup

The frontend is a Next.js application.

```bash
# Install dependencies
npm install

# Run Development Server
npm run dev
```
*The UI will be available at `http://localhost:3000`.*

---

## 3. Google Cloud Storage (GCS) Configuration

The backend automatically attempts to create a bucket named `omni-cast-assets-[project-id]`.

**Manual Step**:
1. Go to GCP Console -> Cloud Storage.
2. Find the bucket `omni-cast-assets-[project-id]`.
3. **Permissions**: Ensure the bucket is **Publicly Readable** if you want audio to play without signed URLs.
    - Grant `Storage Object Viewer` to `allUsers` (Caution: Only for demo/public data).
    - Alternatively, configure CORS on the bucket to allow `localhost:3000`.

## Troubleshooting

- **Audio not playing?** Check the Browser Console. If you see `403 Forbidden` on the audio links, your GCS bucket is not public.
- **"Application Error"?** Check the Backend Terminal. Valid errors usually appear there (e.g., `Quota Exceeded`).
