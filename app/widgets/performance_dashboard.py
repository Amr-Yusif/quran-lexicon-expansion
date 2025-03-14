#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
لوحة تحكم الأداء - واجهة مستخدم تفاعلية لعرض وتحليل مؤشرات الأداء وتحسينات النظام
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

class PerformanceDashboard:
    """مكون لعرض وتحليل مؤشرات الأداء وتحسينات النظام بشكل تفاعلي"""

    def __init__(self):
        """تهيئة مكون لوحة تحكم الأداء"""
        pass

    def render_cache_performance(self, cache_stats: Dict[str, Any]):
        """عرض أداء التخزين المؤقت

        Args:
            cache_stats: إحصائيات التخزين المؤقت
        """
        st.subheader("📊 أداء التخزين المؤقت")
        
        if not cache_stats or cache_stats.get("cache_disabled", False):
            st.warning("التخزين المؤقت غير مفعل أو لا توجد إحصائيات متاحة")
            return

        # عرض المقاييس الرئيسية
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            memory_hits = cache_stats.get("memory_hits", 0)
            disk_hits = cache_stats.get("disk_hits", 0)
            total_hits = memory_hits + disk_hits
            st.metric("إجمالي الاستعلامات الناجحة", total_hits)
        
        with col2:
            misses = cache_stats.get("misses", 0)
            hit_ratio = total_hits / (total_hits + misses) * 100 if (total_hits + misses) > 0 else 0
            st.metric("نسبة نجاح الاستعلامات", f"{hit_ratio:.1f}%")
        
        with col3:
            memory_hit_time = cache_stats.get("memory_hit_time", 0)
            memory_hit_count = cache_stats.get("memory_hits", 1)  # تجنب القسمة على صفر
            avg_memory_time = memory_hit_time / memory_hit_count * 1000 if memory_hit_count > 0 else 0
            st.metric("متوسط زمن استعلام الذاكرة", f"{avg_memory_time:.2f} مللي ثانية")
        
        with col4:
            disk_hit_time = cache_stats.get("disk_hit_time", 0)
            disk_hit_count = cache_stats.get("disk_hits", 1)  # تجنب القسمة على صفر
            avg_disk_time = disk_hit_time / disk_hit_count * 1000 if disk_hit_count > 0 else 0
            st.metric("متوسط زمن استعلام القرص", f"{avg_disk_time:.2f} مللي ثانية")

        # إنشاء بيانات للمخططات
        hit_types = ["ذاكرة", "قرص", "فشل"]
        hit_values = [memory_hits, disk_hits, misses]
        hit_colors = ["#00CC96", "#636EFA", "#EF553B"]

        # مخطط دائري لتوزيع أنواع الاستعلامات
        fig1 = px.pie(
            values=hit_values,
            names=hit_types,
            title="توزيع أنواع الاستعلامات",
            color_discrete_sequence=hit_colors
        )
        fig1.update_layout(
            directionality="rtl",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig1, use_container_width=True)

        # مخطط شريطي لمقارنة أزمنة الاستعلام
        time_types = ["ذاكرة", "قرص", "فشل"]
        time_values = [
            avg_memory_time,
            avg_disk_time,
            cache_stats.get("miss_time", 0) / max(cache_stats.get("misses", 1), 1) * 1000
        ]

        fig2 = px.bar(
            x=time_types,
            y=time_values,
            title="متوسط زمن الاستعلام (مللي ثانية)",
            color=time_types,
            color_discrete_sequence=hit_colors
        )
        fig2.update_layout(
            xaxis_title="نوع الاستعلام",
            yaxis_title="الزمن (مللي ثانية)",
            directionality="rtl"
        )
        st.plotly_chart(fig2, use_container_width=True)
        
        # عرض معلومات إضافية عن التخزين المؤقت
        with st.expander("📋 معلومات تفصيلية عن التخزين المؤقت"):
            # إنشاء جدول بالإحصائيات التفصيلية
            cache_info = [
                {"المؤشر": "حجم التخزين المؤقت في الذاكرة", "القيمة": f"{cache_stats.get('memory_cache_size', 0)} / {cache_stats.get('memory_cache_limit', 0)} عنصر"},
                {"المؤشر": "مدة صلاحية التخزين المؤقت في الذاكرة", "القيمة": f"{cache_stats.get('memory_ttl', 0) // 60} دقيقة"},
                {"المؤشر": "مدة صلاحية التخزين المؤقت في الملفات", "القيمة": f"{cache_stats.get('disk_ttl', 0) // 3600} ساعة"},
                {"المؤشر": "عدد عمليات التخزين", "القيمة": cache_stats.get('sets', 0)},
                {"المؤشر": "عدد عمليات الإزالة", "القيمة": cache_stats.get('evictions', 0)}
            ]
            
            st.table(pd.DataFrame(cache_info))
            
            # مخطط تقدم لنسبة استخدام الذاكرة
            memory_usage = cache_stats.get('memory_cache_size', 0) / max(cache_stats.get('memory_cache_limit', 1), 1) * 100
            st.progress(min(memory_usage / 100, 1.0))
            st.caption(f"استخدام ذاكرة التخزين المؤقت: {memory_usage:.1f}%")
            
            # مخطط خطي لتوزيع الوقت
            if 'avg_memory_hit_time' in cache_stats and 'avg_disk_hit_time' in cache_stats and 'avg_miss_time' in cache_stats:
                time_labels = ["ذاكرة", "قرص", "بدون تخزين مؤقت"]
                time_data = [
                    cache_stats.get('avg_memory_hit_time', 0) * 1000,
                    cache_stats.get('avg_disk_hit_time', 0) * 1000,
                    cache_stats.get('avg_miss_time', 0) * 1000
                ]
                
                fig3 = go.Figure()
                fig3.add_trace(go.Scatter(
                    x=time_labels,
                    y=time_data,
                    mode='lines+markers',
                    name='متوسط زمن الاستجابة',
                    line=dict(color='#00CC96', width=3),
                    marker=dict(size=10)
                ))
                
                fig3.update_layout(
                    title="مقارنة أزمنة الاستجابة (مللي ثانية)",
                    xaxis_title="نوع الاستعلام",
                    yaxis_title="الزمن (مللي ثانية)",
                    directionality="rtl"
                )
                st.plotly_chart(fig3, use_container_width=True)

    def render_parallel_processing_metrics(self, processing_stats: Dict[str, Any]):
        """عرض مقاييس المعالجة المتوازية

        Args:
            processing_stats: إحصائيات المعالجة المتوازية
        """
        st.subheader("⚡ أداء المعالجة المتوازية")

        if not processing_stats or processing_stats.get("stats_disabled", False):
            st.warning("لا توجد إحصائيات متاحة للمعالجة المتوازية")
            return

        # عرض المقاييس الرئيسية
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("عدد العمليات المتوازية", processing_stats.get("workers", 0))
        with col2:
            st.metric("إجمالي وقت المعالجة", f"{processing_stats.get('total_time', 0):.2f} ثانية")
        with col3:
            speedup = processing_stats.get("speedup", 1.0)
            st.metric("تسريع الأداء", f"{speedup:.2f}x")
        with col4:
            efficiency = processing_stats.get("efficiency", 0.0) * 100
            st.metric("كفاءة المعالجة", f"{efficiency:.1f}%")

        # بيانات لمخطط تأثير عدد العمليات المتوازية على الأداء
        if "worker_performance" in processing_stats:
            worker_data = processing_stats["worker_performance"]
            workers = [item["workers"] for item in worker_data]
            times = [item["time"] for item in worker_data]
            speedups = [item["speedup"] for item in worker_data]
            efficiencies = [item.get("efficiency", 0) * 100 for item in worker_data]

            # مخطط خطي للعلاقة بين عدد العمليات والتسريع
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=workers,
                y=speedups,
                mode="lines+markers",
                name="تسريع الأداء",
                line=dict(color="#00CC96", width=3),
                marker=dict(size=10)
            ))

            # إضافة خط مثالي للمقارنة
            ideal_speedup = workers.copy()
            fig.add_trace(go.Scatter(
                x=workers,
                y=ideal_speedup,
                mode="lines",
                name="التسريع المثالي",
                line=dict(color="#EF553B", width=2, dash="dash")
            ))

            fig.update_layout(
                title="تأثير عدد العمليات المتوازية على تسريع الأداء",
                xaxis_title="عدد العمليات المتوازية",
                yaxis_title="تسريع الأداء",
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                directionality="rtl"
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # مخطط خطي للعلاقة بين عدد العمليات والكفاءة
            if efficiencies:
                fig2 = go.Figure()
                fig2.add_trace(go.Scatter(
                    x=workers,
                    y=efficiencies,
                    mode="lines+markers",
                    name="كفاءة المعالجة",
                    line=dict(color="#636EFA", width=3),
                    marker=dict(size=10)
                ))
                
                fig2.update_layout(
                    title="تأثير عدد العمليات المتوازية على كفاءة المعالجة",
                    xaxis_title="عدد العمليات المتوازية",
                    yaxis_title="كفاءة المعالجة (%)",
                    directionality="rtl"
                )
                st.plotly_chart(fig2, use_container_width=True)
            
            # عرض معلومات إضافية عن المعالجة المتوازية
            with st.expander("📋 معلومات تفصيلية عن المعالجة المتوازية"):
                # إنشاء جدول بالإحصائيات التفصيلية
                processing_info = [
                    {"المؤشر": "إجمالي المهام المعالجة", "القيمة": processing_stats.get("total_tasks", 0)},
                    {"المؤشر": "متوسط وقت المهمة", "القيمة": f"{processing_stats.get('avg_task_time', 0) * 1000:.2f} مللي ثانية"},
                    {"المؤشر": "حجم الدفعة الافتراضي", "القيمة": processing_stats.get("default_batch_size", 0)},
                    {"المؤشر": "نوع المعالجة", "القيمة": "عمليات" if processing_stats.get("use_processes", False) else "مؤشرات"}
                ]
                
                st.table(pd.DataFrame(processing_info))
                
                # مخطط شريطي لمقارنة أوقات المعالجة
                if times and workers:
                    df = pd.DataFrame({
                        "عدد العمليات": workers,
                        "وقت المعالجة (ثانية)": times,
                        "التسريع": speedups
                    })
                    
                    st.dataframe(df, use_container_width=True)
                    
                    fig3 = px.bar(
                        x=workers,
                        y=times,
                        title="وقت المعالجة حسب عدد العمليات المتوازية",
                        color_discrete_sequence=["#00CC96"]
                    )
                    fig3.update_layout(
                        xaxis_title="عدد العمليات المتوازية",
                        yaxis_title="وقت المعالجة (ثانية)",
                        directionality="rtl"
                    )
                    st.plotly_chart(fig3, use_container_width=True)

    def render_optimization_recommendations(self, recommendations: List[Dict[str, Any]]):
        """عرض توصيات تحسين الأداء

        Args:
            recommendations: قائمة توصيات تحسين الأداء
        """
        st.subheader("🚀 توصيات تحسين الأداء")

        if not recommendations:
            st.info("لا توجد توصيات متاحة لتحسين الأداء")
            return

        # تصنيف التوصيات حسب الأولوية
        high_priority = []
        medium_priority = []
        low_priority = []

        for rec in recommendations:
            priority = rec.get("priority", "medium").lower()
            if priority == "high":
                high_priority.append(rec)
            elif priority == "medium":
                medium_priority.append(rec)
            else:
                low_priority.append(rec)

        # عرض التوصيات ذات الأولوية العالية
        if high_priority:
            st.markdown("### 🔴 توصيات ذات أولوية عالية")
            for i, rec in enumerate(high_priority):
                with st.expander(f"{i+1}. {rec.get('title', 'توصية')} ⚠️"):
                    st.markdown(f"**الوصف:** {rec.get('description', '')}")
                    st.markdown(f"**التأثير المتوقع:** {rec.get('impact', '')}")
                    if "code_example" in rec:
                        st.code(rec["code_example"], language="python")

        # عرض التوصيات ذات الأولوية المتوسطة
        if medium_priority:
            st.markdown("### 🟠 توصيات ذات أولوية متوسطة")
            for i, rec in enumerate(medium_priority):
                with st.expander(f"{i+1}. {rec.get('title', 'توصية')}"):
                    st.markdown(f"**الوصف:** {rec.get('description', '')}")
                    st.markdown(f"**التأثير المتوقع:** {rec.get('impact', '')}")
                    if "code_example" in rec:
                        st.code(rec["code_example"], language="python")

        # عرض التوصيات ذات الأولوية المنخفضة
        if low_priority:
            st.markdown("### 🟢 توصيات ذات أولوية منخفضة")
            for i, rec in enumerate(low_priority):
                with st.expander(f"{i+1}. {rec.get('title', 'توصية')}"):
                    st.markdown(f"**الوصف:** {rec.get('description', '')}")
                    st.markdown(f"**التأثير المتوقع:** {rec.get('impact', '')}")
                    if "code_example" in rec:
                        st.code(rec["code_example"], language="python")

    def render_performance_comparison(self, comparison_data: Dict[str, Any]):
        """عرض مقارنة أداء قبل وبعد التحسينات

        Args:
            comparison_data: بيانات مقارنة الأداء
        """
        st.subheader("📈 مقارنة الأداء قبل وبعد التحسينات")
        
        if not comparison_data:
            st.warning("لا توجد بيانات مقارنة متاحة")
            return

        # استخراج البيانات
        categories = comparison_data.get("categories", [])
        before = comparison_data.get("before_optimization", [])
        after = comparison_data.get("after_optimization", [])
        improvement = comparison_data.get("improvement_percentage", [])
        
        if not categories or not before or not after:
            st.warning("بيانات المقارنة غير مكتملة")
            return
        
        # عرض نسبة التحسين
        cols = st.columns(len(categories))
        for i, col in enumerate(cols):
            if i < len(improvement):
                col.metric(
                    categories[i],
                    f"{after[i]:.1f} ثانية",
                    f"-{improvement[i]}%",
                    delta_color="normal"
                )
        
        # إنشاء بيانات للمخطط
        df = pd.DataFrame({
            "الفئة": categories * 2,
            "الوقت (ثانية)": before + after,
            "الحالة": ["قبل التحسين"] * len(categories) + ["بعد التحسين"] * len(categories)
        })
        
        # مخطط شريطي للمقارنة
        fig = px.bar(
            df,
            x="الفئة",
            y="الوقت (ثانية)",
            color="الحالة",
            barmode="group",
            title="مقارنة وقت التنفيذ قبل وبعد التحسينات",
            color_discrete_sequence=["#EF553B", "#00CC96"]
        )
        fig.update_layout(
            directionality="rtl",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # إضافة مخطط نسبة التحسين
        if improvement:
            fig2 = px.bar(
                x=categories,
                y=improvement,
                title="نسبة التحسين في الأداء (%)",
                color_discrete_sequence=["#00CC96"]
            )
            fig2.update_layout(
                xaxis_title="الفئة",
                yaxis_title="نسبة التحسين (%)",
                directionality="rtl"
            )
            st.plotly_chart(fig2, use_container_width=True)