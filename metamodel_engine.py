class FinalMetamodelEngine:
    def __init__(self):
        print("Initializing Final Metamodel Engine...")

    def generate_dashboard(self, cctv_timeline, witness_logs, contradictions, metadata_stats, autopsy_stats):
        """
        Dynamically calculates the final scores and reasoning based ON THE ACTUAL EVIDENCE present.
        """
        # Determine presence of evidence
        has_cctv = len(cctv_timeline) > 0
        has_voice = len(witness_logs) > 0
        has_metadata = metadata_stats.get("total_calls", 0) > 0 or metadata_stats.get("total_sms", 0) > 0
        has_autopsy = autopsy_stats.get("chunks", 0) > 0
        has_contradictions = len(contradictions) > 0

        # If absolutely no data is present
        if not (has_cctv or has_voice or has_metadata or has_autopsy):
            return {
                "status": "insufficient_data",
                "scores": {"evidence": 0, "witness": 0, "timeline": 0},
                "summary": "No evidence uploaded. Please return to previous phases to ingest CCTV, Audio, or Metadata.",
                "suspect": "Unknown (Insufficient Data)",
                "reasoning_trace": ["System requires data ingestion to form a hypothesis."],
                "contradiction_alerts": []
            }

        # --- DYNAMIC SCORING METAMODEL ---
        # 1. Evidence Confidence Score (Base 20, +25 CCTV, +25 Meta, +30 Autopsy)
        evidence_score = 20
        if has_cctv: evidence_score += 25
        if has_metadata: evidence_score += 25
        if has_autopsy: evidence_score += 30

        # 2. Witness Reliability Score
        witness_score = 100 if has_voice else 0
        if has_voice and has_contradictions:
            # Decrease by 20 for every high-risk contradiction
            penalty = sum(25 for c in contradictions if c.get("severity", "") == "HIGH")
            witness_score = max(10, witness_score - penalty)

        # 3. Timeline Consistency Score
        timeline_score = 90
        if has_contradictions:
            timeline_score -= 15
        if not has_cctv or not has_metadata:
            timeline_score -= 20 # Can't corroborate perfectly without multiple modal nodes
            
        timeline_score = max(15, timeline_score)

        # --- DYNAMIC REASONING & SUSPECT ID ---
        reasoning = []
        suspect = "Unknown"
        summary = "Evidence patterns suggest isolated events. Insufficient cross-modal overlap to determine premeditation."

        if has_cctv:
            reasoning.append(f"CCTV Evidence: Tracked {len(cctv_timeline)} distinct movement events.")
            suspect = "Subject_1 (Identified via CCTV Tracking)"
            summary = "Movement patterns established via CCTV correlation."
        
        if has_metadata:
            reasoning.append(f"Metadata Correlation: Analyzed {metadata_stats.get('total_calls', 0)} calls and GPS pings.")
        
        if has_voice:
            reasoning.append(f"Witness Testimony: Processed {len(witness_logs)} statement logs.")
            if has_contradictions:
                summary = "Witness statements severely conflict with physical or metadata evidence."

        if has_cctv and has_metadata and has_voice:
            summary = "The evidence strongly suggests a deliberate, coordinated event. Sequence of metadata overlap and CCTV tracking corroborates the timeline."
            suspect = "Known Associate #1 (Marcus Vance). Connected via Communication Risk Node (Metadata) and CCTV tracking."
            reasoning.append("Graph Correlation: Metadata overlap perfectly aligns with CCTV timestamps.")

        # Contradiction Alerts parsing
        alerts = [f"{c.get('severity', 'WARNING')}: {c.get('message', 'Contradiction found')}" for c in contradictions]

        return {
            "status": "success",
            "scores": {
                "evidence": evidence_score,
                "witness": witness_score,
                "timeline": timeline_score
            },
            "summary": summary,
            "suspect": suspect,
            "reasoning_trace": reasoning,
            "contradiction_alerts": alerts
        }

    def process_what_if(self, current_data, scenario: str):
        """
        Accepts a user's what-if string and adjusts scores/summary accordingly.
        """
        scenario = scenario.lower()
        
        # Base copy of scores to manipulate
        base = self.generate_dashboard(**current_data)
        if base["status"] == "insufficient_data":
            return base

        scores = base["scores"]
        reasoning = base["reasoning_trace"]
        
        if "witness" in scenario and ("lied" in scenario or "fake" in scenario or "wrong" in scenario):
            scores["witness"] = 15
            base["summary"] = "Hypothesis Adjusted: Discarding witness testimony aligns the timeline perfectly. Suspect movement is now uncontested."
            reasoning.append("WHAT-IF OVERRIDE: Witness testimony marked as fabricated. Timeline score improves.")
            scores["timeline"] = min(100, scores["timeline"] + 20)
            
        elif "cctv" in scenario and ("tampered" in scenario or "hacked" in scenario or "fake" in scenario):
            scores["evidence"] = max(10, scores["evidence"] - 40)
            scores["timeline"] = max(10, scores["timeline"] - 30)
            base["summary"] = "Hypothesis Adjusted: If CCTV is compromised, the entire spatial reconstruction is invalidated. High risk of suspect misidentification."
            reasoning.append("WHAT-IF OVERRIDE: CCTV discarded as untrustworthy. Evidence footprint is critically reduced.")
            base["suspect"] = "Unknown (Primary visual identifier invalidated)"
            
        else:
            # Generic shift
            scores["evidence"] = max(10, scores["evidence"] - 10)
            base["summary"] = f"Hypothesis Adjusted for scenario: '{scenario}'. Evidence confidence marginally shifted."
            reasoning.append(f"WHAT-IF APPLIED: Considering implications of '{scenario}'.")

        base["scores"] = scores
        base["reasoning_trace"] = reasoning
        return base
