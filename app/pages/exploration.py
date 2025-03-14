#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
صفحة الاستكشاف والفرضيات - واجهة مستخدم لاستكشاف المفاهيم وتوليد الفرضيات في النصوص القرآنية
"""

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import json
import networkx as nx
from pathlib import Path
import os
from typing import List, Dict, Any, Optional

# استيراد المكونات الضرورية من المشروع
from core.explorer.systematic_explorer import SystematicExplorer
from core.utils.config import get_config
from subscription.user_manager import UserManager

# استيراد مكونات مساعدة لعرض البيانات
try:
    import plotly.graph_objects as go
    import plotly.express as px

    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False


class ExplorationInterface:
    """
    واجهة لاستكشاف المفاهيم وتوليد الفرضيات في النصوص القرآنية
    """

    def __init__(self, user_manager: UserManager = None):
        """
        تهيئة واجهة الاستكشاف والفرضيات

        Args:
            user_manager: مدير المستخدمين (اختياري)
        """
        # تهيئة مدير التكوين
        self.config = get_config()

        # تهيئة نظام الاستكشاف المنظم
        self.explorer = SystematicExplorer()

        # تهيئة مدير المستخدمين
        self.user_manager = user_manager

        # تهيئة مسارات البيانات
        self.data_dir = Path(self.config.get_data_path("concepts"))

        # تحميل بيانات المفاهيم إذا كانت موجودة
        self.concepts_file = self.data_dir / "concepts.json"
        if self.concepts_file.exists():
            self.explorer.load_concepts(str(self.concepts_file))

        # تهيئة متغيرات الحالة
        self.current_concept = None
        self.current_hypothesis = None

    def render(self):
        """عرض واجهة الاستكشاف والفرضيات"""
        st.title("🔍 الاستكشاف والفرضيات في النصوص القرآنية")

        # إنشاء تبويبات لوظائف مختلفة
        tabs = st.tabs(
            [
                "استكشاف المفاهيم",
                "توليد الفرضيات",
                "التحقق من الفرضيات",
                "رسم المعرفة",
                "الإعدادات المتقدمة",
            ]
        )

        # تبويب استكشاف المفاهيم
        with tabs[0]:
            self._render_concept_exploration_tab()

        # تبويب توليد الفرضيات
        with tabs[1]:
            self._render_hypothesis_generation_tab()

        # تبويب التحقق من الفرضيات
        with tabs[2]:
            self._render_hypothesis_verification_tab()

        # تبويب رسم المعرفة
        with tabs[3]:
            self._render_knowledge_graph_tab()

        # تبويب الإعدادات المتقدمة
        with tabs[4]:
            self._render_advanced_settings_tab()

    def _render_concept_exploration_tab(self):
        """عرض تبويب استكشاف المفاهيم"""
        st.header("استكشاف المفاهيم")

        # تقسيم الشاشة إلى عمودين
        col1, col2 = st.columns([1, 2])

        with col1:
            # اختيار المفهوم
            concept_options = list(self.explorer.concepts.keys())
            if concept_options:
                selected_concept = st.selectbox("اختر مفهومًا للاستكشاف:", options=concept_options)

                # إعدادات الاستكشاف
                exploration_depth = st.slider(
                    "عمق الاستكشاف:",
                    min_value=1,
                    max_value=5,
                    value=self.explorer.config["max_exploration_depth"],
                )

                # زر الاستكشاف
                if st.button("استكشاف المفهوم"):
                    with st.spinner("جارٍ استكشاف المفهوم..."):
                        self.current_concept = selected_concept
                        exploration_result = self.explorer.explore_concept(
                            concept_name=selected_concept, max_depth=exploration_depth
                        )
                        st.session_state.exploration_result = exploration_result
                        st.success(f"تم استكشاف المفهوم: {selected_concept}")
            else:
                st.warning("لا توجد مفاهيم متاحة. يرجى إضافة مفاهيم أولاً.")

                # نموذج إضافة مفهوم جديد
                with st.form("add_concept_form"):
                    st.subheader("إضافة مفهوم جديد")
                    concept_name = st.text_input("اسم المفهوم:")
                    concept_description = st.text_area("وصف المفهوم:")
                    concept_category = st.selectbox(
                        "فئة المفهوم:", options=["عقيدة", "فقه", "تفسير", "علوم قرآنية", "أخرى"]
                    )

                    # زر الإضافة
                    submit_button = st.form_submit_button("إضافة المفهوم")
                    if submit_button and concept_name and concept_description:
                        # إضافة المفهوم
                        self.explorer.concepts[concept_name] = {
                            "name": concept_name,
                            "description": concept_description,
                            "category": concept_category,
                            "related_concepts": [],
                        }
                        st.success(f"تم إضافة المفهوم: {concept_name}")

        with col2:
            # عرض نتائج الاستكشاف
            if hasattr(st.session_state, "exploration_result"):
                exploration_result = st.session_state.exploration_result

                # عرض المفهوم الرئيسي
                st.subheader(f"المفهوم الرئيسي: {exploration_result['main_concept']}")
                main_concept_data = exploration_result["explored_concepts"][
                    exploration_result["main_concept"]
                ]
                st.write(f"**الوصف:** {main_concept_data.get('description', 'لا يوجد وصف')}")
                st.write(f"**الفئة:** {main_concept_data.get('category', 'غير مصنف')}")

                # عرض المفاهيم المرتبطة
                st.subheader("المفاهيم المرتبطة:")
                related_concepts = [
                    c
                    for c in exploration_result["explored_concepts"].keys()
                    if c != exploration_result["main_concept"]
                ]

                if related_concepts:
                    for concept in related_concepts:
                        concept_data = exploration_result["explored_concepts"][concept]
                        with st.expander(f"{concept}"):
                            st.write(f"**الوصف:** {concept_data.get('description', 'لا يوجد وصف')}")
                            st.write(f"**الفئة:** {concept_data.get('category', 'غير مصنف')}")
                else:
                    st.info("لا توجد مفاهيم مرتبطة.")

    def _render_hypothesis_generation_tab(self):
        """عرض تبويب توليد الفرضيات"""
        st.header("توليد الفرضيات")

        # تقسيم الشاشة إلى عمودين
        col1, col2 = st.columns([1, 2])

        with col1:
            # اختيار المفهوم الأول
            concept_options = list(self.explorer.concepts.keys())
            if concept_options:
                selected_concept1 = st.selectbox(
                    "اختر المفهوم الأول:", options=concept_options, key="concept1"
                )

                # اختيار المفهوم الثاني (اختياري)
                use_second_concept = st.checkbox("إضافة مفهوم ثانٍ للفرضية")
                selected_concept2 = None
                if use_second_concept:
                    selected_concept2 = st.selectbox(
                        "اختر المفهوم الثاني:",
                        options=[c for c in concept_options if c != selected_concept1],
                        key="concept2",
                    )

                # زر توليد الفرضية
                if st.button("توليد فرضية"):
                    with st.spinner("جارٍ توليد الفرضية..."):
                        hypothesis = self.explorer.generate_hypothesis(
                            concept_name=selected_concept1,
                            related_concept=selected_concept2 if use_second_concept else None,
                        )
                        st.session_state.current_hypothesis = hypothesis
                        st.success("تم توليد الفرضية بنجاح")
            else:
                st.warning("لا توجد مفاهيم متاحة. يرجى إضافة مفاهيم أولاً.")

        with col2:
            # عرض الفرضية الحالية
            if hasattr(st.session_state, "current_hypothesis"):
                hypothesis = st.session_state.current_hypothesis

                if "error" in hypothesis:
                    st.error(hypothesis["error"])
                else:
                    st.subheader("الفرضية المولدة:")
                    st.write(f"**الوصف:** {hypothesis['description']}")
                    st.write(f"**المفاهيم:** {', '.join(hypothesis['concepts'])}")
                    st.write(f"**النوع:** {hypothesis['type']}")
                    st.write(f"**الثقة:** {hypothesis['confidence']:.2f}")
                    st.write(f"**الحالة:** {hypothesis['status']}")

                    # عرض الأدلة
                    if hypothesis["evidence"]:
                        st.subheader("الأدلة:")
                        for evidence in hypothesis["evidence"]:
                            st.write(f"- {evidence['description']}")
                    else:
                        st.info("لا توجد أدلة متاحة بعد.")

    def _render_hypothesis_verification_tab(self):
        """عرض تبويب التحقق من الفرضيات"""
        st.header("التحقق من الفرضيات")

        # عرض الفرضيات الحالية
        if self.explorer.hypotheses:
            # اختيار الفرضية
            hypothesis_options = [h["description"] for h in self.explorer.hypotheses]
            selected_hypothesis_idx = st.selectbox(
                "اختر فرضية للتحقق منها:",
                options=range(len(hypothesis_options)),
                format_func=lambda i: hypothesis_options[i],
            )

            selected_hypothesis = self.explorer.hypotheses[selected_hypothesis_idx]

            # عرض تفاصيل الفرضية
            st.subheader("تفاصيل الفرضية:")
            st.write(f"**الوصف:** {selected_hypothesis['description']}")
            st.write(f"**المفاهيم:** {', '.join(selected_hypothesis['concepts'])}")
            st.write(f"**الثقة:** {selected_hypothesis['confidence']:.2f}")
            st.write(f"**الحالة:** {selected_hypothesis['status']}")

            # إضافة دليل جديد
            st.subheader("إضافة دليل جديد:")
            with st.form("add_evidence_form"):
                evidence_description = st.text_area("وصف الدليل:")
                evidence_source = st.text_input("مصدر الدليل:")
                evidence_strength = st.slider(
                    "قوة الدليل:", min_value=0.1, max_value=1.0, value=0.5, step=0.1
                )

                # زر الإضافة
                submit_button = st.form_submit_button("إضافة الدليل")
                if submit_button and evidence_description and evidence_source:
                    # إضافة الدليل
                    evidence = {
                        "description": evidence_description,
                        "source": evidence_source,
                        "strength": evidence_strength,
                    }
                    success = self.explorer.add_evidence(selected_hypothesis["id"], evidence)
                    if success:
                        st.success("تم إضافة الدليل بنجاح")
                        # تحديث الفرضية في واجهة المستخدم
                        st.experimental_rerun()
                    else:
                        st.error("فشل في إضافة الدليل")
            
            # أزرار تحديث حالة الفرضية
            st.subheader("تحديث حالة الفرضية:")
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("تأكيد الفرضية"):
                    self.explorer.update_hypothesis_status(selected_hypothesis["id"], "confirmed")
                    st.success("تم تأكيد الفرضية")
                    st.experimental_rerun()
            with col2:
                if st.button("رفض الفرضية"):
                    self.explorer.update_hypothesis_status(selected_hypothesis["id"], "rejected")
                    st.success("تم رفض الفرضية")
                    st.experimental_rerun()
            with col3:
                if st.button("تعليق الفرضية"):
                    self.explorer.update_hypothesis_status(selected_hypothesis["id"], "pending")
                    st.success("تم تعليق الفرضية")
                    st.experimental_rerun()
        else:
            st.info("لا توجد فرضيات متاحة. يرجى توليد فرضيات أولاً.")
    
    def _render_knowledge_graph_tab(self):
        """عرض تبويب رسم المعرفة"""
        st.header("رسم المعرفة")
        
        # التحقق من وجود مفاهيم
        if not self.explorer.concepts:
            st.warning("لا توجد مفاهيم متاحة لعرض رسم المعرفة.")
            return
        
        # إعدادات الرسم
        st.subheader("إعدادات الرسم:")
        col1, col2 = st.columns(2)
        with col1:
            show_all_concepts = st.checkbox("عرض جميع المفاهيم", value=True)
            show_hypotheses = st.checkbox("عرض الفرضيات", value=True)
        with col2:
            graph_layout = st.selectbox(
                "نوع التخطيط:",
                options=["spring", "circular", "random", "kamada_kawai"],
                format_func=lambda x: {
                    "spring": "زنبركي",
                    "circular": "دائري",
                    "random": "عشوائي",
                    "kamada_kawai": "كامادا-كاواي"
                }.get(x, x)
            )
        
        # إنشاء الرسم البياني
        if PLOTLY_AVAILABLE:
            # إنشاء رسم تفاعلي باستخدام Plotly
            self._render_plotly_graph(show_all_concepts, show_hypotheses, graph_layout)
        else:
            # إنشاء رسم باستخدام Matplotlib
            self._render_matplotlib_graph(show_all_concepts, show_hypotheses, graph_layout)
    
    def _render_plotly_graph(self, show_all_concepts: bool, show_hypotheses: bool, layout: str):
        """إنشاء رسم تفاعلي باستخدام Plotly"""
        # إنشاء الرسم البياني
        G = nx.Graph()
        
        # إضافة المفاهيم كعقد
        for concept_name, concept_data in self.explorer.concepts.items():
            G.add_node(concept_name, type="concept", category=concept_data.get("category", "غير مصنف"))
        
        # إضافة العلاقات بين المفاهيم
        for relation in self.explorer.concept_relations:
            G.add_edge(relation["source"], relation["target"], type=relation["type"])
        
        # إضافة الفرضيات إذا كان مطلوبًا
        if show_hypotheses and self.explorer.hypotheses:
            for hypothesis in self.explorer.hypotheses:
                # إضافة الفرضية كعقدة
                hypothesis_id = hypothesis["id"]
                G.add_node(hypothesis_id, type="hypothesis", status=hypothesis["status"])
                
                # إضافة العلاقات بين الفرضية والمفاهيم
                for concept in hypothesis["concepts"]:
                    G.add_edge(hypothesis_id, concept, type="hypothesis_concept")
        
        # حساب تخطيط الرسم البياني
        if layout == "spring":
            pos = nx.spring_layout(G)
        elif layout == "circular":
            pos = nx.circular_layout(G)
        elif layout == "random":
            pos = nx.random_layout(G)
        else:  # kamada_kawai
            pos = nx.kamada_kawai_layout(G)
        
        # إنشاء قوائم للعقد والحواف
        edge_x = []
        edge_y = []
        for edge in G.edges():
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            edge_x.extend([x0, x1, None])
            edge_y.extend([y0, y1, None])
        
        # إنشاء آثار الحواف
        edge_trace = go.Scatter(
            x=edge_x, y=edge_y,
            line=dict(width=0.5, color='#888'),
            hoverinfo='none',
            mode='lines')
        
        # إنشاء قوائم للعقد
        node_x = []
        node_y = []
        node_text = []
        node_color = []
        
        for node in G.nodes():
            x, y = pos[node]
            node_x.append(x)
            node_y.append(y)
            
            # تحديد نص العقدة ولونها
            if G.nodes[node]["type"] == "concept":
                node_text.append(node)
                node_color.append(0)  # أزرق للمفاهيم
            else:  # hypothesis
                node_text.append(f"فرضية: {node}")
                # تحديد اللون حسب حالة الفرضية
                if G.nodes[node]["status"] == "confirmed":
                    node_color.append(1)  # أخضر للفرضيات المؤكدة
                elif G.nodes[node]["status"] == "rejected":
                    node_color.append(2)  # أحمر للفرضيات المرفوضة
                else:
                    node_color.append(3)  # أصفر للفرضيات المعلقة
        
        # إنشاء آثار العقد
        node_trace = go.Scatter(
            x=node_x, y=node_y,
            mode='markers+text',
            text=node_text,
            textposition="top center",
            hoverinfo='text',
            marker=dict(
                showscale=True,
                colorscale=[[0, 'rgb(41, 128, 185)'], [0.33, 'rgb(39, 174, 96)'], 
                            [0.66, 'rgb(192, 57, 43)'], [1, 'rgb(243, 156, 18)']],
                color=node_color,
                size=15,
                colorbar=dict(
                    thickness=15,
                    title='نوع العقدة',
                    xanchor='left',
                    titleside='right',
                    tickvals=[0, 1, 2, 3],
                    ticktext=['مفهوم', 'فرضية مؤكدة', 'فرضية مرفوضة', 'فرضية معلقة']
                ),
                line_width=2))
        
        # إنشاء الرسم البياني
        fig = go.Figure(data=[edge_trace, node_trace],
                        layout=go.Layout(
                            title='رسم المعرفة والفرضيات',
                            titlefont_size=16,
                            showlegend=False,
                            hovermode='closest',
                            margin=dict(b=20, l=5, r=5, t=40),
                            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False))
                        )
        
        # عرض الرسم البياني
        st.plotly_chart(fig, use_container_width=True)
    
    def _render_matplotlib_graph(self, show_all_concepts: bool, show_hypotheses: bool, layout: str):
        """إنشاء رسم باستخدام Matplotlib"""
        # إنشاء الرسم البياني
        G = nx.Graph()
        
        # إضافة المفاهيم كعقد
        for concept_name, concept_data in self.explorer.concepts.items():
            G.add_node(concept_name, type="concept", category=concept_data.get("category", "غير مصنف"))
        
        # إضافة العلاقات بين المفاهيم
        for relation in self.explorer.concept_relations:
            G.add_edge(relation["source"], relation["target"], type=relation["type"])
        
        # إضافة الفرضيات إذا كان مطلوبًا
        if show_hypotheses and self.explorer.hypotheses:
            for hypothesis in self.explorer.hypotheses:
                # إضافة الفرضية كعقدة
                hypothesis_id = hypothesis["id"]
                G.add_node(hypothesis_id, type="hypothesis", status=hypothesis["status"])
                
                # إضافة العلاقات بين الفرضية والمفاهيم
                for concept in hypothesis["concepts"]:
                    G.add_edge(hypothesis_id, concept, type="hypothesis_concept")
        
        # إنشاء الشكل
        fig, ax = plt.subplots(figsize=(10, 8))
        
        # حساب تخطيط الرسم البياني
        if layout == "spring":
            pos = nx.spring_layout(G)
        elif layout == "circular":
            pos = nx.circular_layout(G)
        elif layout == "random":
            pos = nx.random_layout(G)
        else:  # kamada_kawai
            pos = nx.kamada_kawai_layout(G)
        
        # تحديد ألوان العقد
        node_colors = []
        for node in G.nodes():
            if G.nodes[node]["type"] == "concept":
                node_colors.append("skyblue")
            else:  # hypothesis
                if G.nodes[node]["status"] == "confirmed":
                    node_colors.append("green")
                elif G.nodes[node]["status"] == "rejected":
                    node_colors.append("red")
                else:
                    node_colors.append("yellow")
        
        # رسم العقد
        nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=500, alpha=0.8, ax=ax)
        
        # رسم الحواف
        nx.draw_networkx_edges(G, pos, width=1.0, alpha=0.5, ax=ax)
        
        # رسم التسميات
        nx.draw_networkx_labels(G, pos, font_size=10, font_family="sans-serif", ax=ax)
        
        # تعديل الشكل
        plt.title("رسم المعرفة والفرضيات")
        plt.axis("off")
        
        # عرض الرسم البياني
        st.pyplot(fig)
    
    def _render_advanced_settings_tab(self):
        """عرض تبويب الإعدادات المتقدمة"""
        st.header("الإعدادات المتقدمة")
        
        # عرض الإعدادات الحالية
        st.subheader("الإعدادات الحالية:")
        
        # تحديث الإعدادات
        with st.form("update_settings_form"):
            min_evidence = st.slider(
                "الحد الأدنى للأدلة المطلوبة لتأكيد فرضية:",
                min_value=1,
                max_value=10,
                value=self.explorer.config["min_evidence_threshold"]
            )
            
            confidence_threshold = st.slider(
                "عتبة الثقة للفرضيات:",
                min_value=0.1,
                max_value=1.0,
                value=self.explorer.config["confidence_threshold"],
                step=0.1
            )
            
            max_exploration_depth = st.slider(
                "أقصى عمق للاستكشاف:",
                min_value=1,
                max_value=10,
                value=self.explorer.config["max_exploration_depth"]
            )
            
            enable_active_learning = st.checkbox(
                "تمكين التعلم النشط",
                value=self.explorer.config["enable_active_learning"]
            )
            
            # زر التحديث
            submit_button = st.form_submit_button("تحديث الإعدادات")
            if submit_button:
                # تحديث الإعدادات
                self.explorer.config["min_evidence_threshold"] = min_evidence
                self.explorer.config["confidence_threshold"] = confidence_threshold
                self.explorer.config["max_exploration_depth"] = max_exploration_depth
                self.explorer.config["enable_active_learning"] = enable_active_learning
                
                st.success("تم تحديث الإعدادات بنجاح")
        
        # خيارات حفظ وتحميل البيانات
        st.subheader("حفظ وتحميل البيانات:")
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("حفظ المفاهيم والفرضيات"):
                # إنشاء مجلد البيانات إذا لم يكن موجودًا
                self.data_dir.mkdir(parents=True, exist_ok=True)
                
                # حفظ المفاهيم
                with open(str(self.concepts_file), 'w', encoding='utf-8') as f:
                    json.dump(self.explorer.concepts, f, ensure_ascii=False, indent=4)
                
                # حفظ الفرضيات
                hypotheses_file = self.data_dir / "hypotheses.json"
                with open(str(hypotheses_file), 'w', encoding='utf-8') as f:
                    json.dump(self.explorer.hypotheses, f, ensure_ascii=False, indent=4)
                
                st.success("تم حفظ البيانات بنجاح")
        
        with col2:
            if st.button("تحميل البيانات المحفوظة"):
                # تحميل المفاهيم
                if self.concepts_file.exists():
                    self.explorer.load_concepts(str(self.concepts_file))
                
                # تحميل الفرضيات
                hypotheses_file = self.data_dir / "hypotheses.json"
                if hypotheses_file.exists():
                    try:
                        with open(str(hypotheses_file), 'r', encoding='utf-8') as f:
                            self.explorer.hypotheses = json.load(f)
                        st.success("تم تحميل البيانات بنجاح")
                    except Exception as e:
                        st.error(f"خطأ في تحميل الفرضيات: {str(e)}")
                else:
                    st.warning("لا توجد بيانات محفوظة للتحميل")


# تنفيذ الواجهة عند تشغيل الملف مباشرة
if __name__ == "__main__":
    exploration_interface = ExplorationInterface()
    exploration_interface.render()
