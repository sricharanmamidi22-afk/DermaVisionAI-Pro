try:
    import cv2
    import numpy as np
    CV2_AVAILABLE = True
except Exception:
    cv2 = None
    np = None
    CV2_AVAILABLE = False

class FaceDetector:
    def __init__(self):
        try:
            import mediapipe as mp
            self.mp_face_detection = mp.solutions.face_detection
            self.detector = self.mp_face_detection.FaceDetection(
                model_selection=1,
                min_detection_confidence=0.5
            )
            print("[OK] AI_SUBSYSTEM: MediaPipe Face Detector Online")
        except Exception as e:
            print(f"[WARN] AI_SUBSYSTEM_OFFLINE: Fallback Mode Active. Error: {e}")
            self.detector = None

    def detect_and_crop(self, image_path):
        if not CV2_AVAILABLE:
            print("[WARN] cv2 not installed - face detection skipped.")
            return None

        image = cv2.imread(image_path)
        if image is None:
            return None
        
        # FAILSAFE: If AI is offline, return full image to keep project moving
        if self.detector is None:
            print("DEBUG: AI Offline - Processing full image frame.")
            return image
            
        try:
            rgb_img = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            results = self.detector.process(rgb_img)
            
            if results is None or not results.detections:
                return image
            
            # Crop ROI
            detection = results.detections[0]
            bbox = detection.location_data.relative_bounding_box
            h, w, _ = image.shape
            x, y, bw, bh = int(bbox.xmin * w), int(bbox.ymin * h), int(bbox.width * w), int(bbox.height * h)
            return image[max(0, y):y+bh, max(0, x):x+bw]
        except:
            return image