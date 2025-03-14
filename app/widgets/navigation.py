#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
مكون التنقل - يوفر واجهة تنقل موحدة للتطبيق
"""

import streamlit as st
from streamlit_option_menu import option_menu


def render_navigation():
    """عرض قائمة التنقل الرئيسية"""

    with st.sidebar:
        selected = option_menu(
            "القائمة الرئيسية",
            [
                # مجموعة التحليل
                {"label": "البحث", "icon": "search"},
                {"label": "الاستكشاف", "icon": "compass"},
                # مجموعة المعرفة
                {"label": "المعجزات", "icon": "stars"},
                {"label": "المصادر", "icon": "book"},
                # مجموعة التفاعل
                {"label": "المحادثة", "icon": "chat-dots"},
                # الإعدادات
                {"label": "الإعدادات", "icon": "gear"},
            ],
            icons=["search", "compass", "stars", "book", "chat-dots", "gear"],
            menu_icon="app-indicator",
            default_index=0,
            styles={
                "container": {"padding": "5!important", "background-color": "#fafafa"},
                "icon": {"color": "orange", "font-size": "25px"},
                "nav-link": {"font-size": "16px", "text-align": "right", "margin": "0px"},
                "nav-link-selected": {"background-color": "#02ab21"},
            },
        )

        return selected
