import cv2
import numpy as np
from skimage import feature, measure
from scipy import ndimage

def analyze_fingerprint(image_path):
    # قراءة الصورة
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    
    # تحسين جودة الصورة
    img = cv2.equalizeHist(img)
    
    # تحليل النقاط المميزة
    minutiae_points = detect_minutiae(img)
    
    # تحليل نمط البصمة
    pattern = analyze_pattern(img)
    
    # تحليل التلال والأخاديد
    ridges_analysis = analyze_ridges(img)
    
    # تجميع النتائج
    analysis_results = {
        "pattern_type": pattern,
        "minutiae_points": minutiae_points,
        "ridges_analysis": ridges_analysis,
        "quality_score": calculate_quality_score(img),
        "statistics": calculate_statistics(minutiae_points, ridges_analysis)
    }
    
    return analysis_results

def detect_minutiae(img):
    # تحسين الصورة
    enhanced = cv2.adaptiveThreshold(img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                   cv2.THRESH_BINARY, 11, 2)
    
    # اكتشاف النقاط المميزة
    corners = cv2.goodFeaturesToTrack(enhanced, 100, 0.01, 10)
    
    # تصنيف النقاط
    minutiae = {
        "ending_points": [],
        "bifurcation_points": [],
        "crossing_points": []
    }
    
    if corners is not None:
        corners = np.int32(corners)
        for corner in corners:
            x, y = corner.ravel()
            # تحليل المنطقة المحيطة بالنقطة
            region = enhanced[max(0, y-2):min(enhanced.shape[0], y+3),
                            max(0, x-2):min(enhanced.shape[1], x+3)]
            if region.size > 0:
                # تصنيف النقطة بناءً على خصائصها
                if np.sum(region) < 255 * region.size / 2:
                    minutiae["ending_points"].append((x, y))
                else:
                    minutiae["bifurcation_points"].append((x, y))
    
    return minutiae

def analyze_pattern(img):
    # تحليل نمط البصمة
    # استخدام تحويل فورييه للكشف عن الأنماط
    f = np.fft.fft2(img)
    fshift = np.fft.fftshift(f)
    magnitude_spectrum = 20 * np.log(np.abs(fshift) + 1)
    
    # تحليل النمط
    if np.std(magnitude_spectrum) > 100:
        return "دوامة (Whorl)"
    elif np.mean(magnitude_spectrum) > 50:
        return "قوس (Arch)"
    else:
        return "حلقة (Loop)"

def analyze_ridges(img):
    # تحليل التلال والأخاديد
    # استخدام خوارزمية Canny للكشف عن الحواف
    edges = cv2.Canny(img, 100, 200)
    
    # تحليل الاتجاهات
    angles = np.arctan2(np.gradient(img)[1], np.gradient(img)[0])
    
    return {
        "ridge_count": np.sum(edges > 0) / 1000,  # تقدير عدد التلال
        "ridge_direction": np.mean(angles),
        "ridge_quality": np.std(angles)
    }

def calculate_quality_score(img):
    # حساب جودة الصورة
    # استخدام مؤشرات مختلفة
    contrast = np.std(img)
    clarity = np.mean(cv2.Laplacian(img, cv2.CV_64F))
    
    # حساب النتيجة النهائية
    score = (contrast * 0.4 + clarity * 0.6) / 255 * 100
    return min(100, max(0, score))

def calculate_statistics(minutiae_points, ridges_analysis):
    # حساب الإحصائيات
    total_minutiae = (len(minutiae_points["ending_points"]) + 
                     len(minutiae_points["bifurcation_points"]) + 
                     len(minutiae_points["crossing_points"]))
    
    return {
        "total_minutiae": total_minutiae,
        "ending_points_count": len(minutiae_points["ending_points"]),
        "bifurcation_points_count": len(minutiae_points["bifurcation_points"]),
        "crossing_points_count": len(minutiae_points["crossing_points"]),
        "ridge_density": ridges_analysis["ridge_count"],
        "pattern_complexity": ridges_analysis["ridge_quality"]
    } 