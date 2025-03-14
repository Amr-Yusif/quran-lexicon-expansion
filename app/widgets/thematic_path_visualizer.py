#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
مكون عرض المسارات الموضوعية - واجهة مستخدم تفاعلية لعرض وتحليل المسارات الموضوعية في النصوص القرآنية
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import networkx as nx
from typing import List, Dict, Any, Optional, Tuple
import numpy as np
from pathlib import Path
import json

class ThematicPathVisualizer:
    """مكون لعرض وتحليل المسارات الموضوعية في النصوص القرآنية بشكل تفاعلي"""

    def __init__(self, data_dir: str = "data/concepts"):
        """تهيئة مكون عرض المسارات الموضوعية
        
        Args:
            data_dir: مسار دليل البيانات
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # تحميل بيانات المسارات الموضوعية إذا كانت موجودة
        self.thematic_paths_file = self.data_dir / "thematic_paths.json"
        self.thematic_paths = self._load_thematic_paths()
        
        # ألوان للمسارات المختلفة
        self.colors = px.colors.qualitative.Plotly
    
    def _load_thematic_paths(self) -> List[Dict[str, Any]]:
        """تحميل بيانات المسارات الموضوعية
        
        Returns:
            قائمة المسارات الموضوعية
        """
        if self.thematic_paths_file.exists():
            try:
                with open(self.thematic_paths_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                st.error(f"خطأ في تحميل ملف المسارات الموضوعية: {str(e)}")
                return []
        return []
    
    def render_thematic_path_explorer(self):
        """عرض مستكشف المسارات الموضوعية"""
        st.subheader("📊 مستكشف المسارات الموضوعية")
        
        if not self.thematic_paths:
            st.info("لا توجد مسارات موضوعية متاحة حاليًا. يمكنك إنشاء مسارات جديدة من خلال البحث والاستكشاف.")
            return
        
        # اختيار المسار الموضوعي
        path_names = [path["name"] for path in self.thematic_paths]
        selected_path_name = st.selectbox("اختر المسار الموضوعي", path_names)
        
        # العثور على المسار المحدد
        selected_path = next((path for path in self.thematic_paths if path["name"] == selected_path_name), None)
        
        if selected_path:
            # عرض معلومات المسار
            st.write(f"**الوصف:** {selected_path.get('description', '')}")
            
            # عرض المسار كمخطط شبكي
            self._render_path_network(selected_path)
            
            # عرض الآيات المرتبطة
            self._render_path_verses(selected_path)
            
            # عرض الإحصائيات والتحليلات
            self._render_path_analytics(selected_path)
    
    def _render_path_network(self, path: Dict[str, Any]):
        """عرض المسار الموضوعي كمخطط شبكي
        
        Args:
            path: بيانات المسار الموضوعي
        """
        st.subheader("شبكة المفاهيم والعلاقات")
        
        # إنشاء الرسم البياني
        G = nx.DiGraph()
        
        # إضافة العقد (المفاهيم)
        concepts = path.get("concepts", [])
        for concept in concepts:
            G.add_node(concept["name"], weight=concept.get("weight", 1.0))
        
        # إضافة الحواف (العلاقات)
        relationships = path.get("relationships", [])
        for rel in relationships:
            G.add_edge(
                rel["source"], 
                rel["target"], 
                type=rel.get("type", "related"),
                weight=rel.get("weight", 1.0)
            )
        
        # التحقق من وجود عقد وحواف
        if not G.nodes or not G.edges:
            st.info("لا توجد بيانات كافية لعرض الشبكة")
            return
        
        # حساب تخطيط الرسم البياني
        pos = nx.spring_layout(G, seed=42)
        
        # إنشاء آثار الحواف
        edge_traces = []
        for edge in G.edges(data=True):
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            edge_type = edge[2].get("type", "related")
            edge_weight = edge[2].get("weight", 1.0)
            
            # تحديد لون ونمط الخط بناءً على نوع العلاقة
            if edge_type == "causes":
                line_dash = "solid"
                color = "#FF5733"
            elif edge_type == "supports":
                line_dash = "dot"
                color = "#33FF57"
            else:  # related
                line_dash = "dash"
                color = "#3357FF"
            
            # إنشاء أثر الحافة
            edge_trace = go.Scatter(
                x=[x0, x1, None],
                y=[y0, y1, None],
                line=dict(width=edge_weight*2, color=color, dash=line_dash),
                hoverinfo="text",
                text=f"{edge[0]} → {edge[1]} ({edge_type})",
                mode="lines"
            )
            edge_traces.append(edge_trace)
        
        # إنشاء أثر العقد
        node_x = []
        node_y = []
        node_text = []
        node_size = []
        
        for node in G.nodes(data=True):
            x, y = pos[node[0]]
            node_x.append(x)
            node_y.append(y)
            node_text.append(node[0])
            # حجم العقدة بناءً على الوزن أو عدد الاتصالات
            size = node[1].get("weight", 1.0) * 20
            node_size.append(size)
        
        node_trace = go.Scatter(
            x=node_x,
            y=node_y,
            text=node_text,
            mode="markers+text",
            hoverinfo="text",
            marker=dict(
                showscale=True,
                colorscale="YlGnBu",
                size=node_size,
                color=[len(list(G.neighbors(node))) for node in G.nodes()],
                colorbar=dict(title="عدد الاتصالات")
            ),
            textposition="top center"
        )
        
        # إنشاء الرسم البياني
        fig = go.Figure(
            data=edge_traces + [node_trace],
            layout=go.Layout(
                title=f"شبكة المفاهيم: {path['name']}",
                showlegend=False,
                hovermode="closest",
                margin=dict(b=20, l=5, r=5, t=40),
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                plot_bgcolor="white"
            )
        )
        
        # عرض الرسم البياني
        st.plotly_chart(fig, use_container_width=True)
        
        # عرض مفتاح العلاقات
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("<span style='color:#FF5733'>▬▬▬</span> سببية", unsafe_allow_html=True)
        with col2:
            st.markdown("<span style='color:#33FF57'>····</span> داعمة", unsafe_allow_html=True)
        with col3:
            st.markdown("<span style='color:#3357FF'>- - -</span> مرتبطة", unsafe_allow_html=True)
    
    def _render_path_verses(self, path: Dict[str, Any]):
        """عرض الآيات المرتبطة بالمسار الموضوعي
        
        Args:
            path: بيانات المسار الموضوعي
        """
        st.subheader("الآيات المرتبطة بالمسار")
        
        verses = path.get("verses", [])
        if not verses:
            st.info("لا توجد آيات مرتبطة بهذا المسار")
            return
        
        # عرض الآيات في جدول
        df = pd.DataFrame(verses)
        if "relevance" in df.columns:
            df = df.sort_values("relevance", ascending=False)
        
        # تنسيق الجدول
        if "surah" in df.columns and "ayah" in df.columns:
            df["reference"] = df["surah"].astype(str) + ":" + df["ayah"].astype(str)
        
        # اختيار الأعمدة للعرض
        display_columns = ["text", "reference"]
        if "relevance" in df.columns:
            display_columns.append("relevance")
            df["relevance"] = df["relevance"].round(2)
        
        # عرض الجدول
        st.dataframe(df[display_columns], use_container_width=True)
    
    def _render_path_analytics(self, path: Dict[str, Any]):
        """عرض إحصائيات وتحليلات المسار الموضوعي
        
        Args:
            path: بيانات المسار الموضوعي
        """
        st.subheader("إحصائيات وتحليلات")
        
        # استخراج البيانات
        concepts = path.get("concepts", [])
        relationships = path.get("relationships", [])
        verses = path.get("verses", [])
        
        # عرض الإحصائيات الأساسية
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("عدد المفاهيم", len(concepts))
        with col2:
            st.metric("عدد العلاقات", len(relationships))
        with col3:
            st.metric("عدد الآيات", len(verses))
        
        # عرض توزيع أنواع العلاقات
        if relationships:
            rel_types = {}
            for rel in relationships:
                rel_type = rel.get("type", "related")
                rel_types[rel_type] = rel_types.get(rel_type, 0) + 1
            
            # إنشاء مخطط دائري
            fig = px.pie(
                values=list(rel_types.values()),
                names=list(rel_types.keys()),
                title="توزيع أنواع العلاقات"
            )
            
            # تخصيص المخطط
            fig.update_layout(
                directionality="rtl",
                font=dict(size=14)
            )
            
            # عرض المخطط
            st.plotly_chart(fig, use_container_width=True)
        
        # عرض توزيع الآيات حسب السور
        if verses and any("surah" in verse for verse in verses):
            surah_counts = {}
            for verse in verses:
                if "surah" in verse:
                    surah = verse["surah"]
                    surah_counts[surah] = surah_counts.get(surah, 0) + 1
            
            # تحويل إلى DataFrame للترتيب
            df_surah = pd.DataFrame({
                "سورة": list(surah_counts.keys()),
                "عدد الآيات": list(surah_counts.values())
            })
            df_surah = df_surah.sort_values("عدد الآيات", ascending=False)
            
            # إنشاء مخطط شريطي
            fig = px.bar(
                df_surah,
                x="سورة",
                y="عدد الآيات",
                title="توزيع الآيات حسب السور",
                color="عدد الآيات",
                color_continuous_scale="Viridis"
            )
            
            # تخصيص المخطط
            fig.update_layout(
                xaxis_title="السورة",
                yaxis_title="عدد الآيات",
                directionality="rtl",
                font=dict(size=14)
            )
            
            # عرض المخ