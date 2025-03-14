#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
لوحة تحكم تطوير المعرفة - واجهة مستخدم لتتبع تطور المعرفة والبحث المستمر والأنماط الجديدة في القرآن
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
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go

# استيراد المكونات الضرورية من المشروع
from core.explorer.systematic_explorer import SystematicExplorer
from core.explorer.pattern_discovery import PatternDiscovery
from core.explorer.reasoning_engine import ReasoningEngine
from core.utils.config import get_config
from subscription.user_manager import UserManager


class KnowledgeDashboard:
    """
    واجهة لوحة تحكم تطوير المعرفة والبحث المستمر والأنماط الجديدة في القرآن
    """

    def __init__(self, user_manager: UserManager = None):
        """
        تهيئة واجهة لوحة تحكم تطوير المعرفة

        Args:
            user_manager: مدير المستخدمين (اختياري)
        """
        # تهيئة مدير التكوين
        self.config = get_config()

        # تهيئة نظام الاستكشاف المنظم
        self.explorer = SystematicExplorer()

        # تهيئة نظام اكتشاف الأنماط
        self.pattern_discovery = PatternDiscovery()

        # تهيئة محرك الاستدلال
        self.reasoning_engine = ReasoningEngine()

        # تهيئة مدير المستخدمين
        self.user_manager = user_manager

        # تهيئة مسارات البيانات
        self.data_dir = Path(self.config.get_data_path("concepts"))
        self.learning_progress_file = self.data_dir / "learning_progress.json"
        self.new_patterns_file = self.data_dir / "new_patterns.json"
        self.insights_file = self.data_dir / "insights.json"

        # تحميل بيانات التقدم والأنماط والرؤى إذا كانت موجودة
        self.learning_progress = self._load_json_data(self.learning_progress_file)
        self.new_patterns = self._load_json_data(self.new_patterns_file)
        self.insights = self._load_json_data(self.insights_file)

        # إنشاء بيانات افتراضية إذا لم تكن موجودة
        if not self.learning_progress:
            self._create_default_learning_progress()
        if not self.new_patterns:
            self._create_default_patterns()
        if not self.insights:
            self._create_default_insights()

    def _load_json_data(self, file_path: Path) -> Dict:
        """
        تحميل بيانات من ملف JSON

        Args:
            file_path: مسار الملف

        Returns:
            البيانات المحملة أو قاموس فارغ إذا لم يكن الملف موجودًا
        """
        if file_path.exists():
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                st.error(f"خطأ في تحميل الملف {file_path}: {str(e)}")
                return {}
        return {}

    def _save_json_data(self, data: Dict, file_path: Path) -> bool:
        """
        حفظ بيانات في ملف JSON

        Args:
            data: البيانات المراد حفظها
            file_path: مسار الملف

        Returns:
            نجاح العملية
        """
        try:
            # التأكد من وجود المجلد
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            return True
        except Exception as e:
            st.error(f"خطأ في حفظ الملف {file_path}: {str(e)}")
            return False

    def _create_default_learning_progress(self):
        """
        إنشاء بيانات افتراضية لتقدم التعلم
        """
        # إنشاء بيانات تقدم التعلم للأيام الثلاثين الماضية
        today = datetime.now()
        self.learning_progress = {
            "daily_progress": [
                {
                    "date": (today - timedelta(days=i)).strftime("%Y-%m-%d"),
                    "new_concepts": np.random.randint(0, 5),
                    "new_relations": np.random.randint(0, 8),
                    "new_insights": np.random.randint(0, 3),
                    "processed_resources": np.random.randint(0, 2)
                } for i in range(30, 0, -1)
            ],
            "resource_types": {
                "books": np.random.randint(5, 15),
                "videos": np.random.randint(3, 10),
                "audio": np.random.randint(2, 8),
                "articles": np.random.randint(10, 20)
            },
            "concept_categories": {
                "عقيدة": np.random.randint(10, 30),
                "فقه": np.random.randint(15, 40),
                "تفسير": np.random.randint(20, 50),
                "علوم قرآنية": np.random.randint(25, 60),
                "أخرى": np.random.randint(5, 15)
            }
        }
        self._save_json_data(self.learning_progress, self.learning_progress_file)

    def _create_default_patterns(self):
        """
        إنشاء بيانات افتراضية للأنماط الجديدة
        """
        self.new_patterns = {
            "word_patterns": [
                {
                    "id": f"pattern_{i}",
                    "discovery_date": (datetime.now() - timedelta(days=np.random.randint(1, 30))).strftime("%Y-%m-%d"),
                    "pattern_type": "word_frequency",
                    "description": f"نمط تكرار كلمات متعلقة بـ{['الماء', 'النور', 'الأرض', 'السماء', 'الإنسان'][i % 5]}",
                    "confidence": round(np.random.uniform(0.7, 0.99), 2),
                    "source": "القرآن الكريم"
                } for i in range(1, 11)
            ],
            "concept_patterns": [
                {
                    "id": f"concept_pattern_{i}",
                    "discovery_date": (datetime.now() - timedelta(days=np.random.randint(1, 30))).strftime("%Y-%m-%d"),
                    "pattern_type": "concept_relation",
                    "description": f"علاقة بين مفهوم {['التوحيد', 'الإيمان', 'العبادة', 'الأخلاق', 'العلم'][i % 5]} ومفهوم {['الفطرة', 'العقل', 'القلب', 'الروح', 'النفس'][i % 5]}",
                    "confidence": round(np.random.uniform(0.7, 0.99), 2),
                    "source": "تحليل النصوص القرآنية"
                } for i in range(1, 8)
            ],
            "numerical_patterns": [
                {
                    "id": f"numerical_pattern_{i}",
                    "discovery_date": (datetime.now() - timedelta(days=np.random.randint(1, 30))).strftime("%Y-%m-%d"),
                    "pattern_type": "numerical_relation",
                    "description": f"نمط عددي متعلق بتكرار {['الأيام', 'الشهور', 'السنين', 'الكواكب', 'العناصر'][i % 5]} في القرآن",
                    "confidence": round(np.random.uniform(0.7, 0.99), 2),
                    "source": "تحليل إحصائي للقرآن"
                } for i in range(1, 6)
            ]
        }
        self._save_json_data(self.new_patterns, self.new_patterns_file)

    def _create_default_insights(self):
        """
        إنشاء بيانات افتراضية للرؤى والاستنتاجات
        """
        self.insights = {
            "recent_insights": [
                {
                    "id": f"insight_{i}",
                    "discovery_date": (datetime.now() - timedelta(days=np.random.randint(1, 30))).strftime("%Y-%m-%d"),
                    "title": f"رؤية جديدة حول {['الإعجاز العلمي', 'الإعجاز اللغوي', 'الإعجاز التشريعي', 'الإعجاز الغيبي', 'الإعجاز العددي'][i % 5]}",
                    "description": f"اكتشاف علاقة جديدة بين {['آيات القرآن', 'سور القرآن', 'مفاهيم القرآن', 'قصص القرآن', 'أحكام القرآن'][i % 5]} والمعارف الحديثة",
                    "confidence": round(np.random.uniform(0.7, 0.99), 2),
                    "supporting_evidence": np.random.randint(3, 10),
                    "related_concepts": np.random.randint(2, 6)
                } for i in range(1, 16)
            ],
            "insight_categories": {
                "علمي": np.random.randint(5, 15),
                "لغوي": np.random.randint(8, 20),
                "تشريعي": np.random.randint(6, 18),
                "غيبي": np.random.randint(4, 12),
                "عددي": np.random.randint(3, 10)
            },
            "verification_status": {
                "مؤكد": np.random.randint(10, 25),
                "محتمل": np.random.randint(15, 35),
                "قيد التحقق": np.random.randint(20, 40),
                "مرفوض": np.random.randint(5, 15)
            }
        }
        self._save_json_data(self.insights, self.insights_file)

    def add_learning_progress(self, new_concepts: int, new_relations: int, new_insights: int, processed_resources: int):
        """
        إضافة تقدم تعلم جديد

        Args:
            new_concepts: عدد المفاهيم الجديدة
            new_relations: عدد العلاقات الجديدة
            new_insights: عدد الرؤى الجديدة
            processed_resources: عدد الموارد المعالجة
        """
        today = datetime.now().strftime("%Y-%m-%d")
        
        # التحقق مما إذا كان هناك تقدم لليوم الحالي
        for progress in self.learning_progress["daily_progress"]:
            if progress["date"] == today:
                # تحديث التقدم الحالي
                progress["new_concepts"] += new_concepts
                progress["new_relations"] += new_relations
                progress["new_insights"] += new_insights
                progress["processed_resources"] += processed_resources
                break
        else:
            # إضافة تقدم جديد لليوم الحالي
            self.learning_progress["daily_progress"].append({
                "date": today,
                "new_concepts": new_concepts,
                "new_relations": new_relations,
                "new_insights": new_insights,
                "processed_resources": processed_resources
            })
        
        # حفظ التغييرات
        self._save_json_data(self.learning_progress, self.learning_progress_file)

    def add_new_pattern(self, pattern_type: str, description: str, confidence: float, source: str):
        """
        إضافة نمط جديد

        Args:
            pattern_type: نوع النمط (word_patterns, concept_patterns, numerical_patterns)
            description: وصف النمط
            confidence: مستوى الثقة
            source: مصدر النمط
        """
        today = datetime.now().strftime("%Y-%m-%d")
        
        # تحديد نوع النمط وإضافته إلى القائمة المناسبة
        if pattern_type == "word_frequency":
            category = "word_patterns"
        elif pattern_type == "concept_relation":
            category = "concept_patterns"
        elif pattern_type == "numerical_relation":
            category = "numerical_patterns"
        else:
            category = "word_patterns"  # افتراضي
        
        # إنشاء معرف فريد
        pattern_id = f"{category.split('_')[0]}_{len(self.new_patterns[category]) + 1}"
        
        # إضافة النمط الجديد
        self.new_patterns[category].append({
            "id": pattern_id,
            "discovery_date": today,
            "pattern_type": pattern_type,
            "description": description,
            "confidence": confidence,
            "source": source
        })
        
        # حفظ التغييرات
        self._save_json_data(self.new_patterns, self.new_patterns_file)
        
        return pattern_id

    def add_new_insight(self, title: str, description: str, confidence: float, 
                       category: str, supporting_evidence: int, related_concepts: int):
        """
        إضافة رؤية جديدة

        Args:
            title: عنوان الرؤية
            description: وصف الرؤية
            confidence: مستوى الثقة
            category: فئة الرؤية
            supporting_evidence: عدد الأدلة الداعمة
            related_concepts: عدد المفاهيم المرتبطة
        """
        today = datetime.now().strftime("%Y-%m-%d")
        
        # إنشاء معرف فريد
        insight_id = f"insight_{len(self.insights['recent_insights']) + 1}"
        
        # إضافة الرؤية الجديدة
        self.insights["recent_insights"].append({
            "id": insight_id,
            "discovery_date": today,
            "title": title,
            "description": description,
            "confidence": confidence,
            "supporting_evidence": supporting_evidence,
            "related_concepts": related_concepts
        })
        
        # تحديث إحصائيات الفئات
        if category in self.insights["insight_categories"]:
            self.insights["insight_categories"][category] += 1
        else:
            self.insights["insight_categories"][category] = 1
        
        # تحديث حالة التحقق
        if confidence >= 0.8:
            status = "مؤكد"
        elif confidence >= 0.6:
            status = "محتمل"
        else:
            status = "قيد التحقق"
        
        self.insights["verification_status"][status] += 1
        
        # حفظ التغييرات
        self._save_json_data(self.insights, self.insights_file)
        
        return insight_id

    def render(self):
        """
        عرض واجهة لوحة تحكم تطوير المعرفة
        """
        st.title("📊 لوحة تحكم تطوير المعرفة والبحث المستمر")
        st.markdown("""تتبع تطور المعرفة والبحث المستمر واكتشاف الأنماط الجديدة في القرآن الكريم والنصوص الإسلامية.""")
        
        # إنشاء تبويبات لعرض المعلومات المختلفة
        tabs = st.tabs([
            "📈 تقدم التعلم", 
            "🔍 الأنماط المكتشفة", 
            "💡 الرؤى والاستنتاجات", 
            "📚 مصادر المعرفة"
        ])
        
        # تبويب تقدم التعلم
        with tabs[0]:
            self._render_learning_progress_tab()
        
        # تبويب الأنماط المكتشفة
        with tabs[1]:
            self._render_patterns_tab()
        
        # تبويب الرؤى والاستنتاجات
        with tabs[2]:
            self._render_insights_tab()
        
        # تبويب مصادر المعرفة
        with tabs[3]:
            self._render_resources_tab()

    def _render_learning_progress_tab(self):
        """
        عرض تبويب تقدم التعلم
        """
        st.header("📈 تقدم التعلم المستمر")
        
        # عرض مؤشرات الأداء الرئيسية
        col1, col2, col3, col4 = st.columns(4)
        
        # حساب إجماليات الشهر الحالي
        current_month_data = []
        today = datetime.now()
        first_day_of_month = datetime(today.year, today.month, 1).strftime("%Y-%m-%d")
        
        for progress in self.learning_progress["daily_progress"]:
            if progress["date"] >= first_day_of_month:
                current_month_data.append(progress)
        
        total_concepts = sum(p["new_concepts"] for p in current_month_data)
        total_relations = sum(p["new_relations"] for p in current_month_data)
        total_insights = sum(p["new_insights"] for p in current_month_data)
        total_resources = sum(p["processed_resources"] for p in current_month_data)
        
        with col1:
            st.metric("مفاهيم جديدة", total_concepts)
        
        with col2:
            st.metric("علاقات جديدة", total_relations)
        
        with col3:
            st.metric("رؤى جديدة", total_insights)
        
        with col4:
            st.metric("موارد معالجة", total_resources)
        
        # عرض رسم بياني لتقدم التعلم اليومي
        st.subheader("تقدم التعلم اليومي")
        
        # تحويل البيانات إلى DataFrame
        df_progress = pd.DataFrame(self.learning_progress["daily_progress"])
        df_progress["date"] = pd.to_datetime(df_progress["date"])
        df_progress = df_progress.sort_values("date")
        
        # إنشاء رسم بياني تفاعلي باستخدام Plotly
        fig = px.line(df_progress, x="date", y=["new_concepts", "new_relations", "new_insights"], 
                     labels={
                         "date": "التاريخ",
                         "value": "العدد",
                         "variable": "النوع"
                     },
                     title="تقدم التعلم اليومي",
                     color_discrete_map={
                         "new_concepts": "#1f77b4",
                         "new_relations": "#ff7f0e",
                         "new_insights": "#2ca02c"
                     })
        
        # تعريب أسماء المتغيرات
        fig.for_each_trace(lambda t: t.update(name={
            "new_concepts": "مفاهيم جديدة",
            "new_relations": "علاقات جديدة",
            "new_insights": "رؤى جديدة"
        }[t.name]))
        
        st.plotly_chart(fig, use_container_width=True)
        
        # عرض رسم بياني دائري لفئات المفاهيم
        st.subheader("توزيع فئات المفاهيم")
        
        # تحويل البيانات إلى DataFrame
        df_categories = pd.DataFrame({
            "الفئة": list(self.learning_progress["concept_categories"].keys()),
            "العدد": list(self.learning_progress["concept_categories"].values())
        })
        
        fig = px.pie(df_categories, values="العدد", names="الفئة", title="توزيع فئات المفاهيم")
        st.plotly_chart(fig, use_container_width=True)

    def _render_patterns_tab(self):
        """
        عرض تبويب الأنماط المكتشفة
        """
        st.header("🔍 الأنماط المكتشفة حديثًا")
        
        # عرض إحصائيات الأنماط
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("أنماط الكلمات", len(self.new_patterns["word_patterns"]))
        
        with col2:
            st.metric("أنماط المفاهيم", len(self.new_patterns["concept_patterns"]))
        
        with col3:
            st.metric("أنماط عددية", len(self.new_patterns["numerical_patterns"]))
        
        # عرض الأنماط المكتشفة حديثًا
        st.subheader("أحدث الأنماط المكتشفة")
        
        # دمج جميع الأنماط وترتيبها حسب تاريخ الاكتشاف
        all_patterns = []
        for category, patterns in self.new_patterns.items():
            for pattern in patterns:
                pattern["category"] = category
                all_patterns.append(pattern)
        
        # ترتيب الأنماط حسب تاريخ الاكتشاف (الأحدث أولاً)
        all_patterns.sort(key=lambda x: x["discovery_date"], reverse=True)
        
        # عرض الأنماط في جدول
        if all_patterns:
            # تحويل البيانات إلى DataFrame
            df_patterns = pd.DataFrame(all_patterns)
            
            # تعريب أسماء الأعمدة
            df_patterns = df_patterns.rename(columns={
                "id": "المعرف",
                "discovery_date": "تاريخ الاكتشاف",
                "pattern_type": "نوع النمط",
                "description": "الوصف",
                "confidence": "مستوى الثقة",
                "source": "المصدر",
                "category": "الفئة"
            })
            
            # تعريب قيم الفئات
            df_patterns["الفئة"] = df_patterns["الفئة"].map({
                "word_patterns": "أنماط الكلمات",
                "concept_patterns": "أنماط المفاهيم",
                "numerical_patterns": "أنماط عددية"
            })
            
            # عرض الجدول
            st.dataframe(df_patterns, use_container_width=True)
        else:
            st.info("لا توجد أنماط مكتشفة حتى الآن.")
        
        # إضافة نمط جديد
        with st.expander("إضافة نمط جديد"):
            with st.form("add_pattern_form"):
                pattern_type = st.selectbox(
                    "نوع النمط:",
                    options=["word_frequency", "concept_relation", "numerical_relation"],
                    format_func=lambda x: {
                        "word_frequency": "تكرار كلمات",
                        "concept_relation": "علاقة مفاهيم",
                        "numerical_relation": "علاقة عددية"
                    }[x]
                )
                
                description = st.text_area("وصف النمط:")
                confidence = st.slider("مستوى الثقة:", 0.0, 1.0, 0.7, 0.01)
                source = st.text_input("المصدر:")
                
                submit_button = st.form_submit_button("إضافة النمط")
                if submit_button and description and source:
                    pattern_id = self.add_new_pattern(
                        pattern_type=pattern_type,
                        description=description,
                        confidence=confidence,
                        source=source
                    )
                    st.success(f"تم إضافة النمط بنجاح! المعرف: {pattern_id}")

    def _render_insights_tab(self):
        """
        عرض تبويب الرؤى والاستنتاجات
        """
        st.header("💡 الرؤى والاستنتاجات الجديدة")
        
        # عرض إحصائيات الرؤى
        col1, col2 = st.columns(2)
        
        with col1:
            # عرض رسم بياني دائري لفئات الرؤى
            df_categories = pd.DataFrame({
                "الفئة": list(self.insights["insight_categories"].keys()),
                "العدد": list(self.insights["insight_categories"].values())
            })
            
            fig = px.pie(df_categories, values="العدد", names="الفئة", title="توزيع فئات الرؤى")
            st.plotly_chart(fig, use_container_width
        
        # عرض رسم بياني شريطي لحالة التحقق
        df_status = pd.DataFrame({
            "الحالة": list(self.insights["verification_status"].keys()),
            "العدد": list(self.insights["verification_status"].values())
        })
        
        fig = px.bar(df_status, x="الحالة", y="العدد", title="حالة التحقق من الرؤى")
        st.plotly_chart(fig, use_container_width=True)
        
        # عرض الرؤى الحديثة
        st.subheader("أحدث الرؤى والاستنتاجات")
        
        # ترتيب الرؤى حسب تاريخ الاكتشاف (الأحدث أولاً)
        recent_insights = sorted(
            self.insights["recent_insights"],
            key=lambda x: x["discovery_date"],
            reverse=True
        )
        
        # عرض الرؤى في بطاقات
        if recent_insights:
            for i, insight in enumerate(recent_insights[:10]):  # عرض أحدث 10 رؤى فقط
                with st.container():
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        st.subheader(insight["title"])
                        st.write(insight["description"])
                        st.caption(f"تاريخ الاكتشاف: {insight['discovery_date']}")
                    
                    with col2:
                        # عرض مستوى الثقة كمقياس
                        st.metric("مستوى الثقة", f"{int(insight['confidence'] * 100)}%")
                        st.write(f"الأدلة الداعمة: {insight['supporting_evidence']}")
                        st.write(f"المفاهيم المرتبطة: {insight['related_concepts']}")
                    
                    st.divider()
        else:
            st.info("لا توجد رؤى واستنتاجات حتى الآن.")
        
        # إضافة رؤية جديدة
        with st.expander("إضافة رؤية جديدة"):
            with st.form("add_insight_form"):
                title = st.text_input("عنوان الرؤية:")
                description = st.text_area("وصف الرؤية:")
                confidence = st.slider("مستوى الثقة:", 0.0, 1.0, 0.7, 0.01)
                
                category = st.selectbox(
                    "فئة الرؤية:",
                    options=["علمي", "لغوي", "تشريعي", "غيبي", "عددي"]
                )
                
                supporting_evidence = st.number_input("عدد الأدلة الداعمة:", 0, 100, 3)
                related_concepts = st.number_input("عدد المفاهيم المرتبطة:", 0, 100, 2)
                
                submit_button = st.form_submit_button("إضافة الرؤية")
                if submit_button and title and description:
                    insight_id = self.add_new_insight(
                        title=title,
                        description=description,
                        confidence=confidence,
                        category=category,
                        supporting_evidence=supporting_evidence,
                        related_concepts=related_concepts
                    )
                    st.success(f"تم إضافة الرؤية بنجاح! المعرف: {insight_id}")

    def _render_resources_tab(self):
        """
        عرض تبويب مصادر المعرفة
        """
        st.header("📚 مصادر المعرفة المعالجة")
        
        # عرض إحصائيات الموارد
        col1, col2 = st.columns(2)
        
        with col1:
            # عرض رسم بياني دائري لأنواع الموارد
            df_resources = pd.DataFrame({
                "النوع": list(self.learning_progress["resource_types"].keys()),
                "العدد": list(self.learning_progress["resource_types"].values())
            })
            
            fig = px.pie(df_resources, values="العدد", names="النوع", title="توزيع أنواع الموارد المعالجة")
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # عرض إجمالي الموارد المعالجة
            total_resources = sum(self.learning_progress["resource_types"].values())
            st.metric("إجمالي الموارد المعالجة", total_resources)
            
            # عرض معدل معالجة الموارد الشهري
            monthly_resources = sum(p["processed_resources"] for p in self.learning_progress["daily_progress"][-30:])
            st.metric("معدل المعالجة الشهري", monthly_resources)
            
            # عرض آخر مورد تمت معالجته
            last_processed = next((p for p in reversed(self.learning_progress["daily_progress"]) if p["processed_resources"] > 0), None)
            if last_processed:
                st.metric("آخر معالجة", last_processed["date"])
        
        # عرض نموذج إضافة مورد جديد
        st.subheader("إضافة مورد جديد للمعالجة")
        
        with st.form("add_resource_form"):
            resource_name = st.text_input("اسم المورد:")
            resource_type = st.selectbox(
                "نوع المورد:",
                options=["books", "videos", "audio", "articles"],
                format_func=lambda x: {
                    "books": "كتاب",
                    "videos": "فيديو",
                    "audio": "صوت",
                    "articles": "مقال"
                }[x]
            )
            
            resource_description = st.text_area("وصف المورد:")
            
            # تقدير المعرفة المتوقعة من المورد
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                expected_concepts = st.number_input("المفاهيم المتوقعة:", 0, 100, 2)
            with col2:
                expected_relations = st.number_input("العلاقات المتوقعة:", 0, 100, 3)
            with col3:
                expected_insights = st.number_input("الرؤى المتوقعة:", 0, 100, 1)
            with col4:
                expected_patterns = st.number_input("الأنماط المتوقعة:", 0, 100, 2)
            
            submit_button = st.form_submit_button("إضافة وبدء المعالجة")
            if submit_button and resource_name and resource_description:
                # تحديث إحصائيات الموارد
                self.learning_progress["resource_types"][resource_type] += 1
                
                # إضافة تقدم التعلم
                self.add_learning_progress(
                    new_concepts=expected_concepts,
                    new_relations=expected_relations,
                    new_insights=expected_insights,
                    processed_resources=1
                )
                
                st.success(f"تم إضافة المورد '{resource_name}' ومعالجته بنجاح!")


def render_knowledge_dashboard(user_manager=None):
    """
    دالة لعرض لوحة تحكم تطوير المعرفة
    """
    dashboard = KnowledgeDashboard(user_manager)
    dashboard.render()


if __name__ == "__main__":
    render_knowledge_dashboard()