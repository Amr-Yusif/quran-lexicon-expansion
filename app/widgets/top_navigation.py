#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
مكون التنقل العلوي - يوفر شريط تنقل أفقي جذاب في أعلى التطبيق
"""

import streamlit as st
from streamlit_option_menu import option_menu


def render_top_navigation():
    """عرض شريط التنقل العلوي"""

    selected = option_menu(
        menu_title=None,
        options=[
            "المحادثة",
            "الاستكشاف",
            "لوحة المعرفة",
            "المعجزات",
            "تحسين الأداء",
            "المصادر",
            "البحث",
            "الإعدادات",
        ],
        icons=[
            "chat-dots",
            "compass",
            "graph-up",
            "stars",
            "speedometer2",
            "book",
            "search",
            "gear",
        ],
        menu_icon="cast",
        default_index=0,
        orientation="horizontal",
        styles={
            "container": {
                "padding": "0!important",
                "background-color": "#fafafa",
                "margin": "0!important",
                "width": "100%",
                "direction": "rtl",
            },
            "icon": {"color": "#1f6f3d", "font-size": "1rem", "margin-right": "0.5rem"},
            "nav-link": {
                "font-size": "1rem",
                "text-align": "right",
                "margin": "0px",
                "padding": "0.5rem 1rem",
                "display": "flex",
                "align-items": "center",
                "justify-content": "flex-end",
                "white-space": "nowrap",
                "color": "#2c3e50",
            },
            "nav-link-selected": {
                "background-color": "#1f6f3d",
                "color": "white",
                "font-weight": "600",
            },
        },
    )

    return selected
