import streamlit as st
from typing import Dict, Any
import sys
from pathlib import Path
import traceback

# إضافة المجلد الرئيسي إلى مسار Python
root_dir = Path(__file__).parent.parent.parent.parent
sys.path.append(str(root_dir))

from core.agent_controller import AgentController


class AgentDashboard:
    def __init__(self, agent_type: str):
        """تهيئة داشبورد الوكيل

        Args:
            agent_type: نوع الوكيل (مثل: تفسير، فقه، علوم)
        """
        try:
            self.agent_type = agent_type
            self.agent_controller = AgentController()
            self.agent = self.agent_controller.get_agent(agent_type)
        except Exception as e:
            st.error(f"خطأ في تهيئة داشبورد الوكيل: {str(e)}")
            st.code(traceback.format_exc())

    def render(self):
        """عرض داشبورد الوكيل"""
        try:
            st.header(f"إدارة وكيل {self.agent_type}")

            # عرض حالة الوكيل
            try:
                status = self.agent.get_status()
                st.info(f"الحالة: {status['state']}")
            except Exception as e:
                st.error(f"خطأ في عرض حالة الوكيل: {str(e)}")

            # عرض وتحديث الإعدادات
            self.render_settings()

            # واجهة الاختبار
            self.render_testing_interface()
        except Exception as e:
            st.error(f"خطأ في عرض داشبورد الوكيل: {str(e)}")
            st.code(traceback.format_exc())

    def render_settings(self):
        """عرض وتحديث إعدادات الوكيل"""
        try:
            st.subheader("إعدادات الوكيل")
            settings = self.agent.get_settings()

            new_settings = {}
            for key, value in settings.items():
                try:
                    if isinstance(value, bool):
                        new_settings[key] = st.checkbox(key, value)
                    elif isinstance(value, (int, float)):
                        new_settings[key] = st.number_input(key, value=value)
                    else:
                        new_settings[key] = st.text_input(key, value)
                except Exception as e:
                    st.error(f"خطأ في عرض الإعداد {key}: {str(e)}")

            if st.button("حفظ الإعدادات"):
                try:
                    self.agent.update_settings(new_settings)
                    st.success("تم حفظ الإعدادات بنجاح!")
                except Exception as e:
                    st.error(f"خطأ في حفظ الإعدادات: {str(e)}")
        except Exception as e:
            st.error(f"خطأ في عرض الإعدادات: {str(e)}")

    def render_testing_interface(self):
        """عرض واجهة اختبار الوكيل"""
        try:
            st.subheader("اختبار الوكيل")

            # إدخال نص للتحليل
            test_text = st.text_area("أدخل النص للتحليل")

            if st.button("تحليل"):
                if test_text:
                    with st.spinner("جاري التحليل..."):
                        try:
                            results = self.agent.analyze(test_text)

                            # عرض النتائج
                            st.json(results)

                            # عرض المقاييس
                            col1, col2 = st.columns(2)
                            with col1:
                                st.metric("زمن التحليل", f"{results['time']}ms")
                            with col2:
                                st.metric("درجة الثقة", f"{results['confidence']}%")
                        except Exception as e:
                            st.error(f"حدث خطأ أثناء التحليل: {str(e)}")
                            st.code(traceback.format_exc())
                else:
                    st.warning("الرجاء إدخال نص للتحليل")
        except Exception as e:
            st.error(f"خطأ في عرض واجهة الاختبار: {str(e)}")
            st.code(traceback.format_exc())
