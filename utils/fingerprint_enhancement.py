import cv2
import numpy as np
from scipy import ndimage
from skimage import restoration, exposure

def enhance_fingerprint(image_path):
    """
    تحسين وترميم البصمة من مسرح الجريمة
    """
    # قراءة الصورة
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    
    # حفظ نسخة من الصورة الأصلية
    original = img.copy()
    
    # 1. تحسين التباين
    img = enhance_contrast(img)
    
    # 2. إزالة الضوضاء
    img = remove_noise(img)
    
    # 3. تحسين وضوح التلال
    img = enhance_ridges(img)
    
    # 4. ترميم المناطق التالفة
    img = restore_damaged_areas(img)
    
    # 5. تحسين الحواف
    img = enhance_edges(img)
    
    return {
        "original": original,
        "enhanced": img,
        "enhancement_details": {
            "contrast_improvement": calculate_contrast_improvement(original, img),
            "noise_reduction": calculate_noise_reduction(original, img),
            "ridge_clarity": calculate_ridge_clarity(img),
            "restored_areas": calculate_restored_areas(original, img)
        }
    }

def enhance_contrast(img):
    """
    تحسين تباين الصورة
    """
    # تطبيق CLAHE (Contrast Limited Adaptive Histogram Equalization)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    img = clahe.apply(img)
    
    # تحسين التباين العام
    img = exposure.rescale_intensity(img)
    
    return img

def remove_noise(img):
    """
    إزالة الضوضاء من الصورة
    """
    # إزالة الضوضاء باستخدام مرشح غير محلي
    img = cv2.fastNlMeansDenoising(img, None, 10, 7, 21)
    
    # تطبيق مرشح متوسط للتخلص من الضوضاء المتبقية
    img = cv2.medianBlur(img, 3)
    
    return img

def enhance_ridges(img):
    """
    تحسين وضوح التلال
    """
    # تطبيق مرشح Gabor لتحسين التلال
    kernel = cv2.getGaborKernel((21, 21), 8.0, np.pi/4, 10.0, 0.5, 0, ktype=cv2.CV_32F)
    img = cv2.filter2D(img, cv2.CV_8UC3, kernel)
    
    # تحسين الحواف
    img = cv2.Laplacian(img, cv2.CV_64F)
    img = np.uint8(np.absolute(img))
    
    return img

def restore_damaged_areas(img):
    """
    ترميم المناطق التالفة
    """
    # تحويل الصورة إلى ثنائية
    _, binary = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    
    # إيجاد المناطق التالفة
    kernel = np.ones((3,3), np.uint8)
    damaged = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
    
    # ترميم المناطق التالفة
    img = cv2.inpaint(img, damaged, 3, cv2.INPAINT_TELEA)
    
    return img

def enhance_edges(img):
    """
    تحسين الحواف
    """
    # تطبيق مرشح Canny
    edges = cv2.Canny(img, 100, 200)
    
    # دمج الحواف مع الصورة الأصلية
    img = cv2.addWeighted(img, 0.7, edges, 0.3, 0)
    
    return img

def calculate_contrast_improvement(original, enhanced):
    """
    حساب نسبة تحسن التباين
    """
    original_contrast = np.std(original)
    enhanced_contrast = np.std(enhanced)
    return ((enhanced_contrast - original_contrast) / original_contrast) * 100

def calculate_noise_reduction(original, enhanced):
    """
    حساب نسبة تقليل الضوضاء
    """
    original_noise = np.mean(cv2.Laplacian(original, cv2.CV_64F))
    enhanced_noise = np.mean(cv2.Laplacian(enhanced, cv2.CV_64F))
    return ((original_noise - enhanced_noise) / original_noise) * 100

def calculate_ridge_clarity(img):
    """
    حساب وضوح التلال
    """
    edges = cv2.Canny(img, 100, 200)
    return np.sum(edges > 0) / (img.shape[0] * img.shape[1]) * 100

def calculate_restored_areas(original, enhanced):
    """
    حساب نسبة المناطق المرممة
    """
    diff = cv2.absdiff(original, enhanced)
    return np.sum(diff > 30) / (original.shape[0] * original.shape[1]) * 100 