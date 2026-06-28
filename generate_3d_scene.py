import cv2
import torch
import numpy as np
import json
from ultralytics import YOLO
import sys
import os

class SceneIntakeEngine:
    def __init__(self, obj_model_path='yolov8n.pt'):
        print("Initializing Scene Intake & 3D Reconstruction Engine...")
        self.yolo_model = YOLO(obj_model_path)
        
        print("Loading MiDaS depth estimation model...")
        self.midas_model_type = "DPT_Large"
        self.midas = torch.hub.load("intel-isl/MiDaS", self.midas_model_type)
        self.device = torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu")
        self.midas.to(self.device)
        self.midas.eval()
        
        midas_transforms = torch.hub.load("intel-isl/MiDaS", "transforms")
        self.transform = midas_transforms.dpt_transform

    def generate_point_cloud_ply(self, rgb_image, depth_map, output_file):
        """
        Generates a 3D Point Cloud in PLY format from RGB and Depth images.
        """
        print("Generating 3D Point Cloud (.ply)...")
        h, w = depth_map.shape
        
        # Create a grid of x,y coordinates
        x, y = np.meshgrid(np.arange(w), np.arange(h))
        
        # Flatten the arrays
        x = x.flatten()
        y = y.flatten()
        z = depth_map.flatten()
        
        # Perspective back-projection to form a realistic room geometry
        # Assumed focal length based on image width
        focal_length = w * 1.2
        center_x = w / 2.0
        center_y = h / 2.0
        
        # x3d = (u - cx) * Z / fx
        x3d = (x - center_x) * z / focal_length
        y3d = (y - center_y) * z / focal_length
        z3d = z
        
        # Get colors
        colors = rgb_image.reshape(-1, 3)
        
        # Filter out points
        valid = (z > -10000) # Keep all points
        x3d = x3d[valid]
        y3d = y3d[valid]
        z3d = z3d[valid]
        colors = colors[valid]
        
        num_vertices = len(x3d)
        
        # Write PLY file
        with open(output_file, 'w') as f:
            f.write("ply\n")
            f.write("format ascii 1.0\n")
            f.write(f"element vertex {num_vertices}\n")
            f.write("property float x\n")
            f.write("property float y\n")
            f.write("property float z\n")
            f.write("property uchar red\n")
            f.write("property uchar green\n")
            f.write("property uchar blue\n")
            f.write("end_header\n")
            
            for i in range(num_vertices):
                r, g, b = colors[i]
                # Invert y to match standard coordinate systems, keep z as is
                f.write(f"{x3d[i]} {-y3d[i]} {z3d[i]} {r} {g} {b}\n")
        print(f"3D Point Cloud saved to {output_file}")

    def analyze_scene(self, image_path, output_dir):
        print(f"\nAnalyzing scene: {image_path}")
        img = cv2.imread(image_path)
        if img is None:
            print(f"Could not read image: {image_path}")
            return
            
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        
        # 1. Object Detection
        print("Detecting evidence objects...")
        results = self.yolo_model(img_rgb, verbose=False)
        detected_objects = []
        
        # Create an annotated image for 2D visualization
        img_annotated = img.copy()
        
        for r in results:
            for box in r.boxes:
                cls_id = int(box.cls[0])
                conf = float(box.conf[0])
                xyxy = box.xyxy[0].cpu().numpy().astype(int)
                
                label = self.yolo_model.names[cls_id]
                detected_objects.append({
                    "label": label,
                    "confidence": round(conf, 2),
                    "bbox": xyxy.tolist()
                })
                
                # Draw bounding box
                cv2.rectangle(img_annotated, (xyxy[0], xyxy[1]), (xyxy[2], xyxy[3]), (0, 255, 0), 2)
                cv2.putText(img_annotated, f"{label} {conf:.2f}", (xyxy[0], max(0, xyxy[1]-10)), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        
        cv2.imwrite(f"{output_dir}/evidence_markers.jpg", img_annotated)
        print(f"Saved annotated evidence image to {output_dir}/evidence_markers.jpg")

        # 2. Depth Estimation
        print("Estimating spatial depth...")
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
        
        # Convert disparity to depth (inverse of disparity)
        # We add a small constant to avoid division by zero
        depth = 1.0 / (depth_map + 1e-6)
        
        # Normalize depth to a reasonable scale for a room (e.g., 1 to 10 units)
        depth_min = depth.min()
        depth_max = depth.max()
        
        if depth_max - depth_min > 0:
            normalized_depth = (depth - depth_min) / (depth_max - depth_min)
            # Map to 1.0 (closest) to 15.0 (farthest) to give the room physical depth
            pseudo_depth = (normalized_depth * 14.0) + 1.0
        else:
            pseudo_depth = np.ones_like(depth_map) * 5.0
        
        depth_map_normalized = cv2.normalize(depth_map, None, 0, 255, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_8U)
        depth_colormap = cv2.applyColorMap(depth_map_normalized, cv2.COLORMAP_INFERNO)
        cv2.imwrite(f"{output_dir}/scene_depth.jpg", depth_colormap)
        print(f"Saved depth map to {output_dir}/scene_depth.jpg")
        
        # 3. Generate 3D Point Cloud
        self.generate_point_cloud_ply(img_rgb, pseudo_depth, f"{output_dir}/scene_reconstruction_3d.ply")
        
        # 4. Save JSON Report
        report = {
            "image": image_path,
            "total_objects_detected": len(detected_objects),
            "evidence_markers": detected_objects,
            "reconstruction_files": [
                f"{output_dir}/evidence_markers.jpg",
                f"{output_dir}/scene_depth.jpg",
                f"{output_dir}/scene_reconstruction_3d.ply"
            ]
        }
        with open(f"{output_dir}/scene_analysis_report.json", 'w') as f:
            json.dump(report, f, indent=4)
        print(f"Saved analysis report to {output_dir}/scene_analysis_report.json")

    def analyze_multiple_scenes(self, image_paths, output_dir):
        print(f"\nAnalyzing multiple scenes: {len(image_paths)} images")
        
        all_x3d = []
        all_y3d = []
        all_z3d = []
        all_colors = []
        
        # Process each image and offset them to simulate a room scan
        offset_x = 0
        for idx, img_path in enumerate(image_paths):
            print(f"Processing image {idx+1}/{len(image_paths)}: {img_path}")
            img = cv2.imread(img_path)
            if img is None: continue
            
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            h, w = img_rgb.shape[:2]
            
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
            
            depth = 1.0 / (depth_map + 1e-6)
            depth_min, depth_max = depth.min(), depth.max()
            if depth_max - depth_min > 0:
                normalized_depth = (depth - depth_min) / (depth_max - depth_min)
                pseudo_depth = (normalized_depth * 14.0) + 1.0
            else:
                pseudo_depth = np.ones_like(depth_map) * 5.0
                
            x, y = np.meshgrid(np.arange(w), np.arange(h))
            x = x.flatten()
            y = y.flatten()
            z = pseudo_depth.flatten()
            
            focal_length = w * 1.2
            cx = w / 2.0
            cy = h / 2.0
            
            x3d = (x - cx) * z / focal_length
            y3d = (y - cy) * z / focal_length
            z3d = z
            
            x3d += offset_x
            
            colors = img_rgb.reshape(-1, 3)
            
            stride = 2 # Subsample to keep merged file size manageable
            x3d = x3d[::stride]
            y3d = y3d[::stride]
            z3d = z3d[::stride]
            colors = colors[::stride]
            
            all_x3d.append(x3d)
            all_y3d.append(y3d)
            all_z3d.append(z3d)
            all_colors.append(colors)
            
            offset_x += 15.0 # Spatial shift for next image
            
        if not all_x3d:
            return
            
        final_x = np.concatenate(all_x3d)
        final_y = np.concatenate(all_y3d)
        final_z = np.concatenate(all_z3d)
        final_colors = np.concatenate(all_colors)
        
        output_file = f"{output_dir}/scene_reconstruction_3d.ply"
        num_vertices = len(final_x)
        
        print("Writing merged PLY file...")
        with open(output_file, 'w') as f:
            f.write("ply\n")
            f.write("format ascii 1.0\n")
            f.write(f"element vertex {num_vertices}\n")
            f.write("property float x\n")
            f.write("property float y\n")
            f.write("property float z\n")
            f.write("property uchar red\n")
            f.write("property uchar green\n")
            f.write("property uchar blue\n")
            f.write("end_header\n")
            
            for i in range(num_vertices):
                r, g, b = final_colors[i]
                f.write(f"{final_x[i]} {-final_y[i]} {final_z[i]} {r} {g} {b}\n")
                
        print("Merged 3D Point Cloud saved.")

if __name__ == "__main__":
    engine = SceneIntakeEngine()
    if len(sys.argv) > 1:
        engine.analyze_scene(sys.argv[1], ".")
    else:
        print("Please provide an image path.")
