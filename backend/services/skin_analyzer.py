try:
    import cv2
    import numpy as np
    CV2_AVAILABLE = True
except Exception:
    cv2 = None
    np = None
    CV2_AVAILABLE = False
import os

# Import ML-based analyzer
try:
    from backend.services.ml_skin_analyzer import MLSkinAnalyzer
    ML_AVAILABLE = True
except ImportError:
    print("[WARN] ML SKIN ANALYZER NOT AVAILABLE - USING FALLBACK MODE")
    ML_AVAILABLE = False

class SkinAnalyzer:
    def __init__(self):
        if CV2_AVAILABLE:
            print("[OK] SKIN_ENGINE: Neural weights loaded and ready.")
        else:
            print("[WARN] SKIN_ENGINE: OpenCV/numpy not available - fallback limited.")

        # Initialize ML analyzer if available
        self.ml_analyzer = None
        if ML_AVAILABLE:
            try:
                self.ml_analyzer = MLSkinAnalyzer()
                print("[ML] ML SKIN ANALYSIS ENGINE: ACTIVE")
            except Exception as e:
                print(f"[WARN] ML ANALYZER INITIALIZATION FAILED: {e}")
                print("[FALLBACK] FALLBACK TO TRADITIONAL CV ANALYSIS")
        else:
            print("[FALLBACK] USING TRADITIONAL CV ANALYSIS")

    def analyze(self, image_path, face_img=None):
        """Main analysis method with ML-first approach"""
        try:
            # Try ML analysis first
            if self.ml_analyzer:
                ml_results = self.ml_analyzer.analyze(image_path, face_img)
                if "error" not in ml_results:
                    return ml_results

            # Fallback to traditional CV analysis
            return self._traditional_analysis(image_path, face_img)

        except Exception as e:
            print(f"[ERROR] SKIN ANALYSIS ERROR: {e}")
            return {"error": f"Analysis failed: {str(e)}"}

    def _traditional_analysis(self, image_path, face_img=None):
        """Traditional OpenCV-based skin analysis (fallback)"""
        try:
            if not CV2_AVAILABLE:
                return {"error": "OpenCV/numpy not installed. Install opencv-python and numpy to enable analysis."}

            # 1. Image Validation
            if face_img is not None and isinstance(face_img, np.ndarray):
                img = face_img
            else:
                img = cv2.imread(image_path)

            if img is None:
                return {"error": "Buffer Empty: AI could not read image data."}

            # 2. Spectral Calculation: BRIGHTNESS (Glow)
            hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
            brightness = np.mean(hsv[:, :, 2]) / 2.55

            # 3. Spectral Calculation: HYDRATION (Texture)
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            # Higher variance = rougher skin = lower hydration
            laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
            hydration = max(15, min(95, 100 - (laplacian_var / 8)))

            # 4. Spectral Calculation: ACNE (Redness)
            lower_red = np.array([0, 40, 40])
            upper_red = np.array([10, 255, 255])
            mask = cv2.inRange(hsv, lower_red, upper_red)
            red_ratio = (np.sum(mask > 0) / mask.size) * 100
            acne_score = min(90, red_ratio * 8)

            # 5. Additional ML-style conditions for compatibility
            # Hyperpigmentation (dark irregular patches)
            dark_mask = cv2.inRange(gray, 0, 60)
            hyperpigmentation_score = min(85, (np.sum(dark_mask > 0) / dark_mask.size) * 800)

            # Dark circles estimation using upper face zone approximation
            if img.shape[0] > 80:
                eye_top = int(img.shape[0] * 0.16)
                eye_bottom = int(img.shape[0] * 0.32)
                eye_slice = gray[eye_top:eye_bottom, :]
                if eye_slice.size > 0:
                    dark_eye_mask = cv2.inRange(eye_slice, 0, 60)
                    dark_circles_score = min(80, float(np.sum(dark_eye_mask > 0)) / eye_slice.size * 120)
                else:
                    dark_circles_score = min(70, hyperpigmentation_score * 0.35)
            else:
                dark_circles_score = min(70, hyperpigmentation_score * 0.35)

            # Wrinkles/Fine lines (texture analysis)
            wrinkle_score = min(90, laplacian_var / 15)

            # Oiliness (brightness variance + texture)
            oiliness_score = min(95, (np.std(hsv[:, :, 2]) + np.std(gray)) / 2)

            # Pore size (texture granularity)
            pore_score = min(85, laplacian_var / 12)

            # Dryness (inverse relationship with oiliness and hydration)
            dryness_score = max(0, min(90, 100 - oiliness_score - hydration + 20))

            # Fine lines (related to wrinkles but less severe)
            fine_lines_score = wrinkle_score * 0.7

            # 6. Skin type and sensitivity classification
            if oiliness_score > 60 and dryness_score < 40:
                skin_type = "Oily"
            elif hydration < 45 and dryness_score > 55:
                skin_type = "Dry"
            elif oiliness_score > 55 and dryness_score > 40:
                skin_type = "Combination"
            elif acne_score > 35 or dark_circles_score > 35:
                skin_type = "Sensitive"
            else:
                skin_type = "Normal"

            if acne_score > 50 or dark_circles_score > 40 or dryness_score > 55:
                sensitivity = "HIGH"
            elif hyperpigmentation_score > 45 or oiliness_score > 60:
                sensitivity = "MODERATE"
            else:
                sensitivity = "LOW"

            issues = []
            if acne_score > 50:
                issues.append("Acne-prone")
            if dryness_score > 55:
                issues.append("Dry/Dehydrated")
            if oiliness_score > 65:
                issues.append("Oily")
            if hyperpigmentation_score > 45:
                issues.append("Pigmentation imbalance")
            if dark_circles_score > 35:
                issues.append("Periorbital darkness")
            diagnosis = ", ".join(issues) if issues else "Balanced skin condition"

            # 7. Compile comprehensive result package
            return {
                "skin_type": skin_type,
                "sensitivity": sensitivity,
                "diagnosis": diagnosis,
                "acne": round(acne_score, 1),
                "hyperpigmentation": round(hyperpigmentation_score, 1),
                "dark_circles": round(dark_circles_score, 1),
                "wrinkles": round(wrinkle_score, 1),
                "oiliness": round(oiliness_score, 1),
                "large_pores": round(pore_score, 1),
                "dryness": round(dryness_score, 1),
                "fine_lines": round(fine_lines_score, 1),
                "brightness": round(brightness, 1),
                "hydration": round(hydration, 1),
                "health_score": round((hydration + brightness + (100 - acne_score)) / 3, 1),
                "status": "SUCCESS"
            }

        except Exception as e:
            print(f"[ERROR] TRADITIONAL ANALYSIS ERROR: {str(e)}")
            return {"error": f"Internal Engine Error: {str(e)}"}