# -*- coding: utf-8 -*-

"""
التطبيق الرئيسي - نظام استكشاف وتحليل النصوص الإسلامية المتكامل
"""

# استيراد وتهيئة تكوين الصفحة أولاً قبل أي شيء آخر
from config import init_page_config

init_page_config()

# استيراد streamlit بعد تهيئة التكوين
import streamlit as st

# استيراد المكتبات الأساسية
import os
import time
import sys
from pathlib import Path

# Add project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# استيراد مكونات الواجهة
from widgets.top_navigation import render_top_navigation

# استيراد المكونات الأساسية
from sentence_transformers import SentenceTransformer
from quran_dataset_loader import QuranDatasetLoader
from core.data_loaders.pdf_loader import PDFLoader
from core.rag.qdrant_manager import QdrantManager
from core.embeddings.embedding_models import ArabicEmbeddingModel
from subscription.user_manager import UserManager
from core.ai.memory_client import MemoryClient

# عنوان التطبيق
st.title("نظام استكشاف وتحليل النصوص الإسلامية المتكامل 🕌")
st.markdown("""منصة متقدمة للتحليل والاستكشاف في القرآن الكريم والنصوص الإسلامية""")

# تهيئة التنقل
# Replace sidebar navigation with top navigation
selected_page = render_top_navigation()

# تحميل الصفحة المحددة
if selected_page == "البحث":
    from pages.search import render_search

    render_search()
elif selected_page == "الاستكشاف":
    from pages.exploration import render_exploration

    render_exploration()
elif selected_page == "المعجزات":
    from pages.miracles import render_miracles

    render_miracles()
elif selected_page == "المصادر":
    from pages.resources import render_resources

    render_resources()
elif selected_page == "المحادثة":
    from pages.conversation import render_conversation

    render_conversation()
elif selected_page == "الإعدادات":
    from pages.settings import render_settings

    render_settings()

# ===== تهيئة الموارد الأساسية =====


# تهيئة نموذج التضمين
@st.cache_resource
def load_embedding_model():
    return SentenceTransformer("paraphrase-multilingual-mpnet-base-v2")


# تحميل محمل بيانات القرآن
@st.cache_resource
def get_quran_loader():
    return QuranDatasetLoader()


# تهيئة مدير Qdrant
@st.cache_resource
def get_qdrant_manager():
    return QdrantManager(api_key=None, url="http://localhost:6333")


# تهيئة محمل ملفات PDF
@st.cache_resource
def get_pdf_loader():
    return PDFLoader()


# تهيئة مدير المستخدمين
@st.cache_resource
def get_user_manager():
    return UserManager()


# دالة التضمين المخصصة
def custom_embedding_function(texts):
    model = load_embedding_model()
    if isinstance(texts, str):
        texts = [texts]
    return model.encode(texts)


# إعداد عميل الذاكرة
@st.cache_resource
def get_memory_client():
    qdrant_url = os.environ.get("QDRANT_URL", "http://localhost:6333")
    qdrant_api_key = os.environ.get("QDRANT_API_KEY", "")
    return MemoryClient(url=qdrant_url, api_key=qdrant_api_key)


# تهيئة معلومات الجلسة
if "messages" not in st.session_state:
    st.session_state.messages = []

if "user_id" not in st.session_state:
    st.session_state.user_id = f"user_{int(time.time())}"

# تحديد نموذج Ollama
if "model_choice" not in st.session_state:
    st.session_state.model_choice = "mistral"  # تم تحديث النموذج الافتراضي ليكون Mistral

# إنشاء تبويبات التطبيق
tabs = st.tabs(
    [
        "💬 المحادثة والحوار",
        "🔍 البحث في القرآن الكريم",
        "📊 المعجزات العلمية في القرآن",
        "🔍 الاستكشاف والتحليل",
        "📚 المكتبة الإسلامية",
        "📊 لوحة المعرفة الإسلامية",
        "🚀 تحسين الأداء والسرعة",
        "⚙️ الإعدادات والضبط",
    ]
)

# ===== عرض المحتوى حسب التبويب المحدد =====

# تبويب المحادثة
with tabs[0]:
    # استيراد الصفحة فقط عند الحاجة
    from pages.conversation import render_conversation

    render_conversation()

# تبويب البحث في القرآن
with tabs[1]:
    # استيراد الصفحة فقط عند الحاجة
    from pages.search import render_search

    render_search()

# تبويب المعجزات العلمية
with tabs[2]:
    # استيراد الصفحة فقط عند الحاجة
    from pages.miracles import render_miracles

    render_miracles()

# تبويب الاستكشاف والفرضيات
with tabs[3]:
    # استيراد الصفحة فقط عند الحاجة
    from pages.exploration import render_exploration

    render_exploration()

# تبويب الكتب والمراجع
with tabs[4]:
    # استيراد الصفحة فقط عند الحاجة
    from pages.resources import render_resources

    render_resources()

# تبويب تطوير المعرفة
with tabs[5]:
    # استيراد الصفحة فقط عند الحاجة
    from pages.knowledge_dashboard import render_knowledge_dashboard

    render_knowledge_dashboard()

# تبويب تحسين الأداء
with tabs[6]:
    # استيراد الصفحة فقط عند الحاجة
    from pages.performance_optimization import render_performance_optimization

    render_performance_optimization()

# تبويب الإعدادات
with tabs[7]:
    # استيراد الصفحة فقط عند الحاجة
    from pages.settings import render_settings

    render_settings()
