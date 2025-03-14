import streamlit as st
import traceback

# يجب أن يكون هذا أول أمر Streamlit في التطبيق
st.set_page_config(page_title="نظام تحليل النصوص القرآنية", layout="wide")

from components.dashboard.main_dashboard import MainDashboard
from components.dashboard.agent_dashboard import AgentDashboard


def main():
    try:
        # تطبيق التنسيقات العربية
        st.markdown(
            """
            <style>
            .main {
                font-family: 'Cairo', sans-serif;
                direction: rtl;
            }
            .stButton button {
                background-color: #2c3e50;
                color: white;
                border-radius: 5px;
                padding: 10px 20px;
            }
            .metric-card {
                background-color: #f8f9fa;
                padding: 15px;
                border-radius: 10px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
            .stError {
                background-color: #ffebee;
                padding: 10px;
                border-radius: 5px;
                margin: 10px 0;
            }
            </style>
        """,
            unsafe_allow_html=True,
        )

        try:
            # تهيئة الداشبورد الرئيسي
            main_dashboard = MainDashboard()

            # عرض الداشبورد
            main_dashboard.render()
        except Exception as e:
            st.error("خطأ في تحميل الداشبورد الرئيسي")
            st.code(traceback.format_exc())

        try:
            # إضافة قائمة الوكلاء في الشريط الجانبي
            st.sidebar.header("الوكلاء المتاحون")
            agent_type = st.sidebar.selectbox("اختر الوكيل", ["تفسير", "فقه", "علوم", "تاريخ"])

            # عرض داشبورد الوكيل المحدد
            if agent_type:
                agent_dashboard = AgentDashboard(agent_type)
                agent_dashboard.render()
        except Exception as e:
            st.error("خطأ في تحميل داشبورد الوكيل")
            st.code(traceback.format_exc())

    except Exception as e:
        st.error("خطأ في تشغيل التطبيق")
        st.code(traceback.format_exc())


if __name__ == "__main__":
    main()
