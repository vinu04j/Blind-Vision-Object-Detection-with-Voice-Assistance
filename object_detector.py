import cv2
import numpy as np
from ultralytics import YOLO
import tensorflow as tf
from tensorflow.keras.applications.mobilenet_v2 import MobileNetV2, preprocess_input, decode_predictions
import threading

class ObjectDetector:
    def __init__(self):
        """Initialize hybrid detector with YOLO + TensorFlow"""
        # YOLO for object detection (localization)
        self.yolo_model = YOLO('yolov8s.pt')
        
        # TensorFlow for better classification
        self.tf_model = MobileNetV2(weights='imagenet')
        self.target_size = (224, 224)
        
        self.frame_skip = 5
        self.frame_count = 0
        
        # Priority classes
        self.priority_classes = {
            'person': 1,
            'dog': 2,
            'cat': 2,
            'car': 3,
            'bicycle': 4,
            'motorcycle': 4,
            'bus': 3,
            'truck': 3
        }
        
    def detect_objects(self, frame):
        """
        Hybrid detection using YOLO + TensorFlow
        
        Args:
            frame: Input video frame
            
        Returns:
            List of detected objects with confidence scores
        """
        try:
            self.frame_count += 1
            
            # Process every Nth frame for performance
            if self.frame_count % self.frame_skip != 0:
                return []
            
            objects = []
            
            # Step 1: Use YOLO for object localization
            yolo_objects = self._yolo_detection(frame)
            
            # Step 2: Refine each detection with TensorFlow
            for yolo_obj in yolo_objects:
                refined_obj = self._refine_with_tensorflow(frame, yolo_obj)
                if refined_obj:
                    objects.append(refined_obj)
            
            # Sort by priority and confidence
            objects.sort(key=lambda x: (x['priority'], -x['confidence']))
            
            return objects[:3]  # Top 3 objects
            
        except Exception as e:
            print(f"Error in hybrid detection: {e}")
            return []
    
    def _yolo_detection(self, frame):
        """Step 1: Detect object locations with YOLO"""
        try:
            results = self.yolo_model(
                frame, 
                verbose=False,
                conf=0.40,
                iou=0.4
            )
            
            yolo_objects = []
            frame_height, frame_width = frame.shape[:2]
            frame_area = frame_height * frame_width
            
            for result in results:
                for box in result.boxes:
                    confidence = float(box.conf[0]) * 100
                    class_id = int(box.cls[0])
                    class_name = result.names[class_id].lower()
                    
                    # Get box coordinates
                    x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                    x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
                    
                    box_width = x2 - x1
                    box_height = y2 - y1
                    box_area = box_width * box_height
                    
                    # Basic filtering
                    if confidence < 40:
                        continue
                    
                    min_size = 30
                    if box_width < min_size or box_height < min_size:
                        continue
                    
                    if box_area > frame_area * 0.95:
                        continue
                    
                    aspect_ratio = box_width / box_height
                    if aspect_ratio > 5 or aspect_ratio < 0.2:
                        continue
                    
                    yolo_objects.append({
                        'name': class_name,
                        'yolo_confidence': confidence,
                        'class_id': class_id,
                        'box': (x1, y1, x2, y2),
                        'area': box_area,
                        'frame_area': frame_area
                    })
            
            return yolo_objects
            
        except Exception as e:
            print(f"YOLO detection error: {e}")
            return []
    
    def _refine_with_tensorflow(self, frame, yolo_obj):
        """Step 2: Refine YOLO detection with TensorFlow classification"""
        try:
            x1, y1, x2, y2 = yolo_obj['box']
            
            # Extract region of interest
            roi = frame[y1:y2, x1:x2]
            
            if roi.size == 0:
                return None
            
            # Resize for TensorFlow
            roi_resized = cv2.resize(roi, self.target_size)
            roi_array = np.array(roi_resized)
            roi_array = np.expand_dims(roi_array, axis=0)
            roi_array = preprocess_input(roi_array)
            
            # Get TensorFlow predictions
            tf_predictions = self.tf_model.predict(roi_array, verbose=0)
            decoded_preds = decode_predictions(tf_predictions, top=3)[0]
            
            # Find best match
            best_match = None
            best_tf_confidence = 0
            
            for label, description, score in decoded_preds:
                tf_conf = float(score) * 100
                
                # Check if it matches YOLO detection
                clean_name = self._clean_name(description)
                
                if tf_conf > best_tf_confidence and tf_conf > 25:
                    best_match = clean_name
                    best_tf_confidence = tf_conf
            
            # Combine YOLO and TensorFlow confidence
            if best_match:
                # Average the confidences
                combined_confidence = (yolo_obj['yolo_confidence'] + best_tf_confidence) / 2
                
                # Filter false positives
                if self._is_false_positive(best_match, combined_confidence):
                    return None
                
                return {
                    'name': best_match.capitalize(),
                    'confidence': combined_confidence,
                    'yolo_confidence': yolo_obj['yolo_confidence'],
                    'tf_confidence': best_tf_confidence,
                    'id': yolo_obj['class_id'],
                    'box': yolo_obj['box'],
                    'area': yolo_obj['area'],
                    'priority': self.priority_classes.get(best_match, 5),
                    'method': 'YOLO+TensorFlow'
                }
            else:
                # Use YOLO detection if TensorFlow doesn't find match
                if yolo_obj['yolo_confidence'] > 60:
                    return {
                        'name': yolo_obj['name'].capitalize(),
                        'confidence': yolo_obj['yolo_confidence'],
                        'yolo_confidence': yolo_obj['yolo_confidence'],
                        'tf_confidence': 0,
                        'id': yolo_obj['class_id'],
                        'box': yolo_obj['box'],
                        'area': yolo_obj['area'],
                        'priority': self.priority_classes.get(yolo_obj['name'], 5),
                        'method': 'YOLO'
                    }
        
        except Exception as e:
            print(f"TensorFlow refinement error: {e}")
            return None
    
    def _clean_name(self, description):
        """Clean object name"""
        name = description.replace('_', ' ').lower()
        
        name_map = {
            'person': 'person',
            'man': 'person',
            'woman': 'person',
            'boy': 'person',
            'girl': 'person',
            'human': 'person',
            'cat': 'cat',
            'dog': 'dog',
            'car': 'car',
            'automobile': 'car',
            'bus': 'bus',
            'truck': 'truck',
            'bicycle': 'bicycle',
            'motorcycle': 'motorcycle',
            'chair': 'chair',
            'table': 'table',
            'laptop': 'laptop',
            'mobile': 'mobile phone',
            'phone': 'mobile phone',
        }
        
        for key, value in name_map.items():
            if key in name:
                return value
        
        return name.capitalize()
    
    def _is_false_positive(self, class_name, confidence):
        """Filter false positives"""
        suspicious_classes = {
            'wig': True,
            'hat': True,
            'backpack': True,
            'handbag': True,
            'umbrella': True,
            'tie': True,
            'frisbee': True,
            'banana': True,
            'sports ball': True,
            'bottle': True,
            'wine glass': True,
            'cup': True,
        }
        
        class_lower = class_name.lower()
        
        if class_lower in suspicious_classes and confidence < 60:
            return True
        
        return False
    
    def get_object_distance(self, box_area, frame_area):
        """Calculate distance"""
        ratio = box_area / frame_area
        
        if ratio > 0.25:
            return "Very Close", 1
        elif ratio > 0.10:
            return "Near", 2
        elif ratio > 0.03:
            return "Far", 3
        else:
            return "Very Far", 4