# FORENSEEK: AI-Powered Forensic Triage & Investigative Intelligence 🔍

<!-- Add your project banner/screenshot here, e.g.: -->
<!-- <img width="1920" height="1080" alt="FORENSEEK Dashboard" src="YOUR_IMAGE_URL_HERE" /> -->

[![Python](https://img.shields.io/badge/Python-FastAPI-009688?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
[![Uvicorn](https://img.shields.io/badge/Uvicorn-ASGI-black?style=for-the-badge)](https://www.uvicorn.org/)
[![Computer Vision](https://img.shields.io/badge/Computer_Vision-CCTV%20%2B%203D-red?style=for-the-badge)](#)
[![NLP](https://img.shields.io/badge/NLP-Autopsy%20%2B%20Witness-blue?style=for-the-badge)](#)
[![ElevenLabs](https://img.shields.io/badge/ElevenLabs-Speech--to--Text-purple?style=for-the-badge)](https://elevenlabs.io/)
[![Cytoscape.js](https://img.shields.io/badge/Cytoscape.js-Knowledge_Graph-green?style=for-the-badge)](https://js.cytoscape.org/)

> *⚠️ Disclaimer:* FORENSEEK is a research/educational prototype designed to assist investigators, not replace forensic experts or due legal process. All AI-generated leads, timelines, and contradiction flags require human verification before any operational use.

---

## Problem Statement

- *Fragmented Evidence Streams:* Modern investigations generate evidence across disconnected formats — CCTV footage, witness audio, autopsy reports, and device metadata — each requiring different expertise to interpret.

- *Manual Correlation is Slow:* Investigators must manually cross-reference timelines, locations, and statements across all these sources, which is time-consuming and prone to human oversight.

- *Hidden Contradictions:* Inconsistencies between a witness's account and CCTV timestamps, or between metadata and testimony, are easy to miss without a system that actively compares every source against every other source.

- *Reconstructing Blind Spots:* Gaps in the evidence timeline (where no source has data) often hide the most important leads, but are difficult to spot manually.

- There is a need for a *unified investigative intelligence layer* that ingests multimodal evidence, builds a connected picture automatically, and flags what doesn't add up — reducing manual triage time and surfacing leads faster.

---

## Project Objective

*FORENSEEK* is an AI-powered forensic triage platform that acts as an automated investigative assistant for law enforcement and forensic teams.

The platform aims to:
- *Unify Multimodal Evidence:* Ingest CCTV, witness audio, autopsy reports, and device metadata into one coherent system.
- *Automated Timeline Construction:* Build a unified chronological timeline from all evidence sources, including detection of unexplained gaps.
- *Relationship Discovery:* Connect entities (suspects, victims, locations) across sources into an interactive knowledge graph.
- *Contradiction Detection:* Automatically cross-check evidence streams against each other and flag logical inconsistencies.

---

## Sustainable Development Goals (SDGs)

### SDG 16: Peace, Justice and Strong Institutions
- *Target 16.3:* Promotes the rule of law and equal access to justice by accelerating investigative triage and reducing the time to surface actionable leads, supporting more effective and accountable institutions.

---

## Proposed Solution

FORENSEEK is built around a set of dedicated *"Engines"* — each one handling a specific domain of forensic analysis — feeding into a central reasoning layer.

### Architecture & Workflow:

<img width="1536" height="1024" alt="ChatGPT Image Jun 28, 2026, 01_00_44 PM" src="https://github.com/user-attachments/assets/2852a50f-cca7-4f81-8b03-06cfbe1495f2" />


*Evidence flows from upload through specialized engines into the central Knowledge Graph and Contradiction Engine*

1. *Upload Phase:* Investigators upload evidence (videos, PDFs, audio, metadata) via the web dashboard.
2. *Processing Phase:* The frontend sends files to dedicated FastAPI endpoints (e.g., `/api/upload_cctv`, `/api/autopsy/upload`). Files are temporarily stored in `uploads/` and routed to the relevant AI engine.
3. *Reasoning Phase:* Extracted entities and timestamps from every engine are sent to the Knowledge Graph Engine and Contradiction Engine for cross-referencing.
4. *Visualization Phase:* The frontend fetches structured JSON (timelines, graph nodes, contradictions) and renders the interactive investigator dashboard.

---

## 🧠 Core AI Modules (The "Engines")

| Engine | File | Function |
|:-------|:-----|:---------|
| *Scene Intake Engine* | `generate_3d_scene.py` | Fuses multiple crime scene images into a 3D scene reconstruction (`.ply`) |
| *CCTV Surveillance Engine* | `cctv_engine.py` | Tracks a reference subject across CCTV footage, generating a structured JSON timeline |
| *Witness Audio Engine* | `witness_audio_engine.py` | Transcribes witness audio and extracts key entities (time, location, vehicles) |
| *Autopsy NLP Engine* | `autopsy_nlp_engine.py` | Extracts cause of death, time-of-death estimates, and injuries; supports Q&A on the report |
| *Metadata Intelligence Engine* | `metadata_engine.py` | Parses call logs, SMS, and GPS pings into a digital timeline with anomaly risk scores |
| *Knowledge Graph Engine* | `knowledge_graph_engine.py` | Connects entities from every source into an interactive Cytoscape graph |
| *Contradiction Engine* | `contradiction_engine.py` | Cross-analyzes evidence streams to flag logical inconsistencies and impossible timelines |
| *Temporal Gap Engine* | `temporal_gap_engine.py` | Merges all events into a unified timeline and reconstructs "blind spots" in the sequence |
| *Metamodel Engine* | `metamodel_engine.py` | Aggregates global state from all engines to power the dashboard and "what-if" scenarios |

---

## 🛠️ Technologies Used

### *Backend*
- *Framework:* Python, FastAPI, served via Uvicorn

### *Frontend*
- *Stack:* Vanilla HTML, CSS, and JavaScript, served statically by the FastAPI backend
- *Visualization:* Cytoscape.js for the interactive knowledge graph

### *AI/ML Integrations*
- *NLP:* Document and report understanding (autopsy reports, Q&A)
- *Computer Vision:* CCTV subject tracking + 3D crime scene reconstruction
- *Speech-to-Text:* ElevenLabs for witness audio transcription and entity extraction

---

## 🎯 Key Features

- ✅ *Multimodal Evidence Ingestion:* CCTV, witness audio, autopsy reports, and device metadata in one platform
- ✅ *3D Scene Reconstruction:* Fuses crime scene images into a navigable `.ply` 3D model
- ✅ *Subject Tracking in CCTV:* Upload a reference photo and track that person across footage automatically
- ✅ *Conversational Autopsy Reports:* Chat with the report directly to ask clinical/forensic questions
- ✅ *Interactive Knowledge Graph:* Visual entity relationships across every evidence source
- ✅ *Automated Contradiction Detection:* Flags impossible timelines and conflicting statements
- ✅ *Temporal Gap Reconstruction:* Surfaces blind spots in the timeline that manual review might miss
- ✅ *"What-If" Scenario Modeling:* Run hypothetical scenarios against the aggregated case state

---

## 📸 Demo / Screenshots

### 1. Case Initialization
Starting a new investigation — setting up the case and preparing it to receive multimodal evidence uploads.
<img width="1919" height="963" alt="Screenshot 2026-05-27 133133" src="https://github.com/user-attachments/assets/af50673a-729d-433d-a284-0a50db42d4c1" />


### 2. CCTV Intelligence
Subject tracking across surveillance footage, with a generated movement timeline.
<img width="1919" height="968" alt="Screenshot 2026-05-27 133327" src="https://github.com/user-attachments/assets/f5b755ef-4f50-46bb-8921-186124e59328" />


### 3. Event Timeline
The unified chronological timeline merging events from all evidence sources, including flagged gaps.
<img width="1919" height="972" alt="Screenshot 2026-05-27 133437" src="https://github.com/user-attachments/assets/7bab92c0-007c-4bfc-a2c8-4cbd279e514a" />


### 4. Contradiction Detection
Automatically flagged inconsistencies between evidence streams — e.g., witness statement vs. CCTV timestamp.
<img width="1919" height="966" alt="Screenshot 2026-05-27 133517" src="https://github.com/user-attachments/assets/867a6ef2-487e-401b-bfe2-1821e6f07d07" />


### 5. Evidence Knowledge Graph
The interactive Cytoscape graph connecting suspects, victims, and locations across every evidence source.
<img width="1919" height="969" alt="Screenshot 2026-05-27 133534" src="https://github.com/user-attachments/assets/ba950ad3-1a98-420a-b83e-5a64a159aea7" />


---

## 💻 Local Development Setup

### Prerequisites
- Python 3.9+
- A virtual environment tool (`venv`)

### 1. Clone the Repository
```bash
git clone https://github.com/MonishRCSE/FORENSEEK.git
cd FORENSEEK
```

### 2. Create and Activate a Virtual Environment
```cmd
python -m venv venv
.\venv\Scripts\activate        # Windows
# source venv/bin/activate     # macOS/Linux
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the Application
```bash
python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
```
The dashboard will be available at `http://127.0.0.1:8000`

---

## 📊 Project Status

| Domain | Status | Notes |
|:-------|:-------|:------|
| *Scene Intake (3D)* | ✅ *Functional* | Crime scene image fusion to `.ply` |
| *CCTV Surveillance* | ✅ *Functional* | Reference-photo subject tracking |
| *Witness Audio Engine* | ✅ *Functional* | Transcription + entity extraction |
| *Autopsy NLP Engine* | ✅ *Functional* | Extraction + conversational Q&A |
| *Metadata Intelligence* | ✅ *Functional* | Digital timeline + anomaly scoring |
| *Knowledge Graph* | ✅ *Active* | Cross-source entity correlation |
| *Contradiction Engine* | ✅ *Active* | Cross-evidence inconsistency flags |
| *Temporal Gap Engine* | ✅ *Active* | Blind-spot reconstruction |

---

<p align="center">
  <strong>Connecting the Dots Investigators Don't Have Time to Find</strong><br>
  Built with ❤️ by Monish
</p>
