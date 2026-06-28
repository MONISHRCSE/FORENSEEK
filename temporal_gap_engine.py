import re
from datetime import datetime

class TemporalGapEngine:
    def __init__(self):
        print("Initializing Temporal Gap Reconstruction Engine...")
        
    def _parse_time(self, time_str):
        try:
            return datetime.strptime(time_str, "%I:%M %p")
        except ValueError:
            return None

    def reconstruct_gaps(self, timeline_events, threshold_minutes=5):
        """
        Analyzes a chronological list of events and generates reconstructed gap events
        if the time between two events exceeds the threshold.
        """
        if not timeline_events:
            return []

        # Sort events by time
        sorted_events = []
        for ev in timeline_events:
            t = self._parse_time(ev.get("time", ""))
            if t:
                sorted_events.append({"event": ev, "time_obj": t})
                
        sorted_events.sort(key=lambda x: x["time_obj"])
        
        reconstructed_timeline = []
        
        for i in range(len(sorted_events)):
            reconstructed_timeline.append(sorted_events[i]["event"])
            
            # Check gap with the next event
            if i < len(sorted_events) - 1:
                current_time = sorted_events[i]["time_obj"]
                next_time = sorted_events[i+1]["time_obj"]
                
                diff_minutes = (next_time - current_time).total_seconds() / 60.0
                
                if diff_minutes > threshold_minutes:
                    # Generate a probabilistic reconstruction for the gap
                    gap_start = current_time.strftime("%I:%M %p")
                    gap_end = next_time.strftime("%I:%M %p")
                    
                    # Simulated LLM Inference based on surrounding events
                    prev_desc = sorted_events[i]["event"].get("content", "").lower()
                    next_desc = sorted_events[i+1]["event"].get("content", "").lower()
                    
                    activities = [
                        "Unobserved movement activity likely occurred",
                        "Potential interaction window detected"
                    ]
                    
                    if "victim" in prev_desc and "suspect" in next_desc:
                        activities.insert(0, "Victim movement toward kitchen area inferred")
                        confidence = "67%"
                        reasoning = "Suspect vehicle arrived shortly after victim entered; spatial relationship suggests convergence."
                    elif "vehicle" in prev_desc or "vehicle" in next_desc:
                        activities.insert(0, "Vehicle repositioning or suspect staging")
                        confidence = "58%"
                        reasoning = "Time gap exceeds normal transit time; indicates staging behavior."
                    else:
                        activities.insert(0, "Possible evidence manipulation or concealed movement")
                        confidence = "52%"
                        reasoning = "Extended absence of CCTV or metadata pings indicates deliberate evasion."

                    gap_event = {
                        "is_gap": True,
                        "time": f"{gap_start} - {gap_end}",
                        "content": "⚠ Timeline Gap Detected",
                        "activities": activities,
                        "confidence": confidence,
                        "supporting_evidence": f"Gap of {int(diff_minutes)} minutes between established events.",
                        "related_timestamps": f"{gap_start} to {gap_end}",
                        "reasoning": reasoning
                    }
                    reconstructed_timeline.append(gap_event)
                    
        return reconstructed_timeline
