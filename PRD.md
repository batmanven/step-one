# Product Requirements Document (PRD) and System Design Blueprint

## 1. Project Meta Information

**Project Name:** Automated Content & Design Engine  
**Target Event:** StepOne AI Engine Buildathon  
**Team Name:** Charizard  
**Team Members:** Priyansh Narang, Kaushal Loya

**Objective:**  
Design and deploy a multi-agent system that transforms raw experiential marketing media (50-150 mixed items) into platform-ready marketing assets without manual human intervention.

---

## 2. Product Requirements

### Functional Requirements

**Data Ingestion:**  
The engine must automatically ingest raw event datasets consisting of mixed formats and orientations without manual reconfiguration.

**Intelligent Selection Logic:**  
The system must evaluate assets mathematically based on semantic relevance (brand visibility, room energy) and aesthetic quality, documenting the rationale behind each selection.

**Platform-Specific Outputs:**

- **LinkedIn:** Generate a cohesive 4-6 image collage with context-aware, professional copy reflecting the viewpoint of an event attendee.
- **Instagram Reel:** Output a 30-60 second highlight video, automatically extracting peak moments from raw footage.
- **Instagram Stories:** Automatically generate a 3-4 frame sequential vertical narrative, adapting horizontal photos non-destructively.
- **Case Study:** Draft a structured, post-ready document mapping the overall event narrative and metrics.

**Quality Assurance (QA) Layer:**  
The system must actively flag low-confidence outputs for human review instead of forcing incorrect assets (e.g., destructive crops or hallucinated text) into the final pipeline.

---

### Non-Functional Requirements

**Robustness:**  
Zero-shot adaptability across completely unseen datasets.

**Scalability:**  
Backend must efficiently process high-resolution media payloads without timeout failures.

**Transparency:**  
The demonstration must feature live telemetry exposing the AI's internal operations (saliency maps, confidence score tracking).

---

## 3. System Design and Technical Architecture

The architecture operates on a decoupled client-server model, ensuring a frictionless live demonstration while delegating heavy computational loads to a Python-native environment.

---

### Frontend (User Interface & Telemetry)

**Framework:** React (Standalone SPA)  
Selected over Next.js as SEO is irrelevant for an authenticated hackathon dashboard, prioritizing a lightweight, highly interactive live telemetry view.

**Function:**  
Hosts the dataset ingestion portal and the real-time "Mission Control" visualization, displaying live aesthetic scoring, bounding boxes, and final categorized outputs.

---

### Backend (Processing & Orchestration)

**API Layer:** FastAPI (Python)  
Ideal for asynchronous, high-speed routing of media processing and API calls.

**Agent Orchestration:** LangGraph  
This framework constructs the critical self-correcting AI loop (Reflexion), allowing the agent to evaluate its own outputs, retry failing logic, and trigger the QA "flag" mechanism if confidence scores remain below thresholds.

**Database:** MongoDB  
Used for logging session metadata, confidence scores, and asset URIs.

---

### Artificial Intelligence & Machine Learning Layer

**Multimodal Reasoning:** Gemini 3.1 Pro  
Integrated for its exceptional context window, allowing it to process multiple selected images simultaneously to draft visually grounded copy for LinkedIn, Instagram, and the Case Study.

**Object Detection:** YOLO26  
Deployed specifically with the new MuSGD optimizer, which delivers up to 43% faster CPU inference. This guarantees real-time brand logo and stage detection during the demo without heavy cloud GPU reliance.

**Aesthetic Evaluation:**  
Fine-Grained Image Aesthetic Assessment (FG-IAA) models to quantify lighting, noise, and compositional flow programmatically.

---

### Media Transformation Layer

**Video Processing:**  
FFmpeg wrappers utilized for initial video transcoding and final reel concatenation.

**Image Saliency & Cropping:**  
OpenCV combined with Smartcrop.js (via Python port). These algorithms generate topological heatmaps to safely execute 9:16 vertical aspect ratio crops without severing faces or critical text.

**Collage Generation:**  
Python Pillow (PIL) library programmatically executes the bin-packing logic required to stitch the 4-6 image grids for LinkedIn.

---

### Development Environment

**Coding Assistant:** OpenCode  
A terminal-native AI coding agent featuring dual "build" and "plan" agents, providing multi-model support for rapid, autonomous hackathon prototyping.
