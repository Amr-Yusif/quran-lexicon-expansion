#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
إستراتيجيات استرجاع متعددة المراحل للنصوص القرآنية والإسلامية
مع دعم معالجة البيانات الكبيرة وتحسين البحث الدلالي والتعلم المستمر
"""

import logging
import re
import os
import json
from typing import List, Dict, Any, Optional, Tuple, Union
from pathlib import Path
import numpy as np
from tqdm import tqdm
import pandas as pd
from sentence_transformers import SentenceTransformer, util
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

# استيراد معالج البيانات المتقدم
from core.data_processing.advanced_data_processor import AdvancedDataProcessor

# إعداد التسجيل
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MultiStageRetriever:
    """استرجاع متعدد المراحل للنصوص القرآنية والإسلامية مع دعم معالجة البيانات الكبيرة والتعلم المستمر"""
    
    def __init__(self, embedding_model: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
                 cache_dir: str = "data/cache", feedback_dir: str = "data/user_feedback"):
        """
        تهيئة نظام الاسترجاع متعدد المراحل
        
        Args:
            embedding_model: نموذج التضمين المستخدم للتحليل الدلالي
            cache_dir: مسار دليل التخزين المؤقت
            feedback_dir: مسار دليل تخزين تفاعلات المستخدم
        """
        logger.info("تهيئة نظام الاسترجاع متعدد المراحل...")
        
        # تهيئة معالج البيانات المتقدم
        self.data_processor = AdvancedDataProcessor(
            cache_dir=cache_dir,
            embedding_model=embedding_model,
            feedback_dir=feedback_dir
        )
        
        # تحميل نموذج التضمين
        self.model = self.data_processor.model
        
        # تخزين المستندات والفقرات والتضمينات
        self.documents = []
        self.passages = []
        self.document_embeddings = None
        self.passage_embeddings = None
        
        # إعدادات متقدمة
        self.enable_cache = True
        self.cache = {}
        self.config = {
            "passage_length": 3,  # عدد الجمل في الفقرة الواحدة
            "overlap": 1,  # مقدار التداخل بين الفقرات
            "rerank_ratio": 0.3,  # نسبة إعادة ترتيب النتائج في المرحلة الثانية
            "hybrid_search_weight": 0.7,  # وزن البحث الدلالي في البحث الهجين
            "use_feedback": True,  # استخدام التغذية الراجعة من المستخدم
            "batch_size": 32  # حجم الدفعة للمعالجة المتوازية
        }
        
        logger.info("تم تهيئة نظام الاسترجاع متعدد المراحل بنجاح")
    
    def index_documents(self, documents: List[Dict[str, Any]]) -> None:
        """
        فهرسة مجموعة من المستندات واستخراج الفقرات منها
        مع دعم معالجة البيانات الكبيرة باستخدام المعالجة المتوازية
        
        Args:
            documents: قائمة المستندات المراد فهرستها
        """
        logger.info(f"فهرسة {len(documents)} من المستندات...")
        
        # معالجة المستندات باستخدام معالج البيانات المتقدم
        batch_size = self.config["batch_size"]
        self.documents = self.data_processor.process_large_dataset(documents, batch_size=batch_size)
        
        # استخراج الفقرات من المستندات
        self._extract_passages()
        
        # حساب تضمينات المستندات باستخدام المعالجة المتوازية
        logger.info("حساب تضمينات المستندات باستخدام المعالجة المتوازية...")
        document_texts = [doc.get("text", "") for doc in self.documents]
        document_embeddings_np = self.data_processor.parallel_encode_texts(
            document_texts, 
            batch_size=batch_size
        )
        self.document_embeddings = util.pytorch_cos_sim(document_embeddings_np, document_embeddings_np)[0]
        
        # حساب تضمينات الفقرات باستخدام المعالجة المتوازية
        logger.info("حساب تضمينات الفقرات باستخدام المعالجة المتوازية...")
        passage_texts = [passage.get("text", "") for passage in self.passages]
        passage_embeddings_np = self.data_processor.parallel_encode_texts(
            passage_texts, 
            batch_size=batch_size
        )
        self.passage_embeddings = util.pytorch_cos_sim(passage_embeddings_np, passage_embeddings_np)[0]
        
        logger.info(f"تمت فهرسة {len(self.documents)} مستند و {len(self.passages)} فقرة بنجاح باستخدام المعالجة المتوازية")
    
    def _extract_passages(self) -> None:
        """استخراج الفقرات من المستندات"""
        logger.info("استخراج الفقرات من المستندات...")
        
        self.passages = []
        passage_id = 0
        
        for doc_idx, doc in enumerate(self.documents):
            doc_text = doc.get("text", "")
            doc_id = doc.get("id", str(doc_idx))
            
            # تقسيم النص إلى جمل
            sentences = re.split(r'[.،؛!؟\n]', doc_text)
            sentences = [s.strip() for s in sentences if s.strip()]
            
            # إنشاء فقرات متداخلة
            passage_length = self.config["passage_length"]
            overlap = self.config["overlap"]
            step = passage_length - overlap
            
            for i in range(0, len(sentences), step):
                if i + passage_length <= len(sentences):
                    passage_sentences = sentences[i:i+passage_length]
                else:
                    passage_sentences = sentences[i:]
                
                passage_text = " ".join(passage_sentences)
                
                if passage_text.strip():
                    passage = {
                        "id": f"p{passage_id}",
                        "doc_id": doc_id,
                        "text": passage_text,
                        "position": i,
                        "metadata": {
                            "doc_title": doc.get("title", ""),
                            "doc_type": doc.get("type", ""),
                            **{k: v for k, v in doc.items() if k not in ["text", "id", "title", "type"]}
                        }
                    }
                    self.passages.append(passage)
                    passage_id += 1
    
    def search(self, query: str, limit: int = 10, strategy: str = "multi_stage") -> List[Dict]:
        """
        البحث في المستندات المفهرسة باستخدام استراتيجية محددة
        
        Args:
            query: استعلام البحث
            limit: عدد النتائج المطلوبة
            strategy: استراتيجية البحث (multi_stage, semantic, hybrid, dense_passage)
            
        Returns:
            قائمة بالنتائج المسترجعة
        """
        if strategy == "multi_stage":
            return self._multi_stage_search(query, limit)
        elif strategy == "semantic":
            return self._semantic_search(query, limit)
        elif strategy == "hybrid":
            return self._hybrid_search(query, limit)
        elif strategy == "dense_passage":
            return self._dense_passage_retrieval(query, limit)
        else:
            logger.warning(f"استراتيجية غير معروفة: {strategy}، استخدام multi_stage بدلاً")
            return self._multi_stage_search(query, limit)
    
    def _multi_stage_search(self, query: str, limit: int = 10) -> List[Dict]:
        """
        استراتيجية البحث متعدد المراحل المحسنة
        
        المرحلة 1: استرجاع المستندات ذات الصلة باستخدام البحث الدلالي المحسن
        المرحلة 2: استرجاع الفقرات المحددة من المستندات ذات الصلة
        المرحلة 3: إعادة ترتيب الفقرات المسترجعة باستخدام البحث المفاهيمي والتغذية الراجعة
        
        Args:
            query: استعلام البحث
            limit: عدد النتائج المطلوبة
            
        Returns:
            قائمة بالنتائج المسترجعة
        """
        # التحقق من وجود المستندات
        if not self.documents or not self.passages:
            logger.warning("لا توجد مستندات مفهرسة للبحث")
            return []
        
        # التحقق من وجود النتائج في الذاكرة المؤقتة
        cache_key = f"multi_stage_{query}_{limit}"
        cached_result = self.data_processor._get_from_cache(cache_key)
        if cached_result is not None:
            logger.info("تم استرجاع نتائج البحث متعدد المراحل من التخزين المؤقت")
            return cached_result
        
        # المرحلة 1: استرجاع المستندات ذات الصلة باستخدام البحث الدلالي المحسن
        docs_limit = min(limit * 2, len(self.documents))
        
        # استخدام البحث التكيفي إذا كان استخدام التغذية الراجعة مفعلاً
        if self.config["use_feedback"]:
            relevant_docs = self.data_processor.adaptive_search(query, self.documents, docs_limit)
        else:
            relevant_docs = self._semantic_search(query, docs_limit)
            
        relevant_doc_ids = [doc.get("id", "") for doc in relevant_docs]
        
        # المرحلة 2: استرجاع الفقرات من المستندات ذات الصلة
        relevant_passages = []
        for passage in self.passages:
            if passage.get("doc_id", "") in relevant_doc_ids:
                relevant_passages.append(passage)
        
        # استخدام البحث المفاهيمي لتحسين استرجاع الفقرات
        # استخراج المفاهيم من الاستعلام
        query_concepts = self.data_processor._extract_concepts(query)
        
        # حساب تضمين الاستعلام باستخدام المعالجة المتوازية
        query_embedding = self.model.encode(query, convert_to_tensor=True)
        
        # حساب التشابه بين الاستعلام والفقرات
        passage_texts = [passage.get("text", "") for passage in relevant_passages]
        if passage_texts:
            # استخدام المعالجة المتوازية لتشفير الفقرات
            passage_embeddings_np = self.data_processor.parallel_encode_texts(
                passage_texts, 
                batch_size=self.config["batch_size"]
            )
            similarities = util.pytorch_cos_sim(query_embedding, passage_embeddings_np)[0]
            
            # ترتيب الفقرات حسب التشابه
            sorted_indices = similarities.argsort(descending=True)
            
            # المرحلة 3: إعادة ترتيب النتائج باستخدام البحث المفاهيمي
            top_k = min(limit, len(sorted_indices))
            reranked_passages = []
            
            for idx in sorted_indices[:top_k]:
                passage = relevant_passages[idx.item()]
                semantic_score = similarities[idx].item()
                
                # حساب درجة التطابق المفاهيمي
                passage_text = passage.get("text", "")
                passage_concepts = self.data_processor._extract_concepts(passage_text)
                concept_score = self.data_processor._calculate_concept_similarity(query_concepts, passage_concepts)
                
                # الجمع بين الدرجات مع ترجيح
                combined_score = (semantic_score * 0.7) + (concept_score * 0.3)
                
                result = {
                    **passage,
                    "score": combined_score,
                    "semantic_score": semantic_score,
                    "concept_score": concept_score,
                    "text_summary": self._get_summary(passage_text)
                }
                reranked_passages.append(result)
            
            # تخزين النتائج في الذاكرة المؤقتة
            self.data_processor._save_to_cache(cache_key, reranked_passages)
            
            # تسجيل الاستعلام للتعلم المستمر إذا كان مفعلاً
            if self.config["use_feedback"]:
                self.data_processor.record_user_query(query, reranked_passages)
            
            return reranked_passages
        
        return []
    
    def _semantic_search(self, query: str, limit: int = 10) -> List[Dict]:
        """
        بحث دلالي محسن في المستندات باستخدام معالج البيانات المتقدم
        
        Args:
            query: استعلام البحث
            limit: عدد النتائج المطلوبة
            
        Returns:
            قائمة بالنتائج المسترجعة
        """
        # التحقق من وجود المستندات
        if not self.documents or self.document_embeddings is None:
            logger.warning("لا توجد مستندات مفهرسة للبحث")
            return []
        
        # التحقق من وجود النتائج في الذاكرة المؤقتة
        cache_key = f"semantic_{query}_{limit}"
        cached_result = self.data_processor._get_from_cache(cache_key)
        if cached_result is not None:
            logger.info("تم استرجاع نتائج البحث من التخزين المؤقت")
            return cached_result
        
        # استخدام البحث الدلالي المحسن من معالج البيانات المتقدم
        use_clustering = True  # استخدام التجميع لتحسين تنوع النتائج
        results = self.data_processor.improved_semantic_search(
            query=query,
            documents=self.documents,
            top_k=limit,
            use_clustering=use_clustering
        )
        
        # تسجيل الاستعلام للتعلم المستمر إذا كان مفعلاً
        if self.config["use_feedback"]:
            self.data_processor.record_user_query(query, results)
        
        # تخزين النتائج في الذاكرة المؤقتة
        self.data_processor._save_to_cache(cache_key, results)
        
        return results
    
    def _hybrid_search(self, query: str, limit: int = 10) -> List[Dict]:
        """
        بحث هجين يجمع بين البحث الدلالي والبحث المستند إلى الكلمات المفتاحية
        
        Args:
            query: استعلام البحث
            limit: عدد النتائج المطلوبة
            
        Returns:
            قائمة بالنتائج المسترجعة
        """
        # التحقق من وجود المستندات
        if not self.documents:
            logger.warning("لا توجد مستندات مفهرسة للبحث")
            return []
        
        # حساب نتائج البحث الدلالي
        semantic_results = self._semantic_search(query, limit=limit*2)
        
        # البحث المستند إلى الكلمات المفتاحية
        keywords = self._extract_keywords(query)
        keyword_scores = {}
        
        for doc_idx, doc in enumerate(self.documents):
            doc_text = doc.get("text", "").lower()
            score = 0
            
            for keyword in keywords:
                if keyword.lower() in doc_text:
                    # زيادة الدرجة بناءً على تكرار الكلمة المفتاحية
                    count = doc_text.count(keyword.lower())
                    score += count / len(doc_text.split())
            
            if score > 0:
                keyword_scores[doc.get("id", str(doc_idx))] = score
        
        # دمج النتائج وإعادة ترتيبها
        hybrid_weight = self.config["hybrid_search_weight"]
        hybrid_results = []
        
        for result in semantic_results:
            doc_id = result.get("id", "")
            semantic_score = result.get("score", 0)
            keyword_score = keyword_scores.get(doc_id, 0)
            
            # حساب الدرجة الهجينة
            hybrid_score = (hybrid_weight * semantic_score) + ((1 - hybrid_weight) * keyword_score)
            
            hybrid_result = {
                **result,
                "semantic_score": semantic_score,
                "keyword_score": keyword_score,
                "score": hybrid_score
            }
            hybrid_results.append(hybrid_result)
        
        # ترتيب النتائج حسب الدرجة الهجينة
        hybrid_results.sort(key=lambda x: x.get("score", 0), reverse=True)
        
        return hybrid_results[:limit]
    
    def _dense_passage_retrieval(self, query: str, limit: int = 10) -> List[Dict]:
        """
        استرجاع الفقرات الكثيفة (Dense Passage Retrieval)
        
        Args:
            query: استعلام البحث
            limit: عدد النتائج المطلوبة
            
        Returns:
            قائمة بالفقرات المسترجعة
        """
        # التحقق من وجود الفقرات
        if not self.passages or self.passage_embeddings is None:
            logger.warning("لا توجد فقرات مفهرسة للبحث")
            return []
        
        # التحقق من وجود النتائج في الذاكرة المؤقتة
        cache_key = f"dpr_{query}_{limit}"
        if self.enable_cache and cache_key in self.cache:
            return self.cache[cache_key]
        
        # حساب تضمين الاستعلام
        query_embedding = self.model.encode(query, convert_to_tensor=True)
        
        # حساب التشابه بين الاستعلام والفقرات
        similarities = util.pytorch_cos_sim(query_embedding, self.passage_embeddings)[0]
        
        # ترتيب الفقرات حسب التشابه
        sorted_indices = similarities.argsort(descending=True)
        
        # استرجاع أفضل النتائج
        top_k = min(limit, len(sorted_indices))
        results = []
        
        for idx in sorted_indices[:top_k]:
            passage = self.passages[idx.item()]
            score = similarities[idx].item()
            
            result = {
                **passage,
                "score": score
            }
            results.append(result)
        
        # تخزين النتائج في الذاكرة المؤقتة
        if self.enable_cache:
            self.cache[cache_key] = results
        
        return results
    
    def expand_query(self, query: str) -> str:
        """
        توسيع الاستعلام باستخدام كلمات وعبارات ذات صلة مع الاستفادة من التغذية الراجعة
        
        Args:
            query: الاستعلام الأصلي
            
        Returns:
            الاستعلام الموسع
        """
        logger.info(f"توسيع الاستعلام: '{query}'")
        
        # التحقق من وجود النتائج في الذاكرة المؤقتة
        cache_key = f"expanded_query_{query}"
        cached_result = self.data_processor._get_from_cache(cache_key)
        if cached_result is not None:
            logger.info("تم استرجاع الاستعلام الموسع من التخزين المؤقت")
            return cached_result
        
        # 1. استخدام التغذية الراجعة من المستخدم لتوسيع الاستعلام إذا كانت متاحة
        expanded_query = query
        if self.config["use_feedback"]:
            # البحث عن استعلامات مشابهة في التغذية الراجعة السابقة
            similar_queries = self.data_processor._find_similar_queries(query, threshold=0.7)
            if similar_queries:
                expanded_query = self.data_processor._expand_query_with_feedback(query, similar_queries)
        
        # 2. إضافة المترادفات
        expanded_terms = self._get_synonyms(query)
        
        # 3. إضافة مصطلحات ذات صلة من المستندات المسترجعة
        related_docs = self._semantic_search(query, limit=3)
        related_terms = self._extract_related_terms(related_docs, query)
        
        # 4. استخراج المفاهيم من الاستعلام
        query_concepts = self.data_processor._extract_concepts(query)
        
        # دمج الاستعلام الأصلي مع المصطلحات الموسعة
        if expanded_terms:
            expanded_query += f" {' '.join(expanded_terms)}"
        
        if related_terms:
            expanded_query += f" {' '.join(related_terms)}"
        
        # تخزين الاستعلام الموسع في الذاكرة المؤقتة
        self.data_processor._save_to_cache(cache_key, expanded_query)
        
        logger.info(f"توسيع الاستعلام: '{query}' -> '{expanded_query}'")
        return expanded_query
    
    def _extract_keywords(self, text: str) -> List[str]:
        """استخراج الكلمات المفتاحية من النص"""
        # تنظيف النص
        clean_text = re.sub(r'[^\w\s]', ' ', text)
        
        # تقسيم النص إلى كلمات
        words = clean_text.split()
        
        # إزالة كلمات التوقف (يمكن توسيعها)
        stop_words = {'و', 'في', 'من', 'على', 'إلى', 'عن', 'مع', 'هو', 'هي', 'أنا', 'نحن', 'أنت', 'أنتم'}
        keywords = [word for word in words if word.lower() not in stop_words and len(word) > 1]
        
        return keywords
    
    def _get_synonyms(self, text: str) -> List[str]:
        """استخراج مترادفات للكلمات الأساسية (مثال بسيط)"""
        # قاموس مترادفات بسيط (يمكن استبداله بمكتبة أكثر تطوراً)
        synonyms_dict = {
            "قرآن": ["مصحف", "كتاب الله", "الذكر"],
            "نبي": ["رسول", "مرسل"],
            "صلاة": ["عبادة", "فريضة"],
            "علم": ["معرفة", "فهم", "دراية"],
            "إيمان": ["عقيدة", "تصديق", "اعتقاد"],
            "توحيد": ["عقيدة التوحيد", "وحدانية الله"]
        }
        
        result = []
        keywords = self._extract_keywords(text)
        
        for word in keywords:
            if word in synonyms_dict:
                result.extend(synonyms_dict[word])
        
        return result[:3]  # عودة بأهم 3 مترادفات لتجنب توسيع الاستعلام بشكل مفرط
    
    def _extract_related_terms(self, docs: List[Dict], query: str) -> List[str]:
        """استخراج مصطلحات ذات صلة من المستندات"""
        related_terms = []
        query_keywords = set(self._extract_keywords(query))
        
        for doc in docs:
            doc_text = doc.get("text", "")
            doc_keywords = set(self._extract_keywords(doc_text))
            
            # إضافة الكلمات التي لم تظهر في الاستعلام الأصلي
            new_keywords = doc_keywords - query_keywords
            related_terms.extend(list(new_keywords)[:5])  # أخذ أهم 5 كلمات جديدة
        
        # إزالة التكرار والاقتصار على أهم 3 مصطلحات
        return list(set(related_terms))[:3]
    
    def _get_summary(self, text: str, max_length: int = 200) -> str:
        """الحصول على ملخص للنص"""
        if len(text) <= max_length:
            return text
        
        # استراتيجية بسيطة: أخذ الجمل الأولى
        sentences = re.split(r'[.،؛!؟]', text)
        summary = ""
        
        for sentence in sentences:
            if len(summary) + len(sentence) <= max_length:
                summary += sentence + "."
            else:
                break
        
        return summary
    
    def record_user_feedback(self, query: str, result_id: str, is_relevant: bool, feedback_text: str = "") -> None:
        """
        تسجيل تغذية راجعة من المستخدم حول نتيجة بحث
        
        Args:
            query: استعلام المستخدم
            result_id: معرف النتيجة
            is_relevant: هل النتيجة ذات صلة
            feedback_text: نص التغذية الراجعة (اختياري)
        """
        if not self.config["use_feedback"]:
            logger.info("تم تعطيل استخدام التغذية الراجعة في الإعدادات")
            return
            
        logger.info(f"تسجيل تغذية راجعة للاستعلام: {query}, النتيجة: {result_id}, ذات صلة: {is_relevant}")
        
        # استخدام معالج البيانات المتقدم لتسجيل التغذية الراجعة
        self.data_processor.record_user_feedback(query, result_id, is_relevant, feedback_text)
        
        # تحديث النموذج بناءً على التغذية الراجعة إذا كان هناك عدد كافٍ من التغذيات الراجعة
        if len(self.data_processor.user_feedback) % 10 == 0:  # تحديث كل 10 تغذيات راجعة
            self.data_processor.update_model_from_feedback()
            
        logger.info("تم تسجيل التغذية الراجعة بنجاح")
        
    def get_search_improvement_suggestions(self) -> List[Dict[str, Any]]:
        """
        الحصول على اقتراحات لتحسين البحث بناءً على تحليل التغذية الراجعة
        
        Returns:
            قائمة بالاقتراحات لتحسين البحث
        """
        if not self.config["use_feedback"]:
            logger.info("تم تعطيل استخدام التغذية الراجعة في الإعدادات")
            return []
            
        logger.info("جاري تحليل التغذية الراجعة للحصول على اقتراحات تحسين البحث...")
        
        # استخدام معالج البيانات المتقدم للحصول على اقتراحات التحسين
        suggestions = self.data_processor.get_search_improvement_suggestions()
        
        logger.info(f"تم العثور على {len(suggestions)} اقتراح لتحسين البحث")
        return suggestions

# مثال للاستخدام
if __name__ == "__main__":
    retriever = MultiStageRetriever()
    
    # مثال لمستندات
    sample_docs = [
        {
            "id": "doc1",
            "text": "بسم الله الرحمن الرحيم. قل هو الله أحد. الله الصمد. لم يلد ولم يولد. ولم يكن له كفوا أحد.",
            "title": "سورة الإخلاص",
            "type": "quran"
        },
        {
            "id": "doc2",
            "text": "التوحيد هو أساس الدين الإسلامي والعقيدة الإسلامية، ويعني الإيمان بوحدانية الله وعدم الشرك به.",
            "title": "مفهوم التوحيد",
            "type": "article"
        }
    ]
    
    # فهرسة المستندات
    retriever.index_documents(sample_docs)
    
    # البحث باستخدام استراتيجيات مختلفة
    query = "وحدانية الله"
    
    print("البحث متعدد المراحل:")
    multi_results = retriever.search(query, strategy="multi_stage")
    for result in multi_results:
        print(f"النتيجة: {result['text']} (الدرجة: {result['score']:.2f})")
    
    print("\nالبحث الهجين:")
    hybrid_results = retriever.search(query, strategy="hybrid")
    for result in hybrid_results:
        print(f"النتيجة: {result['text']} (الدرجة: {result['score']:.2f})")
    
    # توسيع الاستعلام
    expanded_query = retriever.expand_query(query)
    print(f"\nالاستعلام الموسع: {expanded_query}")
