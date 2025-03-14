#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
صفحة إعدادات التطبيق
"""

import streamlit as st
import sys
import os

# إضافة المسار الرئيسي للمشروع إلى مسار البحث
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from core.utils.config import ConfigManager

def render():
    """عرض صفحة الإعدادات"""
    st.header("⚙️ إعدادات التطبيق")
    
    # تهيئة مدير التكوين
    config_manager = ConfigManager()
    
    # تقسيم الشاشة إلى أقسام
    tabs = st.tabs(["إعدادات عامة", "إعدادات النموذج", "إعدادات البحث", "إعدادات المستخدم", "حول التطبيق"])
    
    # إعدادات عامة
    with tabs[0]:
        st.subheader("الإعدادات العامة")
        
        # اللغة
        language = st.selectbox(
            "لغة واجهة المستخدم:",
            options=["العربية", "English"],
            index=0
        )
        
        # المظهر
        theme = st.radio(
            "مظهر التطبيق:",
            options=["فاتح", "داكن", "تلقائي (حسب إعدادات النظام)"],
            index=2
        )
        
        # حجم الخط
        font_size = st.slider(
            "حجم الخط:",
            min_value=80,
            max_value=120,
            value=100,
            step=5,
            format="%d%%"
        )
        
        # زر حفظ الإعدادات العامة
        if st.button("حفظ الإعدادات العامة"):
            # هنا يمكن حفظ الإعدادات في ملف التكوين
            st.success("تم حفظ الإعدادات بنجاح!")
    
    # إعدادات النموذج
    with tabs[1]:
        st.subheader("إعدادات نموذج الذكاء الاصطناعي")
        
        # اختيار النموذج
        model_choice = st.selectbox(
            "النموذج المستخدم:",
            options=["mistral", "llama2:arabic", "llama2", "gemma"],
            index=0
        )
        
        # معلمات النموذج
        temperature = st.slider(
            "درجة الإبداعية (Temperature):",
            min_value=0.0,
            max_value=1.0,
            value=0.7,
            step=0.1
        )
        
        max_tokens = st.slider(
            "الحد الأقصى للرموز (Max Tokens):",
            min_value=256,
            max_value=4096,
            value=2048,
            step=256
        )
        
        # زر حفظ إعدادات النموذج
        if st.button("حفظ إعدادات النموذج"):
            # حفظ إعدادات النموذج
            st.session_state.model_choice = model_choice
            st.success("تم حفظ إعدادات النموذج بنجاح!")
    
    # إعدادات البحث
    with tabs[2]:
        st.subheader("إعدادات البحث والاسترجاع")
        
        # نموذج التضمين
        embedding_model = st.selectbox(
            "نموذج التضمين:",
            options=[
                "paraphrase-multilingual-mpnet-base-v2",
                "sentence-transformers/paraphrase-arabic-mpnet-base-v2",
                "UBC-NLP/ARBERT"
            ],
            index=0
        )
        
        # إعدادات البحث الدلالي
        semantic_search_threshold = st.slider(
            "عتبة التشابه الدلالي:",
            min_value=0.5,
            max_value=0.95,
            value=0.75,
            step=0.05
        )
        
        # زر حفظ إعدادات البحث
        if st.button("حفظ إعدادات البحث"):
            # حفظ إعدادات البحث
            st.success("تم حفظ إعدادات البحث بنجاح!")
    
    # إعدادات المستخدم
    with tabs[3]:
        st.subheader("إعدادات المستخدم")
        
        # معلومات المستخدم
        st.markdown(f"**معرف المستخدم**: {st.session_state.user_id}")
        
        # تغيير كلمة المرور (للتوضيح فقط)
        with st.form("change_password_form"):
            st.subheader("تغيير كلمة المرور")
            current_password = st.text_input("كلمة المرور الحالية", type="password")
            new_password = st.text_input("كلمة المرور الجديدة", type="password")
            confirm_password = st.text_input("تأكيد كلمة المرور الجديدة", type="password")
            
            submit_button = st.form_submit_button("تغيير كلمة المرور")
            
            if submit_button:
                if not current_password or not new_password or not confirm_password:
                    st.error("يرجى ملء جميع الحقول")
                elif new_password != confirm_password:
                    st.error("كلمة المرور الجديدة وتأكيدها غير متطابقين")
                else:
                    # هنا يمكن تنفيذ تغيير كلمة المرور
                    st.success("تم تغيير كلمة المرور بنجاح!")
        
        # حذف بيانات المحادثة
        st.subheader("إدارة البيانات")
        if st.button("حذف سجل المحادثات"):
            # حذف سجل المحادثات
            if "messages" in st.session_state:
                st.session_state.messages = []
            st.success("تم حذف سجل المحادثات بنجاح!")
    
    # حول التطبيق
    with tabs[4]:
        st.subheader("حول التطبيق")
        
        st.markdown("""
        ### مُرشد القرآن الذكي 🧠
        
        **الإصدار**: 0.1.0
        
        **وصف التطبيق**: مساعد ذكي متخصص في العلوم القرآنية والإسلامية، يجمع بين تقنيات الذكاء الاصطناعي والبحث الدلالي لتقديم تجربة تفاعلية فريدة للباحثين والمهتمين بالعلوم الإسلامية.
        
        **المميزات الرئيسية**:
        - محادثة ذكية مع نظام متخصص في العلوم القرآنية
        - بحث دلالي متقدم في القرآن الكريم
        - استكشاف المعجزات العلمية في القرآن
        - تحليل متقدم للنصوص القرآنية
        - الوصول إلى مكتبة شاملة من المراجع الإسلامية
        
        **التقنيات المستخدمة**:
        - نماذج لغوية متقدمة (LLMs) مع دعم قوي للغة العربية
        - تقنيات البحث الدلالي والتضمين النصي
        - استرجاع المعلومات المعزز بالذكاء الاصطناعي (RAG)
        - تخزين وإدارة الذاكرة المحلية
        
        **الترخيص**: هذا التطبيق مفتوح المصدر تحت رخصة MIT
        
        **المطورون**: فريق تطوير مُرشد القرآن الذكي
        """)
        
        # روابط مفيدة
        st.subheader("روابط مفيدة")
        st.markdown("""
        - [دليل المستخدم](https://example.com/user-guide)
        - [الإبلاغ عن مشكلة](https://example.com/report-issue)
        - [المساهمة في المشروع](https://example.com/contribute)
        - [الموقع الرسمي](https://example.com)
        """)


if __name__ == "__main__":
    # هذا للاختبار المستقل فقط
    render()