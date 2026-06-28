import cv2
import torch
import numpy as np
from ultralytics import YOLO

class SceneIntakeEngine:
    def __init__(self, obj_model_path='yolov8n.pt'):
        print("Initializing Scene Intake Engine...")
        # Load YOLOv8 for Object Detection
        self.yolo_model = YOLO(obj_model_path)
        
        # Load MiDaS for Monocular Depth Estimation (3D Reconstruction foundation)
        print("Loading MiDaS depth estimation model...")
        self.midas_model_type = "DPT_Large"     # MiDaS v3 - Large     (highest accuracy, slowest inference speed)
        # self.midas_model_type = "MiDaS_small"  # MiDaS v2.1 - Small   (lowest accuracy, highest inference speed)
        
        self.midas = torch.hub.load("intel-isl/MiDaS", self.midas_model_type)
        self.device = torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu")
        self.midas.to(self.device)
        self.midas.eval()
        
        # Load transforms to resize and normalize the image
        midas_transforms = torch.hub.load("intel-isl/MiDaS", "transforms")
        if self.midas_model_type == "DPT_Large" or self.midas_model_type == "DPT_Hybrid":
            self.transform = midas_transforms.dpt_transform
        else:
            self.transform = midas_transforms.small_transform

    def analyze_scene(self, image_path, output_depth_path=None):
        """
        Analyzes a crime scene image to detect objects and generate a 3D depth map.
        """
        print(f"Analyzing scene: {image_path}")
        img = cv2.imread(image_path)
        if img is None:
            raise ValueError(f"Could not read image at {image_path}")
            
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        
        # 1. Object Detection & Evidence Identification
        results = self.yolo_model(img_rgb)
        
        detected_objects = []
        for r in results:
            boxes = r.boxes
            for box in boxes:
                cls_id = int(box.cls[0])
                conf = float(box.conf[0])
                xyxy = box.xyxy[0].tolist()
                
                label = self.yolo_model.names[cls_id]
                detected_objects.append({
                    "label": label,
                    "confidence": round(conf, 2),
                    "bbox": [round(x, 2) for x in xyxy]
                })
        
        # 2. 3D Scene Reconstruction (Depth Map Generation)
        input_batch = self.transform(img_rgb).to(self.device)
        
        with torch.no_grad():
            prediction = self.midas(input_batch)
            
            prediction = torch.nn.functional.interpolate(
                prediction.unsqueeze(1),
                size=img_rgb.shape[:2],
                mode="bicubic",
                align_corners=False,
            ).squeeze()
            
        depth_map = prediction.cpu().numpy()
        
        # Normalize depth map for visualization
        depth_map_normalized = cv2.normalize(depth_map, None, 0, 255, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_8U)
        depth_colormap = cv2.applyColorMap(depth_map_normalized, cv2.COLORMAP_INFERNO)
        
        if output_depth_path:
            cv2.imwrite(output_depth_path, depth_colormap)
            print(f"Saved depth map (3D reconstruction base) to {output_depth_path}")
            
        # 3. Environmental Context Analysis (Heuristic based on objects)
        environment = "Unknown"
        if any(obj['label'] in ['bed', 'chair', 'sofa', 'tv', 'laptop'] for obj in detected_objects):
            environment = "Indoor Environment"
        elif any(obj['label'] in ['car', 'truck', 'traffic light', 'stop sign'] for obj in detected_objects):
            environment = "Outdoor Environment"
            
        scene_report = {
            "image": image_path,
            "environment_analysis": environment,
            "total_objects_detected": len(detected_objects),
            "evidence_markers": detected_objects,
            "3d_reconstruction_ready": True
        }
        
        return scene_report

if __name__ == "__main__":
    print("Crime Scene Intake Engine Ready.")
    # engine = SceneIntakeEngine()
    # report = engine.analyze_scene("sample_scene.jpg", output_depth_path="scene_depth.png")
    # print(report)
