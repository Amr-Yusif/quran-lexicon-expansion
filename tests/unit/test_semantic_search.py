#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
اختبارات وحدة لنظام البحث الدلالي متعدد المراحل
"""

import pytest
import os
import sys
import numpy as np
import dotenv
from unittest.mock import MagicMock, patch

# تحميل متغيرات البيئة للاختبارات
dotenv.load_dotenv()

# إضافة المجلد الرئيسي للمشروع إلى مسار Python
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))


@pytest.fixture(scope="module", autouse=True)
def mock_global_qdrant_client():
    """تجهيز موك لعميل Qdrant العالمي قبل استيراد الوحدة"""
    # استخدام موك المكتبات لتجنب الاتصال بالخادم
    with patch.dict('sys.modules', {'qdrant_client': MagicMock(), 'qdrant_client.http': MagicMock()}):
        # نحتاج إلى إعادة تحميل الوحدة بعد تطبيق الموك
        if 'core.search.semantic_search' in sys.modules:
            del sys.modules['core.search.semantic_search']
        
        # الآن نستورد الوحدة
        # نستورد فقط نوع الكلاس للتوثيق، ليس لاستخدامه لأنه سيتم استيراده في كل اختبار
        from core.search.semantic_search import EnhancedSemanticSearch  # noqa: F401
        
        # عميل Qdrant المزيف
        mock_client = MagicMock()
        mock_collections = MagicMock()
        mock_collections.collections = [MagicMock(name="islamic_texts")]
        mock_client.get_collections.return_value = mock_collections
        
        # تعيين عميل Qdrant المزيف
        with patch('core.search.semantic_search.client', mock_client):
            yield mock_client


class TestEnhancedSemanticSearch:
    """اختبارات لفئة البحث الدلالي المحسن"""

    @pytest.fixture
    def search_engine(self):
        """إعداد وإرجاع نموذج محرك البحث للاختبارات"""
        from core.search.semantic_search import EnhancedSemanticSearch
        
        # موك لنموذج التضمين
        with patch('sentence_transformers.SentenceTransformer') as mock_transformer:
            # تكوين نموذج التحويل المزيف
            mock_model = MagicMock()
            mock_model.encode.return_value = np.array([0.1, 0.2, 0.3, 0.4])
            mock_transformer.return_value = mock_model
            
            engine = EnhancedSemanticSearch(model_name="test-model")
            return engine
    
    def test_initialization(self, search_engine):
        """اختبار تهيئة محرك البحث الدلالي"""
        assert search_engine is not None
        assert search_engine.collection_name == "islamic_texts"
    
    def test_encode_text(self, search_engine):
        """اختبار تشفير النص إلى تضمين"""
        result = search_engine.encode_text("نص اختباري")
        assert isinstance(result, np.ndarray)
        assert len(result) == 4  # حجم التضمين المزيف المحدد في التجهيزات
    
    def test_advanced_semantic_search(self, search_engine):
        """اختبار البحث الدلالي المتقدم"""
        from core.search.semantic_search import client
        
        # إعداد نتائج البحث المزيفة
        mock_search_result = MagicMock()
        mock_search_result.id = "doc1"
        mock_search_result.score = 0.95
        mock_search_result.payload = {"text": "نص اختباري"}
        client.search.return_value = [mock_search_result]
        
        results = search_engine.advanced_semantic_search("استعلام اختباري", limit=1)
        assert len(results) == 1
        assert results[0]["score"] == 0.95
        assert results[0]["text"] == "نص اختباري"
    
    def test_multi_stage_search(self, search_engine):
        """اختبار البحث متعدد المراحل"""
        # تجهيز النتائج المزيفة
        with patch.object(search_engine, 'advanced_semantic_search') as mock_search:
            mock_search.return_value = [
                {"id": "doc1", "score": 0.9, "payload": {"text": "نص اختباري أول"}},
                {"id": "doc2", "score": 0.8, "payload": {"text": "نص اختباري ثاني"}},
                {"id": "doc3", "score": 0.7, "payload": {"text": "نص اختباري ثالث"}},
            ]
            
            with patch.object(search_engine, '_rerank_results') as mock_rerank:
                mock_rerank.return_value = [
                    {"id": "doc2", "score": 0.95, "payload": {"text": "نص اختباري ثاني"}},
                    {"id": "doc1", "score": 0.92, "payload": {"text": "نص اختباري أول"}},
                    {"id": "doc3", "score": 0.85, "payload": {"text": "نص اختباري ثالث"}},
                ]
                
                with patch.object(search_engine, '_enrich_results') as mock_enrich:
                    mock_enrich.return_value = [
                        {
                            "id": "doc2", 
                            "score": 0.95, 
                            "payload": {"text": "نص اختباري ثاني"},
                            "summary": "ملخص للنص",
                            "related_concepts": ["مفهوم1", "مفهوم2"]
                        }
                    ]
                    
                    results = search_engine.multi_stage_search("استعلام اختباري", initial_limit=3, rerank_limit=1)
                    
                    # التحقق من النتائج
                    assert len(results) == 1
                    assert results[0]["id"] == "doc2"
                    assert results[0]["score"] == 0.95
                    assert "summary" in results[0]
                    assert "related_concepts" in results[0]
    
    def test_extract_concepts(self, search_engine):
        """اختبار استخراج المفاهيم من النص"""
        concepts = search_engine._extract_concepts("هذا نص اختباري للمفاهيم الإسلامية")
        assert isinstance(concepts, list)
        assert len(concepts) > 0
    
    def test_calculate_concept_match(self, search_engine):
        """اختبار حساب درجة تطابق المفاهيم"""
        query_concepts = ["مفهوم", "إسلامي", "بحث"]
        text = "هذا نص يحتوي على مفهوم بحث إسلامي"
        
        match_score = search_engine._calculate_concept_match(query_concepts, text)
        assert 0 <= match_score <= 1  # التحقق من أن الدرجة بين 0 و 1
        
        # اختبار الحالات الحدية
        assert search_engine._calculate_concept_match([], "") == 0.0
        assert search_engine._calculate_concept_match(query_concepts, "") == 0.0
    
    def test_calculate_context_relevance(self, search_engine):
        """اختبار حساب مدى ملاءمة السياق"""
        query = "استعلام اختباري"
        text = "نص اختباري"
        
        # تجهيز موك التشابه بطريقة أكثر نظافة
        with patch.object(search_engine, 'encode_text', side_effect=[
            np.array([0.1, 0.2, 0.3]), np.array([0.2, 0.3, 0.4])
        ]), patch('numpy.dot', return_value=0.85), patch('numpy.linalg.norm', return_value=1.0):
            relevance = search_engine._calculate_context_relevance(query, text)
            assert 0 <= relevance <= 1  # التحقق من أن الدرجة بين 0 و 1
            assert relevance == 0.85  # القيمة المزيفة المتوقعة


if __name__ == "__main__":
    pytest.main(["-v", "test_semantic_search.py"])
