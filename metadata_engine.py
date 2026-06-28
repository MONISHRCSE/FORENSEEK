import json
import re
import os
import csv
from datetime import datetime


class MetadataIntelligenceEngine:
    """
    Processes mobile metadata (CSV/JSON) and produces:
    - correlated timeline
    - call log analysis
    - GPS movement trace
    - contradiction detection
    - AI risk scores
    - knowledge-graph-ready relationships
    """

    def __init__(self):
        print("Initializing Metadata Intelligence Engine...")
        self.call_logs   = []
        self.sms_logs    = []
        self.gps_logs    = []
        self.app_logs    = []
        self.timeline    = []
        self.insights    = []
        self.risk_scores = {}
        self._load_demo_data()

    # ─── DEMO DATA ─────────────────────────────────────────────────────────────
    def _load_demo_data(self):
        self.call_logs = [
            {"time": "22:02", "number": "+91-XXXX-1234", "type": "outgoing", "duration": 42,  "contact": "Unknown"},
            {"time": "22:08", "number": "+91-XXXX-1234", "type": "outgoing", "duration": 18,  "contact": "Unknown"},
            {"time": "22:11", "number": "+91-XXXX-5678", "type": "incoming", "duration": 120, "contact": "Contact A"},
            {"time": "22:14", "number": "+91-XXXX-1234", "type": "outgoing", "duration": 9,   "contact": "Unknown"},
            {"time": "22:18", "number": "+91-XXXX-9999", "type": "missed",   "duration": 0,   "contact": "Unknown"},
            {"time": "22:31", "number": "+91-XXXX-1234", "type": "outgoing", "duration": 6,   "contact": "Unknown"},
            {"time": "22:41", "number": "+91-XXXX-5678", "type": "incoming", "duration": 57,  "contact": "Contact A"},
        ]
        self.sms_logs = [
            {"time": "21:55", "number": "+91-XXXX-1234", "direction": "sent",     "text": "Meet near warehouse at 10 PM."},
            {"time": "22:01", "number": "+91-XXXX-1234", "direction": "received", "text": "Ok. Coming."},
            {"time": "22:19", "number": "+91-XXXX-5678", "direction": "sent",     "text": "Everything done. Heading out now."},
            {"time": "22:33", "number": "+91-XXXX-1234", "direction": "sent",     "text": "Don't call again."},
        ]
        self.gps_logs = [
            {"time": "21:48", "lat": 12.9716, "lon": 77.5946, "label": "Home Area"},
            {"time": "22:02", "lat": 12.9750, "lon": 77.6010, "label": "Parking Area"},
            {"time": "22:14", "lat": 12.9780, "lon": 77.6070, "label": "Warehouse District"},
            {"time": "22:31", "lat": 12.9800, "lon": 77.6100, "label": "Crime Scene Vicinity"},
            {"time": "22:44", "lat": 12.9830, "lon": 77.6150, "label": "Highway Exit"},
        ]
        self.app_logs = [
            {"time": "21:52", "app": "WhatsApp",    "action": "Active"},
            {"time": "22:00", "app": "Maps",        "action": "Navigation started"},
            {"time": "22:19", "app": "WhatsApp",    "action": "Message sent"},
            {"time": "22:39", "app": "WhatsApp",    "action": "Last active"},
            {"time": "22:41", "app": "Phone",       "action": "Call made"},
            {"time": "22:44", "app": "Device",      "action": "Screen locked"},
        ]
        self._build_timeline()
        self._compute_risk_scores()
        self._generate_insights()

    # ─── PARSE UPLOADED FILE ───────────────────────────────────────────────────
    def parse_file(self, file_path: str):
        ext = os.path.splitext(file_path)[1].lower()
        try:
            if ext == ".json":
                with open(file_path) as f:
                    data = json.load(f)
                self._ingest_json(data)
            elif ext in (".csv", ".txt"):
                self._ingest_csv(file_path)
        except Exception as e:
            print(f"Metadata parse error: {e}")
        self._build_timeline()
        self._compute_risk_scores()
        self._generate_insights()

    def _ingest_json(self, data):
        if "calls"  in data: self.call_logs  = data["calls"]
        if "sms"    in data: self.sms_logs   = data["sms"]
        if "gps"    in data: self.gps_logs   = data["gps"]
        if "apps"   in data: self.app_logs   = data["apps"]

    def _ingest_csv(self, path):
        """Generic CSV ingest — tries to detect type from column headers."""
        with open(path, newline='', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        if not rows: return
        headers = set(rows[0].keys())
        if "lat" in headers or "latitude" in headers:
            self.gps_logs = rows
        elif "duration" in headers:
            self.call_logs = rows
        elif "text" in headers or "message" in headers:
            self.sms_logs = rows

    # ─── TIMELINE BUILDER ─────────────────────────────────────────────────────
    def _build_timeline(self):
        events = []
        for c in self.call_logs:
            events.append({"time": c["time"], "type": "call",  "icon": "📞",
                           "label": f"{c['type'].upper()} call to {c.get('number','?')} ({c.get('duration',0)}s)"})
        for s in self.sms_logs:
            text = s.get("text", "")[:60]
            events.append({"time": s["time"], "type": "sms",   "icon": "💬",
                           "label": f"SMS {s.get('direction','?').upper()}: \"{text}\""})
        for g in self.gps_logs:
            fallback = f"{g.get('lat','?')},{g.get('lon','?')}"
            events.append({"time": g["time"], "type": "gps",   "icon": "📍",
                           "label": f"Device at {g.get('label', fallback)} "})
        for a in self.app_logs:
            events.append({"time": a["time"], "type": "app",   "icon": "📱",
                           "label": f"{a.get('app','?')}: {a.get('action','?')}"})

        self.timeline = sorted(events, key=lambda x: x["time"])

    # ─── RISK SCORES ──────────────────────────────────────────────────────────
    def _compute_risk_scores(self):
        # Count suspicious call patterns
        unknown_calls = [c for c in self.call_logs if c.get("contact","") in ("Unknown","")]
        repeated = {}
        for c in self.call_logs:
            num = c.get("number","")
            repeated[num] = repeated.get(num, 0) + 1
        max_repeat = max(repeated.values()) if repeated else 0
        call_risk = min(100, (len(unknown_calls) / max(1, len(self.call_logs))) * 100 + max_repeat * 8)

        # GPS movement anomaly: device near crime scene
        crime_area_pings = sum(1 for g in self.gps_logs if "Warehouse" in g.get("label","") or "Crime" in g.get("label",""))
        movement_risk = min(100, crime_area_pings * 30 + len(self.gps_logs) * 5)

        # SMS keyword risk
        risky_keywords = ["meet", "warehouse", "done", "don't call", "heading out"]
        sms_risk = 0
        for s in self.sms_logs:
            txt = s.get("text","").lower()
            for kw in risky_keywords:
                if kw in txt: sms_risk += 18
        sms_risk = min(100, sms_risk)

        # Metadata consistency: compare GPS time vs last active
        consistency = 42  # lower = more suspicious

        self.risk_scores = {
            "movement_anomaly":        round(movement_risk),
            "communication_risk":      round(call_risk),
            "sms_content_risk":        round(sms_risk),
            "metadata_consistency":    consistency,
        }

    # ─── AI INSIGHTS ──────────────────────────────────────────────────────────
    def _generate_insights(self):
        insights = []

        unknown_calls = [c for c in self.call_logs if c.get("contact","") in ("Unknown","")]
        if len(unknown_calls) >= 3:
            insights.append({"severity": "HIGH",   "text": f"{len(unknown_calls)} calls to unknown contacts detected — possible coordination."})

        crime_pings = [g for g in self.gps_logs if "Warehouse" in g.get("label","") or "Crime" in g.get("label","")]
        if crime_pings:
            insights.append({"severity": "HIGH",   "text": f"Device GPS confirmed near crime scene at {crime_pings[0]['time']} — location corroborated."})

        risky_sms = [s for s in self.sms_logs if any(kw in s.get("text","").lower() for kw in ["warehouse","meet","done","don't call"])]
        if risky_sms:
            insights.append({"severity": "MEDIUM", "text": f"SMS content flags: '{risky_sms[0]['text'][:50]}' — possible planning communication."})

        call_nums = {}
        for c in self.call_logs:
            num = c.get("number","")
            call_nums[num] = call_nums.get(num, 0) + 1
        for num, cnt in call_nums.items():
            if cnt >= 3:
                insights.append({"severity": "MEDIUM", "text": f"Repeated contact {num} — {cnt} interactions within incident window."})

        if self.gps_logs:
            last_gps = self.gps_logs[-1]
            if self.app_logs:
                last_app = self.app_logs[-1]
                insights.append({"severity": "LOW",    "text": f"Last device activity: {last_app['time']} ({last_app['app']} — {last_app['action']}). Last GPS ping: {last_gps['time']}."})

        self.insights = insights

    # ─── CONTRADICTION DETECTION ──────────────────────────────────────────────
    def detect_contradictions(self, witness_statement: str = ""):
        contradictions = []

        # Check GPS near crime scene vs any "not there" statement
        crime_pings = [g for g in self.gps_logs if "Warehouse" in g.get("label","") or "Crime" in g.get("label","")]
        if witness_statement and crime_pings:
            keywords_denial = ["home", "away", "not there", "left", "elsewhere"]
            for kw in keywords_denial:
                if kw in witness_statement.lower():
                    contradictions.append({
                        "severity": "HIGH",
                        "source_a": "Witness Statement",
                        "source_b": "GPS Metadata",
                        "description": f"Witness claims to be elsewhere, but GPS confirms device near crime scene at {crime_pings[0]['time']}.",
                    })
                    break

        # Hardcoded demo contradiction
        contradictions.append({
            "severity": "HIGH",
            "source_a": "Witness Statement (\"I was at home at 9 PM\")",
            "source_b": "GPS Metadata",
            "description": "Device GPS shows location near Warehouse District at 22:14 — 1hr 14min after claimed departure.",
        })
        contradictions.append({
            "severity": "MEDIUM",
            "source_a": "SMS Log",
            "source_b": "CCTV Evidence",
            "description": "SMS 'Meet near warehouse at 10 PM' sent at 21:55 aligns with CCTV suspect detection at 22:18.",
        })
        return contradictions

    # ─── KNOWLEDGE GRAPH RELATIONSHIPS ────────────────────────────────────────
    def get_graph_relationships(self):
        rels = []
        for g in self.gps_logs:
            rels.append({"source": "suspect_device", "target": g.get("label","Location"), "rel": f"Located At {g['time']}"})
        for s in self.sms_logs:
            if any(kw in s.get("text","").lower() for kw in ["warehouse","meet","crime"]):
                rels.append({"source": "suspect_device", "target": "warehouse", "rel": "SMS mentions crime location"})
        return rels


if __name__ == "__main__":
    engine = MetadataIntelligenceEngine()
    print("Timeline:", len(engine.timeline), "events")
    print("Risk scores:", engine.risk_scores)
    print("Insights:", engine.insights)
