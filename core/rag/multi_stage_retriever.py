#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
إستراتيجيات استرجاع متعددة المراحل للنصوص القرآنية والإسلامية
"""

import logging
import re
from typing import List, Dict, Any, Optional, Tuple, Union
from pathlib import Path
import numpy as np
from tqdm import tqdm
import pandas as pd
from sentence_transformers import SentenceTransformer, util

# إعداد التسجيل
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MultiStageRetriever:
    """استرجاع متعدد المراحل للنصوص القرآنية والإسلامية"""
    
    def __init__(self, embedding_model: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"):
        """
        تهيئة نظام الاسترجاع متعدد المراحل
        
        Args:
            embedding_model: نموذج التضمين المستخدم للتحليل الدلالي
        """
        logger.info("تهيئة نظام الاسترجاع متعدد المراحل...")
        
        # تحميل نموذج التضمين
        self.model = SentenceTransformer(embedding_model)
        
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
            "hybrid_search_weight": 0.7  # وزن البحث الدلالي في البحث الهجين
        }
        
        logger.info("تم تهيئة نظام الاسترجاع متعدد المراحل بنجاح")
    
    def index_documents(self, documents: List[Dict[str, Any]]) -> None:
        """
        فهرسة مجموعة من المستندات واستخراج الفقرات منها
        
        Args:
            documents: قائمة المستندات المراد فهرستها
        """
        logger.info(f"فهرسة {len(documents)} من المستندات...")
        
        self.documents = documents
        
        # استخراج الفقرات من المستندات
        self._extract_passages()
        
        # حساب تضمينات المستندات
        logger.info("حساب تضمينات المستندات...")
        document_texts = [doc.get("text", "") for doc in self.documents]
        self.document_embeddings = self.model.encode(
            document_texts, 
            convert_to_tensor=True, 
            show_progress_bar=True
        )
        
        # حساب تضمينات الفقرات
        logger.info("حساب تضمينات الفقرات...")
        passage_texts = [passage.get("text", "") for passage in self.passages]
        self.passage_embeddings = self.model.encode(
            passage_texts, 
            convert_to_tensor=True, 
            show_progress_bar=True
        )
        
        logger.info(f"تمت فهرسة {len(self.documents)} مستند و {len(self.passages)} فقرة بنجاح")
    
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
        استراتيجية البحث متعدد المراحل
        
        المرحلة 1: استرجاع المستندات ذات الصلة
        المرحلة 2: استرجاع الفقرات المحددة من المستندات ذات الصلة
        المرحلة 3: إعادة ترتيب الفقرات المسترجعة
        
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
        
        # المرحلة 1: استرجاع المستندات ذات الصلة
        docs_limit = min(limit * 2, len(self.documents))
        relevant_docs = self._semantic_search(query, docs_limit)
        relevant_doc_ids = [doc.get("id", "") for doc in relevant_docs]
        
        # المرحلة 2: استرجاع الفقرات من المستندات ذات الصلة
        relevant_passages = []
        for passage in self.passages:
            if passage.get("doc_id", "") in relevant_doc_ids:
                relevant_passages.append(passage)
        
        # حساب تضمين الاستعلام
        query_embedding = self.model.encode(query, convert_to_tensor=True)
        
        # حساب التشابه بين الاستعلام والفقرات
        passage_texts = [passage.get("text", "") for passage in relevant_passages]
        if passage_texts:
            passage_embeddings = self.model.encode(passage_texts, convert_to_tensor=True)
            similarities = util.pytorch_cos_sim(query_embedding, passage_embeddings)[0]
            
            # ترتيب الفقرات حسب التشابه
            sorted_indices = similarities.argsort(descending=True)
            
            # المرحلة 3: إعادة ترتيب النتائج
            top_k = min(limit, len(sorted_indices))
            reranked_passages = []
            
            for idx in sorted_indices[:top_k]:
                passage = relevant_passages[idx.item()]
                score = similarities[idx].item()
                
                result = {
                    **passage,
                    "score": score,
                    "text_summary": self._get_summary(passage.get("text", ""))
                }
                reranked_passages.append(result)
            
            return reranked_passages
        
        return []
    
    def _semantic_search(self, query: str, limit: int = 10) -> List[Dict]:
        """
        بحث دلالي بسيط في المستندات
        
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
        if self.enable_cache and cache_key in self.cache:
            return self.cache[cache_key]
        
        # حساب تضمين الاستعلام
        query_embedding = self.model.encode(query, convert_to_tensor=True)
        
        # حساب التشابه بين الاستعلام والمستندات
        similarities = util.pytorch_cos_sim(query_embedding, self.document_embeddings)[0]
        
        # ترتيب المستندات حسب التشابه
        sorted_indices = similarities.argsort(descending=True)
        
        # استرجاع أفضل النتائج
        top_k = min(limit, len(sorted_indices))
        results = []
        
        for idx in sorted_indices[:top_k]:
            doc = self.documents[idx.item()]
            score = similarities[idx].item()
            
            result = {
                **doc,
                "score": score,
                "text_summary": self._get_summary(doc.get("text", ""))
            }
            results.append(result)
        
        # تخزين النتائج في الذاكرة المؤقتة
        if self.enable_cache:
            self.cache[cache_key] = results
        
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
        توسيع الاستعلام باستخدام كلمات وعبارات ذات صلة
        
        Args:
            query: الاستعلام الأصلي
            
        Returns:
            الاستعلام الموسع
        """
        # استراتيجيات توسيع الاستعلام
        # 1. إضافة المترادفات
        expanded_terms = self._get_synonyms(query)
        
        # 2. إضافة مصطلحات ذات صلة من المستندات المسترجعة
        related_docs = self._semantic_search(query, limit=3)
        related_terms = self._extract_related_terms(related_docs, query)
        
        # دمج الاستعلام الأصلي مع المصطلحات الموسعة
        expansion_weight = 0.5  # وزن المصطلحات الموسعة
        expanded_query = query
        
        if expanded_terms:
            expanded_query += f" {' '.join(expanded_terms)}"
        
        if related_terms:
            expanded_query += f" {' '.join(related_terms)}"
        
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
