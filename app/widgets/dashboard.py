#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
مكون لوحة المعرفة - يوفر واجهة تفاعلية لعرض وتحليل المعرفة الإسلامية
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from typing import List, Dict, Any


class KnowledgeDashboard:
    """مكون لوحة المعرفة الإسلامية"""

    def __init__(self):
        """تهيئة مكون لوحة المعرفة"""
        pass

    def render_topic_distribution(self, topics: List[Dict[str, Any]]):
        """عرض توزيع المواضيع

        Args:
            topics: قائمة المواضيع مع إحصائياتها
        """
        if not topics:
            st.warning("لا توجد بيانات متاحة للمواضيع")
            return

        df = pd.DataFrame(topics)
        fig = px.pie(df, values="count", names="topic", title="توزيع المواضيع في القرآن الكريم")
        fig.update_layout(
            font=dict(size=14),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        )
        st.plotly_chart(fig, use_container_width=True)

    def render_surah_stats(self, surah_data: List[Dict[str, Any]]):
        """عرض إحصائيات السور

        Args:
            surah_data: بيانات السور وإحصائياتها
        """
        if not surah_data:
            st.warning("لا توجد بيانات متاحة للسور")
            return

        df = pd.DataFrame(surah_data)
        fig = px.bar(
            df,
            x="name",
            y="ayah_count",
            title="عدد الآيات في كل سورة",
            labels={"name": "اسم السورة", "ayah_count": "عدد الآيات"},
        )
        fig.update_layout(xaxis_tickangle=-45, font=dict(size=12), height=500)
        st.plotly_chart(fig, use_container_width=True)

    def render_miracle_categories(self, miracle_data: List[Dict[str, Any]]):
        """عرض فئات المعجزات

        Args:
            miracle_data: بيانات المعجزات وفئاتها
        """
        if not miracle_data:
            st.warning("لا توجد بيانات متاحة للمعجزات")
            return

        df = pd.DataFrame(miracle_data)
        fig = px.treemap(
            df, path=["category", "subcategory"], values="count", title="تصنيف المعجزات القرآنية"
        )
        fig.update_layout(font=dict(size=14))
        st.plotly_chart(fig, use_container_width=True)

    def render_search_trends(self, trend_data: List[Dict[str, Any]]):
        """عرض اتجاهات البحث

        Args:
            trend_data: بيانات اتجاهات البحث
        """
        if not trend_data:
            st.warning("لا توجد بيانات متاحة لاتجاهات البحث")
            return

        df = pd.DataFrame(trend_data)
        fig = px.line(
            df,
            x="date",
            y="count",
            color="term",
            title="اتجاهات البحث عبر الزمن",
            labels={"date": "التاريخ", "count": "عدد عمليات البحث", "term": "مصطلح البحث"},
        )
        fig.update_layout(
            xaxis_tickangle=-45,
            font=dict(size=12),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        )
        st.plotly_chart(fig, use_container_width=True)
