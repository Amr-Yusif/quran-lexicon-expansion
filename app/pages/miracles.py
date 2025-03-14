#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
صفحة المعجزات العلمية في القرآن الكريم
"""

import streamlit as st
import sys
import os
import json
import pandas as pd
import matplotlib.pyplot as plt

# إضافة المسار الرئيسي للمشروع إلى مسار البحث
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from pathlib import Path

def render(quran_loader_func):
    """عرض صفحة المعجزات العلمية"""
    st.header("📊 المعجزات العلمية في القرآن الكريم")
    
    # تحميل بيانات المعجزات العلمية
    try:
        # الحصول على مسار ملف المعجزات العلمية
        data_dir = Path(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../data")))
        miracles_file = data_dir / "miracles" / "scientific_miracles.json"
        
        if miracles_file.exists():
            with open(miracles_file, 'r', encoding='utf-8') as f:
                miracles_data = json.load(f)
        else:
            # استخدام بيانات افتراضية إذا لم يتم العثور على الملف
            miracles_data = {
                "categories": [
                    "علم الفلك",
                    "علم الأحياء",
                    "علم الجيولوجيا",
                    "علم الأجنة",
                    "علم البحار",
                    "علم الفيزياء"
                ],
                "miracles": []
            }
    except Exception as e:
        st.error(f"حدث خطأ أثناء تحميل بيانات المعجزات العلمية: {str(e)}")
        miracles_data = {"categories": [], "miracles": []}
    
    # تقسيم الشاشة إلى عمودين
    col1, col2 = st.columns([1, 3])
    
    with col1:
        # قائمة التصفية والبحث
        st.subheader("تصفية المعجزات")
        
        # البحث بالنص
        search_query = st.text_input("بحث عن معجزة:", key="miracle_search")
        
        # تصفية حسب الفئة
        selected_category = st.selectbox(
            "تصفية حسب المجال العلمي:",
            ["جميع المجالات"] + miracles_data.get("categories", [])
        )
        
        # تصفية حسب السورة
        quran_loader = quran_loader_func()
        surah_names = ["جميع السور"] + [f"{i+1}. {surah.get('name', '')}" for i, surah in enumerate(quran_loader.get_all_surahs())]
        selected_surah = st.selectbox("تصفية حسب السورة:", surah_names)
        
        # زر البحث
        search_button = st.button("بحث", key="miracle_search_button")
        
        # إضافة معجزة جديدة (للمستخدمين المصرح لهم)
        with st.expander("إضافة معجزة علمية جديدة"):
            st.info("هذه الميزة متاحة فقط للمستخدمين المصرح لهم.")
            # هنا يمكن إضافة نموذج لإضافة معجزة جديدة
    
    with col2:
        # عرض المعجزات العلمية
        st.subheader("المعجزات العلمية في القرآن الكريم")
        
        # تطبيق التصفية على البيانات
        filtered_miracles = miracles_data.get("miracles", [])
        
        if search_query:
            filtered_miracles = [m for m in filtered_miracles if search_query.lower() in m.get("title", "").lower() or search_query.lower() in m.get("description", "").lower()]
        
        if selected_category != "جميع المجالات":
            filtered_miracles = [m for m in filtered_miracles if m.get("category") == selected_category]
        
        if selected_surah != "جميع السور":
            surah_number = int(selected_surah.split(".")[0])
            filtered_miracles = [m for m in filtered_miracles if m.get("surah_number") == surah_number]
        
        # عرض النتائج
        if filtered_miracles:
            for i, miracle in enumerate(filtered_miracles):
                with st.container():
                    st.markdown(f"### {i+1}. {miracle.get('title', 'معجزة علمية')}")
                    st.markdown(f"**المجال العلمي**: {miracle.get('category', 'غير محدد')}")
                    st.markdown(f"**الآية**: {miracle.get('verse_text', '')}")
                    st.markdown(f"**السورة**: {miracle.get('surah_name', '')} ({miracle.get('surah_number', '')})")
                    st.markdown(f"**رقم الآية**: {miracle.get('verse_number', '')}")
                    
                    # وصف المعجزة
                    st.markdown("#### الوصف")
                    st.markdown(miracle.get('description', 'لا يوجد وصف'))
                    
                    # الشرح العلمي
                    with st.expander("الشرح العلمي"):
                        st.markdown(miracle.get('scientific_explanation', 'لا يوجد شرح علمي'))
                        
                        # إضافة صورة إذا كانت متوفرة
                        if 'image_url' in miracle and miracle['image_url']:
                            st.image(miracle['image_url'], caption=miracle.get('image_caption', ''))
                    
                    # المراجع
                    with st.expander("المراجع والمصادر"):
                        references = miracle.get('references', [])
                        if references:
                            for ref in references:
                                st.markdown(f"- {ref}")
                        else:
                            st.markdown("لا توجد مراجع متاحة")
                    
                    st.divider()
        else:
            if search_query or selected_category != "جميع المجالات" or selected_surah != "جميع السور":
                st.warning("لم يتم العثور على نتائج مطابقة للتصفية. يرجى تعديل معايير البحث.")
            else:
                # عرض محتوى افتراضي عندما لا توجد بيانات
                st.info("لا توجد بيانات معجزات علمية متاحة حاليًا. سيتم إضافة المزيد من المعجزات قريبًا.")
                
                # عرض أمثلة للمعجزات العلمية
                st.subheader("أمثلة للمعجزات العلمية في القرآن الكريم")
                
                example1, example2 = st.columns(2)
                
                with example1:
                    st.markdown("### توسع الكون")
                    st.markdown("**الآية**: وَالسَّمَاءَ بَنَيْنَاهَا بِأَيْدٍ وَإِنَّا لَمُوسِعُونَ")
                    st.markdown("**السورة**: الذاريات (51)، الآية: 47")
                    st.markdown("تشير هذه الآية إلى حقيقة علمية اكتشفها العلماء في القرن العشرين وهي أن الكون يتوسع باستمرار.")
                
                with example2:
                    st.markdown("### مراحل تكوين الجنين")
                    st.markdown("**الآية**: وَلَقَدْ خَلَقْنَا الْإِنسَانَ مِن سُلَالَةٍ مِّن طِينٍ ثُمَّ جَعَلْنَاهُ نُطْفَةً فِي قَرَارٍ مَّكِينٍ ثُمَّ خَلَقْنَا النُّطْفَةَ عَلَقَةً فَخَلَقْنَا الْعَلَقَةَ مُضْغَةً فَخَلَقْنَا الْمُضْغَةَ عِظَامًا فَكَسَوْنَا الْعِظَامَ لَحْمًا ثُمَّ أَنشَأْنَاهُ خَلْقًا آخَرَ فَتَبَارَكَ اللَّهُ أَحْسَنُ الْخَالِقِينَ")
                    st.markdown("**السورة**: المؤمنون (23)، الآيات: 12-14")
                    st.markdown("تصف هذه الآيات مراحل تكوين الجنين بدقة علمية مذهلة تتوافق مع ما اكتشفه علم الأجنة الحديث.")


if __name__ == "__main__":
    # هذا للاختبار المستقل فقط
    render(None)