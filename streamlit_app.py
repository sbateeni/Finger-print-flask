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
    page_title="نظام تحليل ومطابقة البصمات",
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

def display_comprehensive_results(enhancement_results1, enhancement_results2, 
                                analysis_results1, analysis_results2,
                                match_results):
    """عرض النتائج الشاملة للتحليل"""
    st.markdown("### 📊 التقرير الشامل")
    
    # عرض الصور المحسنة
    st.markdown("#### 🔍 الصور المحسنة")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("##### البصمة الأولى")
        st.image(enhancement_results1["enhanced"], caption="الصورة المحسنة", use_container_width=True)
    with col2:
        st.markdown("##### البصمة الثانية")
        st.image(enhancement_results2["enhanced"], caption="الصورة المحسنة", use_container_width=True)
    
    # ملخص النتائج
    st.markdown("#### 📝 ملخص النتائج")
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("درجة المطابقة النهائية", f"{match_results['match_score']:.2f}%")
        st.metric("جودة البصمة الأولى", f"{analysis_results1['quality_score']:.1f}%")
    
    with col2:
        st.metric("درجة SourceAFIS", f"{match_results['sourceafis_score']:.2f}%")
        st.metric("جودة البصمة الثانية", f"{analysis_results2['quality_score']:.1f}%")
    
    # التوصية النهائية
    st.markdown("#### 🎯 التوصية النهائية")
    match_score = match_results['match_score']
    quality1 = analysis_results1['quality_score']
    quality2 = analysis_results2['quality_score']
    
    if match_score >= 80 and quality1 >= 70 and quality2 >= 70:
        st.success("""
        ### ✅ النتيجة: مطابقة إيجابية
        - درجة المطابقة عالية
        - جودة البصمات جيدة
        - يمكن الاعتماد على النتيجة في التحليل الجنائي
        """)
    elif match_score >= 60 and quality1 >= 60 and quality2 >= 60:
        st.warning("""
        ### ⚠️ النتيجة: مطابقة محتملة
        - درجة المطابقة متوسطة
        - جودة البصمات مقبولة
        - يفضل إجراء تحليل إضافي
        """)
    else:
        st.error("""
        ### ❌ النتيجة: عدم مطابقة
        - درجة المطابقة منخفضة
        - جودة البصمات غير كافية
        - يفضل إعادة التقاط البصمات
        """)
    
    # تفاصيل التحليل
    with st.expander("📋 تفاصيل التحليل الكاملة"):
        # نتائج التحسين
        st.markdown("#### 🔍 نتائج التحسين")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("##### البصمة الأولى")
            details = enhancement_results1["enhancement_details"]
            st.metric("تحسن التباين", f"{details['contrast_improvement']:.1f}%")
            st.metric("وضوح التلال", f"{details['ridge_clarity']:.1f}%")
            st.metric("تقليل الضوضاء", f"{details['noise_reduction']:.1f}%")
        with col2:
            st.markdown("##### البصمة الثانية")
            details = enhancement_results2["enhancement_details"]
            st.metric("تحسن التباين", f"{details['contrast_improvement']:.1f}%")
            st.metric("وضوح التلال", f"{details['ridge_clarity']:.1f}%")
            st.metric("تقليل الضوضاء", f"{details['noise_reduction']:.1f}%")
        
        # نتائج التحليل التفصيلي
        st.markdown("#### 📊 نتائج التحليل التفصيلي")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("##### البصمة الأولى")
            stats = analysis_results1["statistics"]
            st.metric("إجمالي النقاط", stats["total_minutiae"])
            st.metric("نقاط النهاية", stats["ending_points_count"])
            st.metric("نقاط التفرع", stats["bifurcation_points_count"])
        with col2:
            st.markdown("##### البصمة الثانية")
            stats = analysis_results2["statistics"]
            st.metric("إجمالي النقاط", stats["total_minutiae"])
            st.metric("نقاط النهاية", stats["ending_points_count"])
            st.metric("نقاط التفرع", stats["bifurcation_points_count"])
        
        # نتائج المقارنة
        st.markdown("#### 🔄 نتائج المقارنة")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("النقاط المميزة في البصمة الأولى", match_results['kp1_count'])
            st.metric("النقاط المميزة في البصمة الثانية", match_results['kp2_count'])
        with col2:
            st.metric("نقاط المطابقة الجيدة", match_results['good_matches_count'])
            st.metric("درجة المطابقة", f"{match_results['match_score']:.2f}%")

# Main app
st.title("👆 نظام تحليل ومطابقة البصمات")

# إضافة شرح عن النظام
with st.expander("ℹ️ عن النظام", expanded=False):
    st.markdown("""
    ### مرحباً بك في نظام تحليل ومطابقة البصمات
    
    هذا النظام يتيح لك:
    1. **تحسين جودة البصمات**: تحسين وضوح البصمات وإزالة الضوضاء
    2. **تحليل تفصيلي**: تحليل خصائص البصمات وأنماطها
    3. **مطابقة البصمات**: مقارنة البصمات وتحديد درجة المطابقة
    
    ### كيفية الاستخدام
    1. قم برفع البصمتين المراد تحليلهما
    2. اختر المرحلة المطلوبة (تحسين، تحليل، أو مقارنة)
    3. انتظر ظهور النتائج
    """)

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
    
    # إضافة تبويبات
    tab1, tab2, tab3, tab4 = st.tabs(["تحسين البصمات", "تحليل تفصيلي", "مقارنة البصمات", "تحليل شامل"])
    
    with tab1:
        st.markdown("""
        ### تحسين جودة البصمات
        في هذه المرحلة يتم:
        - تحسين التباين
        - إزالة الضوضاء
        - تحسين وضوح التلال
        - ترميم المناطق التالفة
        """)
        
        # خيارات متقدمة للتحسين
        with st.expander("⚙️ خيارات متقدمة"):
            contrast_level = st.slider("مستوى التباين", 1.0, 3.0, 2.0, 0.1, key="tab1_contrast")
            noise_reduction = st.slider("قوة إزالة الضوضاء", 1, 10, 5, key="tab1_noise")
            ridge_enhancement = st.slider("تحسين التلال", 1, 10, 5, key="tab1_ridge")
        
        if st.button("بدء التحسين", type="primary"):
            temp_path1 = save_temp_file(file1)
            temp_path2 = save_temp_file(file2)
            
            try:
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                # تحسين البصمة الأولى
                status_text.text("جاري تحسين البصمة الأولى...")
                enhancement_results1 = enhance_fingerprint(temp_path1)
                progress_bar.progress(50)
                
                # تحسين البصمة الثانية
                status_text.text("جاري تحسين البصمة الثانية...")
                enhancement_results2 = enhance_fingerprint(temp_path2)
                progress_bar.progress(100)
                
                status_text.text("اكتمل التحسين!")
                display_enhancement_results(enhancement_results1, enhancement_results2)
            finally:
                cleanup_temp_files()
    
    with tab2:
        st.markdown("""
        ### التحليل التفصيلي
        في هذه المرحلة يتم:
        - تحليل نوع النمط
        - تحديد النقاط المميزة
        - تحليل التلال والأخاديد
        - تقييم جودة البصمة
        """)
        
        # خيارات متقدمة للتحليل
        with st.expander("⚙️ خيارات متقدمة"):
            min_quality = st.slider("الحد الأدنى لجودة البصمة", 0, 100, 60, key="tab2_quality")
            analysis_depth = st.select_slider(
                "عمق التحليل",
                options=["سريع", "متوسط", "دقيق"],
                value="متوسط",
                key="tab2_depth"
            )
        
        if st.button("بدء التحليل", type="primary"):
            temp_path1 = save_temp_file(file1)
            temp_path2 = save_temp_file(file2)
            
            try:
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                # تحليل البصمة الأولى
                status_text.text("جاري تحليل البصمة الأولى...")
                analysis_results1 = analyze_fingerprint(temp_path1)
                progress_bar.progress(50)
                
                # تحليل البصمة الثانية
                status_text.text("جاري تحليل البصمة الثانية...")
                analysis_results2 = analyze_fingerprint(temp_path2)
                progress_bar.progress(100)
                
                status_text.text("اكتمل التحليل!")
                display_analysis_results(analysis_results1, analysis_results2)
            finally:
                cleanup_temp_files()
    
    with tab3:
        st.markdown("""
        ### مقارنة البصمات
        في هذه المرحلة يتم:
        - مقارنة النقاط المميزة
        - حساب درجة المطابقة
        - عرض النتائج بصرياً
        """)
        
        # خيارات متقدمة للمقارنة
        with st.expander("⚙️ خيارات متقدمة"):
            match_threshold = st.slider("حد المطابقة", 0, 100, 80, key="tab3_threshold")
            show_details = st.checkbox("عرض التفاصيل الكاملة", value=True, key="tab3_details")
        
        if st.button("بدء المقارنة", type="primary"):
            temp_path1 = save_temp_file(file1)
            temp_path2 = save_temp_file(file2)
            
            try:
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                # معالجة البصمات
                status_text.text("جاري معالجة البصمات...")
                progress_bar.progress(30)
                
                # مقارنة البصمات
                status_text.text("جاري مقارنة البصمات...")
                match_score, kp1_count, kp2_count, good_matches_count, match_filename, minutiae1_filename, minutiae2_filename, sourceafis_score = match_fingerprint(
                    temp_path1, temp_path2, TEMP_DIR
                )
                progress_bar.progress(100)
                
                status_text.text("اكتملت المقارنة!")
                
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
    
    with tab4:
        st.markdown("""
        ### التحليل الشامل
        في هذه المرحلة يتم:
        - تحسين جودة البصمات
        - تحليل تفصيلي للبصمات
        - مقارنة البصمات
        - إصدار تقرير نهائي شامل
        """)
        
        # خيارات متقدمة للتحليل الشامل
        with st.expander("⚙️ خيارات متقدمة"):
            st.markdown("#### إعدادات التحسين")
            contrast_level = st.slider("مستوى التباين", 1.0, 3.0, 2.0, 0.1, key="tab4_contrast")
            noise_reduction = st.slider("قوة إزالة الضوضاء", 1, 10, 5, key="tab4_noise")
            
            st.markdown("#### إعدادات التحليل")
            min_quality = st.slider("الحد الأدنى لجودة البصمة", 0, 100, 60, key="tab4_quality")
            analysis_depth = st.select_slider(
                "عمق التحليل",
                options=["سريع", "متوسط", "دقيق"],
                value="متوسط",
                key="tab4_depth"
            )
            
            st.markdown("#### إعدادات المقارنة")
            match_threshold = st.slider("حد المطابقة", 0, 100, 80, key="tab4_threshold")
            show_details = st.checkbox("عرض التفاصيل الكاملة", value=True, key="tab4_details")
        
        if st.button("بدء التحليل الشامل", type="primary"):
            temp_path1 = save_temp_file(file1)
            temp_path2 = save_temp_file(file2)
            
            try:
                # شريط التقدم الرئيسي
                main_progress = st.progress(0)
                status_text = st.empty()
                
                # 1. مرحلة التحسين
                status_text.text("المرحلة 1/3: تحسين البصمات...")
                enhancement_results1 = enhance_fingerprint(temp_path1)
                enhancement_results2 = enhance_fingerprint(temp_path2)
                main_progress.progress(33)
                
                # 2. مرحلة التحليل
                status_text.text("المرحلة 2/3: تحليل البصمات...")
                analysis_results1 = analyze_fingerprint(temp_path1)
                analysis_results2 = analyze_fingerprint(temp_path2)
                main_progress.progress(66)
                
                # 3. مرحلة المقارنة
                status_text.text("المرحلة 3/3: مقارنة البصمات...")
                match_score, kp1_count, kp2_count, good_matches_count, match_filename, minutiae1_filename, minutiae2_filename, sourceafis_score = match_fingerprint(
                    temp_path1, temp_path2, TEMP_DIR
                )
                main_progress.progress(100)
                
                status_text.text("اكتمل التحليل الشامل!")
                
                # تجميع النتائج
                match_results = {
                    'match_score': match_score,
                    'kp1_count': kp1_count,
                    'kp2_count': kp2_count,
                    'good_matches_count': good_matches_count,
                    'sourceafis_score': sourceafis_score
                }
                
                # عرض النتائج الشاملة
                display_comprehensive_results(
                    enhancement_results1, enhancement_results2,
                    analysis_results1, analysis_results2,
                    match_results
                )
                
                # عرض الصور النهائية
                if match_filename and minutiae1_filename and minutiae2_filename:
                    st.markdown("#### 📸 الصور النهائية")
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