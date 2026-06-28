from fastapi import FastAPI, UploadFile, File, Form
from typing import List
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import shutil
import os
import uvicorn
import json
from generate_3d_scene import SceneIntakeEngine
from cctv_engine import CCTVSurveillanceEngine
from witness_audio_engine import WitnessAudioEngine
from knowledge_graph_engine import KnowledgeGraphEngine
from metadata_engine import MetadataIntelligenceEngine
from autopsy_nlp_engine import AutopsyNLPEngine
from contradiction_engine import ContradictionEngine
from temporal_gap_engine import TemporalGapEngine
from metamodel_engine import FinalMetamodelEngine

app = FastAPI()

engine = None
cctv_engine_instance = None
voice_engine_instance = None
graph_engine_instance = None
metadata_engine_instance = None
autopsy_engine_instance = None
contradiction_engine_instance = None

@app.on_event("startup")
def load_engine():
    global engine, cctv_engine_instance, voice_engine_instance, graph_engine_instance, metadata_engine_instance, autopsy_engine_instance, contradiction_engine_instance
    # Initialize the heavy AI models once on startup
    engine = SceneIntakeEngine()
    cctv_engine_instance = CCTVSurveillanceEngine()
    voice_engine_instance = WitnessAudioEngine()
    graph_engine_instance = KnowledgeGraphEngine()
    metadata_engine_instance = MetadataIntelligenceEngine()
    autopsy_engine_instance = AutopsyNLPEngine()
    contradiction_engine_instance = ContradictionEngine()
    global temporal_gap_engine_instance
    temporal_gap_engine_instance = TemporalGapEngine()
    global metamodel_engine_instance
    metamodel_engine_instance = FinalMetamodelEngine()

@app.post("/api/upload_scene_multi")
async def upload_scene_multi(files: List[UploadFile] = File(...)):
    # Save the uploaded files temporarily
    upload_dir = "uploads"
    os.makedirs(upload_dir, exist_ok=True)
    
    saved_paths = []
    for file in files:
        file_path = os.path.join(upload_dir, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        saved_paths.append(file_path)
    
    # Process the scenes using the AI engine
    # This will generate a merged scene_reconstruction_3d.ply
    engine.analyze_multiple_scenes(saved_paths, ".")
    
    return {"status": "success", "message": f"Processed {len(files)} images and fused 3D Scene generated."}

@app.post("/api/cctv/reference_photo")
async def upload_reference_photo(photo: UploadFile = File(...), role: str = Form("VICTIM")):
    try:
        upload_dir = "uploads"
        os.makedirs(upload_dir, exist_ok=True)
        file_path = os.path.join(upload_dir, photo.filename)
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(photo.file, buffer)
            
        cctv_engine_instance.register_reference_photo(file_path, role)
        
        return {
            "status": "success",
            "victim_label": role.upper()
        }
    except Exception as e:
        import traceback
        return {"status": "error", "message": str(e), "traceback": traceback.format_exc()}

@app.post("/api/upload_cctv")
async def upload_cctv(file: UploadFile = File(...)):
    # Save the uploaded video temporarily
    upload_dir = "uploads"
    os.makedirs(upload_dir, exist_ok=True)
    file_path = os.path.join(upload_dir, file.filename)
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    output_video_path = os.path.join(upload_dir, "tracked_" + file.filename.split('.')[0] + ".webm")
    output_json_path = os.path.join(upload_dir, "timeline_" + file.filename + ".json")
    
    # Process the video
    timeline = cctv_engine_instance.analyze_video(file_path, output_path=output_video_path)
    cctv_engine_instance.timeline = timeline
    
    with open(output_json_path, 'w') as f:
        json.dump(timeline, f, indent=4)
        
    return {
        "status": "success", 
        "video_url": output_video_path,
        "json_url": output_json_path
    }

@app.post("/api/upload_voice")
async def upload_voice(
    file: UploadFile = File(...),
    target_language: str = Form("English")
):
    # Save the uploaded audio temporarily
    upload_dir = "uploads"
    os.makedirs(upload_dir, exist_ok=True)
    file_path = os.path.join(upload_dir, file.filename)
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    # Process the audio with ElevenLabs STT
    result = voice_engine_instance.analyze_audio(file_path, target_language=target_language)
    
    return {
        "status": "success", 
        "transcript": result["transcript"],
        "entities": result["entities"]
    }

# ─── KNOWLEDGE GRAPH ROUTES ──────────────────────────────────────────────────

@app.get("/api/graph/data")
def get_graph_data():
    return {"elements": graph_engine_instance.get_cytoscape_data()}

@app.get("/api/graph/timeline")
def get_timeline():
    return {"timeline": graph_engine_instance.timeline}

@app.get("/api/graph/contradictions")
def get_contradictions():
    return {"contradictions": graph_engine_instance.detect_contradictions()}

@app.get("/api/graph/search")
def search_graph(q: str = ""):
    results = graph_engine_instance.search(q)
    return {"results": results}

@app.post("/api/graph/ingest_voice")
async def ingest_voice_to_graph(file: UploadFile = File(...)):
    upload_dir = "uploads"
    os.makedirs(upload_dir, exist_ok=True)
    file_path = os.path.join(upload_dir, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    result = voice_engine_instance.analyze_audio(file_path)
    graph_engine_instance.ingest_voice_transcript(result["transcript"])
    return {"status": "ingested", "transcript": result["transcript"]}

@app.post("/api/graph/ingest_cctv")
async def ingest_cctv_to_graph():
    # Try to load the default CCTV timeline
    cctv_json = "CCTV sample/cctv_timeline_events.json"
    graph_engine_instance.ingest_cctv_timeline(cctv_json)
    return {"status": "ingested"}

@app.post("/api/graph/add_node")
async def add_node(request: dict):
    graph_engine_instance.add_node(
        request["id"], request["label"], request.get("type", "person"), request.get("details", "")
    )
    return {"status": "added"}

@app.post("/api/graph/reset")
async def reset_graph():
    graph_engine_instance.nodes = {}
    graph_engine_instance.edges = []
    graph_engine_instance.timeline = []
    graph_engine_instance._load_demo_data()
    return {"status": "reset"}

# ─── METADATA INTELLIGENCE ROUTES ────────────────────────────────────────────

@app.post("/api/metadata/upload")
async def upload_metadata(file: UploadFile = File(...)):
    upload_dir = "uploads"
    os.makedirs(upload_dir, exist_ok=True)
    file_path = os.path.join(upload_dir, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    metadata_engine_instance.parse_file(file_path)
    return {"status": "success", "message": f"Parsed {file.filename} — {len(metadata_engine_instance.timeline)} timeline events extracted."}

@app.get("/api/metadata/timeline")
def get_metadata_timeline():
    return {"timeline": metadata_engine_instance.timeline}

@app.get("/api/metadata/risk_scores")
def get_risk_scores():
    return {"scores": metadata_engine_instance.risk_scores}

@app.get("/api/metadata/insights")
def get_insights():
    return {"insights": metadata_engine_instance.insights}

@app.get("/api/metadata/calls")
def get_calls():
    return {"calls": metadata_engine_instance.call_logs}

@app.get("/api/metadata/sms")
def get_sms():
    return {"sms": metadata_engine_instance.sms_logs}

@app.get("/api/metadata/gps")
def get_gps():
    return {"gps": metadata_engine_instance.gps_logs}

@app.get("/api/metadata/contradictions")
def get_metadata_contradictions():
    return {"contradictions": metadata_engine_instance.detect_contradictions()}

@app.post("/api/metadata/reset")
def reset_metadata():
    metadata_engine_instance.__init__()
    return {"status": "reset"}

# ─── CONTRADICTION CROSS-ANALYSIS ─────────────────────────────────────────

@app.post("/api/contradictions/cross_analyze")
async def cross_analyze(request: dict):
    witness_logs = request.get("witness_logs", [])
    cctv_timeline = getattr(cctv_engine_instance, "timeline", []) if cctv_engine_instance else []
    
    contradictions = contradiction_engine_instance.analyze_evidence(witness_logs, cctv_timeline)
    return {"contradictions": contradictions}

# ─── TIMELINE RECONSTRUCTION ─────────────────────────────────────────

@app.post("/api/timeline/reconstruct")
async def reconstruct_timeline(request: dict):
    try:
        witness_logs = request.get("witness_logs", [])
        cctv_timeline = getattr(cctv_engine_instance, "timeline", []) if cctv_engine_instance else []
        
        if not cctv_timeline:
            return {"timeline": [{"time": "--:--", "content": "No CCTV Video Uploaded", "source": "Upload CCTV footage first to generate the Event Timeline.", "is_gap": False}]}
            
        # Dynamically build the combined timeline list
        events = []
        
        from datetime import datetime, timedelta
        base_time = datetime.strptime("10:12 PM", "%I:%M %p")
        
        # 1. Process CCTV Events (cap at 2 key pivot events)
        for i, cctv in enumerate(cctv_timeline):
            if i > 1:
                break
            event_time = base_time + timedelta(minutes=i * 12)
            subj = str(cctv.get("subject_id", "Unknown"))
            ent = str(cctv.get("entity_type", "subject"))
            action = "Enters Area" if i == 0 else "Detected in Frame"
            events.append({
                "time": event_time.strftime("%I:%M %p"),
                "content": f"{ent.capitalize()} {action}",
                "source": f"CCTV Intelligence: {subj}"
            })
            
        # 2. Process Witness Logs (cap at 1)
        witness_time = base_time + timedelta(minutes=45)
        for i, log in enumerate(witness_logs):
            if i > 0:
                break
            log_str = str(log)[:60] if log else ""
            events.append({
                "time": witness_time.strftime("%I:%M %p"),
                "content": "Witness Transcript Recorded",
                "source": f"Voice Intel: '{log_str}...'"
            })

        # 3. Metadata anchor event
        events.append({
            "time": (base_time + timedelta(minutes=70)).strftime("%I:%M %p"),
            "content": "Metadata Device Pinged Offline",
            "source": "Network Logs"
        })
            
        reconstructed = temporal_gap_engine_instance.reconstruct_gaps(events)
        return {"timeline": reconstructed}
    
    except Exception as e:
        print(f"[Timeline Reconstruct Error]: {e}")
        return {"timeline": [{"time": "--:--", "content": f"Internal Engine Error: {str(e)}", "source": "System", "is_gap": False}]}

# ─── AUTOPSY NLP ROUTES ──────────────────────────────────────────────────────

@app.post("/api/autopsy/upload")
async def upload_autopsy(file: UploadFile = File(...)):
    upload_dir = "uploads"
    os.makedirs(upload_dir, exist_ok=True)
    file_path = os.path.join(upload_dir, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    autopsy_engine_instance.load_file(file_path)
    return {
        "status": "success",
        "title": autopsy_engine_instance.report_title,
        "chunks": len(autopsy_engine_instance.get_chunks()),
        "summary": autopsy_engine_instance.get_summary(),
    }

@app.post("/api/autopsy/ask")
async def autopsy_ask(request: dict):
    question = request.get("question", "")
    if not question:
        return {"error": "No question provided"}
    result = autopsy_engine_instance.ask(question)
    return result

@app.get("/api/autopsy/summary")
def get_autopsy_summary():
    return {
        "title": autopsy_engine_instance.report_title,
        "summary": autopsy_engine_instance.get_summary(),
        "chunk_count": len(autopsy_engine_instance.get_chunks()),
    }

@app.get("/api/autopsy/report_text")
def get_report_text():
    return {"text": autopsy_engine_instance.get_report_text()}

@app.get("/api/autopsy/chat_history")
def get_chat_history():
    return {"history": autopsy_engine_instance.get_chat_history()}

@app.post("/api/autopsy/reset")
def reset_autopsy():
    autopsy_engine_instance.reset()
    return {"status": "reset"}

# ─── FINAL DASHBOARD METAMODEL ROUTES ────────────────────────────────────────

def _get_current_global_state():
    return {
        "cctv_timeline": getattr(cctv_engine_instance, "timeline", []) if cctv_engine_instance else [],
        "witness_logs": [], # Passed from frontend via request
        "contradictions": getattr(contradiction_engine_instance, "last_analysis", []) if contradiction_engine_instance else [],
        "metadata_stats": {
            "total_calls": len(getattr(metadata_engine_instance, "calls_df", [])) if hasattr(metadata_engine_instance, "calls_df") and metadata_engine_instance.calls_df is not None else 0,
            "total_sms": len(getattr(metadata_engine_instance, "sms_df", [])) if hasattr(metadata_engine_instance, "sms_df") and metadata_engine_instance.sms_df is not None else 0,
        },
        "autopsy_stats": {
            "chunks": len(getattr(autopsy_engine_instance, "chunks", [])) if autopsy_engine_instance else 0
        }
    }

@app.post("/api/final/dashboard")
async def generate_final_dashboard(request: dict):
    state = _get_current_global_state()
    state["witness_logs"] = request.get("witness_logs", [])
    
    # Store contradictions in engine for retrieval here
    # If they haven't run contradiction engine, run it now silently to get the state
    if not state["contradictions"] and (state["witness_logs"] or state["cctv_timeline"]):
        state["contradictions"] = contradiction_engine_instance.analyze_evidence(state["witness_logs"], state["cctv_timeline"])
        
    dashboard_data = metamodel_engine_instance.generate_dashboard(**state)
    return dashboard_data

@app.post("/api/final/whatif")
async def run_what_if(request: dict):
    state = _get_current_global_state()
    state["witness_logs"] = request.get("witness_logs", [])
    scenario = request.get("scenario", "")
    
    if not state["contradictions"] and (state["witness_logs"] or state["cctv_timeline"]):
        state["contradictions"] = contradiction_engine_instance.analyze_evidence(state["witness_logs"], state["cctv_timeline"])
        
    whatif_data = metamodel_engine_instance.process_what_if(state, scenario)
    return whatif_data

# Mount static files so the frontend can load index.html, style.css, script.js, and .ply files
app.mount("/", StaticFiles(directory=".", html=True), name="static")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
