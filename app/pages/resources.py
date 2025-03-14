#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
صفحة الكتب والمراجع الإسلامية
"""

import streamlit as st
import sys
import os

# إضافة المسار الرئيسي للمشروع إلى مسار البحث
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))


def render(embedding_model_loader, qdrant_manager_loader):
    """عرض صفحة الكتب والمراجع الإسلامية"""
    st.header("📚 الكتب والمراجع الإسلامية")
    
    # تقسيم الشاشة إلى عمودين
    col1, col2 = st.columns([1, 2])
    
    with col1:
        # اختيار نوع المصدر للبحث
        source_type = st.radio(
            "نوع المصدر:",
            ["تفاسير القرآن", "كتب العلماء", "المعجزات العلمية", "جميع المصادر"],
            index=3
        )
        
        # مربع البحث
        islamic_search_query = st.text_input("أدخل نص البحث:", key="islamic_resources_search")
        
        # زر البحث
        search_clicked = st.button("بحث في المصادر الإسلامية", key="islamic_search_button")
        
        # إعدادات متقدمة مع خيار طي/فتح
        with st.expander("إعدادات البحث المتقدمة"):
            max_results = st.slider("عدد النتائج الأقصى:", min_value=5, max_value=50, value=10)
            similarity_threshold = st.slider("عتبة التشابه:", min_value=0.5, max_value=0.99, value=0.75, step=0.01)
            
            # فلترة حسب المؤلف/المصدر (ديناميكية حسب نوع المصدر)
            if source_type == "تفاسير القرآن":
                tafsir_options = ["الشعراوي", "النابلسي", "جميع التفاسير"]
                selected_author = st.multiselect("اختر التفسير:", tafsir_options, default=["جميع التفاسير"])
            elif source_type == "كتب العلماء":
                scholar_options = ["ابن القيم", "ابن تيمية", "الأئمة الأربعة", "النابلسي", "الشعراوي", "مصطفى محمود", "راغب السرجاني", "جميع العلماء"]
                selected_author = st.multiselect("اختر العالم:", scholar_options, default=["جميع العلماء"])
            elif source_type == "المعجزات العلمية":
                miracle_options = ["الإعجاز العلمي", "الإعجاز العددي", "الإعجاز اللغوي", "جميع أنواع الإعجاز"]
                selected_author = st.multiselect("نوع الإعجاز:", miracle_options, default=["جميع أنواع الإعجاز"])
    
    with col2:
        # منطقة عرض النتائج
        if search_clicked and islamic_search_query:
            with st.spinner("جاري البحث في المصادر الإسلامية..."):
                try:
                    # تهيئة العناصر المطلوبة
                    embedding_model = embedding_model_loader()
                    qdrant_manager = qdrant_manager_loader()
                    
                    # تحديد المجموعات التي سيتم البحث فيها
                    collections_to_search = []
                    if source_type == "تفاسير القرآن" or source_type == "جميع المصادر":
                        collections_to_search.append("tafsir_explanations")
                    if source_type == "كتب العلماء" or source_type == "جميع المصادر":
                        collections_to_search.append("scholars_books")
                    if source_type == "المعجزات العلمية" or source_type == "جميع المصادر":
                        collections_to_search.append("scientific_miracles")
                    
                    # تحويل نص البحث إلى تضمين (embedding)
                    query_embedding = embedding_model.encode(islamic_search_query)
                    
                    # جمع النتائج من جميع المجموعات المطلوبة
                    all_results = []
                    
                    for collection_name in collections_to_search:
                        try:
                            results = qdrant_manager.search(
                                collection_name=collection_name,
                                query_vector=query_embedding.tolist(),
                                limit=max_results,
                                score_threshold=similarity_threshold # تعديل هنا لاضافة  threshold
                            )
                            
                            # إضافة المجموعة إلى كل نتيجة للتمييز لاحقًا
                            for result in results:
                                result.payload["collection"] = collection_name
                                all_results.append(result)
                                
                        except Exception as e:
                            st.warning(f"تعذر البحث في مجموعة {collection_name}: {str(e)}")
                    
                    # ترتيب النتائج حسب درجة التشابه
                    all_results.sort(key=lambda x: x.score, reverse=True)
                    
                    # عرض النتائج
                    if all_results:
                        st.subheader(f"تم العثور على {len(all_results)} نتيجة:")
                        
                        for i, result in enumerate(all_results, 1):
                            # تحديد نوع المصدر للعرض
                            source_icon = "📚"
                            if result.payload.get("collection") == "tafsir_explanations":
                                source_icon = "📖"
                                source_type_display = "تفسير"
                                author_display = result.payload.get("tafsir_name", "غير معروف")
                            elif result.payload.get("collection") == "scholars_books":
                                source_icon = "👨‍🏫"
                                source_type_display = "كتاب"
                                author_display = result.payload.get("scholar_name", "غير معروف")
                            elif result.payload.get("collection") == "scientific_miracles":
                                source_icon = "🔬"
                                source_type_display = "معجزة علمية"
                                author_display = result.payload.get("category", "غير معروف")
                            else:
                                source_type_display = "مصدر"
                                author_display = "غير معروف"
                            
                            # عرض النتيجة في بطاقة
                            with st.container():
                                st.markdown(f"### {i}. {source_icon} {source_type_display}: {author_display}")
                                st.markdown(f"**النص**: {result.payload.get('text', 'لا يوجد نص')}")
                                st.markdown(f"**المصدر**: {result.payload.get('source', 'غير معروف')}")
                                st.markdown(f"**درجة التطابق**: {result.score:.2f}")
                                st.divider()
                    else:
                        st.warning("لم يتم العثور على نتائج. حاول تعديل معايير البحث أو استخدام كلمات مختلفة.")
                except Exception as e:
                    st.error(f"حدث خطأ أثناء البحث: {str(e)}")
        else:
            # عرض محتوى افتراضي عندما لا يوجد بحث
            st.info("أدخل نص البحث واضغط على زر 'بحث في المصادر الإسلامية' للبدء.")
            
            # عرض بعض المصادر المقترحة
            st.subheader("مصادر مقترحة")
            
            # عرض بعض المصادر المقترحة في شكل بطاقات
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("### 📖 تفاسير القرآن")
                st.markdown("- تفسير ابن كثير")
                st.markdown("- تفسير الطبري")
                st.markdown("- تفسير القرطبي")
                st.markdown("- تفسير الشعراوي")
            
            with col2:
                st.markdown("### 👨‍🏫 كتب العلماء")
                st.markdown("- زاد المعاد لابن القيم")
                st.markdown("- إحياء علوم الدين للغزالي")
                st.markdown("- فقه السنة للسيد سابق")
                st.markdown("- الرحيق المختوم للمباركفوري")
            
            with col3:
                st.markdown("### 🔬 المعجزات العلمية")
                st.markdown("- الإعجاز العلمي في القرآن والسنة")
                st.markdown("- الإشارات الكونية في القرآن")
                st.markdown("- الإعجاز العددي في القرآن")
                st.markdown("- الإعجاز اللغوي في القرآن")


if __name__ == "__main__":
    # هذا للاختبار المستقل فقط
    render(None, None)