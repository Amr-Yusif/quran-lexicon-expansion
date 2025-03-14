#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
صفحة المحادثة التفاعلية مع نظام تحليل القرآن
"""

import sys
import os

# إضافة المسار الرئيسي للمشروع إلى مسار البحث
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from core.ai.memory_client import MemoryClient
from core.ai.ollama_client import OllamaClient

def render_conversation():
    """عرض صفحة المحادثة"""
    # استيراد streamlit داخل الدالة لتجنب التنفيذ عند استيراد الوحدة
    import streamlit as st
    
    st.title("محادثة مع نظام تحليل القرآن")
    
    # تهيئة عميل الذاكرة إذا لم يكن موجوداً
    if "memory_client" not in st.session_state:
        st.session_state.memory_client = MemoryClient()
    
    # تهيئة عميل Ollama إذا لم يكن موجوداً
    if "ollama_client" not in st.session_state:
        st.session_state.ollama_client = OllamaClient()
    
    # تهيئة سجل المحادثة إذا لم يكن موجوداً
    if "conversation_history" not in st.session_state:
        st.session_state.conversation_history = []
    
    # عرض سجل المحادثة
    for message in st.session_state.conversation_history:
        role = message["role"]
        content = message["content"]
        
        if role == "user":
            st.chat_message("user").write(content)
        else:
            st.chat_message("assistant").write(content)
    
    # إدخال المستخدم
    if prompt := st.chat_input("أدخل سؤالك حول القرآن الكريم..."):
        # إضافة رسالة المستخدم إلى سجل المحادثة
        st.session_state.conversation_history.append({"role": "user", "content": prompt})
        st.chat_message("user").write(prompt)
        
        # إعداد الرسائل لطلب الذكاء الاصطناعي
        messages = [
            {"role": message["role"], "content": message["content"]}
            for message in st.session_state.conversation_history
        ]
        
        # توجيه النظام
        system_prompt = """
        أنت نظام متخصص في تحليل القرآن الكريم. مهمتك هي:
        1. الإجابة على الأسئلة المتعلقة بالقرآن الكريم بدقة.
        2. تحليل النصوص القرآنية وشرح معانيها ومعجزاتها.
        3. ربط المفاهيم القرآنية بالعلوم الحديثة عند الطلب.
        4. التعرف على الأنماط والمفاهيم في القرآن الكريم.
        
        استخدم المعرفة المتخصصة وكن دقيقاً في إجاباتك. يمكنك الاستشهاد بالآيات من القرآن الكريم والتفاسير الموثوقة.
        """
        
        # معالجة الاستجابة مع عرض مؤشر التقدم
        with st.chat_message("assistant"):
            response_placeholder = st.empty()
            response_placeholder.markdown("جاري التفكير...")
            
            # الحصول على استجابة النموذج
            response = st.session_state.ollama_client.chat_completion(
                model="llama2:arabic",  # استبدل بالنموذج المناسب
                messages=messages,
                system_prompt=system_prompt
            )
            
            # عرض الاستجابة
            response_placeholder.markdown(response)
            
            # حفظ الاستجابة في سجل المحادثة
            st.session_state.conversation_history.append({"role": "assistant", "content": response})
            
            # حفظ المحادثة في قاعدة البيانات
            st.session_state.memory_client.store_conversation(
                st.session_state.conversation_history,
                metadata={"source": "conversation_page"}
            )
    
    # أزرار التحكم
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("محادثة جديدة"):
            st.session_state.conversation_history = []
            st.rerun()
    
    with col2:
        if st.button("حفظ المحادثة"):
            # حفظ المحادثة في ملف
            st.download_button(
                label="تحميل المحادثة",
                data=str(st.session_state.conversation_history),
                file_name="conversation.txt",
                mime="text/plain"
            )
