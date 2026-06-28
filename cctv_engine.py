import cv2
from ultralytics import YOLO
import json
import sys
import os
import numpy as np

class CCTVSurveillanceEngine:
    def __init__(self, model_path='yolov8n.pt'):
        print(f"Loading YOLOv8 model from {model_path}...")
        self.model = YOLO(model_path)
        self.reference_subjects = {} # Map of role -> {'hist': hist, 'track_id': None}
    
    def register_reference_photo(self, photo_path: str, role: str = "VICTIM"):
        """Compute a color histogram from the reference image for fast matching."""
        img = cv2.imread(photo_path)
        if img is None:
            print(f"WARNING: Could not read reference photo for {role}.")
            return
        img_resized = cv2.resize(img, (128, 256))
        hsv = cv2.cvtColor(img_resized, cv2.COLOR_BGR2HSV)
        hist = cv2.calcHist([hsv], [0, 1], None, [50, 60], [0, 180, 0, 256])
        cv2.normalize(hist, hist, alpha=0, beta=1, norm_type=cv2.NORM_MINMAX)
        self.reference_subjects[role.upper()] = {'hist': hist, 'track_id': None}
        print(f"{role} reference photo registered: {photo_path}")

    def _match_subject(self, frame, box, role: str) -> bool:
        """Compare a detected box's colour histogram against the reference. Returns True if match."""
        subject = self.reference_subjects.get(role.upper())
        if subject is None or subject['hist'] is None:
            return False
        x1, y1, x2, y2 = map(int, box)
        # Guard bounds
        x1, y1 = max(0, x1), max(0, y1)
        x2, y2 = min(frame.shape[1], x2), min(frame.shape[0], y2)
        if x2 <= x1 or y2 <= y1:
            return False
        crop = frame[y1:y2, x1:x2]
        if crop.size == 0:
            return False
        crop_resized = cv2.resize(crop, (128, 256))
        hsv_crop = cv2.cvtColor(crop_resized, cv2.COLOR_BGR2HSV)
        hist_crop = cv2.calcHist([hsv_crop], [0, 1], None, [50, 60], [0, 180, 0, 256])
        cv2.normalize(hist_crop, hist_crop, alpha=0, beta=1, norm_type=cv2.NORM_MINMAX)
        score = cv2.compareHist(subject['hist'], hist_crop, cv2.HISTCMP_CORREL)
        return score > 0.55  # Threshold: >0.55 correlation = likely match

    def analyze_video(self, video_path, output_path=None):
        """
        Analyzes a CCTV video to detect and track persons and vehicles.
        Generates movement timelines.
        Victim subject is identified via reference photo histogram matching.
        """
        print(f"Starting analysis for: {video_path}")
        cap = cv2.VideoCapture(video_path)
        
        # Get video properties for timeline calculation and output video
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        out = None
        if output_path:
            # Browsers support WebM (VP80) natively better than raw MP4 from OpenCV
            if output_path.endswith('.webm'):
                fourcc = cv2.VideoWriter_fourcc(*'vp80')
            else:
                fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
            
        frame_count = 0
        timeline_events = []
        frame_skip = 3  # Analyze 1 out of every 3 frames (3x speed boost)
        max_frames = 450 # Increased to cover 15 seconds of video instead of 5
        
        while cap.isOpened():
            success, frame = cap.read()
            if not success or frame_count >= max_frames:
                break
                
            frame_count += 1
            
            # Skip frames to dramatically reduce processing delay
            if frame_count % frame_skip != 0:
                continue
            
            # Run YOLOv8 tracking with ByteTrack/DeepSORT logic built-in
            # classes=[0, 2, 3, 5, 7] correspond to person, car, motorcycle, bus, truck
            # imgsz=480 tells YOLO to infer at a lower internal resolution for extra speed
            results = self.model.track(frame, persist=True, classes=[0, 2, 3, 5, 7], verbose=False, imgsz=480)
            
            # Extract tracking info for timeline generation
            if results[0].boxes.id is not None:
                boxes = results[0].boxes.xyxy.cpu()
                track_ids = results[0].boxes.id.int().cpu().tolist()
                class_ids = results[0].boxes.cls.int().cpu().tolist()
                
                for box, track_id, cls in zip(boxes, track_ids, class_ids):
                    time_in_seconds = frame_count / fps
                    entity_name = self.model.names[cls]

                    # --- SUBJECT IDENTIFICATION ---
                    # If this is a person and reference photos are loaded, try to match
                    role = "unknown"
                    if entity_name == "person":
                        for r, data in self.reference_subjects.items():
                            if data['track_id'] is not None and track_id == data['track_id']:
                                role = r
                                break
                            elif data['track_id'] is None and self._match_subject(frame, box, r):
                                data['track_id'] = track_id
                                role = r
                                print(f"[CCTV Engine] {r} matched to Track ID: {track_id}")
                                break
                        else:
                            role = "suspect_or_bystander"

                    subject_label = role if role in self.reference_subjects else f"Subject_{track_id}"

                    event = {
                        "frame_number": frame_count,
                        "time_offset_sec": round(time_in_seconds, 2),
                        "subject_id": subject_label,
                        "entity_type": entity_name,
                        "role": role,
                        "bbox": box.tolist()
                    }
                    timeline_events.append(event)
            
            # Visualize the tracking results on the frame
            annotated_frame = results[0].plot()
            
            if out:
                out.write(annotated_frame)
                
        cap.release()
        if out:
            out.release()
            print(f"Annotated video saved to: {output_path}")
            
        print(f"Analysis complete. Extracted {len(timeline_events)} timeline data points.")
        return timeline_events

if __name__ == "__main__":
    print("CCTV Camera Intelligence Module Ready.")
    if len(sys.argv) < 2:
        print("Usage: python cctv_engine.py <video_path>")
        sys.exit(1)
        
    video_path = sys.argv[1]
    video_dir = os.path.dirname(video_path)
    if not video_dir:
        video_dir = "."
        
    output_video_path = os.path.join(video_dir, "tracked_" + os.path.basename(video_path))
    output_json_path = os.path.join(video_dir, "cctv_timeline_events.json")
    
    engine = CCTVSurveillanceEngine()
    timeline = engine.analyze_video(video_path, output_path=output_video_path)
    
    with open(output_json_path, 'w') as f:
        json.dump(timeline, f, indent=4)
    print(f"Saved timeline data to {output_json_path}")

