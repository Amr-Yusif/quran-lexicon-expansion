import streamlit as st
import plotly.graph_objects as go
from typing import Dict, List
import sys
from pathlib import Path

# إضافة المجلد الرئيسي إلى مسار Python
root_dir = Path(__file__).parent.parent.parent.parent
sys.path.append(str(root_dir))

from core.agent_controller import AgentController
from core.resource_manager import ResourceManager


class MainDashboard:
    def __init__(self):
        """تهيئة الداشبورد الرئيسي"""
        self.agent_controller = AgentController()
        self.resource_manager = ResourceManager()

    def render(self):
        """عرض الداشبورد الرئيسي"""
        # الشريط الجانبي للتحكم العام
        with st.sidebar:
            self.render_system_controls()

        # تقسيم الشاشة الرئيسية
        col1, col2 = st.columns([2, 1])

        with col1:
            self.render_main_content()

        with col2:
            self.render_performance_metrics()

    def render_system_controls(self):
        """عرض عناصر التحكم في النظام"""
        st.header("التحكم في النظام")

        # زر تشغيل/إيقاف النظام
        system_running = st.toggle("تشغيل النظام", value=True)

        # التحكم في الموارد
        st.subheader("إدارة الموارد")
        max_memory = st.slider("الحد الأقصى للذاكرة (GB)", 1, 16, 4)
        max_cpu = st.slider("الحد الأقصى للمعالج (%)", 10, 100, 50)

        if st.button("تطبيق الإعدادات"):
            self.resource_manager.update_limits(max_memory, max_cpu)

    def render_main_content(self):
        """عرض المحتوى الرئيسي"""
        st.header("نظام تحليل النصوص القرآنية")

        # عرض حالة النظام العامة
        st.subheader("حالة النظام")
        metrics = self.resource_manager.get_current_metrics()

        if metrics["cpu_usage"] > 80:
            st.warning("استخدام المعالج مرتفع!")
        if metrics["memory_usage"] > 12:
            st.warning("استخدام الذاكرة مرتفع!")

    def render_performance_metrics(self):
        """عرض مؤشرات الأداء"""
        st.header("مؤشرات الأداء")

        # عرض استخدام الموارد
        metrics = self.resource_manager.get_current_metrics()

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("استخدام المعالج", f"{metrics['cpu_usage']}%", f"{metrics['cpu_change']}%")
        with col2:
            st.metric(
                "استخدام الذاكرة", f"{metrics['memory_usage']}GB", f"{metrics['memory_change']}GB"
            )
        with col3:
            st.metric("عدد العمليات", metrics["active_tasks"], metrics["tasks_change"])

        # رسم بياني للأداء
        fig = go.Figure()
        fig.add_trace(
            go.Line(x=metrics["timestamps"], y=metrics["response_times"], name="زمن الاستجابة")
        )
        st.plotly_chart(fig)
