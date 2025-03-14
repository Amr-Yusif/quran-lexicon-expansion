#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
صفحة البحث الدلالي في القرآن الكريم
"""

import streamlit as st
import sys
import os

# إضافة المسار الرئيسي للمشروع إلى مسار البحث
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from core.search.semantic_search import SemanticSearch
from core.utils.text_utils import ArabicTextProcessor


def render_search():
    """عرض صفحة البحث في القرآن"""
    st.title("البحث في القرآن الكريم")

    # تهيئة محرك البحث الدلالي إذا لم يكن موجوداً
    if "semantic_search" not in st.session_state:
        with st.spinner("جاري تحميل محرك البحث..."):
            st.session_state.semantic_search = SemanticSearch()
            st.session_state.text_processor = ArabicTextProcessor()

    # تقسيم الصفحة إلى قسمين
    search_col, info_col = st.columns([2, 1])

    with search_col:
        # مكونات واجهة المستخدم للبحث
        with st.form("search_form"):
            # مدخل البحث
            query = st.text_input(
                "أدخل سؤالاً أو نصاً للبحث في القرآن الكريم",
                placeholder="مثال: ما هي آيات الصبر في القرآن؟",
            )

            # خيارات البحث في صف واحد
            col1, col2 = st.columns(2)

            with col1:
                search_type = st.selectbox(
                    "نوع البحث",
                    options=["بحث دلالي", "بحث نصي", "بحث مختلط"],
                    index=0,
                    help="اختر نوع البحث المناسب لاحتياجاتك",
                )

            with col2:
                result_count = st.slider(
                    "عدد النتائج",
                    min_value=3,
                    max_value=20,
                    value=5,
                    help="حدد عدد النتائج التي تريد عرضها",
                )

            # خيارات متقدمة في قسم قابل للتوسيع
            with st.expander("خيارات متقدمة"):
                threshold = st.slider(
                    "حد التشابه (البحث الدلالي)",
                    min_value=0.0,
                    max_value=1.0,
                    value=0.7,
                    step=0.05,
                    help="كلما زادت القيمة، كانت النتائج أكثر دقة",
                )

                include_tafsir = st.checkbox(
                    "تضمين التفسير في النتائج", value=True, help="عرض تفسير الآيات مع النتائج"
                )

                surah_filter = st.multiselect(
                    "تصفية حسب السورة",
                    options=[
                        f"{i + 1}. {name}"
                        for i, name in enumerate(
                            ["الفاتحة", "البقرة", "آل عمران", "النساء", "المائدة"]
                        )
                    ],
                    default=[],
                    help="اختر سورة أو أكثر للبحث فيها فقط",
                )

            # زر البحث
            search_button = st.form_submit_button("بحث", use_container_width=True, type="primary")

    # عرض المعلومات والتلميحات
    with info_col:
        st.markdown("### نصائح للبحث الفعال")
        st.markdown("""
        - استخدم **البحث الدلالي** للعثور على المفاهيم والمعاني
        - استخدم **البحث النصي** للعثور على نص محدد
        - استخدم **البحث المختلط** للحصول على نتائج متوازنة
        - قلل حد التشابه للحصول على نتائج أكثر
        - صفِّ حسب السورة للنتائج المحددة
        """)

        st.markdown("### أمثلة للبحث")
        examples = [
            "ماذا يقول القرآن عن الصبر؟",
            "آيات عن العدل والإحسان",
            "خلق السماوات والأرض",
            "الذين ينفقون أموالهم",
        ]

        for example in examples:
            if st.button(example, use_container_width=True):
                st.experimental_set_query_params(query=example)
                st.rerun()

    # تنفيذ البحث وعرض النتائج
    if search_button and query:
        with st.spinner("جاري البحث..."):
            # معالجة مدخل المستخدم
            processed_query = st.session_state.text_processor.preprocess(query)

            # تنفيذ البحث
            results = st.session_state.semantic_search.search(
                processed_query,
                search_type=search_type,
                limit=result_count,
                threshold=threshold,
                include_tafsir=include_tafsir,
                surah_filter=[int(s.split(".")[0]) for s in surah_filter] if surah_filter else None,
            )

            # عرض النتائج
            if results:
                st.subheader(f"نتائج البحث ({len(results)} نتيجة)")

                for i, result in enumerate(results):
                    with st.container():
                        # عنوان النتيجة
                        st.markdown(
                            f"### {i + 1}. سورة {result['surah_name']} ({result['surah_number']}): الآية {result['ayah_number']}"
                        )

                        # نص الآية
                        st.markdown(f"**الآية**: {result['text']}")

                        # التفسير (إذا كان مطلوباً)
                        if include_tafsir and "tafsir" in result:
                            with st.expander("التفسير"):
                                st.markdown(result["tafsir"])

                        # درجة التطابق
                        if "score" in result:
                            col1, col2 = st.columns([3, 1])
                            with col1:
                                st.progress(result["score"])
                            with col2:
                                st.text(f"{result['score']:.2f}")

                        st.divider()
            else:
                st.warning("لم يتم العثور على نتائج مطابقة. جرب تعديل البحث أو تقليل حد التشابه.")


if __name__ == "__main__":
    render()
