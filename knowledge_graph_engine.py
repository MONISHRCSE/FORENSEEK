import json
import re
from datetime import datetime


# ─── ENTITY TYPES & COLORS ───────────────────────────────────────────────────
ENTITY_COLORS = {
    "person":    {"bg": "#1c3a5e", "border": "#58a6ff", "icon": "👤"},
    "suspect":   {"bg": "#3a1c1c", "border": "#f85149", "icon": "🔴"},
    "victim":    {"bg": "#1c3a2a", "border": "#3fb950", "icon": "🟢"},
    "witness":   {"bg": "#2a2a1c", "border": "#d29922", "icon": "🟡"},
    "vehicle":   {"bg": "#2a1c3a", "border": "#bc8cff", "icon": "🚗"},
    "location":  {"bg": "#1c2a3a", "border": "#79c0ff", "icon": "📍"},
    "object":    {"bg": "#1c1c3a", "border": "#ffa657", "icon": "🔪"},
    "event":     {"bg": "#3a1c3a", "border": "#f778ba", "icon": "⚡"},
    "timestamp": {"bg": "#1c3a3a", "border": "#56d364", "icon": "🕐"},
}


class KnowledgeGraphEngine:
    def __init__(self):
        print("Initializing Knowledge Graph Engine...")
        self.nodes = {}   # id -> node dict
        self.edges = []   # list of edge dicts
        self.timeline = []
        self._load_demo_data()

    # ─── DEMO DATA ─────────────────────────────────────────────────────────────
    def _load_demo_data(self):
        """Pre-load a realistic forensic investigation graph for demo."""
        demo_nodes = [
            {"id": "victim_1",    "label": "Victim (John Doe)",     "type": "victim",    "details": "Found at warehouse entrance at 10:38 PM"},
            {"id": "suspect_1",   "label": "Suspect #1 (Unknown)",  "type": "suspect",   "details": "Tracked by CCTV Camera 3 at 10:18 PM"},
            {"id": "witness_1",   "label": "Witness (Mary S.)",     "type": "witness",   "details": "Stated she left at 9 PM – contradicts CCTV"},
            {"id": "vehicle_1",   "label": "Red Motorcycle",        "type": "vehicle",   "details": "Detected near crime scene at 10:24 PM"},
            {"id": "location_1",  "label": "Warehouse Gate",        "type": "location",  "details": "Primary crime scene location"},
            {"id": "location_2",  "label": "Parking Lot B",         "type": "location",  "details": "Vehicle last seen here"},
            {"id": "object_1",    "label": "Mobile Phone",          "type": "object",    "details": "Recovered near victim – cracked screen"},
            {"id": "event_1",     "label": "Gunshot Detected",      "type": "event",     "details": "CCTV audio trigger at 10:31 PM"},
            {"id": "ts_1",        "label": "10:12 PM",              "type": "timestamp", "details": "Victim enters area"},
            {"id": "ts_2",        "label": "10:18 PM",              "type": "timestamp", "details": "Suspect detected on CCTV"},
            {"id": "ts_3",        "label": "10:24 PM",              "type": "timestamp", "details": "Red motorcycle appears"},
            {"id": "ts_4",        "label": "10:31 PM",              "type": "timestamp", "details": "Gunshot detected"},
            {"id": "ts_5",        "label": "10:38 PM",              "type": "timestamp", "details": "Subject exits area"},
        ]
        for n in demo_nodes:
            self.add_node(n["id"], n["label"], n["type"], n["details"])

        demo_edges = [
            {"source": "victim_1",   "target": "location_1",  "rel": "Found At"},
            {"source": "suspect_1",  "target": "location_1",  "rel": "Seen Near"},
            {"source": "suspect_1",  "target": "victim_1",    "rel": "Followed"},
            {"source": "witness_1",  "target": "victim_1",    "rel": "Witnessed"},
            {"source": "witness_1",  "target": "location_1",  "rel": "Located At"},
            {"source": "vehicle_1",  "target": "location_2",  "rel": "Parked At"},
            {"source": "vehicle_1",  "target": "suspect_1",   "rel": "Associated With"},
            {"source": "object_1",   "target": "victim_1",    "rel": "Belongs To"},
            {"source": "event_1",    "target": "location_1",  "rel": "Occurred At"},
            {"source": "ts_1",       "target": "victim_1",    "rel": "Entry Time"},
            {"source": "ts_2",       "target": "suspect_1",   "rel": "Detection Time"},
            {"source": "ts_3",       "target": "vehicle_1",   "rel": "Appearance Time"},
            {"source": "ts_4",       "target": "event_1",     "rel": "Event Time"},
            {"source": "ts_1",       "target": "ts_2",        "rel": "Before"},
            {"source": "ts_2",       "target": "ts_3",        "rel": "Before"},
            {"source": "ts_3",       "target": "ts_4",        "rel": "Before"},
            {"source": "ts_4",       "target": "ts_5",        "rel": "Before"},
        ]
        for e in demo_edges:
            self.add_edge(e["source"], e["target"], e["rel"])

        self.timeline = [
            {"time": "10:12 PM", "event": "Victim enters area", "source": "CCTV", "node_id": "victim_1"},
            {"time": "10:18 PM", "event": "Suspect detected by Camera 3", "source": "CCTV", "node_id": "suspect_1"},
            {"time": "10:24 PM", "event": "Red motorcycle appears near Parking Lot B", "source": "CCTV", "node_id": "vehicle_1"},
            {"time": "10:31 PM", "event": "Gunshot detected (audio trigger)", "source": "CCTV Audio", "node_id": "event_1"},
            {"time": "10:38 PM", "event": "Subject exits area via north gate", "source": "CCTV", "node_id": "suspect_1"},
        ]

    # ─── NODE / EDGE MANAGEMENT ────────────────────────────────────────────────
    def add_node(self, node_id, label, node_type="person", details=""):
        color = ENTITY_COLORS.get(node_type, ENTITY_COLORS["person"])
        self.nodes[node_id] = {
            "id": node_id,
            "label": label,
            "type": node_type,
            "details": details,
            "color": color,
        }

    def add_edge(self, source_id, target_id, relationship):
        self.edges.append({
            "id": f"{source_id}__{target_id}",
            "source": source_id,
            "target": target_id,
            "relationship": relationship,
        })

    # ─── GET GRAPH DATA (Cytoscape.js format) ──────────────────────────────────
    def get_cytoscape_data(self):
        elements = []
        for nid, node in self.nodes.items():
            elements.append({
                "data": {
                    "id": nid,
                    "label": node["label"],
                    "type": node["type"],
                    "details": node["details"],
                    "bg": node["color"]["bg"],
                    "border": node["color"]["border"],
                    "icon": node["color"]["icon"],
                }
            })
        for edge in self.edges:
            elements.append({
                "data": {
                    "id": edge["id"],
                    "source": edge["source"],
                    "target": edge["target"],
                    "label": edge["relationship"],
                }
            })
        return elements

    # ─── CONTRADICTION DETECTION ───────────────────────────────────────────────
    def detect_contradictions(self):
        contradictions = []

        # Check witness vs CCTV timestamps
        for node in self.nodes.values():
            if node["type"] == "witness":
                # Simple rule: if witness node exists and so does CCTV timestamp after 10 PM
                for ts_node in self.nodes.values():
                    if ts_node["type"] == "timestamp" and "PM" in ts_node["label"]:
                        try:
                            hour = int(ts_node["label"].split(":")[0])
                            if hour >= 22 or hour == 10:
                                contradictions.append({
                                    "severity": "HIGH",
                                    "source_a": node["label"],
                                    "source_b": ts_node["label"],
                                    "description": f"{node['label']} statement may conflict with CCTV event at {ts_node['label']}",
                                    "node_ids": [node["id"], ts_node["id"]]
                                })
                        except:
                            pass

        return contradictions[:3]  # Return top 3 for UI

    # ─── INGEST FROM CCTV JSON ────────────────────────────────────────────────
    def ingest_cctv_timeline(self, timeline_json_path):
        try:
            with open(timeline_json_path) as f:
                events = json.load(f)
            for i, ev in enumerate(events[:10]):
                ts_id = f"cctv_ts_{i}"
                node_id = f"cctv_subject_{ev.get('subject_id', i)}"
                ts_label = f"{ev.get('time_offset_sec', 0):.0f}s"
                self.add_node(ts_id, ts_label, "timestamp", f"CCTV frame event")
                self.add_node(node_id, f"Subject {ev.get('subject_id','?')} ({ev.get('entity_type','?')})", "person", "Tracked by CCTV")
                self.add_edge(ts_id, node_id, "Detected At")
        except Exception as e:
            print(f"Could not ingest CCTV timeline: {e}")

    # ─── INGEST FROM VOICE TRANSCRIPT ─────────────────────────────────────────
    def ingest_voice_transcript(self, transcript_text, source_name="Witness"):
        # Simple rule-based entity extraction
        witness_id = f"witness_{len([n for n in self.nodes.values() if n['type']=='witness'])+1}"
        self.add_node(witness_id, f"{source_name} Statement", "witness", transcript_text[:100])

        # Extract time patterns (e.g. "9 PM", "10:30 PM")
        times = re.findall(r'\b\d{1,2}(?::\d{2})?\s*(?:AM|PM|am|pm)\b', transcript_text)
        for t in times:
            tid = f"ts_voice_{t.replace(' ', '').replace(':', '')}"
            self.add_node(tid, t, "timestamp", f"Mentioned in {source_name} statement")
            self.add_edge(witness_id, tid, "Mentioned Time")

        # Extract vehicle keywords
        vehicles = re.findall(r'\b(bike|motorcycle|car|truck|van|vehicle|scooter)\b', transcript_text, re.I)
        for v in set(vehicles):
            vid = f"vehicle_voice_{v.lower()}"
            if vid not in self.nodes:
                self.add_node(vid, v.capitalize(), "vehicle", f"Mentioned in {source_name} statement")
            self.add_edge(witness_id, vid, "Mentioned Vehicle")

    # ─── SEARCH ───────────────────────────────────────────────────────────────
    def search(self, query):
        query = query.lower()
        results = []
        for node in self.nodes.values():
            if query in node["label"].lower() or query in node["type"].lower() or query in node["details"].lower():
                results.append(node)
        return results


if __name__ == "__main__":
    engine = KnowledgeGraphEngine()
    data = engine.get_cytoscape_data()
    print(f"Graph has {len(engine.nodes)} nodes and {len(engine.edges)} edges")
    print("Contradictions:", engine.detect_contradictions())
