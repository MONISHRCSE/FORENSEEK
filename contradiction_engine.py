import re

class ContradictionEngine:
    def __init__(self):
        print("Initializing Contradiction Detection Engine...")
        
    def analyze_evidence(self, witness_transcripts, cctv_timeline):
        """
        Dynamically compares witness transcripts against the CCTV timeline.
        Simulates an LLM for the prototype by looking for semantic overlaps/contradictions.
        """
        contradictions = []
        
        # Aggregate all witness statements
        full_statement = " ".join([t.get("text", "") for t in witness_transcripts]).lower()
        
        # Aggregate all CCTV findings
        cctv_subjects = set()
        cctv_events = []
        for event in cctv_timeline:
            # Handle both direct text and raw CCTV JSON tracking structures
            text = event.get("text", "")
            if not text:
                subj = event.get("subject_id", "")
                ent = event.get("entity_type", "")
                text = f"{subj} {ent} detected tracking"
            
            text = text.lower()
            cctv_events.append(text)
            if "subject_1" in text or "person" in text:
                cctv_subjects.add("Subject_1")
                
        # Simulated LLM Rule 1: Denial of presence vs CCTV evidence
        denial_keywords = ["wasn't there", "was not there", "never at the warehouse", "was at home", "nowhere near"]
        cctv_presence = any("detected" in ev or "tracking" in ev for ev in cctv_events)
        
        if cctv_presence:
            for keyword in denial_keywords:
                if keyword in full_statement:
                    contradictions.append({
                        "type": "TIMELINE_CONFLICT",
                        "description": "Witness claims they were not present, but CCTV establishes physical presence at the scene.",
                        "source_1": f"Witness Statement: \"...{keyword}...\"",
                        "source_2": "CCTV Evidence: Subject detected and tracked in camera view.",
                        "severity": "HIGH"
                    })
                    break # Avoid duplicates for this rule
                    
        # Simulated LLM Rule 2: Denial of interaction/overlap
        if "alone" in full_statement or "didn't see anyone" in full_statement or "did not see anyone" in full_statement:
            overlap_detected = any("overlap" in ev or "subject_2" in ev for ev in cctv_events)
            if overlap_detected:
                 contradictions.append({
                    "type": "INTERACTION_CONFLICT",
                    "description": "Witness claims to have been alone, but CCTV shows suspicious overlap with another subject.",
                    "source_1": "Witness Statement: Claims to be alone.",
                    "source_2": "CCTV Evidence: Multiple subjects detected in close proximity.",
                    "severity": "HIGH"
                })

        # If no contradictions found but data exists
        if not contradictions and witness_transcripts and cctv_timeline:
             contradictions.append({
                "type": "VERIFIED",
                "description": "Witness statement appears generally consistent with CCTV timeline. No direct contradictions found.",
                "source_1": "Witness Transcripts",
                "source_2": "CCTV Logs",
                "severity": "LOW"
            })
            
        # If missing data
        if not witness_transcripts or not cctv_timeline:
             contradictions.append({
                "type": "INSUFFICIENT_DATA",
                "description": "Cannot perform cross-analysis. Missing either Witness Transcripts or CCTV Evidence.",
                "source_1": "System",
                "source_2": "System",
                "severity": "LOW"
            })

        return contradictions

if __name__ == "__main__":
    engine = ContradictionEngine()
    print(engine.analyze_evidence([{"text": "I was never at the warehouse"}], [{"text": "Subject_1 detected"}]))
