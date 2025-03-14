#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
مكون لوحة المعرفة - يوفر واجهة تفاعلية لعرض وتحليل المعرفة القرآنية
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from typing import List, Dict, Any


class KnowledgeDashboard:
    """مكون لوحة المعرفة القرآنية"""

    def __init__(self):
        """تهيئة مكون لوحة المعرفة"""
        pass

    def render_quran_overview(self):
        """عرض نظرة عامة على القرآن الكريم"""
        st.subheader("نظرة عامة على القرآن الكريم")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("عدد السور", "114")

        with col2:
            st.metric("عدد الآيات", "6,236")

        with col3:
            st.metric("عدد الكلمات", "77,430")

    def render_surah_info(self, surah_data: List[Dict[str, Any]]):
        """عرض معلومات السور

        Args:
            surah_data: بيانات السور
        """
        st.subheader("معلومات السور")

        if not surah_data:
            st.warning("لا توجد بيانات متاحة للسور")
            return

        # عرض جدول السور
        df = pd.DataFrame(surah_data)
        st.dataframe(
            df,
            column_config={
                "name": "اسم السورة",
                "revelation_type": "نوع النزول",
                "ayah_count": "عدد الآيات",
            },
            hide_index=True,
        )

    def render_topic_analysis(self, topics: List[Dict[str, Any]]):
        """تحليل المواضيع في القرآن

        Args:
            topics: بيانات المواضيع
        """
        st.subheader("تحليل المواضيع")

        if not topics:
            st.warning("لا توجد بيانات متاحة للمواضيع")
            return

        # رسم بياني للمواضيع
        df = pd.DataFrame(topics)
        fig = px.treemap(
            df,
            path=["category", "subcategory"],
            values="count",
            title="المواضيع الرئيسية في القرآن الكريم",
        )
        fig.update_layout(font=dict(size=14, family="Arial"))
        st.plotly_chart(fig, use_container_width=True)

    def render_revelation_timeline(self, timeline_data: List[Dict[str, Any]]):
        """عرض الخط الزمني للنزول

        Args:
            timeline_data: بيانات النزول
        """
        st.subheader("الخط الزمني للنزول")

        if not timeline_data:
            st.warning("لا توجد بيانات متاحة للخط الزمني")
            return

        # رسم الخط الزمني
        df = pd.DataFrame(timeline_data)
        fig = go.Figure()

        fig.add_trace(
            go.Scatter(x=df["year"], y=df["surah_count"], mode="lines+markers", name="عدد السور")
        )

        fig.update_layout(
            title="توزيع نزول السور عبر السنوات",
            xaxis_title="السنة",
            yaxis_title="عدد السور",
            font=dict(size=12, family="Arial"),
        )

        st.plotly_chart(fig, use_container_width=True)
