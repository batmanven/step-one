# StepOne AI - Content & Design Engine

AI-powered automated content generation for experiential marketing events.

## Overview

This system transforms raw event media (50-150 mixed images/videos) into platform-ready marketing assets:
- LinkedIn posts with collages
- Instagram reels and stories
- Case study drafts

## Tech Stack

### Backend
- FastAPI (Python)
- MongoDB + Redis
- Celery task queue
- YOLO26, Gemini 3.1 Pro, Claude Opus 4.7
- FFmpeg, OpenCV, Pillow

### Frontend
- React 19 + TypeScript
- Vite
- shadcn/ui
- TailwindCSS
- Zustand

## Project Structure

```
stepone-ai/
├── backend/          # FastAPI backend
├── frontend/         # React frontend
├── IDEA.md          # Architecture document
├── PRD.md           # Product requirements
└── README.md        # This file
```

## Quick Start

### Backend
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python -m app.main
```

### Frontend
```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

## Documentation

- [Implementation Plan](.windsurf/plans/content-design-engine-implementation-8229ce.md)
- [Task Breakdown](.windsurf/plans/task-breakdown-8229ce.md)
- [Architecture](IDEA.md)
- [PRD](PRD.md)

## Team

- Priyansh Narang
- Kaushal Loya

## License

Proprietary - StepOne AI Buildathon 2026
