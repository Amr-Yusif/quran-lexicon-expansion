"""
استكشاف المعجزات العلمية - واجهة مستخدم لاكتشاف وتحليل المعجزات العلمية في القرآن الكريم
"""
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import json
from pathlib import Path
import os
from typing import List, Dict, Any, Optional

# استيراد المكونات الضرورية من المشروع
from local_mem0_agent.core.analysis.scientific_miracle_detector import ScientificMiracleDetector
from local_mem0_agent.core.utils.config import get_config
from local_mem0_agent.core.utils.arabic_text_utils import ArabicTextProcessor
from local_mem0_agent.subscription.user_manager import UserManager

# استيراد مكونات مساعدة لعرض البيانات
from local_mem0_agent.ui.components.charts import create_category_chart, create_timeline_chart
from local_mem0_agent.ui.components.text_display import display_verse_with_tafseer

class MiracleExplorer:
    """
    واجهة لاستكشاف المعجزات العلمية في القرآن الكريم والكتب الإسلامية
    """
    
    def __init__(self, user_manager: UserManager = None):
        """
        تهيئة مستكشف المعجزات العلمية

        Args:
            user_manager: مدير المستخدمين (اختياري)
        """
        # تهيئة مدير التكوين
        self.config = get_config()
        
        # تهيئة كاشف المعجزات العلمية
        self.miracle_detector = ScientificMiracleDetector()
        
        # تهيئة مدير المستخدمين
        self.user_manager = user_manager
        
        # تهيئة مسارات البيانات
        self.data_dir = self.config.get_data_path("scientific_miracles")
        
        # تحميل بيانات المعجزات
        self.miracles = self.miracle_detector.knowledge_base
        self.discoveries = self.miracle_detector.discoveries
    
    def render(self):
        """عرض واجهة استكشاف المعجزات العلمية"""
        st.title("استكشاف المعجزات العلمية في القرآن الكريم")
        
        # إنشاء تبويبات لوظائف مختلفة
        tabs = st.tabs([
            "البحث والاستكشاف", 
            "تحليل النصوص",
            "إضافة معجزة علمية",
            "إحصائيات وتحليلات",
            "التفسير العلمي"
        ])
        
        # تبويب البحث والاستكشاف
        with tabs[0]:
            self._render_search_tab()
        
        # تبويب تحليل النصوص
        with tabs[1]:
            self._render_analysis_tab()
        
        # تبويب إضافة معجزة علمية
        with tabs[2]:
            self._render_add_miracle_tab()
        
        # تبويب الإحصائيات والتحليلات
        with tabs[3]:
            self._render_statistics_tab()
        
        # تبويب التفسير العلمي
        with tabs[4]:
            self._render_tafseer_tab()
    
    def _render_search_tab(self):
        """عرض تبويب البحث والاستكشاف"""
        st.header("البحث في المعجزات العلمية")
        
        # حقل البحث
        query = st.text_input("أدخل استعلام البحث (موضوع، كلمة مفتاحية، آية...)")
        category_filter = st.selectbox(
            "تصفية حسب الفئة العلمية",
            ["جميع الفئات"] + list(self.miracle_detector.MIRACLE_CATEGORIES.keys()),
            format_func=lambda x: self._translate_category(x)
        )
        
        # زر البحث
        if st.button("بحث") and query:
            # إجراء البحث
            results = self.miracle_detector.search_miracles(query)
            
            # تطبيق التصفية حسب الفئة
            if category_filter != "جميع الفئات":
                results = [r for r in results if r.get("category") == category_filter]
            
            # عرض النتائج
            if results:
                st.success(f"تم العثور على {len(results)} نتيجة")
                
                for result in results:
                    with st.expander(f"{result['title']} (تشابه: {result['similarity']:.2f})"):
                        st.subheader(result["title"])
                        st.write(f"**الفئة:** {self._translate_category(result['category'])}")
                        st.write(f"**الوصف:** {result['description']}")
                        st.write(f"**الدليل العلمي:** {result['evidence']}")
                        
                        # عرض الآيات المرتبطة
                        if "verses" in result and result["verses"]:
                            st.subheader("الآيات القرآنية")
                            for verse in result["verses"]:
                                st.markdown(f"**{verse['surah']} ({verse['ayah']}):** {verse.get('text', '')}")
            else:
                st.info("لم يتم العثور على نتائج متطابقة مع استعلام البحث")
    
    def _render_analysis_tab(self):
        """عرض تبويب تحليل النصوص"""
        st.header("تحليل النصوص للكشف عن المعجزات العلمية")
        
        # مساحة نصية للتحليل
        text_to_analyze = st.text_area(
            "أدخل النص للتحليل",
            height=200,
            help="يمكنك إدخال نص من مقال أو كتاب لتحليله والكشف عن المعجزات العلمية المحتملة"
        )
        
        # زر التحليل
        if st.button("تحليل النص") and text_to_analyze:
            with st.spinner("جارٍ تحليل النص..."):
                # تحليل النص
                analysis_result = self.miracle_detector.analyze_text_for_miracles(text_to_analyze)
                
                # عرض النتائج
                st.success(f"تم العثور على {analysis_result['total_candidates']} مرشح محتمل للإعجاز العلمي")
                
                # عرض المرشحين المحتملين
                if analysis_result["miracle_candidates"]:
                    st.subheader("المرشحون المحتملون للإعجاز العلمي")
                    
                    for i, candidate in enumerate(analysis_result["miracle_candidates"]):
                        with st.expander(f"المرشح #{i+1} (درجة الأهمية: {candidate['score']})"):
                            st.write(candidate["text"])
                            
                            # عرض معلومات الكشف
                            detection = candidate["detection_result"]
                            st.write(f"**الكلمات العلمية:** {', '.join(detection['scientific_keywords'])}")
                            st.write(f"**الفئة العلمية الرئيسية:** {self._translate_category(detection['primary_category'])}")
                            
                            # عرض الآيات
                            if detection["quran_verses"]:
                                st.subheader("الآيات القرآنية المكتشفة")
                                for verse in detection["quran_verses"]:
                                    st.markdown(f"> {verse}")
                            
                            # عرض المعجزات المشابهة
                            if detection["similar_miracles"]:
                                st.subheader("معجزات علمية مشابهة")
                                for similar in detection["similar_miracles"]:
                                    st.markdown(f"- **{similar['title']}** (تشابه: {similar['similarity']:.2f})")
                else:
                    st.info("لم يتم اكتشاف مرشحين محتملين للإعجاز العلمي في النص")
    
    def _render_add_miracle_tab(self):
        """عرض تبويب إضافة معجزة علمية"""
        st.header("إضافة معجزة علمية جديدة")
        
        # التحقق من صلاحيات المستخدم
        if self.user_manager and not self.user_manager.current_user.has_permission("add_miracles"):
            st.warning("هذه الميزة متاحة فقط للمشتركين في الخطة المتقدمة")
            st.info("يمكنك الترقية إلى خطة مشتركة متقدمة للوصول إلى هذه الميزة")
            return
        
        # نموذج إضافة معجزة
        with st.form("add_miracle_form"):
            title = st.text_input("عنوان المعجزة العلمية")
            description = st.text_area("وصف المعجزة")
            evidence = st.text_area("الدليل العلمي")
            
            # إضافة الآيات
            st.subheader("الآيات القرآنية")
            num_verses = st.number_input("عدد الآيات", min_value=1, max_value=10, value=1)
            
            verses = []
            for i in range(num_verses):
                col1, col2, col3 = st.columns([2, 1, 3])
                with col1:
                    surah = st.text_input(f"اسم السورة #{i+1}", key=f"surah_{i}")
                with col2:
                    ayah = st.number_input(f"رقم الآية #{i+1}", min_value=1, key=f"ayah_{i}")
                with col3:
                    verse_text = st.text_input(f"نص الآية #{i+1} (اختياري)", key=f"text_{i}")
                
                if surah and ayah:
                    verses.append({
                        "surah": surah,
                        "ayah": ayah,
                        "text": verse_text
                    })
            
            # اختيار الفئة
            category = st.selectbox(
                "الفئة العلمية",
                list(self.miracle_detector.MIRACLE_CATEGORIES.keys()),
                format_func=lambda x: self._translate_category(x)
            )
            
            # زر الإضافة
            submit = st.form_submit_button("إضافة المعجزة العلمية")
            
            if submit and title and description and evidence and verses:
                # إضافة المعجزة
                miracle = self.miracle_detector.add_scientific_miracle(
                    title=title,
                    description=description,
                    evidence=evidence,
                    verses=verses,
                    category=category
                )
                
                if miracle:
                    st.success(f"تمت إضافة المعجزة العلمية '{title}' بنجاح")
                    
                    # إعادة تحميل البيانات
                    self.miracles = self.miracle_detector.knowledge_base
                else:
                    st.error("حدث خطأ أثناء إضافة المعجزة العلمية")
    
    def _render_statistics_tab(self):
        """عرض تبويب الإحصائيات والتحليلات"""
        st.header("إحصائيات وتحليلات المعجزات العلمية")
        
        if not self.miracles:
            st.info("لا توجد بيانات كافية لعرض الإحصائيات")
            return
        
        # إحصائيات عامة
        st.subheader("إحصائيات عامة")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("إجمالي المعجزات العلمية", len(self.miracles))
        with col2:
            st.metric("إجمالي الاكتشافات العلمية", len(self.discoveries))
        with col3:
            categories = [m.get("category", "other") for m in self.miracles]
            most_common_category = max(set(categories), key=categories.count)
            st.metric("أكثر فئة شائعة", self._translate_category(most_common_category))
        
        # توزيع المعجزات حسب الفئة
        st.subheader("توزيع المعجزات حسب الفئة العلمية")
        
        # إنشاء بيانات الرسم البياني
        category_counts = {}
        for miracle in self.miracles:
            category = miracle.get("category", "other")
            category_counts[category] = category_counts.get(category, 0) + 1
        
        # ترجمة الفئات
        translated_counts = {self._translate_category(k): v for k, v in category_counts.items()}
        
        # عرض الرسم البياني
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.bar(translated_counts.keys(), translated_counts.values())
        ax.set_xlabel("الفئة العلمية")
        ax.set_ylabel("عدد المعجزات")
        ax.set_title("توزيع المعجزات حسب الفئة العلمية")
        plt.xticks(rotation=45, ha="right")
        plt.tight_layout()
        st.pyplot(fig)
        
        # تحليل السور الأكثر ذكرًا للمعجزات
        st.subheader("السور الأكثر ذكرًا للمعجزات العلمية")
        
        # جمع بيانات السور
        surah_counts = {}
        for miracle in self.miracles:
            if "verses" in miracle:
                for verse in miracle["verses"]:
                    surah = verse.get("surah", "")
                    if surah:
                        surah_counts[surah] = surah_counts.get(surah, 0) + 1
        
        # ترتيب السور حسب العدد
        sorted_surahs = sorted(surah_counts.items(), key=lambda x: x[1], reverse=True)
        
        # عرض الرسم البياني للسور الأكثر ذكرًا (أعلى 10)
        if sorted_surahs:
            top_surahs = sorted_surahs[:10]
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.barh([s[0] for s in top_surahs], [s[1] for s in top_surahs])
            ax.set_xlabel("عدد المعجزات")
            ax.set_ylabel("اسم السورة")
            ax.set_title("السور العشر الأكثر ذكرًا للمعجزات العلمية")
            plt.tight_layout()
            st.pyplot(fig)
    
    def _render_tafseer_tab(self):
        """عرض تبويب التفسير العلمي"""
        st.header("التفسير العلمي للآيات القرآنية")
        
        # اختيار السورة والآية
        col1, col2 = st.columns(2)
        with col1:
            surah = st.selectbox("اختر السورة", ArabicTextProcessor.SURAH_NAMES)
        with col2:
            # تحديد عدد آيات السورة (هذا يحتاج إلى بيانات إضافية)
            max_ayah = 286 if surah == "البقرة" else 200  # مثال بسيط
            ayah = st.number_input("رقم الآية", min_value=1, max_value=max_ayah, value=1)
        
        if st.button("عرض التفسير العلمي"):
            # البحث عن المعجزات المرتبطة بالآية
            related_miracles = []
            for miracle in self.miracles:
                if "verses" in miracle:
                    for verse in miracle["verses"]:
                        if verse.get("surah") == surah and verse.get("ayah") == ayah:
                            related_miracles.append(miracle)
            
            if related_miracles:
                st.success(f"تم العثور على {len(related_miracles)} تفسير علمي لهذه الآية")
                
                for miracle in related_miracles:
                    with st.expander(miracle["title"]):
                        st.write(f"**الوصف:** {miracle['description']}")
                        st.write(f"**الدليل العلمي:** {miracle['evidence']}")
                        st.write(f"**الفئة:** {self._translate_category(miracle['category'])}")
            else:
                st.info("لم يتم العثور على تفسير علمي لهذه الآية")
                st.write("يمكنك إضافة تفسير علمي جديد من خلال تبويب 'إضافة معجزة علمية'")
    
    def _translate_category(self, category: str) -> str:
        """
        ترجمة اسم الفئة العلمية إلى العربية

        Args:
            category: اسم الفئة بالإنجليزية

        Returns:
            اسم الفئة بالعربية
        """
        translations = {
            "astronomy": "علم الفلك",
            "earth": "علوم الأرض",
            "biology": "علم الأحياء",
            "physics": "علم الفيزياء",
            "chemistry": "علم الكيمياء",
            "medicine": "الطب",
            "mathematics": "الرياضيات",
            "other": "أخرى",
            "all": "جميع الفئات"
        }
        
        return translations.get(category, category)
