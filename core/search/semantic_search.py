#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
نظام البحث الدلالي المطور للنصوص الإسلامية
يستخدم نماذج تضمين متخصصة ويدعم البحث السياقي والمفاهيمي
"""

from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.http import models
import numpy as np
import os
import json
import logging
import dotenv
from typing import List, Dict, Any, Tuple
from pathlib import Path

# تحميل متغيرات البيئة
dotenv.load_dotenv()

# إعداد التسجيل
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# الاتصال بقاعدة بيانات Qdrant المحلية من Docker
client = QdrantClient(
    url=os.getenv("QDRANT_URL", "http://localhost:6333"),
    api_key=os.getenv("QDRANT_API_KEY", "")
)

class EnhancedSemanticSearch:
    def __init__(self, model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"):
        """
        تهيئة محرك البحث الدلالي باستخدام نموذج تضمين متعدد اللغات
        
        Args:
            model_name: اسم نموذج التضمين المستخدم
        """
        # هنستخدم نموذج متعدد اللغات كبداية ثم نعدله للعربية والنصوص الإسلامية
        logger.info(f"تحميل نموذج التضمين: {model_name}")
        self.model = SentenceTransformer(model_name)
        self.collection_name = "islamic_texts"
        
        # إنشاء مجموعة جديدة إذا لم تكن موجودة
        self._initialize_collection()
        
    def _initialize_collection(self):
        """تهيئة مجموعة Qdrant إذا لم تكن موجودة"""
        collections = client.get_collections().collections
        collection_names = [collection.name for collection in collections]
        
        if self.collection_name not in collection_names:
            logger.info(f"إنشاء مجموعة جديدة: {self.collection_name}")
            client.create_collection(
                collection_name=self.collection_name,
                vectors_config=models.VectorParams(
                    size=384,  # حجم التضمين المناسب للنموذج
                    distance=models.Distance.COSINE
                )
            )
            logger.info(f"تم إنشاء مجموعة جديدة: {self.collection_name}")
        else:
            logger.info(f"المجموعة موجودة بالفعل: {self.collection_name}")
    
    def encode_text(self, text: str) -> List[float]:
        """
        تحويل النص إلى تضمين باستخدام النموذج
        
        Args:
            text: النص المراد تحويله
            
        Returns:
            قائمة من الأرقام العشرية تمثل تضمين النص
        """
        return self.model.encode(text).tolist()
    
    def index_document(self, document: Dict[str, Any], doc_id: str = None) -> str:
        """
        إضافة وثيقة إلى الفهرس
        
        Args:
            document: قاموس يحتوي على النص والبيانات الوصفية
            doc_id: معرف الوثيقة (اختياري)
            
        Returns:
            معرف الوثيقة المضافة
        """
        # استخراج النص والبيانات الوصفية
        text = document.get("text", "")
        if not text:
            logger.warning("محاولة فهرسة وثيقة بدون نص")
            return None
            
        metadata = {k: v for k, v in document.items() if k != "text"}
        
        # تحويل النص إلى تضمين
        vector = self.encode_text(text)
        
        # إضافة الوثيقة إلى Qdrant
        if not doc_id:
            doc_id = str(hash(text))
        
        client.upsert(
            collection_name=self.collection_name,
            points=[
                models.PointStruct(
                    id=doc_id,
                    vector=vector,
                    payload={"text": text, "metadata": metadata}
                )
            ]
        )
        
        logger.info(f"تمت إضافة الوثيقة بنجاح (المعرف: {doc_id})")
        return doc_id
    
    def batch_index_documents(self, documents: List[Dict[str, Any]]) -> List[str]:
        """
        فهرسة مجموعة من الوثائق دفعة واحدة
        
        Args:
            documents: قائمة من الوثائق
            
        Returns:
            قائمة من معرفات الوثائق المضافة
        """
        if not documents:
            logger.warning("محاولة فهرسة قائمة فارغة من الوثائق")
            return []
            
        points = []
        doc_ids = []
        
        for document in documents:
            text = document.get("text", "")
            if not text:
                continue
                
            metadata = {k: v for k, v in document.items() if k != "text"}
            vector = self.encode_text(text)
            doc_id = str(hash(text))
            doc_ids.append(doc_id)
            
            points.append(
                models.PointStruct(
                    id=doc_id,
                    vector=vector,
                    payload={"text": text, "metadata": metadata}
                )
            )
        
        if points:
            client.upsert(
                collection_name=self.collection_name,
                points=points
            )
            
            logger.info(f"تمت إضافة {len(points)} وثيقة بنجاح")
        
        return doc_ids
    
    def advanced_semantic_search(self, query: str, limit: int = 5, filters: Dict = None) -> List[Dict]:
        """
        بحث دلالي متقدم مع إمكانية التصفية
        
        Args:
            query: نص الاستعلام
            limit: عدد النتائج المطلوبة
            filters: فلاتر إضافية للبحث
            
        Returns:
            قائمة من نتائج البحث
        """
        logger.info(f"بحث دلالي: {query}")
        query_vector = self.encode_text(query)
        
        # إعداد الفلاتر
        filter_query = None
        if filters:
            filter_conditions = []
            for key, value in filters.items():
                filter_conditions.append(
                    models.FieldCondition(
                        key=f"metadata.{key}",
                        match=models.MatchValue(value=value)
                    )
                )
            filter_query = models.Filter(
                must=filter_conditions
            )
        
        # البحث في Qdrant
        search_results = client.search(
            collection_name=self.collection_name,
            query_vector=query_vector,
            query_filter=filter_query,
            limit=limit
        )
        
        # تنسيق النتائج
        results = []
        for hit in search_results:
            result = {
                "id": hit.id,
                "score": hit.score,
                "text": hit.payload.get("text", ""),
                "metadata": hit.payload.get("metadata", {})
            }
            results.append(result)
        
        logger.info(f"تم العثور على {len(results)} نتيجة")
        return results
    
    def contextual_search(self, query: str, context: str, limit: int = 5) -> List[Dict]:
        """
        بحث دلالي يأخذ في الاعتبار السياق
        
        Args:
            query: نص الاستعلام
            context: السياق المرتبط بالاستعلام
            limit: عدد النتائج المطلوبة
            
        Returns:
            قائمة من نتائج البحث
        """
        logger.info(f"بحث سياقي: {query} (السياق: {context[:50]}...)")
        # دمج السياق مع الاستعلام
        contextual_query = f"{query} {context}"
        query_vector = self.encode_text(contextual_query)
        
        # البحث في Qdrant
        search_results = client.search(
            collection_name=self.collection_name,
            query_vector=query_vector,
            limit=limit
        )
        
        # تنسيق النتائج
        results = []
        for hit in search_results:
            result = {
                "id": hit.id,
                "score": hit.score,
                "text": hit.payload.get("text", ""),
                "metadata": hit.payload.get("metadata", {})
            }
            results.append(result)
        
        logger.info(f"تم العثور على {len(results)} نتيجة")
        return results
    
    def concept_search(self, concepts: List[str], limit: int = 5) -> List[Dict]:
        """
        بحث بالمفاهيم بدلاً من الكلمات المحددة
        
        Args:
            concepts: قائمة من المفاهيم للبحث عنها
            limit: عدد النتائج المطلوبة
            
        Returns:
            قائمة من نتائج البحث
        """
        logger.info(f"بحث بالمفاهيم: {concepts}")
        # تحويل المفاهيم إلى تضمينات وجمعها
        concept_vectors = [self.encode_text(concept) for concept in concepts]
        query_vector = np.mean(concept_vectors, axis=0).tolist()
        
        # البحث في Qdrant
        search_results = client.search(
            collection_name=self.collection_name,
            query_vector=query_vector,
            limit=limit
        )
        
        # تنسيق النتائج
        results = []
        for hit in search_results:
            result = {
                "id": hit.id,
                "score": hit.score,
                "text": hit.payload.get("text", ""),
                "metadata": hit.payload.get("metadata", {})
            }
            results.append(result)
        
        logger.info(f"تم العثور على {len(results)} نتيجة")
        return results
    
    def similar_documents(self, doc_id: str, limit: int = 5) -> List[Dict]:
        """
        البحث عن وثائق مشابهة لوثيقة معينة
        
        Args:
            doc_id: معرف الوثيقة المرجعية
            limit: عدد النتائج المطلوبة
            
        Returns:
            قائمة من الوثائق المشابهة
        """
        logger.info(f"البحث عن وثائق مشابهة للوثيقة: {doc_id}")
        # البحث في Qdrant
        try:
            search_results = client.recommend(
                collection_name=self.collection_name,
                positive=[doc_id],
                limit=limit
            )
            
            # تنسيق النتائج
            results = []
            for hit in search_results:
                result = {
                    "id": hit.id,
                    "score": hit.score,
                    "text": hit.payload.get("text", ""),
                    "metadata": hit.payload.get("metadata", {})
                }
                results.append(result)
            
            logger.info(f"تم العثور على {len(results)} وثيقة مشابهة")
            return results
        except Exception as e:
            logger.error(f"خطأ أثناء البحث عن وثائق مشابهة: {str(e)}")
            return []
    
    def multi_stage_search(self, query: str, initial_limit: int = 10, rerank_limit: int = 3, 
                          collections: list = None, filters: dict = None) -> list:
        """
        استراتيجية بحث متعددة المراحل:
        1. استرجاع مجموعة أولية من الوثائق ذات الصلة
        2. إعادة ترتيب النتائج باستخدام معايير إضافية
        3. توسيع النتائج للحصول على سياق أكثر ثراءً
        
        Args:
            query: استعلام المستخدم
            initial_limit: عدد النتائج في المرحلة الأولى
            rerank_limit: عدد النتائج النهائية بعد إعادة الترتيب
            collections: مجموعات البحث (إذا كانت None، سيتم البحث في المجموعة الافتراضية)
            filters: مرشحات إضافية للبحث
            
        Returns:
            قائمة الوثائق النهائية المعاد ترتيبها
        """
        logger.info(f"بدء البحث متعدد المراحل: {query}")
        
        # 1. المرحلة الأولى: استرجاع مجموعة أولية
        initial_results = self.search(query, limit=initial_limit, collections=collections, filters=filters)
        
        if not initial_results:
            return []
            
        # 2. المرحلة الثانية: إعادة الترتيب باستخدام معايير إضافية
        reranked_results = self._rerank_results(query, initial_results)
        
        # 3. المرحلة الثالثة: توسيع النتائج للحصول على سياق أكثر ثراءً
        enriched_results = self._enrich_results(reranked_results[:rerank_limit])
        
        return enriched_results
        
    def _rerank_results(self, query: str, results: list) -> list:
        """
        إعادة ترتيب النتائج باستخدام معايير إضافية مثل التطابق المفاهيمي والسياقي
        
        Args:
            query: استعلام المستخدم
            results: النتائج الأولية
            
        Returns:
            النتائج المعاد ترتيبها
        """
        # استخراج المفاهيم الرئيسية من الاستعلام
        query_concepts = self._extract_concepts(query)
        
        # حساب درجة تطابق جديدة لكل نتيجة
        for result in results:
            # درجة التطابق المفاهيمي (0-1)
            concept_score = self._calculate_concept_match(query_concepts, result.get("payload", {}).get("text", ""))
            
            # درجة التطابق السياقي (0-1)
            context_score = self._calculate_context_relevance(query, result.get("payload", {}).get("text", ""))
            
            # الجمع بين الدرجات مع ترجيح
            combined_score = (result.get("score", 0) * 0.4) + (concept_score * 0.3) + (context_score * 0.3)
            result["score"] = combined_score
        
        # إعادة ترتيب النتائج حسب الدرجة الجديدة
        return sorted(results, key=lambda x: x.get("score", 0), reverse=True)
    
    def _extract_concepts(self, text: str) -> list:
        """استخراج المفاهيم الرئيسية من النص"""
        # هذه مجرد طريقة بسيطة لاستخراج المفاهيم، يمكن تحسينها
        words = text.split()
        # إزالة الكلمات الشائعة والقصيرة
        concepts = [word for word in words if len(word) > 3]
        return concepts
    
    def _calculate_concept_match(self, query_concepts: list, text: str) -> float:
        """حساب درجة تطابق المفاهيم بين المفاهيم المستخرجة من الاستعلام والنص"""
        if not query_concepts or not text:
            return 0.0
            
        text_concepts = self._extract_concepts(text)
        if not text_concepts:
            return 0.0
            
        # حساب عدد المفاهيم المشتركة
        common_concepts = set(query_concepts).intersection(set(text_concepts))
        
        # حساب درجة التطابق
        score = len(common_concepts) / max(len(query_concepts), 1)
        return min(1.0, score)
    
    def _calculate_context_relevance(self, query: str, text: str) -> float:
        """حساب مدى ملاءمة السياق بين الاستعلام والنص"""
        if not query or not text:
            return 0.0
            
        # تضمين الاستعلام والنص
        query_embedding = self.model.encode(query)
        text_embedding = self.model.encode(text)
        
        # حساب تشابه جيب التمام
        similarity = np.dot(query_embedding, text_embedding) / (np.linalg.norm(query_embedding) * np.linalg.norm(text_embedding))
        return float(similarity)
    
    def _enrich_results(self, results: list) -> list:
        """
        إثراء النتائج بمعلومات إضافية مثل السياق المحيط
        
        Args:
            results: النتائج المعاد ترتيبها
            
        Returns:
            النتائج المثراة
        """
        enriched_results = []
        
        for result in results:
            # نسخ النتيجة الأصلية
            enriched_result = result.copy()
            
            # إضافة بيانات السياق إذا كانت متاحة
            text = result.get("payload", {}).get("text", "")
            ref = result.get("payload", {}).get("reference", {})
            
            if ref:
                # استرجاع السياق المحيط (مثل الآيات المجاورة، أو فقرات إضافية)
                surrounding_context = self._get_surrounding_context(ref)
                
                if surrounding_context:
                    enriched_result["surrounding_context"] = surrounding_context
            
            # إضافة تحليل موجز
            enriched_result["summary"] = self._generate_brief_summary(text)
            
            # إضافة المفاهيم المرتبطة
            enriched_result["related_concepts"] = self._get_related_concepts(text)
            
            enriched_results.append(enriched_result)
        
        return enriched_results
    
    def _get_surrounding_context(self, reference: dict) -> dict:
        """
        استرجاع السياق المحيط للمرجع
        
        Args:
            reference: بيانات المرجع (مثل سورة/آية، أو كتاب/صفحة)
            
        Returns:
            بيانات السياق المحيط
        """
        # هذه دالة تجريبية يمكن تحسينها وتخصيصها حسب نوع المرجع
        context = {}
        
        # إذا كان المرجع آية قرآنية
        if "surah" in reference and "ayah" in reference:
            surah = reference["surah"]
            ayah = reference["ayah"]
            
            # استرجاع الآيات السابقة واللاحقة (إذا وجدت)
            prev_ayahs = self._get_ayahs(surah, max(1, ayah - 2), ayah - 1)
            next_ayahs = self._get_ayahs(surah, ayah + 1, ayah + 2)
            
            if prev_ayahs:
                context["previous_ayahs"] = prev_ayahs
            if next_ayahs:
                context["next_ayahs"] = next_ayahs
        
        return context
    
    def _get_ayahs(self, surah: int, start_ayah: int, end_ayah: int) -> list:
        """
        استرجاع آيات محددة من القرآن
        
        Args:
            surah: رقم السورة
            start_ayah: رقم الآية البداية
            end_ayah: رقم الآية النهاية
            
        Returns:
            قائمة بالآيات المسترجعة
        """
        # هذه دالة تجريبية، يجب استبدالها باتصال فعلي بقاعدة البيانات
        # في التطبيق الحقيقي، يمكن استرجاع هذه البيانات من MongoDB
        return []
    
    def _generate_brief_summary(self, text: str) -> str:
        """
        توليد ملخص موجز للنص
        
        Args:
            text: النص المراد تلخيصه
            
        Returns:
            ملخص موجز
        """
        # هذه دالة تجريبية يمكن تحسينها باستخدام نماذج التلخيص
        if not text:
            return ""
            
        # كمثال بسيط: استخراج الجملة الأولى كملخص
        sentences = text.split(".")
        if sentences:
            summary = sentences[0].strip()
            return summary + "." if not summary.endswith(".") else summary
        
        return ""
    
    def _get_related_concepts(self, text: str) -> list:
        """
        استخراج المفاهيم المرتبطة بالنص
        
        Args:
            text: النص المراد تحليله
            
        Returns:
            قائمة بالمفاهيم المرتبطة
        """
        # هذه دالة تجريبية يمكن تحسينها
        # في التطبيق الحقيقي، يمكن استخدام تقنيات استخراج الكلمات المفتاحية
        if not text:
            return []
            
        # مثال بسيط: استخراج الكلمات الأطول كمفاهيم محتملة
        words = text.split()
        concepts = sorted(set([word for word in words if len(word) > 5]), key=len, reverse=True)
        return concepts[:5]  # إرجاع أطول 5 كلمات كمفاهيم

# مثال للاستخدام
if __name__ == "__main__":
    search_engine = EnhancedSemanticSearch()
    
    # إضافة بعض النصوص للتجربة
    search_engine.index_document({
        "text": "إِنَّ فِي خَلْقِ السَّمَاوَاتِ وَالْأَرْضِ وَاخْتِلَافِ اللَّيْلِ وَالنَّهَارِ لَآيَاتٍ لِأُولِي الْأَلْبَابِ",
        "source": "quran",
        "surah": "آل عمران",
        "ayah": 190
    })
    
    search_engine.index_document({
        "text": "الَّذِينَ يَذْكُرُونَ اللَّهَ قِيَامًا وَقُعُودًا وَعَلَىٰ جُنُوبِهِمْ وَيَتَفَكَّرُونَ فِي خَلْقِ السَّمَاوَاتِ وَالْأَرْضِ رَبَّنَا مَا خَلَقْتَ هَٰذَا بَاطِلًا سُبْحَانَكَ فَقِنَا عَذَابَ النَّارِ",
        "source": "quran",
        "surah": "آل عمران",
        "ayah": 191
    })
    
    # تجربة البحث
    results = search_engine.advanced_semantic_search("دلائل وجود الله في الكون")
    
    print("\nنتائج البحث الدلالي:")
    for i, result in enumerate(results, 1):
        print(f"{i}. النص: {result['text']}")
        print(f"   الدرجة: {result['score']:.4f}")
        print(f"   المصدر: {result['metadata'].get('source', 'غير معروف')}")
        if 'surah' in result['metadata']:
            print(f"   السورة: {result['metadata']['surah']} - الآية: {result['metadata']['ayah']}")
        print("---")
    
    # البحث بالمفاهيم
    concept_results = search_engine.concept_search(["خلق الكون", "آيات الله", "التفكر"])
    
    print("\nنتائج البحث بالمفاهيم:")
    for i, result in enumerate(concept_results, 1):
        print(f"{i}. النص: {result['text']}")
        print(f"   الدرجة: {result['score']:.4f}")
        print("---")
