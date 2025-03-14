#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
مدير المعالجة المتوازية - نظام متكامل لإدارة المعالجة المتوازية وتحسين الأداء

يوفر هذا النظام واجهة موحدة للتعامل مع المعالجة المتوازية في التطبيق، ويدعم:
1. معالجة متوازية باستخدام المؤشرات (Threads) والعمليات (Processes)
2. تحديد العدد الأمثل للعمليات المتوازية بناءً على موارد النظام
3. معالجة البيانات على دفعات بشكل متوازي
4. قياس أداء المعالجة المتوازية
5. تكامل مع نظام التخزين المؤقت
"""

import os
import time
import logging
import functools
import numpy as np
from typing import List, Dict, Any, Callable, TypeVar, Generic, Iterable, Optional, Union, Tuple
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed
from multiprocessing import cpu_count

# استيراد مدير التخزين المؤقت
from core.utils.cache_manager import get_cache_manager, cache_with_manager

# إعداد التسجيل
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# تعريف أنواع عامة للمدخلات والمخرجات
T = TypeVar('T')  # نوع المدخلات
R = TypeVar('R')  # نوع المخرجات

class ParallelManager:
    """مدير متكامل للمعالجة المتوازية وتحسين الأداء"""
    
    _instance = None  # نمط Singleton للتأكد من وجود نسخة واحدة فقط
    
    def __new__(cls, *args, **kwargs):
        """تنفيذ نمط Singleton"""
        if cls._instance is None:
            cls._instance = super(ParallelManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self, max_workers: int = None, 
                 default_batch_size: int = 100,
                 enable_stats: bool = True,
                 use_processes: bool = False):
        """تهيئة مدير المعالجة المتوازية
        
        Args:
            max_workers: الحد الأقصى لعدد العمليات المتوازية (يتم حسابه تلقائيًا إذا كان None)
            default_batch_size: حجم الدفعة الافتراضي للمعالجة المتوازية
            enable_stats: تمكين إحصائيات الأداء
            use_processes: استخدام العمليات بدلاً من المؤشرات (أبطأ في البدء ولكن أفضل للمهام كثيفة الحوسبة)
        """
        # تجنب إعادة التهيئة في نمط Singleton
        if self._initialized:
            return
        
        # تحديد العدد الأمثل للعمليات المتوازية
        self.max_workers = max_workers if max_workers is not None else self._get_optimal_workers()
        self.default_batch_size = default_batch_size
        self.enable_stats = enable_stats
        self.use_processes = use_processes
        
        # إحصائيات الأداء
        self.stats = {
            "total_tasks": 0,
            "total_time": 0,
            "avg_task_time": 0,
            "speedup": 0,
            "efficiency": 0,
            "worker_performance": []
        }
        
        # تسجيل التهيئة
        logger.info(f"تم تهيئة مدير المعالجة المتوازية بنجاح (عدد العمليات: {self.max_workers})")
        self._initialized = True
    
    def _get_optimal_workers(self) -> int:
        """تحديد العدد الأمثل للعمليات المتوازية بناءً على موارد النظام
        
        Returns:
            العدد الأمثل للعمليات المتوازية
        """
        # الحصول على عدد وحدات المعالجة المركزية
        cpu_cores = cpu_count()
        
        # تحديد العدد الأمثل للعمليات المتوازية
        # عادة ما يكون العدد الأمثل هو عدد وحدات المعالجة المركزية + 1 للمهام التي تنتظر I/O
        optimal_workers = cpu_cores + 1
        
        return optimal_workers
    
    def process_in_parallel(self, items: List[T], process_func: Callable[[T], R], 
                           batch_size: int = None, workers: int = None, 
                           use_processes: bool = None) -> List[R]:
        """معالجة قائمة من العناصر بشكل متوازي
        
        Args:
            items: قائمة العناصر المراد معالجتها
            process_func: دالة المعالجة (تأخذ عنصرًا واحدًا وتعيد النتيجة)
            batch_size: حجم الدفعة (يستخدم القيمة الافتراضية إذا كان None)
            workers: عدد العمليات المتوازية (يستخدم القيمة الافتراضية إذا كان None)
            use_processes: استخدام العمليات بدلاً من المؤشرات (يستخدم القيمة الافتراضية إذا كان None)
            
        Returns:
            قائمة النتائج المعالجة
        """
        start_time = time.time()
        
        # استخدام القيم الافتراضية إذا لم يتم توفير قيم
        batch_size = batch_size if batch_size is not None else self.default_batch_size
        workers = workers if workers is not None else self.max_workers
        use_processes = use_processes if use_processes is not None else self.use_processes
        
        # تقسيم العناصر إلى دفعات
        batches = [items[i:i+batch_size] for i in range(0, len(items), batch_size)]
        results = []
        
        # تحديد عدد العمليات المتوازية المناسب
        actual_workers = min(workers, len(batches))
        
        logger.info(f"معالجة {len(items)} عنصر في {len(batches)} دفعة باستخدام {actual_workers} عملية متوازية")
        
        # اختيار نوع المنفذ (مؤشرات أو عمليات)
        executor_class = ProcessPoolExecutor if use_processes else ThreadPoolExecutor
        
        # معالجة الدفعات بشكل متوازي
        with executor_class(max_workers=actual_workers) as executor:
            # تعريف دالة لمعالجة دفعة واحدة
            def process_batch(batch):
                batch_results = []
                for item in batch:
                    try:
                        result = process_func(item)
                        batch_results.append(result)
                    except Exception as e:
                        logger.error(f"خطأ أثناء معالجة العنصر: {str(e)}")
                return batch_results
            
            # تنفيذ المعالجة المتوازية
            future_to_batch = {executor.submit(process_batch, batch): i for i, batch in enumerate(batches)}
            
            # جمع النتائج
            for future in as_completed(future_to_batch):
                try:
                    batch_results = future.result()
                    results.extend(batch_results)
                except Exception as e:
                    logger.error(f"خطأ أثناء معالجة الدفعة: {str(e)}")
        
        # حساب إحصائيات الأداء
        end_time = time.time()
        total_time = end_time - start_time
        
        if self.enable_stats:
            # تقدير الوقت التسلسلي (بدون توازي)
            sequential_time = self._estimate_sequential_time(items, process_func)
            
            # تحديث الإحصائيات
            self.stats["total_tasks"] += len(items)
            self.stats["total_time"] += total_time
            self.stats["avg_task_time"] = self.stats["total_time"] / self.stats["total_tasks"]
            
            # حساب التسريع والكفاءة
            speedup = sequential_time / total_time if total_time > 0 else 1
            efficiency = speedup / actual_workers if actual_workers > 0 else 0
            
            self.stats["speedup"] = speedup
            self.stats["efficiency"] = efficiency
            
            # تسجيل أداء العمليات المتوازية
            worker_perf = {
                "workers": actual_workers,
                "items": len(items),
                "batches": len(batches),
                "time": total_time,
                "speedup": speedup,
                "efficiency": efficiency
            }
            self.stats["worker_performance"].append(worker_perf)
            
            logger.info(f"تمت المعالجة في {total_time:.2f} ثانية (تسريع: {speedup:.2f}x، كفاءة: {efficiency:.2f})")
        else:
            logger.info(f"تمت المعالجة في {total_time:.2f} ثانية")
        
        return results
    
    def process_batches(self, items: List[T], process_func: Callable[[List[T]], List[R]], 
                       batch_size: int = None, workers: int = None, 
                       use_processes: bool = None) -> List[R]:
        """معالجة قائمة من العناصر على شكل دفعات بشكل متوازي
        
        Args:
            items: قائمة العناصر المراد معالجتها
            process_func: دالة المعالجة (تأخذ دفعة كاملة وتعيد قائمة النتائج)
            batch_size: حجم الدفعة (يستخدم القيمة الافتراضية إذا كان None)
            workers: عدد العمليات المتوازية (يستخدم القيمة الافتراضية إذا كان None)
            use_processes: استخدام العمليات بدلاً من المؤشرات (يستخدم القيمة الافتراضية إذا كان None)
            
        Returns:
            قائمة النتائج المعالجة
        """
        start_time = time.time()
        
        # استخدام القيم الافتراضية إذا لم يتم توفير قيم
        batch_size = batch_size if batch_size is not None else self.default_batch_size
        workers = workers if workers is not None else self.max_workers
        use_processes = use_processes if use_processes is not None else self.use_processes
        
        # تقسيم العناصر إلى دفعات
        batches = [items[i:i+batch_size] for i in range(0, len(items), batch_size)]
        results = []
        
        # تحديد عدد العمليات المتوازية المناسب
        actual_workers = min(workers, len(batches))
        
        logger.info(f"معالجة {len(items)} عنصر في {len(batches)} دفعة باستخدام {actual_workers} عملية متوازية")
        
        # اختيار نوع المنفذ (مؤشرات أو عمليات)
        executor_class = ProcessPoolExecutor if use_processes else ThreadPoolExecutor
        
        # معالجة الدفعات بشكل متوازي
        with executor_class(max_workers=actual_workers) as executor:
            # تنفيذ المعالجة المتوازية
            future_to_batch = {executor.submit(process_func, batch): i for i, batch in enumerate(batches)}
            
            # جمع النتائج
            for future in as_completed(future_to_batch):
                try:
                    batch_results = future.result()
                    results.extend(batch_results)
                except Exception as e:
                    logger.error(f"خطأ أثناء معالجة الدفعة: {str(e)}")
        
        # حساب إحصائيات الأداء
        end_time = time.time()
        total_time = end_time - start_time
        
        if self.enable_stats:
            # تقدير الوقت التسلسلي (بدون توازي)
            sequential_time = self._estimate_sequential_batch_time(batches, process_func)
            
            # تحديث الإحصائيات
            self.stats["total_tasks"] += len(batches)
            self.stats["total_time"] += total_time
            self.stats["avg_task_time"] = self.stats["total_time"] / self.stats["total_tasks"]
            
            # حساب التسريع والكفاءة
            speedup = sequential_time / total_time if total_time > 0 else 1
            efficiency = speedup / actual_workers if actual_workers > 0 else 0
            
            self.stats["speedup"] = speedup
            self.stats["efficiency"] = efficiency
            
            # تسجيل أداء العمليات المتوازية
            worker_perf = {
                "workers": actual_workers,
                "items": len(items),
                "batches": len(batches),
                "time": total_time,
                "speedup": speedup,
                "efficiency": efficiency
            }
            self.stats["worker_performance"].append(worker_perf)
            
            logger.info(f"تمت معالجة الدفعات في {total_time:.2f} ثانية (تسريع: {speedup:.2f}x، كفاءة: {efficiency:.2f})")
        else:
            logger.info(f"تمت معالجة الدفعات في {total_time:.2f} ثانية")
        
        return results
    
    def _estimate_sequential_time(self, items: List[T], process_func: Callable[[T], R]) -> float:
        """تقدير الوقت التسلسلي لمعالجة العناصر بدون توازي
        
        Args:
            items: قائمة العناصر المراد معالجتها
            process_func: دالة المعالجة
            
        Returns:
            الوقت التقديري للمعالجة التسلسلية
        """
        # أخذ عينة من العناصر لتقدير الوقت
        sample_size = min(5, len(items))
        sample_indices = np.linspace(0, len(items) - 1, sample_size, dtype=int)
        sample_items = [items[i] for i in sample_indices]
        
        # قياس وقت معالجة العينة
        start_time = time.time()
        for item in sample_items:
            try:
                process_func(item)
            except Exception:
                pass
        end_time = time.time()
        
        # تقدير الوقت الكلي
        sample_time = end_time - start_time
        estimated_time = sample_time * (len(items) / sample_size)
        
        return max(estimated_time, 0.001)  # تجنب القسمة على صفر
    
    def _estimate_sequential_batch_time(self, batches: List[List[T]], process_func: Callable[[List[T]], List[R]]) -> float:
        """تقدير الوقت التسلسلي لمعالجة الدفعات بدون توازي
        
        Args:
            batches: قائمة الدفعات المراد معالجتها
            process_func: دالة المعالجة
            
        Returns:
            الوقت التقديري للمعالجة التسلسلية
        """
        # أخذ عينة من الدفعات لتقدير الوقت
        sample_size = min(3, len(batches))
        sample_indices = np.linspace(0, len(batches) - 1, sample_size, dtype=int)
        sample_batches = [batches[i] for i in sample_indices]
        
        # قياس وقت معالجة العينة
        start_time = time.time()
        for batch in sample_batches:
            try:
                process_func(batch)
            except Exception:
                pass
        end_time = time.time()
        
        # تقدير الوقت الكلي
        sample_time = end_time - start_time
        estimated_time = sample_time * (len(batches) / sample_size)
        
        return max(estimated_time, 0.001)  # تجنب القسمة على صفر
    
    def get_stats(self) -> Dict[str, Any]:
        """الحصول على إحصائيات أداء المعالجة المتوازية
        
        Returns:
            قاموس بإحصائيات الأداء
        """
        if not self.enable_stats:
            return {"stats_disabled": True}
        
        return self.stats.copy()
    
    def update_settings(self, max_workers: int = None, default_batch_size: int = None,
                       use_processes: bool = None) -> None:
        """تحديث إعدادات المعالجة المتوازية
        
        Args:
            max_workers: الحد الأقصى لعدد العمليات المتوازية
            default_batch_size: حجم الدفعة الافتراضي
            use_processes: استخدام العمليات بدلاً من المؤشرات
        """
        if max_workers is not None:
            self.max_workers = max_workers
        
        if default_batch_size is not None:
            self.default_batch_size = default_batch_size
        
        if use_processes is not None:
            self.use_processes = use_processes
        
        logger.info(f"تم تحديث إعدادات المعالجة المتوازية (عدد العمليات: {self.max_workers}, حجم الدفعة: {self.default_batch_size})")

# دالة مساعدة للحصول على مدير المعالجة المتوازية
def get_parallel_manager() -> ParallelManager:
    """الحصول على نسخة من مدير المعالجة المتوازية
    
    Returns:
        نسخة من مدير المعالجة المتوازية
    """
    return ParallelManager()

# مزخرف للمعالجة المتوازية
def parallel_process(batch_size: int = None, workers: int = None, use_processes: bool = None):
    """مزخرف للمعالجة المتوازية للدوال
    
    Args:
        batch_size: حجم الدفعة (يستخدم القيمة الافتراضية إذا كان None)
        workers: عدد العمليات المتوازية (يستخدم القيمة الافتراضية إذا كان None)
        use_processes: استخدام العمليات بدلاً من المؤشرات (يستخدم القيمة الافتراضية إذا كان None)
        
    Returns:
        دالة مغلفة
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(items, *args, **kwargs):
            # الحصول على مدير المعالجة المتوازية
            parallel_manager = get_parallel_manager()
            
            # تعريف دالة المعالجة
            def process_item(item):
                return func(item, *args, **kwargs)
            
            # تنفيذ المعالجة المتوازية
            return parallel_manager.process_in_parallel(
                items=items,
                process_func=process_item,
                batch_size=batch_size,
                workers=workers,
                use_processes=use_processes
            )
        
        return wrapper
    
    return decoratorساب الت