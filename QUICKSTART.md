# Quick Start Guide

## Backend Setup

1. Navigate to backend directory:
```bash
cd backend
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create `.env` file:
```env
MONGODB_URI=mongodb://localhost:27017/stepone
REDIS_URL=redis://localhost:6379/0
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
AWS_REGION=us-east-1
AWS_S3_BUCKET=your-bucket
GEMINI_API_KEY=your_gemini_key
JWT_SECRET_KEY=dev_secret_key_change_in_production
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
CONFIDENCE_THRESHOLD=0.7
```

5. Start MongoDB (local):
```bash
# Using Docker
docker run -d -p 27017:27017 --name mongodb mongo:7.0

# Or install MongoDB locally
```

6. Start Redis (local):
```bash
# Using Docker
docker run -d -p 6379:6379 --name redis redis:7-alpine
```

7. Start backend server:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend will be available at: **http://localhost:8000**
API docs at: **http://localhost:8000/docs**

## Frontend Setup

1. Navigate to frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start development server:
```bash
npm run dev
```

Frontend will be available at: **http://localhost:5173**

## Download Demo Dataset

For testing without real event data, download demo images and videos:

```bash
# Download 60 demo files (42 images, 18 videos)
python scripts/download_demo_dataset.py --count 60

# Or specify custom count (50-150)
python scripts/download_demo_dataset.py --count 100

# Custom output directory
python scripts/download_demo_dataset.py --count 80 --output my_test_data
```

This downloads free-to-use images from Unsplash and videos from Pexels to a `demo_dataset` folder.

## Using Docker Compose (Recommended)

1. Create `.env` file in project root with all environment variables

2. Start all services:
```bash
docker-compose up -d
```

3. Services:
- Backend: http://localhost:8000
- Frontend: http://localhost:3000
- MongoDB: localhost:27017
- Redis: localhost:6379

## Testing the Connection

1. Start backend (port 8000)
2. Start frontend (port 5173)
3. Open http://localhost:5173
4. Click "+ New Session" to create a session
5. Upload 50-150 demo files from the demo_dataset folder
6. The session should appear in the dashboard with asset count

## Troubleshooting

**CORS errors:**
- Make sure backend is running on port 8000
- Check CORS settings in `backend/app/main.py`

**MongoDB connection errors:**
- Ensure MongoDB is running on port 27017
- Check MONGODB_URI in `.env`

**Frontend not loading sessions:**
- Check browser console for errors
- Verify API URL in `frontend/.env`
- Ensure backend is accessible

**Upload errors:**
- Ensure you're uploading 50-150 files (requirement)
- Check file types (JPEG, PNG, WebP, HEIC, MP4, MOV, AVI, MKV)
- Verify S3 credentials in `.env`
