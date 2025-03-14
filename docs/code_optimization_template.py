#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
قالب تحسين الأداء - نموذج مرجعي لتطبيق تقنيات تحسين الأداء

هذا الملف يقدم أمثلة عملية لتقنيات تحسين الأداء التي يمكن تطبيقها في مشروع تحليل النصوص القرآنية والإسلامية.
يمكن استخدام هذه الأمثلة كمرجع عند تحسين المكونات المختلفة للنظام.
"""

import time
import logging
import json
import functools
import os
from typing import List, Dict, Any, Optional
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import numpy as np

# إعداد التسجيل
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ===== 1. تحسين التخزين المؤقت =====

class OptimizedCache:
    """نموذج لتخزين مؤقت متعدد المستويات"""
    
    def __init__(self, cache_dir: str = "data/cache", ttl: int = 86400):
        """تهيئة نظام التخزين المؤقت
        
        Args:
            cache_dir: مسار دليل التخزين المؤقت
            ttl: مدة صلاحية التخزين المؤقت بالثواني
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.memory_cache = {}
        self.cache_ttl = ttl
    
    def get(self, key: str) -> Any:
        """استرجاع قيمة من التخزين المؤقت
        
        Args:
            key: مفتاح القيمة
            
        Returns:
            القيمة المخزنة أو None إذا لم تكن موجودة
        """
        # البحث أولاً في ذاكرة التخزين المؤقت (أسرع)
        if key in self.memory_cache:
            cache_data = self.memory_cache[key]
            if time.time() - cache_data["timestamp"] <= self.cache_ttl:
                logger.debug(f"استرجاع من ذاكرة التخزين المؤقت: {key}")
                return cache_data["data"]
        
        # البحث في ملفات التخزين المؤقت (أبطأ)
        try:
            cache_file = self.cache_dir / f"{key}.json"
            if cache_file.exists():
                with open(cache_file, "r", encoding="utf-8") as f:
                    cache_data = json.load(f)
                
                if time.time() - cache_data.get("timestamp", 0) <= self.cache_ttl:
                    # تحديث ذاكرة التخزين المؤقت
                    self.memory_cache[key] = {
                        "timestamp": cache_data["timestamp"],
                        "data": cache_data["data"]
                    }
                    logger.debug(f"استرجاع من ملف التخزين المؤقت: {key}")
                    return cache_data["data"]
        except Exception as e:
            logger.warning(f"خطأ أثناء استرجاع التخزين المؤقت: {str(e)}")
        
        return None
    
    def set(self, key: str, data: Any) -> None:
        """تخزين قيمة في التخزين المؤقت
        
        Args:
            key: مفتاح القيمة
            data: القيمة المراد تخزينها
        """
        cache_data = {
            "timestamp": time.time(),
            "data": data
        }
        
        # تخزين في ذاكرة التخزين المؤقت
        self.memory_cache[key] = cache_data
        
        # تخزين في ملف التخزين المؤقت
        try:
            cache_file = self.cache_dir / f"{key}.json"
            with open(cache_file, "w", encoding="utf-8") as f:
                json.dump(cache_data, f, ensure_ascii=False)
            logger.debug(f"تم تخزين البيانات في التخزين المؤقت: {key}")
        except Exception as e:
            logger.warning(f"خطأ أثناء التخزين المؤقت: {str(e)}")
    
    def clear(self, key: str = None) -> None:
        """مسح التخزين المؤقت
        
        Args:
            key: مفتاح القيمة (إذا كان None، يتم مسح كل التخزين المؤقت)
        """
        if key is None:
            # مسح كل التخزين المؤقت
            self.memory_cache = {}
            for cache_file in self.cache_dir.glob("*.json"):
                cache_file.unlink()
            logger.info("تم مسح كل التخزين المؤقت")
        else:
            # مسح قيمة محددة
            if key in self.memory_cache:
                del self.memory_cache[key]
            
            cache_file = self.cache_dir / f"{key}.json"
            if cache_file.exists():
                cache_file.unlink()
            logger.debug(f"تم مسح التخزين المؤقت: {key}")

# ===== 2. تحسين المعالجة المتوازية =====

def process_in_parallel(items: List[Any], process_func, batch_size: int = 100, max_workers: int = None) -> List[Any]:
    """معالجة قائمة من العناصر بشكل متوازي
    
    Args:
        items: قائمة العناصر المراد معالجتها
        process_func: دالة المعالجة
        batch_size: حجم الدفعة
        max_workers: أقصى عدد للعمليات المتوازية
        
    Returns:
        قائمة النتائج
    """
    if not items:
        return []
    
    # تحديد عدد العمليات المتوازية
    if max_workers is None:
        max_workers = os.cpu_count() or 4
    
    # تقسيم العناصر إلى دفعات
    batches = [items[i:i+batch_size] for i in range(0, len(items), batch_size)]
    results = []
    
    logger.info(f"معالجة {len(items)} عنصر في {len(batches)} دفعة")
    
    # معالجة الدفعات بشكل متوازي
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        batch_results = list(executor.map(process_func, batches))
        
        # دمج النتائج
        for batch_result in batch_results:
            results.extend(batch_result)
    
    return results

# مثال لدالة معالجة دفعة
def process_batch(batch: List[Dict]) -> List[Dict]:
    """معالجة دفعة من البيانات
    
    Args:
        batch: دفعة البيانات
        
    Returns:
        البيانات المعالجة
    """
    processed_batch = []
    
    for item in batch:
        # معالجة العنصر
        processed_item = item.copy()
        processed_item["processed"] = True
        processed_batch.append(processed_item)
    
    return processed_batch

# ===== 3. قياس الأداء =====

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

# مثال لاستخدام مزخرف قياس الأداء
@measure_performance
def expensive_operation(size: int = 1000) -> np.ndarray:
    """عملية مكلفة للاختبار
    
    Args:
        size: حجم المصفوفة
        
    Returns:
        مصفوفة النتائج
    """
    # محاكاة عملية مكلفة
    time.sleep(0.1)
    return np.random.rand(size, size)

# ===== 4. الحوسبة الكسولة =====

class LazyComputation:
    """نموذج للحوسبة الكسولة"""
    
    def __init__(self, compute_func, *args, **kwargs):
        """تهيئة الحوسبة الكسولة
        
        Args:
            compute_func: دالة الحساب
            *args, **kwargs: وسائط دالة الحساب
        """
        self.compute_func = compute_func
        self.args = args
        self.kwargs = kwargs
        self._result = None
        self._computed = False
    
    def get_result(self):
        """الحصول على نتيجة الحساب
        
        Returns:
            نتيجة الحساب
        """
        if not self._computed:
            logger.debug("تنفيذ الحساب الكسول")
            self._result = self.compute_func(*self.args, **self.kwargs)
            self._computed = True
        return self._result

# مثال لاستخدام الحوسبة الكسولة
def expensive_calculation(a: int, b: int) -> int:
    """حساب مكلف للاختبار
    
    Args:
        a: العدد الأول
        b: العدد الثاني
        
    Returns:
        نتيجة الحساب
    """
    logger.info("تنفيذ حساب مكلف")
    time.sleep(1)  # محاكاة عملية مكلفة
    return a * b

# ===== 5. تحسين البحث =====

class OptimizedSearch:
    """نموذج لبحث محسن"""
    
    def __init__(self, cache: OptimizedCache = None):
        """تهيئة البحث المحسن
        
        Args:
            cache: نظام التخزين المؤقت
        """
        self.cache = cache or OptimizedCache()
    
    def search(self, query: str, documents: List[Dict], limit: int = 10) -> List[Dict]:
        """بحث محسن في المستندات
        
        Args:
            query: استعلام البحث
            documents: المستندات المراد البحث فيها
            limit: عدد النتائج المطلوبة
            
        Returns:
            قائمة بالنتائج المسترجعة
        """
        # التحقق من وجود النتائج في التخزين المؤقت
        cache_key = f"search_{hash(query)}_{hash(str(documents)[:100])}"
        cached_result = self.cache.get(cache_key)
        
        if cached_result is not None:
            logger.info("تم استرجاع نتائج البحث من التخزين المؤقت")
            return cached_result[:limit]
        
        # تنفيذ البحث
        logger.info(f"تنفيذ بحث جديد: {query}")
        
        # محاكاة عملية بحث
        results = []
        for i, doc in enumerate(documents):
            # حساب درجة التشابه (محاكاة)
            score = 1.0 / (i + 1)  # درجة تشابه بسيطة للتوضيح
            
            result = {
                **doc,
                "score": score,
                "rank": i + 1
            }
            results.append(result)
        
        # ترتيب النتائج حسب درجة التشابه
        results = sorted(results, key=lambda x: x["score"], reverse=True)[:limit]
        
        # تخزين النتائج في التخزين المؤقت
        self.cache.set(cache_key, results)
        
        return results

# ===== 6. مثال للاستخدام =====

def main():
    """دالة رئيسية للتوضيح"""
    # إنشاء بيانات اختبار
    documents = [
        {"id": f"doc{i}", "text": f"نص المستند {i}"} for i in range(1000)
    ]