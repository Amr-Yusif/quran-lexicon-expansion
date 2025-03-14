# -*- coding: utf-8 -*-

"""
تكوين التطبيق - إعدادات وتهيئة صفحات التطبيق
"""

import streamlit as st


def init_page_config():
    """تهيئة تكوين الصفحة الرئيسية"""
    st.set_page_config(
        page_title="نظام استكشاف وتحليل النصوص الإسلامية المتكامل",
        page_icon="🕌",
        layout="wide",
        initial_sidebar_state="expanded",
        menu_items={
            "Get Help": "https://github.com/yourusername/quran-app/wiki",
            "Report a bug": "https://github.com/yourusername/quran-app/issues",
            "About": """
            ## نظام استكشاف وتحليل النصوص الإسلامية المتكامل
            
            منصة متقدمة للتحليل والاستكشاف في القرآن الكريم والنصوص الإسلامية.
            
            * البحث الدلالي المتقدم
            * تحليل المواضيع والمفاهيم
            * اكتشاف المعجزات العلمية
            * التفاعل الذكي مع النصوص
            """,
        },
    )

    # تخصيص نمط الصفحة
    st.markdown(
        """
    <style>
    .main {
        background-color: #f8f9fa;
    }
    .stButton>button {
        background-color: #198754;
        color: white;
    }
    .stProgress .st-bo {
        background-color: #198754;
    }
    .stTextInput>div>div>input {
        text-align: right;
    }
    </style>
    """,
        unsafe_allow_html=True,
    )
