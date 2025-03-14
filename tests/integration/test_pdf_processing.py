"""اختبارات التكامل لمعالجة ملفات PDF والبحث فيها."""

import os
import pytest
import tempfile
from pathlib import Path
from unittest.mock import patch

from local_mem0_agent.core.data_loaders.pdf_loader import PDFLoader
from local_mem0_agent.core.rag.qdrant_manager import QdrantManager
from local_mem0_agent.core.embeddings.embedding_models import ArabicEmbeddingModel

# تخطي هذه الاختبارات إذا لم تكن متغيرات البيئة معرفة
pytestmark = pytest.mark.skipif(
    os.environ.get("QDRANT_API_KEY") is None or os.environ.get("QDRANT_URL") is None,
    reason="متغيرات بيئة Qdrant غير معرفة"
)

@pytest.fixture
def sample_content():
    """محتوى نصي للاختبار."""
    return """
    بسم الله الرحمن الرحيم
    
    المعجزات العلمية في القرآن الكريم
    
    يقول الله تعالى: "وَالسَّمَاءَ بَنَيْنَاهَا بِأَيْدٍ وَإِنَّا لَمُوسِعُونَ" (الذاريات: 47)
    
    تشير هذه الآية إلى حقيقة علمية اكتشفها العلماء في القرن العشرين، وهي أن الكون يتوسع باستمرار.
    في عام 1929 اكتشف العالم إدوين هابل أن المجرات تتباعد عن بعضها البعض، وهذا يدل على أن الكون يتوسع.
    
    ومن المعجزات العلمية أيضًا ما ذكره القرآن عن دورة الماء في الطبيعة في قوله تعالى:
    "أَلَمْ تَرَ أَنَّ اللَّهَ يُزْجِي سَحَابًا ثُمَّ يُؤَلِّفُ بَيْنَهُ ثُمَّ يَجْعَلُهُ رُكَامًا فَتَرَى الْوَدْقَ يَخْرُجُ مِنْ خِلَالِهِ" (النور: 43)
    """


@pytest.fixture
def pdf_loader():
    """تهيئة PDFLoader للاختبار."""
    return PDFLoader()


@pytest.fixture
def qdrant_manager():
    """تهيئة QdrantManager باستخدام بيانات الاعتماد من متغيرات البيئة."""
    return QdrantManager(
        api_key=os.environ.get("QDRANT_API_KEY"),
        url=os.environ.get("QDRANT_URL")
    )


@pytest.fixture
def embedding_model():
    """تهيئة نموذج التضمين العربي."""
    return ArabicEmbeddingModel()


def test_pdf_creation_and_processing(pdf_loader, sample_content, tmpdir):
    """اختبار إنشاء ومعالجة ملف PDF."""
    # إنشاء ملف PDF اختباري باستخدام مكتبة للإنشاء المباشر
    with tempfile.NamedTemporaryFile(suffix=".pdf", dir=tmpdir, delete=False) as tmp_file:
        pdf_path = tmp_file.name
    
    # استخدام وهم لتجنب الاعتماد على مكتبة إنشاء PDF في الاختبار
    with patch.object(pdf_loader, "_extract_text_from_pdf") as mock_extract:
        mock_extract.return_value = {
            "metadata": {"title": "المعجزات العلمية في القرآن", "author": "مؤلف اختباري", "pages": 5},
            "content": sample_content
        }
        
        # اختبار تحميل الملف
        book_info = pdf_loader.load_pdf(pdf_path, category="الإعجاز العلمي")
        
        # التحقق من نتائج التحميل
        assert book_info is not None
        assert "id" in book_info
        assert book_info["title"] == "المعجزات العلمية في القرآن"
        assert book_info["category"] == "الإعجاز العلمي"
        
        # اختبار معالجة الملف وتقسيمه
        with patch.object(pdf_loader, "_get_book_content") as mock_content:
            mock_content.return_value = sample_content
            
            chunks = pdf_loader.process_pdf(book_info["id"])
            
            # التحقق من تقسيم النص إلى قطع
            assert len(chunks) > 0
            assert "وَالسَّمَاءَ بَنَيْنَاهَا بِأَيْدٍ وَإِنَّا لَمُوسِعُونَ" in "".join(chunks)


def test_qdrant_collection_management(qdrant_manager, embedding_model):
    """اختبار إدارة مجموعات Qdrant."""
    # اسم مجموعة فريد للاختبار
    collection_name = f"test_collection_{os.getpid()}"
    
    try:
        # إنشاء مجموعة
        created = qdrant_manager.create_collection(
            collection_name,
            embedding_model.get_sentence_embedding_dimension()
        )
        assert created
        
        # التحقق من وجود المجموعة
        exists = qdrant_manager.collection_exists(collection_name)
        assert exists
        
    finally:
        # تنظيف - حذف مجموعة الاختبار
        if qdrant_manager.collection_exists(collection_name):
            qdrant_manager.delete_collection(collection_name)


def test_document_upload_and_search(qdrant_manager, embedding_model, sample_content):
    """اختبار تحميل والبحث في المستندات."""
    # اسم مجموعة فريد للاختبار
    collection_name = f"test_search_{os.getpid()}"
    
    try:
        # إنشاء مجموعة
        qdrant_manager.create_collection(
            collection_name,
            embedding_model.get_sentence_embedding_dimension()
        )
        
        # إعداد وثائق الاختبار
        documents = [{
            "text": sample_content,
            "metadata": {
                "source": "اختبار",
                "category": "الإعجاز العلمي",
                "book_id": "test_book_1"
            }
        }]
        
        # تضمين المستندات
        embedded_docs = embedding_model.embed_documents(documents)
        
        # تحميل المستندات
        uploaded = qdrant_manager.upload_documents(collection_name, embedded_docs)
        assert uploaded
        
        # اختبار البحث
        search_query = "توسع الكون"
        search_results = qdrant_manager.search(
            collection_name=collection_name,
            query=search_query,
            embedding_model=embedding_model,
            limit=5
        )
        
        # التحقق من نتائج البحث
        assert len(search_results) > 0
        assert search_results[0].get("text") is not None
        assert search_results[0].get("score") > 0
        
    finally:
        # تنظيف - حذف مجموعة الاختبار
        if qdrant_manager.collection_exists(collection_name):
            qdrant_manager.delete_collection(collection_name)
