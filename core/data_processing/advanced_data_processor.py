#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
معالج البيانات المتقدم للتعامل مع البيانات الكبيرة وتحسين البحث الدلالي والتعلم المستمر
"""

import logging
import os
import json
import time
import functools
import numpy as np
import pandas as pd
from typing import List, Dict, Any, Tuple, Optional, Union, Callable
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from sentence_transformers import SentenceTransformer, util
from sklearn.cluster import KMeans, DBSCAN
from sklearn.metrics import silhouette_score
from datetime import datetime

# استيراد نظام التخزين المؤقت المحسن
from core.data_processing.optimized_cache import OptimizedCache, cached

# إعداد التسجيل
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ===== مزخرف لقياس الأداء =====

def measure_performance(func):
    """مزخرف لقياس أداء الدوال
    
    Args:
        func: الدالة المراد قياس أدائها
        
    Returns:
        دالة مغلفة
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        execution_time = end_time - start_time
        logger.info(f"أداء {func.__name__}: {execution_time:.4f} ثانية")
        return result
    return wrapper

class AdvancedDataProcessor:
    """معالج البيانات المتقدم للتعامل مع البيانات الكبيرة وتحسين البحث الدلالي والتعلم المستمر"""
    
    def __init__(self, cache_dir: str = "data/cache", 
                 embedding_model: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
                 feedback_dir: str = "data/user_feedback"):
        """
        تهيئة معالج البيانات المتقدم
        
        Args:
            cache_dir: مسار دليل التخزين المؤقت
            embedding_model: نموذج التضمين المستخدم
            feedback_dir: مسار دليل تخزين تفاعلات المستخدم
        """
        logger.info("تهيئة معالج البيانات المتقدم...")
        
        # إنشاء الدلائل إذا لم تكن موجودة
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        self.feedback_dir = Path(feedback_dir)
        self.feedback_dir.mkdir(parents=True, exist_ok=True)
        
        # تحميل نموذج التضمين
        self.model = SentenceTransformer(embedding_model)
        
        # إعدادات التخزين المؤقت المحسن
        self.cache = OptimizedCache(
            cache_dir=cache_dir,
            memory_ttl=3600,  # ساعة واحدة للتخزين المؤقت في الذاكرة
            disk_ttl=86400,   # يوم واحد للتخزين المؤقت في الملفات
            max_memory_items=1000,  # الحد الأقصى لعدد العناصر في الذاكرة
            enable_stats=True  # تمكين إحصائيات الأداء
        )
        self.enable_cache = True
        
        # إعدادات المعالجة المتوازية
        self.max_workers = os.cpu_count() or 4
        
        # بيانات تفاعل المستخدم
        self.user_queries = []
        self.user_feedback = []
        self.load_user_feedback()
        
        # تنظيف التخزين المؤقت من العناصر منتهية الصلاحية عند بدء التشغيل
        if self.enable_cache:
            cleared_count = self.cache.clear_expired()
            if cleared_count > 0:
                logger.info(f"تم مسح {cleared_count} عنصر منتهي الصلاحية من التخزين المؤقت")
        
        logger.info("تم تهيئة معالج البيانات المتقدم بنجاح")
    
    # ===== إدارة التخزين المؤقت =====
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """
        الحصول على إحصائيات أداء التخزين المؤقت
        
        Returns:
            قاموس بإحصائيات الأداء
        """
        if not self.enable_cache:
            return {"cache_disabled": True}
        
        return self.cache.get_stats()
    
    def clear_cache(self, key: str = None) -> None:
        """
        مسح التخزين المؤقت
        
        Args:
            key: مفتاح القيمة (إذا كان None، يتم مسح كل التخزين المؤقت)
        """
        if not self.enable_cache:
            return
        
        self.cache.clear(key)
        logger.info(f"تم مسح التخزين المؤقت: {key if key else 'الكل'}")
    
    def optimize_cache(self) -> Dict[str, Any]:
        """
        تحسين أداء التخزين المؤقت
        
        Returns:
            إحصائيات التحسين
        """
        if not self.enable_cache:
            return {"cache_disabled": True}
        
        # مسح العناصر منتهية الصلاحية
        cleared_count = self.cache.clear_expired()
        
        # الحصول على إحصائيات التخزين المؤقت بعد التحسين
        stats = self.cache.get_stats()
        stats["cleared_count"] = cleared_count
        
        logger.info(f"تم تحسين أداء التخزين المؤقت، تم مسح {cleared_count} عنصر منتهي الصلاحية")
        return stats
    
    # ===== آليات التعامل مع البيانات الكبيرة =====
    
    @measure_performance
    def process_large_dataset(self, dataset: List[Dict], batch_size: int = 100) -> List[Dict]:
        """
        معالجة مجموعة بيانات كبيرة باستخدام المعالجة على دفعات مع تحسين الأداء باستخدام التخزين المؤقت متعدد المستويات
        
        Args:
            dataset: مجموعة البيانات الكبيرة
            batch_size: حجم الدفعة الواحدة
            
        Returns:
            البيانات المعالجة
        """
        logger.info(f"معالجة مجموعة بيانات كبيرة ({len(dataset)} عنصر)...")
        
        # التحقق من وجود البيانات في التخزين المؤقت المحسن
        cache_key = f"large_dataset_{hash(str(dataset)[:1000])}"
        cached_result = self._get_from_cache(cache_key)
        
        if cached_result is not None:
            logger.info("تم استرجاع البيانات المعالجة من التخزين المؤقت")
            return cached_result
        
        # تقسيم البيانات إلى دفعات
        batches = [dataset[i:i+batch_size] for i in range(0, len(dataset), batch_size)]
        processed_data = []
        
        # تحديد عدد العمليات المتوازية المناسب
        max_workers = min(self.max_workers, len(batches))
        logger.info(f"معالجة {len(batches)} دفعة باستخدام {max_workers} عملية متوازية")
        
        # معالجة الدفعات بشكل متوازي
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # تعريف دالة لمعالجة دفعة واحدة مع التخزين المؤقت
            def process_batch_with_cache(batch_index):
                batch = batches[batch_index]
                # التحقق من وجود معالجة الدفعة في التخزين المؤقت
                batch_key = f"batch_processed_{hash(str(batch))}"
                batch_cached = self._get_from_cache(batch_key)
                
                if batch_cached is not None:
                    logger.debug(f"تم استرجاع الدفعة {batch_index} من التخزين المؤقت")
                    return batch_cached
                
                # معالجة الدفعة
                processed_batch = self._process_batch(batch)
                
                # تخزين معالجة الدفعة في التخزين المؤقت (في الذاكرة فقط لتوفير مساحة القرص)
                self._save_to_cache(batch_key, processed_batch, memory_only=True)
                
                return processed_batch
            
            # تنفيذ المعالجة المتوازية
            batch_indices = list(range(len(batches)))
            batch_results = list(executor.map(process_batch_with_cache, batch_indices))
            
            # دمج النتائج
            for batch_result in batch_results:
                processed_data.extend(batch_result)
        
        # تخزين النتائج النهائية في التخزين المؤقت (في الذاكرة والملفات)
        self._save_to_cache(cache_key, processed_data)
        
        logger.info(f"تمت معالجة {len(processed_data)} عنصر بنجاح")
        return processed_data
    
    def _process_batch(self, batch: List[Dict]) -> List[Dict]:
        """
        معالجة دفعة واحدة من البيانات
        
        Args:
            batch: دفعة البيانات
            
        Returns:
            البيانات المعالجة
        """
        processed_batch = []
        
        for item in batch:
            # استخراج النص
            text = item.get("text", "")
            
            if text:
                # معالجة النص (يمكن تخصيص هذه الخطوة حسب الحاجة)
                processed_text = self._preprocess_text(text)
                
                # تحديث العنصر
                processed_item = item.copy()
                processed_item["processed_text"] = processed_text
                processed_batch.append(processed_item)
            else:
                processed_batch.append(item)
        
        return processed_batch
    
    def _preprocess_text(self, text: str) -> str:
        """
        معالجة أولية للنص
        
        Args:
            text: النص المراد معالجته
            
        Returns:
            النص بعد المعالجة
        """
        # إزالة الأحرف الخاصة والمسافات الزائدة
        processed_text = " ".join(text.split())
        
        # يمكن إضافة خطوات معالجة أخرى هنا
        
        return processed_text
    
    @measure_performance
    def parallel_encode_texts(self, texts: List[str], batch_size: int = 32) -> np.ndarray:
        """
        تشفير مجموعة من النصوص بشكل متوازي مع تحسين الأداء باستخدام التخزين المؤقت متعدد المستويات
        
        Args:
            texts: قائمة النصوص المراد تشفيرها
            batch_size: حجم الدفعة الواحدة
            
        Returns:
            مصفوفة التضمينات
        """
        logger.info(f"تشفير {len(texts)} نص بشكل متوازي...")
        
        # التحقق من وجود البيانات في التخزين المؤقت المحسن
        cache_key = f"text_embeddings_{hash(str(texts)[:1000])}"
        cached_result = self._get_from_cache(cache_key)
        
        if cached_result is not None:
            logger.info("تم استرجاع التضمينات من التخزين المؤقت")
            return np.array(cached_result)
        
        # تقسيم النصوص إلى دفعات
        batches = [texts[i:i+batch_size] for i in range(0, len(texts), batch_size)]
        all_embeddings = []
        
        # تحديد عدد العمليات المتوازية المناسب
        max_workers = min(self.max_workers, len(batches))
        
        # تشفير الدفعات بشكل متوازي
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # تعريف دالة لتشفير دفعة واحدة
            def encode_batch(batch):
                # التحقق من وجود تشفير الدفعة في التخزين المؤقت
                batch_key = f"batch_embeddings_{hash(str(batch))}"
                batch_cached = self._get_from_cache(batch_key)
                
                if batch_cached is not None:
                    return np.array(batch_cached)
                
                # تشفير الدفعة
                batch_embeddings = self.model.encode(batch, convert_to_tensor=True)
                numpy_embeddings = batch_embeddings.cpu().numpy()
                
                # تخزين تشفير الدفعة في التخزين المؤقت (في الذاكرة فقط لتوفير مساحة القرص)
                self._save_to_cache(batch_key, numpy_embeddings.tolist(), memory_only=True)
                
                return numpy_embeddings
            
            # تنفيذ التشفير المتوازي
            batch_results = list(executor.map(encode_batch, batches))
            all_embeddings.extend(batch_results)
        
        # دمج التضمينات
        embeddings = np.vstack(all_embeddings)
        
        # تخزين النتائج النهائية في التخزين المؤقت (في الذاكرة والملفات)
        self._save_to_cache(cache_key, embeddings.tolist())
        
        logger.info(f"تم تشفير {len(texts)} نص بنجاح")
        return embeddings
    
    def _save_to_cache(self, key: str, data: Any, memory_only: bool = False) -> None:
        """
        تخزين البيانات في التخزين المؤقت المحسن
        
        Args:
            key: مفتاح التخزين
            data: البيانات المراد تخزينها
            memory_only: تخزين في الذاكرة فقط دون الملفات
        """
        if not self.enable_cache:
            return
        
        try:
            # استخدام نظام التخزين المؤقت المحسن
            self.cache.set(key, data, memory_only=memory_only)
            logger.debug(f"تم تخزين البيانات في التخزين المؤقت المحسن: {key}")
        except Exception as e:
            logger.warning(f"خطأ أثناء التخزين المؤقت: {str(e)}")
    
    def _get_from_cache(self, key: str) -> Any:
        """
        استرجاع البيانات من التخزين المؤقت المحسن
        
        Args:
            key: مفتاح التخزين
            
        Returns:
            البيانات المسترجعة أو None إذا لم تكن موجودة
        """
        if not self.enable_cache:
            return None
        
        try:
            # استخدام نظام التخزين المؤقت المحسن
            result = self.cache.get(key)
            if result is not None:
                logger.debug(f"تم استرجاع البيانات من التخزين المؤقت المحسن: {key}")
            return result
        except Exception as e:
            logger.warning(f"خطأ أثناء استرجاع التخزين المؤقت: {str(e)}")
            return None
    
    # ===== تحسين خوارزميات البحث الدلالي =====
    
    @measure_performance
    def improved_semantic_search(self, query: str, documents: List[Dict], 
                                top_k: int = 10, use_clustering: bool = True) -> List[Dict]:
        """
        بحث دلالي محسن باستخدام تقنيات متقدمة مع تحسين الأداء باستخدام التخزين المؤقت متعدد المستويات
        
        Args:
            query: استعلام البحث
            documents: المستندات المراد البحث فيها
            top_k: عدد النتائج المطلوبة
            use_clustering: استخدام التجميع لتحسين النتائج
            
        Returns:
            قائمة بالنتائج المسترجعة
        """
        logger.info(f"بحث دلالي محسن: {query}")
        
        # التحقق من وجود النتائج في التخزين المؤقت المحسن
        cache_key = f"semantic_search_{hash(query)}_{hash(str(documents)[:1000])}"
        cached_result = self._get_from_cache(cache_key)
        
        if cached_result is not None:
            logger.info("تم استرجاع نتائج البحث من التخزين المؤقت")
            return cached_result
        
        # استخراج النصوص من المستندات
        texts = [doc.get("text", "") for doc in documents]
        
        # تخزين استعلامات المستخدم للتحليل المستقبلي
        self._store_user_query(query)
        
        # تشفير الاستعلام والنصوص
        query_embedding = self.model.encode(query, convert_to_tensor=True)
        document_embeddings = self.parallel_encode_texts(texts)
        
        # حساب التشابه بين الاستعلام والمستندات
        similarities = util.pytorch_cos_sim(query_embedding, document_embeddings)[0].cpu().numpy()
        
        # إنشاء قائمة النتائج
        results = []
        for i, score in enumerate(similarities):
            results.append({
                **documents[i],
                "score": float(score),
                "rank": i + 1
            })
        
        # ترتيب النتائج حسب درجة التشابه
        results = sorted(results, key=lambda x: x["score"], reverse=True)
        
        # تحسين النتائج باستخدام التجميع (إذا كان مطلوبًا)
        if use_clustering and len(results) > top_k:
            results = self._cluster_and_diversify(results, document_embeddings, top_k)
        else:
            results = results[:top_k]
        
        # تخزين النتائج في التخزين المؤقت المحسن
        # استخدام memory_only=False لتخزين النتائج في الذاكرة والملفات
        # لأن نتائج البحث غالبًا ما يتم استخدامها بشكل متكرر
        self._save_to_cache(cache_key, results, memory_only=False)
        
        logger.info(f"تم العثور على {len(results)} نتيجة")
        return results
        
    def _store_user_query(self, query: str) -> None:
        """
        تخزين استعلام المستخدم للتحليل المستقبلي وتحسين الأداء
        
        Args:
            query: استعلام البحث
        """
        try:
            # إضافة الاستعلام إلى قائمة الاستعلامات مع الطابع الزمني
            query_data = {
                "query": query,
                "timestamp": time.time()
            }
            self.user_queries.append(query_data)
            
            # تخزين الاستعلامات في ملف إذا وصل العدد إلى 10
            if len(self.user_queries) >= 10:
                self._save_user_queries()
        except Exception as e:
            logger.warning(f"خطأ أثناء تخزين استعلام المستخدم: {str(e)}")
    
    def _save_user_queries(self) -> None:
        """
        حفظ استعلامات المستخدم في ملف
        """
        try:
            queries_file = self.feedback_dir / "user_queries.json"
            
            # تحميل الاستعلامات الموجودة إذا كان الملف موجودًا
            existing_queries = []
            if queries_file.exists():
                with open(queries_file, "r", encoding="utf-8") as f:
                    existing_queries = json.load(f)
            
            # دمج الاستعلامات الجديدة مع الموجودة
            all_queries = existing_queries + self.user_queries
            
            # حفظ الاستعلامات في الملف
            with open(queries_file, "w", encoding="utf-8") as f:
                json.dump(all_queries, f, ensure_ascii=False)
            
            # مسح قائمة الاستعلامات بعد الحفظ
            self.user_queries = []
            
            logger.debug(f"تم حفظ {len(all_queries)} استعلام للمستخدم")
        except Exception as e:
            logger.warning(f"خطأ أثناء حفظ استعلامات المستخدم: {str(e)}")
    
    def _cluster_and_diversify(self, results: List[Dict], embeddings: np.ndarray, top_k: int) -> List[Dict]:
        """
        تجميع وتنويع النتائج لضمان التنوع والشمولية
        
        Args:
            results: نتائج البحث الأولية
            embeddings: تضمينات المستندات
            top_k: عدد النتائج المطلوبة
            
        Returns:
            نتائج متنوعة
        """
        # تحديد عدد المجموعات المناسب
        n_clusters = min(max(2, top_k // 2), len(results) // 2)
        
        # تطبيق خوارزمية K-means للتجميع
        try:
            kmeans = KMeans(n_clusters=n_clusters, random_state=42)
            cluster_labels = kmeans.fit_predict(embeddings[:len(results)])
            
            # إضافة تسميات المجموعات إلى النتائج
            for i, result in enumerate(results):
                result["cluster"] = int(cluster_labels[i])
            
            # اختيار أفضل النتائج من كل مجموعة
            diversified_results = []
            clusters = {}
            
            # تجميع النتائج حسب المجموعة
            for result in results:
                cluster = result["cluster"]
                if cluster not in clusters:
                    clusters[cluster] = []
                clusters[cluster].append(result)
            
            # اختيار أفضل نتيجة من كل مجموعة بالتناوب
            while len(diversified_results) < top_k and clusters:
                for cluster_id in list(clusters.keys()):
                    if not clusters[cluster_id]:
                        del clusters[cluster_id]
                        continue
                        
                    diversified_results.append(clusters[cluster_id].pop(0))
                    
                    if len(diversified_results) >= top_k:
                        break
            
            return diversified_results
        except Exception as e:
            logger.warning(f"خطأ أثناء تجميع النتائج: {str(e)}")
            return results[:top_k]
    
    def concept_based_search(self, query: str, documents: List[Dict], top_k: int = 10) -> List[Dict]:
        """
        بحث قائم على المفاهيم بدلاً من التطابق الحرفي
        
        Args:
            query: استعلام البحث
            documents: المستندات المراد البحث فيها
            top_k: عدد النتائج المطلوبة
            
        Returns:
            قائمة بالنتائج المسترجعة
        """
        logger.info(f"بحث قائم على المفاهيم: {query}")
        
        # استخراج المفاهيم من الاستعلام
        query_concepts = self._extract_concepts(query)
        
        # تشفير المفاهيم
        concept_embeddings = [self.model.encode(concept) for concept in query_concepts]
        query_embedding = np.mean(concept_embeddings, axis=0) if concept_embeddings else self.model.encode(query)
        
        # تشفير المستندات
        texts = [doc.get("text", "") for doc in documents]
        document_embeddings = self.parallel_encode_texts(texts)
        
        # حساب التشابه المفاهيمي
        similarities = np.zeros(len(documents))
        for i, doc_embedding in enumerate(document_embeddings):
            # استخراج المفاهيم من المستند
            doc_text = documents[i].get("text", "")
            doc_concepts = self._extract_concepts(doc_text)
            
            # حساب تشابه المفاهيم
            concept_similarity = self._calculate_concept_similarity(query_concepts, doc_concepts)
            
            # حساب تشابه التضمينات
            embedding_similarity = np.dot(query_embedding, doc_embedding) / (np.linalg.norm(query_embedding) * np.linalg.norm(doc_embedding))
            
            # الجمع بين التشابهات مع ترجيح
            similarities[i] = (0.7 * embedding_similarity) + (0.3 * concept_similarity)
        
        # إنشاء قائمة النتائج
        results = []
        for i, score in enumerate(similarities):
            results.append({
                **documents[i],
                "score": float(score),
                "rank": i + 1
            })
        
        # ترتيب النتائج حسب درجة التشابه
        results = sorted(results, key=lambda x: x["score"], reverse=True)[:top_k]
        
        logger.info(f"تم العثور على {len(results)} نتيجة")
        return results
    
    def _extract_concepts(self, text: str) -> List[str]:
        """
        استخراج المفاهيم الرئيسية من النص
        
        Args:
            text: النص المراد استخراج المفاهيم منه
            
        Returns:
            قائمة بالمفاهيم المستخرجة
        """
        # تنظيف النص
        clean_text = " ".join(text.split())
        
        # تقسيم النص إلى كلمات
        words = clean_text.split()
        
        # إزالة كلمات التوقف (يمكن توسيعها)
        stop_words = {'و', 'في', 'من', 'على', 'إلى', 'عن', 'مع', 'هو', 'هي', 'أنا', 'نحن', 'أنت', 'أنتم', 'هذا', 'هذه', 'ذلك', 'تلك'}
        filtered_words = [word for word in words if word.lower() not in stop_words and len(word) > 2]
        
        # اختيار أهم الكلمات كمفاهيم (يمكن تحسين هذه الخطوة)
        concepts = filtered_words[:10]  # أخذ أول 10 كلمات كمفاهيم
        
        return concepts
    
    def _calculate_concept_similarity(self, concepts1: List[str], concepts2: List[str]) -> float:
        """
        حساب التشابه بين مجموعتين من المفاهيم
        
        Args:
            concepts1: المجموعة الأولى من المفاهيم
            concepts2: المجموعة الثانية من المفاهيم
            
        Returns:
            درجة التشابه (0-1)
        """
        if not concepts1 or not concepts2:
            return 0.0
        
        # حساب المفاهيم المشتركة
        common_concepts = set(concepts1).intersection(set(concepts2))
        
        # حساب معامل جاكارد للتشابه
        similarity = len(common_concepts) / len(set(concepts1).union(set(concepts2)))
        
        return similarity
    
    # ===== آليات التعلم المستمر من تفاعل المستخدم =====
    
    def record_user_query(self, query: str, results: List[Dict]) -> None:
        """
        تسجيل استعلام المستخدم ونتائج البحث
        
        Args:
            query: استعلام المستخدم
            results: نتائج البحث
        """
        query_record = {
            "timestamp": datetime.now().isoformat(),
            "query": query,
            "results": [{
                "id": result.get("id", ""),
                "score": result.get("score", 0.0),
                "text_snippet": result.get("text", "")[:100] if result.get("text") else ""
            } for result in results[:5]]  # تخزين أول 5 نتائج فقط
        }
        
        self.user_queries.append(query_record)
        
        # حفظ البيانات إلى ملف
        self._save_user_queries()
    
    def record_user_feedback(self, query: str, result_id: str, is_relevant: bool, feedback_text: str = "") -> None:
        """
        تسجيل تغذية راجعة من المستخدم حول نتيجة بحث
        
        Args:
            query: استعلام المستخدم
            result_id: معرف النتيجة
            is_relevant: هل النتيجة ذات صلة
            feedback_text: نص التغذية الراجعة (اختياري)
        """
        feedback_record = {
            "timestamp": datetime.now().isoformat(),
            "query": query,
            "result_id": result_id,
            "is_relevant": is_relevant,
            "feedback_text": feedback_text
        }
        
        self.user_feedback.append(feedback_record)
        
        # حفظ البيانات إلى ملف
        self._save_user_feedback()
    
    def _save_user_queries(self) -> None:
        """
        حفظ استعلامات المستخدم إلى ملف
        """
        queries_file = self.feedback_dir / "user_queries.json"
        
        try:
            with open(queries_file, "w", encoding="utf-8") as f:
                json.dump(self.user_queries, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.warning(f"خطأ أثناء حفظ استعلامات المستخدم: {str(e)}")
    
    def _save_user_feedback(self) -> None:
        """
        حفظ التغذية الراجعة من المستخدم إلى ملف
        """
        feedback_file = self.feedback_dir / "user_feedback.json"
        
        try:
            with open(feedback_file, "w", encoding="utf-8") as f:
                json.dump(self.user_feedback, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.warning(f"خطأ أثناء حفظ التغذية الراجعة: {str(e)}")
    
    def load_user_feedback(self) -> None:
        """
        تحميل التغذية الراجعة من المستخدم من الملفات
        """
        queries_file = self.feedback_dir / "user_queries.json"
        feedback_file = self.feedback_dir / "user_feedback.json"
        
        # تحميل استعلامات المستخدم
        if queries_file.exists():
            try:
                # استخدام التخزين المؤقت المحسن لتحميل بيانات الاستعلامات
                cache_key = "user_queries_data"
                cached_queries = self._get_from_cache(cache_key)
                
                if cached_queries is not None:
                    self.user_queries = cached_queries
                    logger.info(f"تم تحميل {len(self.user_queries)} استعلام للمستخدم من التخزين المؤقت")
                else:
                    with open(queries_file, "r", encoding="utf-8") as f:
                        self.user_queries = json.load(f)
                    # تخزين البيانات في التخزين المؤقت للاستخدام المستقبلي
                    self._save_to_cache(cache_key, self.user_queries)
                    logger.info(f"تم تحميل {len(self.user_queries)} استعلام للمستخدم")
            except Exception as e:
                logger.warning(f"خطأ أثناء تحميل استعلامات المستخدم: {str(e)}")
        
        # تحميل التغذية الراجعة
        if feedback_file.exists():
            try:
                # استخدام التخزين المؤقت المحسن لتحميل بيانات التغذية الراجعة
                cache_key = "user_feedback_data"
                cached_feedback = self._get_from_cache(cache_key)
                
                if cached_feedback is not None:
                    self.user_feedback = cached_feedback
                    logger.info(f"تم تحميل {len(self.user_feedback)} تغذية راجعة من المستخدم من التخزين المؤقت")
                else:
                    with open(feedback_file, "r", encoding="utf-8") as f:
                        self.user_feedback = json.load(f)
                    # تخزين البيانات في التخزين المؤقت للاستخدام المستقبلي
                    self._save_to_cache(cache_key, self.user_feedback)
                    logger.info(f"تم تحميل {len(self.user_feedback)} تغذية راجعة من المستخدم")
            except Exception as e:
                logger.warning(f"خطأ أثناء تحميل التغذية الراجعة: {str(e)}")
    
    def update_model_from_feedback(self) -> None:
        """
        تحديث نموذج البحث بناءً على التغذية الراجعة من المستخدم
        """
        if not self.user_feedback:
            logger.info("لا توجد تغذية راجعة كافية لتحديث النموذج")
            return
        
        logger.info("تحديث نموذج البحث بناءً على التغذية الراجعة...")
        
        # استخراج أزواج الاستعلامات والنتائج ذات الصلة
        positive_pairs = []
        negative_pairs = []
        
        for feedback in self.user_feedback:
            query = feedback.get("query", "")
            result_id = feedback.get("result_id", "")
            is_relevant = feedback.get("is_relevant", False)
            
            # البحث عن النص الكامل للنتيجة في استعلامات المستخدم
            result_text = self._find_result_text(query, result_id)
            
            if query and result_text:
                if is_relevant:
                    positive_pairs.append((query, result_text))
                else:
                    negative_pairs.append((query, result_text))
        
        logger.info(f"تم استخراج {len(positive_pairs)} زوج إيجابي و {len(negative_pairs)} زوج سلبي")
        
        # تحليل أنماط التغذية الراجعة لتحسين البحث
        self._analyze_feedback_patterns()
        
        # في المستقبل، يمكن تنفيذ آليات أكثر تقدمًا لتحديث النموذج
        # مثل التعلم التدريجي أو ضبط النموذج الأساسي
    
    def _find_result_text(self, query: str, result_id: str) -> str:
        """
        البحث عن النص الكامل للنتيجة في استعلامات المستخدم
        
        Args:
            query: استعلام المستخدم
            result_id: معرف النتيجة
            
        Returns:
            النص الكامل للنتيجة أو سلسلة فارغة
        """
        for query_record in self.user_queries:
            if query_record.get("query") == query:
                for result in query_record.get("results", []):
                    if result.get("id") == result_id:
                        return result.get("text_snippet", "")
        
        return ""
    
    def _analyze_feedback_patterns(self) -> Dict[str, Any]:
        """
        تحليل أنماط التغذية الراجعة لاكتشاف الاتجاهات وتحسين البحث
        
        Returns:
            قاموس يحتوي على تحليلات التغذية الراجعة
        """
        if not self.user_feedback:
            return {}
        
        # تحليل نسبة الرضا العامة
        total_feedback = len(self.user_feedback)
        positive_feedback = sum(1 for f in self.user_feedback if f.get("is_relevant", False))
        satisfaction_rate = positive_feedback / total_feedback if total_feedback > 0 else 0
        
        # تحليل الاستعلامات الأكثر شيوعًا
        query_counts = {}
        for feedback in self.user_feedback:
            query = feedback.get("query", "")
            if query:
                query_counts[query] = query_counts.get(query, 0) + 1
        
        top_queries = sorted(query_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        
        # تحليل الاستعلامات ذات نسبة الرضا المنخفضة
        query_satisfaction = {}
        for feedback in self.user_feedback:
            query = feedback.get("query", "")
            is_relevant = feedback.get("is_relevant", False)
            
            if query not in query_satisfaction:
                query_satisfaction[query] = {"total": 0, "positive": 0}
            
            query_satisfaction[query]["total"] += 1
            if is_relevant:
                query_satisfaction[query]["positive"] += 1
        
        for query, stats in query_satisfaction.items():
            stats["rate"] = stats["positive"] / stats["total"] if stats["total"] > 0 else 0
        
        problematic_queries = [q for q, stats in query_satisfaction.items() 
                              if stats["total"] >= 3 and stats["rate"] < 0.5]
        
        # تجميع النتائج
        analysis = {
            "satisfaction_rate": satisfaction_rate,
            "top_queries": top_queries,
            "problematic_queries": problematic_queries,
            "total_feedback": total_feedback
        }
        
        logger.info(f"تحليل التغذية الراجعة: معدل الرضا العام {satisfaction_rate:.2f}, عدد الاستعلامات المشكلة: {len(problematic_queries)}")
        return analysis
    
    def get_search_improvement_suggestions(self) -> List[Dict[str, Any]]:
        """
        الحصول على اقتراحات لتحسين البحث بناءً على تحليل التغذية الراجعة
        
        Returns:
            قائمة بالاقتراحات لتحسين البحث
        """
        analysis = self._analyze_feedback_patterns()
        suggestions = []
        
        # اقتراحات بناءً على معدل الرضا العام
        satisfaction_rate = analysis.get("satisfaction_rate", 0)
        if satisfaction_rate < 0.7:
            suggestions.append({
                "type": "general",
                "priority": "high",
                "description": "معدل الرضا العام منخفض، يجب مراجعة خوارزمية البحث الأساسية"
            })
        
        # اقتراحات بناءً على الاستعلامات المشكلة
        problematic_queries = analysis.get("problematic_queries", [])
        for query in problematic_queries:
            suggestions.append({
                "type": "query_specific",
                "priority": "medium",
                "query": query,
                "description": f"استعلام ذو معدل رضا منخفض: {query}",
                "action": "تحسين استخراج المفاهيم والتوسيع لهذا النوع من الاستعلامات"
            })
        
        # اقتراحات عامة لتحسين النظام
        if len(analysis.get("top_queries", [])) > 0:
            suggestions.append({
                "type": "optimization",
                "priority": "low",
                "description": "تحسين التخزين المؤقت للاستعلامات الشائعة",
                "queries": [q[0] for q in analysis.get("top_queries", [])[:3]]
            })
        
        return suggestions
    
    def adaptive_search(self, query: str, documents: List[Dict], top_k: int = 10) -> List[Dict]:
        """
        بحث تكيفي يستفيد من التغذية الراجعة السابقة لتحسين النتائج
        
        Args:
            query: استعلام البحث
            documents: المستندات المراد البحث فيها
            top_k: عدد النتائج المطلوبة
            
        Returns:
            قائمة بالنتائج المسترجعة
        """
        logger.info(f"بحث تكيفي: {query}")
        
        # البحث عن استعلامات مشابهة في التغذية الراجعة السابقة
        similar_queries = self._find_similar_queries(query)
        
        if similar_queries:
            logger.info(f"تم العثور على {len(similar_queries)} استعلام مشابه")
            
            # استخدام استراتيجية بحث محسنة بناءً على التغذية الراجعة
            # 1. توسيع الاستعلام بالمفاهيم من الاستعلامات المشابهة
            expanded_query = self._expand_query_with_feedback(query, similar_queries)
            
            # 2. تعديل ترتيب النتائج بناءً على التغذية الراجعة السابقة
            initial_results = self.improved_semantic_search(expanded_query, documents, top_k * 2)
            reranked_results = self._rerank_with_feedback(initial_results, similar_queries)
            
            return reranked_results[:top_k]
        else:
            # استخدام البحث الدلالي المحسن العادي
            return self.improved_semantic_search(query, documents, top_k)
    
    def _find_similar_queries(self, query: str, threshold: float = 0.7) -> List[Dict]:
        """
        البحث عن استعلامات مشابهة في التغذية الراجعة السابقة
        
        Args:
            query: استعلام البحث الحالي
            threshold: عتبة التشابه
            
        Returns:
            قائمة بالاستعلامات المشابهة والتغذية الراجعة المرتبطة بها
        """
        similar_queries = []
        query_embedding = self.model.encode(query)
        
        # استخراج الاستعلامات الفريدة من التغذية الراجعة
        unique_queries = {}
        for feedback in self.user_feedback:
            past_query = feedback.get("query", "")
            if past_query and past_query not in unique_queries:
                unique_queries[past_query] = []
            
            if past_query:
                unique_queries[past_query].append(feedback)
        
        # حساب التشابه مع الاستعلامات السابقة
        for past_query, feedbacks in unique_queries.items():
            past_query_embedding = self.model.encode(past_query)
            similarity = np.dot(query_embedding, past_query_embedding) / (np.linalg.norm(query_embedding) * np.linalg.norm(past_query_embedding))
            
            if similarity >= threshold:
                similar_queries.append({
                    "query": past_query,
                    "similarity": float(similarity),
                    "feedbacks": feedbacks
                })
        
        # ترتيب الاستعلامات حسب التشابه
        similar_queries.sort(key=lambda x: x["similarity"], reverse=True)
        
        return similar_queries
    
    def _expand_query_with_feedback(self, query: str, similar_queries: List[Dict]) -> str:
        """
        توسيع الاستعلام باستخدام المفاهيم من الاستعلامات المشابهة
        
        Args:
            query: استعلام البحث الحالي
            similar_queries: الاستعلامات المشابهة والتغذية الراجعة المرتبطة بها
            
        Returns:
            الاستعلام الموسع
        """
        # استخراج المفاهيم من الاستعلام الحالي
        query_concepts = set(self._extract_concepts(query))
        
        # استخراج المفاهيم من الاستعلامات المشابهة ذات التغذية الراجعة الإيجابية
        additional_concepts = set()
        for similar_query in similar_queries[:3]:  # استخدام أفضل 3 استعلامات مشابهة
            past_query = similar_query["query"]
            positive_feedbacks = [f for f in similar_query["feedbacks"] if f.get("is_relevant", False)]
            
            if positive_feedbacks:
                past_concepts = set(self._extract_concepts(past_query))
                additional_concepts.update(past_concepts - query_concepts)
        
        # إضافة المفاهيم الإضافية إلى الاستعلام
        expanded_query = query
        if additional_concepts:
            expanded_query += " " + " ".join(list(additional_concepts)[:5])  # إضافة أهم 5 مفاهيم
        
        logger.info(f"توسيع الاستعلام: '{query}' -> '{expanded_query}'")
        return expanded_query
    
    def _rerank_with_feedback(self, results: List[Dict], similar_queries: List[Dict]) -> List[Dict]:
        """
        إعادة ترتيب النتائج بناءً على التغذية الراجعة السابقة
        
        Args:
            results: نتائج البحث الأولية
            similar_queries: الاستعلامات المشابهة والتغذية الراجعة المرتبطة بها
            
        Returns:
            النتائج المعاد ترتيبها
        """
        # استخراج معرفات النتائج ذات التغذية الراجعة الإيجابية والسلبية
        positive_ids = set()
        negative_ids = set()
        
        for similar_query in similar_queries:
            for feedback in similar_query["feedbacks"]:
                result_id = feedback.get("result_id", "")
                is_relevant = feedback.get("is_relevant", False)
                
                if result_id:
                    if is_relevant:
                        positive_ids.add(result_id)
                    else:
                        negative_ids.add(result_id)
        
        # تعديل درجات النتائج بناءً على التغذية الراجعة
        for result in results:
            result_id = result.get("id", "")
            current_score = result.get("score", 0.0)
            
            # زيادة درجة النتائج ذات التغذية الراجعة الإيجابية
            if result_id in positive_ids:
                result["score"] = current_score * 1.2  # زيادة الدرجة بنسبة 20%
                result["boosted"] = True
            
            # خفض درجة النتائج ذات التغذية الراجعة السلبية
            if result_id in negative_ids:
                result["score"] = current_score * 0.8  # خفض الدرجة بنسبة 20%
                result["demoted"] = True
        
        # إعادة ترتيب النتائج
        return sorted(results, key=lambda x: x.get("score", 0.0), reverse=True)