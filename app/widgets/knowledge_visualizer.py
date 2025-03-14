#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
مكون عرض المعرفة - واجهة مستخدم تفاعلية لعرض وتحليل المعرفة المكتسبة
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import networkx as nx
from typing import List, Dict, Any, Optional

class KnowledgeVisualizer:
    """مكون لعرض وتحليل المعرفة بشكل تفاعلي"""

    def __init__(self):
        """تهيئة مكون عرض المعرفة"""
        pass

    def render_progress_chart(self, progress_data: List[Dict[str, Any]]):
        """عرض مخطط تقدم التعلم

        Args:
            progress_data: بيانات التقدم في شكل قائمة من القواميس
        """
        if not progress_data:
            st.warning("لا توجد بيانات تقدم متاحة")
            return

        # تحويل البيانات إلى DataFrame
        df = pd.DataFrame(progress_data)

        # إنشاء مخطط خطي تفاعلي
        fig = px.line(df, x='date', y='progress',
                     title='تقدم التعلم عبر الزمن',
                     labels={'date': 'التاريخ', 'progress': 'نسبة التقدم'})

        # تخصيص المخطط
        fig.update_layout(
            directionality='rtl',
            plot_bgcolor='white',
            paper_bgcolor='white',
            font=dict(size=14)
        )

        # عرض المخطط
        st.plotly_chart(fig, use_container_width=True)

    def render_pattern_network(self, patterns: List[Dict[str, Any]]):
        """عرض شبكة الأنماط المكتشفة

        Args:
            patterns: قائمة الأنماط المكتشفة
        """
        if not patterns:
            st.warning("لا توجد أنماط مكتشفة")
            return

        # إنشاء رسم بياني
        G = nx.Graph()

        # إضافة العقد والحواف
        for pattern in patterns:
            G.add_node(pattern['name'], weight=pattern.get('confidence', 1.0))
            for related in pattern.get('related_patterns', []):
                G.add_edge(pattern['name'], related)

        # حساب تخطيط الرسم البياني
        pos = nx.spring_layout(G)

        # إنشاء مخطط تفاعلي
        edge_trace = go.Scatter(
            x=[], y=[],
            line=dict(width=0.5, color='#888'),
            hoverinfo='none',
            mode='lines')

        for edge in G.edges():
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            edge_trace['x'] += (x0, x1, None)
            edge_trace['y'] += (y0, y1, None)

        node_trace = go.Scatter(
            x=[], y=[],
            text=[],
            mode='markers+text',
            hoverinfo='text',
            marker=dict(
                showscale=True,
                colorscale='YlOrRd',
                size=20,
                colorbar=dict(title='الثقة')
            ))

        for node in G.nodes():
            x, y = pos[node]
            node_trace['x'] += (x,)
            node_trace['y'] += (y,)
            node_trace['text'] += (node,)

        # إنشاء الرسم البياني
        fig = go.Figure(data=[edge_trace, node_trace],
                     layout=go.Layout(
                         title='شبكة الأنماط المكتشفة',
                         showlegend=False,
                         hovermode='closest',
                         margin=dict(b=20,l=5,r=5,t=40),
                         plot_bgcolor='white'
                     ))

        # عرض الرسم البياني
        st.plotly_chart(fig, use_container_width=True)

    def render_insights_summary(self, insights: List[Dict[str, Any]]):
        """عرض ملخص الرؤى المكتشفة

        Args:
            insights: قائمة الرؤى المكتشفة
        """
        if not insights:
            st.warning("لا توجد رؤى مكتشفة")
            return

        # تصنيف الرؤى حسب النوع
        insights_by_type = {}
        for insight in insights:
            insight_type = insight.get('type', 'أخرى')
            if insight_type not in insights_by_type:
                insights_by_type[insight_type] = []
            insights_by_type[insight_type].append(insight)

        # إنشاء مخطط دائري للتوزيع
        fig = px.pie(values=[len(v) for v in insights_by_type.values()],
                    names=list(insights_by_type.keys()),
                    title='توزيع الرؤى حسب النوع')

        # تخصيص المخطط
        fig.update_layout(
            directionality='rtl',
            font=dict(size=14)
        )

        # عرض المخطط
        st.plotly_chart(fig, use_container_width=True)

        # عرض تفاصيل الرؤى
        for insight_type, type_insights in insights_by_type.items():
            with st.expander(f"{insight_type} ({len(type_insights)} رؤى)"):
                for insight in type_insights:
                    st.write(f"**{insight['title']}**")
                    st.write(insight['description'])
                    st.write("---")