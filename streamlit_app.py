import streamlit as st
import os
import tempfile
from datetime import datetime
import uuid
from werkzeug.utils import secure_filename
from utils.preprocess import preprocess_fingerprint
from utils.extract_features import extract_features
from utils.match_fingerprint import match_fingerprint
from utils.fingerprint_analysis import analyze_fingerprint
from utils.fingerprint_enhancement import enhance_fingerprint

# Configure page
st.set_page_config(
    page_title="Fingerprint Matching System",
    page_icon="👆",
    layout="wide"
)

# Create temporary directory
TEMP_DIR = tempfile.mkdtemp()

# Constants
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'tif', 'tiff'}
MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_temp_file(uploaded_file):
    """حفظ الملف مؤقتاً وإرجاع مساره"""
    temp_path = os.path.join(TEMP_DIR, f"temp_{uploaded_file.name}")
    with open(temp_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return temp_path

def cleanup_temp_files():
    """حذف جميع الملفات المؤقتة"""
    for file in os.listdir(TEMP_DIR):
        try:
            os.remove(os.path.join(TEMP_DIR, file))
        except:
            pass

def display_enhancement_results(enhancement_results1, enhancement_results2):
    st.markdown("### 🔍 نتائج تحسين البصمات")
    
    # عرض الصور
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### البصمة الأولى")
        st.image(enhancement_results1["original"], caption="الصورة الأصلية", use_container_width=True)
        st.image(enhancement_results1["enhanced"], caption="الصورة المحسنة", use_container_width=True)
        
        # عرض تفاصيل التحسين للبصمة الأولى
        st.markdown("##### 📊 تفاصيل التحسين")
        details = enhancement_results1["enhancement_details"]
        st.metric("تحسن التباين", f"{details['contrast_improvement']:.1f}%")
        st.metric("وضوح التلال", f"{details['ridge_clarity']:.1f}%")
        st.metric("تقليل الضوضاء", f"{details['noise_reduction']:.1f}%")
        st.metric("المناطق المرممة", f"{details['restored_areas']:.1f}%")
    
    with col2:
        st.markdown("#### البصمة الثانية")
        st.image(enhancement_results2["original"], caption="الصورة الأصلية", use_container_width=True)
        st.image(enhancement_results2["enhanced"], caption="الصورة المحسنة", use_container_width=True)
        
        # عرض تفاصيل التحسين للبصمة الثانية
        st.markdown("##### 📊 تفاصيل التحسين")
        details = enhancement_results2["enhancement_details"]
        st.metric("تحسن التباين", f"{details['contrast_improvement']:.1f}%")
        st.metric("وضوح التلال", f"{details['ridge_clarity']:.1f}%")
        st.metric("تقليل الضوضاء", f"{details['noise_reduction']:.1f}%")
        st.metric("المناطق المرممة", f"{details['restored_areas']:.1f}%")

def display_analysis_results(analysis_results1, analysis_results2):
    st.markdown("### 📊 تحليل تفصيلي للبصمات")
    
    col1, col2 = st.columns(2)
    
    # عرض نتائج البصمة الأولى
    with col1:
        st.markdown("#### البصمة الأولى")
        # معلومات عامة
        st.markdown("##### معلومات عامة")
        st.metric("نوع النمط", analysis_results1["pattern_type"])
        st.metric("جودة الصورة", f"{analysis_results1['quality_score']:.1f}%")
        
        # إحصائيات النقاط المميزة
        st.markdown("##### النقاط المميزة")
        stats = analysis_results1["statistics"]
        st.metric("إجمالي النقاط", stats["total_minutiae"])
        st.metric("نقاط النهاية", stats["ending_points_count"])
        st.metric("نقاط التفرع", stats["bifurcation_points_count"])
        
        # تحليل التلال
        st.markdown("##### تحليل التلال والأخاديد")
        ridges = analysis_results1["ridges_analysis"]
        st.metric("كثافة التلال", f"{ridges['ridge_count']:.1f}")
        st.metric("تعقيد النمط", f"{ridges['ridge_quality']:.2f}")
        
        # ملاحظات وتوصيات
        st.markdown("##### ملاحظات وتوصيات")
        quality_score = analysis_results1["quality_score"]
        if quality_score > 80:
            st.success("جودة البصمة ممتازة ومناسبة للتحليل الجنائي")
        elif quality_score > 60:
            st.warning("جودة البصمة جيدة ولكن يمكن تحسينها")
        else:
            st.error("جودة البصمة منخفضة، يفضل إعادة التقاط الصورة")
    
    # عرض نتائج البصمة الثانية
    with col2:
        st.markdown("#### البصمة الثانية")
        # معلومات عامة
        st.markdown("##### معلومات عامة")
        st.metric("نوع النمط", analysis_results2["pattern_type"])
        st.metric("جودة الصورة", f"{analysis_results2['quality_score']:.1f}%")
        
        # إحصائيات النقاط المميزة
        st.markdown("##### النقاط المميزة")
        stats = analysis_results2["statistics"]
        st.metric("إجمالي النقاط", stats["total_minutiae"])
        st.metric("نقاط النهاية", stats["ending_points_count"])
        st.metric("نقاط التفرع", stats["bifurcation_points_count"])
        
        # تحليل التلال
        st.markdown("##### تحليل التلال والأخاديد")
        ridges = analysis_results2["ridges_analysis"]
        st.metric("كثافة التلال", f"{ridges['ridge_count']:.1f}")
        st.metric("تعقيد النمط", f"{ridges['ridge_quality']:.2f}")
        
        # ملاحظات وتوصيات
        st.markdown("##### ملاحظات وتوصيات")
        quality_score = analysis_results2["quality_score"]
        if quality_score > 80:
            st.success("جودة البصمة ممتازة ومناسبة للتحليل الجنائي")
        elif quality_score > 60:
            st.warning("جودة البصمة جيدة ولكن يمكن تحسينها")
        else:
            st.error("جودة البصمة منخفضة، يفضل إعادة التقاط الصورة")

# Main app
st.title("👆 نظام تحليل ومطابقة البصمات")

# File upload section
st.header("رفع البصمات")
col1, col2 = st.columns(2)

with col1:
    st.subheader("البصمة الأولى")
    file1 = st.file_uploader("رفع البصمة الأولى", type=list(ALLOWED_EXTENSIONS), key="fp1")
    if file1:
        st.image(file1, caption="معاينة البصمة الأولى", use_container_width=True)

with col2:
    st.subheader("البصمة الثانية")
    file2 = st.file_uploader("رفع البصمة الثانية", type=list(ALLOWED_EXTENSIONS), key="fp2")
    if file2:
        st.image(file2, caption="معاينة البصمة الثانية", use_container_width=True)

# أزرار المعالجة
if file1 and file2:
    st.header("مراحل المعالجة")
    
    # مرحلة التحسين
    if st.button("تحسين البصمات", type="primary"):
        temp_path1 = save_temp_file(file1)
        temp_path2 = save_temp_file(file2)
        
        try:
            with st.spinner("جاري تحسين البصمات..."):
                enhancement_results1 = enhance_fingerprint(temp_path1)
                enhancement_results2 = enhance_fingerprint(temp_path2)
                display_enhancement_results(enhancement_results1, enhancement_results2)
        finally:
            cleanup_temp_files()
    
    # مرحلة التحليل
    if st.button("تحليل تفصيلي للبصمات", type="primary"):
        temp_path1 = save_temp_file(file1)
        temp_path2 = save_temp_file(file2)
        
        try:
            with st.spinner("جاري تحليل البصمات..."):
                analysis_results1 = analyze_fingerprint(temp_path1)
                analysis_results2 = analyze_fingerprint(temp_path2)
                display_analysis_results(analysis_results1, analysis_results2)
        finally:
            cleanup_temp_files()
    
    # مرحلة المقارنة
    if st.button("مقارنة البصمات", type="primary"):
        temp_path1 = save_temp_file(file1)
        temp_path2 = save_temp_file(file2)
        
        try:
            with st.spinner("جاري مقارنة البصمات..."):
                match_score, kp1_count, kp2_count, good_matches_count, match_filename, minutiae1_filename, minutiae2_filename, sourceafis_score = match_fingerprint(
                    temp_path1, temp_path2, TEMP_DIR
                )
            
            # Display results
            st.header("نتائج المقارنة")
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("درجة المطابقة", f"{match_score:.2f}%")
                st.metric("درجة SourceAFIS", f"{sourceafis_score:.2f}%")
            
            with col2:
                st.metric("النقاط المميزة في البصمة الأولى", kp1_count)
                st.metric("النقاط المميزة في البصمة الثانية", kp2_count)
                st.metric("نقاط المطابقة الجيدة", good_matches_count)
            
            # Display result images
            if match_filename and minutiae1_filename and minutiae2_filename:
                st.header("التحليل البصري")
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.image(os.path.join(TEMP_DIR, minutiae1_filename), 
                            caption="خصائص البصمة الأولى", use_container_width=True)
                with col2:
                    st.image(os.path.join(TEMP_DIR, match_filename), 
                            caption="نتائج المطابقة", use_container_width=True)
                with col3:
                    st.image(os.path.join(TEMP_DIR, minutiae2_filename), 
                            caption="خصائص البصمة الثانية", use_container_width=True)
            
        except Exception as e:
            st.error(f"حدث خطأ: {str(e)}")
        finally:
            cleanup_temp_files()
else:
    st.warning("الرجاء رفع البصمتين للمقارنة")

# Add footer
st.markdown("---")
st.markdown("### عن النظام")
st.markdown("""
هذا النظام يستخدم تقنيات متقدمة في معالجة الصور والتعلم الآلي لتحليل ومطابقة البصمات.
يمكن للنظام تحسين جودة البصمات من مسرح الجريمة وتحليلها بدقة عالية.
""")

# تنظيف الملفات المؤقتة عند إغلاق التطبيق
import atexit
atexit.register(cleanup_temp_files) 