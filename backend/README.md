# StepOne AI - Backend

AI-powered Content & Design Engine backend service.

## Tech Stack

- **Framework**: FastAPI 0.115
- **Database**: MongoDB (via Motor)
- **Cache**: Redis
- **Task Queue**: Celery
- **AI/ML**: YOLO26, Gemini 3.1 Pro, Claude Opus 4.7, FER, CLIP
- **Media Processing**: FFmpeg, OpenCV, Pillow

## Setup

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment variables
cp .env.example .env
# Edit .env with your configuration

# Run development server
python -m app.main
```

## API Documentation

Once running, visit http://localhost:8000/docs for interactive API documentation.
