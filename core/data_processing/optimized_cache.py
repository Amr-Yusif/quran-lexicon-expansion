#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
نظام تخزين مؤقت متعدد المستويات محسن للأداء

يوفر هذا النظام آلية تخزين مؤقت متعددة المستويات تجمع بين:
1. تخزين مؤقت في الذاكرة للوصول السريع للبيانات المستخدمة بشكل متكرر
2. تخزين مؤقت في الملفات للبيانات طويلة الأمد
3. استراتيجيات إدارة الذاكرة المؤقتة وتنظيفها
4. قياس أداء عمليات التخزين المؤقت
"""

import time
import logging
import json
import os
import functools
import hashlib
from typing import Dict, Any, Optional, List, Callable, Union
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import threading

# إعداد التسجيل
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class OptimizedCache:
    """نظام تخزين مؤقت متعدد المستويات محسن للأداء"""
    
    def __init__(self, cache_dir: str = "data/cache", 
                 memory_ttl: int = 3600, 
                 disk_ttl: int = 86400,
                 max_memory_items: int = 1000,
                 enable_stats: bool = True):
        """
        تهيئة نظام التخزين المؤقت المحسن
        
        Args:
            cache_dir: مسار دليل التخزين المؤقت
            memory_ttl: مدة صلاحية التخزين المؤقت في الذاكرة بالثواني (ساعة واحدة افتراضيًا)
            disk_ttl: مدة صلاحية التخزين المؤقت في الملفات بالثواني (يوم واحد افتراضيًا)
            max_memory_items: الحد الأقصى لعدد العناصر في ذاكرة التخزين المؤقت
            enable_stats: تمكين إحصائيات الأداء
        """
        # إنشاء دليل التخزين المؤقت إذا لم يكن موجودًا
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # إعدادات التخزين المؤقت
        self.memory_cache = {}
        self.memory_ttl = memory_ttl
        self.disk_ttl = disk_ttl
        self.max_memory_items = max_memory_items
        self.enable_stats = enable_stats
        
        # قفل للتزامن في البيئات متعددة المؤشرات
        self.lock = threading.RLock()
        
        # إحصائيات الأداء
        self.stats = {
            "memory_hits": 0,
            "disk_hits": 0,
            "misses": 0,
            "sets": 0,
            "evictions": 0,
            "memory_hit_time": 0,
            "disk_hit_time": 0,
            "miss_time": 0,
            "set_time": 0
        }
        
        logger.info(f"تم تهيئة نظام التخزين المؤقت المحسن في {cache_dir}")
        
        # بدء عملية تنظيف دورية للتخزين المؤقت
        self._start_cleanup_thread()
    
    def get(self, key: str) -> Any:
        """
        استرجاع قيمة من التخزين المؤقت
        
        Args:
            key: مفتاح القيمة
            
        Returns:
            القيمة المخزنة أو None إذا لم تكن موجودة
        """
        start_time = time.time()
        
        # تحويل المفتاح إلى سلسلة آمنة للاستخدام في أسماء الملفات
        safe_key = self._get_safe_key(key)
        
        with self.lock:
            # البحث أولاً في ذاكرة التخزين المؤقت (أسرع)
            if safe_key in self.memory_cache:
                cache_data = self.memory_cache[safe_key]
                if time.time() - cache_data["timestamp"] <= self.memory_ttl:
                    # تحديث إحصائيات الأداء
                    if self.enable_stats:
                        self.stats["memory_hits"] += 1
                        self.stats["memory_hit_time"] += time.time() - start_time
                    
                    logger.debug(f"استرجاع من ذاكرة التخزين المؤقت: {key}")
                    return cache_data["data"]
        
        # البحث في ملفات التخزين المؤقت (أبطأ)
        try:
            cache_file = self.cache_dir / f"{safe_key}.json"
            if cache_file.exists():
                with open(cache_file, "r", encoding="utf-8") as f:
                    cache_data = json.load(f)
                
                if time.time() - cache_data.get("timestamp", 0) <= self.disk_ttl:
                    # تحديث ذاكرة التخزين المؤقت
                    with self.lock:
                        self.memory_cache[safe_key] = {
                            "timestamp": cache_data["timestamp"],
                            "data": cache_data["data"],
                            "access_count": 1,
                            "last_access": time.time()
                        }
                        
                        # تنظيف ذاكرة التخزين المؤقت إذا تجاوزت الحد الأقصى
                        self._cleanup_memory_cache_if_needed()
                    
                    # تحديث إحصائيات الأداء
                    if self.enable_stats:
                        with self.lock:
                            self.stats["disk_hits"] += 1
                            self.stats["disk_hit_time"] += time.time() - start_time
                    
                    logger.debug(f"استرجاع من ملف التخزين المؤقت: {key}")
                    return cache_data["data"]
        except Exception as e:
            logger.warning(f"خطأ أثناء استرجاع التخزين المؤقت: {str(e)}")
        
        # تحديث إحصائيات الأداء
        if self.enable_stats:
            with self.lock:
                self.stats["misses"] += 1
                self.stats["miss_time"] += time.time() - start_time
        
        return None
    
    def set(self, key: str, data: Any, memory_only: bool = False) -> None:
        """
        تخزين قيمة في التخزين المؤقت
        
        Args:
            key: مفتاح القيمة
            data: القيمة المراد تخزينها
            memory_only: تخزين في الذاكرة فقط دون الملفات
        """
        start_time = time.time()
        
        # تحويل المفتاح إلى سلسلة آمنة للاستخدام في أسماء الملفات
        safe_key = self._get_safe_key(key)
        
        cache_data = {
            "timestamp": time.time(),
            "data": data
        }
        
        # تخزين في ذاكرة التخزين المؤقت
        with self.lock:
            self.memory_cache[safe_key] = {
                **cache_data,
                "access_count": 0,
                "last_access": time.time()
            }
            
            # تنظيف ذاكرة التخزين المؤقت إذا تجاوزت الحد الأقصى
            self._cleanup_memory_cache_if_needed()
        
        # تخزين في ملف التخزين المؤقت (إذا لم يكن memory_only)
        if not memory_only:
            try:
                cache_file = self.cache_dir / f"{safe_key}.json"
                with open(cache_file, "w", encoding="utf-8") as f:
                    json.dump(cache_data, f, ensure_ascii=False)
                logger.debug(f"تم تخزين البيانات في ملف التخزين المؤقت: {key}")
            except Exception as e:
                logger.warning(f"خطأ أثناء التخزين المؤقت في الملف: {str(e)}")
        
        # تحديث إحصائيات الأداء
        if self.enable_stats:
            with self.lock:
                self.stats["sets"] += 1
                self.stats["set_time"] += time.time() - start_time
        
        logger.debug(f"تم تخزين البيانات في التخزين المؤقت: {key}")
    
    def clear(self, key: str = None) -> None:
        """
        مسح التخزين المؤقت
        
        Args:
            key: مفتاح القيمة (إذا كان None، يتم مسح كل التخزين المؤقت)
        """
        with self.lock:
            if key is None:
                # مسح كل التخزين المؤقت
                self.memory_cache = {}
                for cache_file in self.cache_dir.glob("*.json"):
                    try:
                        cache_file.unlink()
                    except Exception as e:
                        logger.warning(f"خطأ أثناء مسح ملف التخزين المؤقت {cache_file}: {str(e)}")
                logger.info("تم مسح كل التخزين المؤقت")
            else:
                # مسح قيمة محددة
                safe_key = self._get_safe_key(key)
                
                if safe_key in self.memory_cache:
                    del self.memory_cache[safe_key]
                
                cache_file = self.cache_dir / f"{safe_key}.json"
                if cache_file.exists():
                    try:
                        cache_file.unlink()
                    except Exception as e:
                        logger.warning(f"خطأ أثناء مسح ملف التخزين المؤقت {cache_file}: {str(e)}")
                logger.debug(f"تم مسح التخزين المؤقت: {key}")
    
    def clear_expired(self) -> int:
        """
        مسح العناصر منتهية الصلاحية من التخزين المؤقت
        
        Returns:
            عدد العناصر التي تم مسحها
        """
        current_time = time.time()
        cleared_count = 0
        
        # مسح العناصر منتهية الصلاحية من ذاكرة التخزين المؤقت
        with self.lock:
            expired_keys = []
            for key, cache_data in self.memory_cache.items():
                if current_time - cache_data["timestamp"] > self.memory_ttl:
                    expired_keys.append(key)
            
            for key in expired_keys:
                del self.memory_cache[key]
            
            cleared_count += len(expired_keys)
        
        # مسح العناصر منتهية الصلاحية من ملفات التخزين المؤقت
        for cache_file in self.cache_dir.glob("*.json"):
            try:
                with open(cache_file, "r", encoding="utf-8") as f:
                    cache_data = json.load(f)
                
                if current_time - cache_data.get("timestamp", 0) > self.disk_ttl:
                    cache_file.unlink()
                    cleared_count += 1
            except Exception as e:
                logger.warning(f"خطأ أثناء مسح ملف التخزين المؤقت {cache_file}: {str(e)}")
                # مسح الملف إذا كان هناك خطأ في قراءته
                try:
                    cache_file.unlink()
                    cleared_count += 1
                except:
                    pass
        
        logger.info(f"تم مسح {cleared_count} عنصر منتهي الصلاحية من التخزين المؤقت")
        return cleared_count
    
    def get_stats(self) -> Dict[str, Any]:
        """
        الحصول على إحصائيات أداء التخزين المؤقت
        
        Returns:
            قاموس بإحصائيات الأداء
        """
        if not self.enable_stats:
            return {"stats_disabled": True}
        
        with self.lock:
            stats = self.stats.copy()
            
            # حساب معدلات الإصابة والفقدان
            total_requests = stats["memory_hits"] + stats["disk_hits"] + stats["misses"]
            if total_requests > 0:
                stats["hit_rate"] = (stats["memory_hits"] + stats["disk_hits"]) / total_requests
                stats["memory_hit_rate"] = stats["memory_hits"] / total_requests if stats["memory_hits"] > 0 else 0
                stats["disk_hit_rate"] = stats["disk_hits"] / total_requests if stats["disk_hits"] > 0 else 0
                stats["miss_rate"] = stats["misses"] / total_requests
            
            # حساب متوسط أوقات الاستجابة
            if stats["memory_hits"] > 0:
                stats["avg_memory_hit_time"] = stats["memory_hit_time"] / stats["memory_hits"]
            if stats["disk_hits"] > 0:
                stats["avg_disk_hit_time"] = stats["disk_hit_time"] / stats["disk_hits"]
            if stats["misses"] > 0:
                stats["avg_miss_time"] = stats["miss_time"] / stats["misses"]
            if stats["sets"] > 0:
                stats["avg_set_time"] = stats["set_time"] / stats["sets"]
            
            # إضافة معلومات حول حجم التخزين المؤقت
            stats["memory_cache_size"] = len(self.memory_cache)
            stats["memory_cache_limit"] = self.max_memory_items
            
            return stats
    
    def _cleanup_memory_cache_if_needed(self) -> None:
        """
        تنظيف ذاكرة التخزين المؤقت إذا تجاوزت الحد الأقصى
        """
        if len(self.memory_cache) <= self.max_memory_items:
            return
        
        # عدد العناصر التي سيتم إزالتها
        items_to_remove = len(self.memory_cache) - self.max_memory_items + int(self.max_memory_items * 0.1)  # إزالة 10% إضافية لتجنب التنظيف المتكرر
        
        # ترتيب العناصر حسب عدد مرات الوصول والوقت الأخير للوصول
        items = [(k, v.get("access_count", 0), v.get("last_access", 0)) for k, v in self.memory_cache.items()]
        items.sort(key=lambda x: (x[1], x[2]))  # ترتيب تصاعدي حسب عدد مرات الوصول ثم وقت آخر وصول
        
        # إزالة العناصر الأقل استخدامًا
        for i in range(min(items_to_remove, len(items))):
            if items[i][0] in self.memory_cache:
                del self.memory_cache[items[i][0]]
                if self.enable_stats:
                    self.stats["evictions"] += 1
        
        logger.debug(f"تم تنظيف ذاكرة التخزين المؤقت، تم إزالة {items_to_remove} عنصر")
    
    def _start_cleanup_thread(self) -> None:
        """
        بدء عملية تنظيف دورية للتخزين المؤقت
        """
        def cleanup_task():
            while True:
                try:
                    # تنظيف كل ساعة
                    time.sleep(3600)
                    self.clear_expired()
                except Exception as e:
                    logger.error(f"خطأ في عملية التنظيف الدورية: {str(e)}")
        
        # بدء العملية في خلفية منفصلة
        cleanup_thread = threading.Thread(target=cleanup_task, daemon=True)
        cleanup_thread.start()
        logger.debug("تم بدء عملية التنظيف الدورية للتخزين المؤقت")
    
    def _get_safe_key(self, key: str) -> str:
        """
        تحويل المفتاح إلى سلسلة آمنة للاستخدام في أسماء الملفات
        
        Args:
            key: المفتاح الأصلي
            
        Returns:
            مفتاح آمن للاستخدام في أسماء الملفات
        """
        # استخدام تجزئة MD5 لتحويل المفتاح إلى سلسلة آمنة وقصيرة
        return hashlib.md5(str(key).encode()).hexdigest()

# ===== مزخرف للتخزين المؤقت =====

def cached(cache: OptimizedCache = None, ttl: int = None, key_prefix: str = ""):
    """
    مزخرف للتخزين المؤقت للدوال
    
    Args:
        cache: كائن التخزين المؤقت المستخدم
        ttl: مدة صلاحية التخزين المؤقت بالثواني
        key_prefix: بادئة مفتاح التخزين المؤقت
        
    Returns:
        دالة مغلفة
    """
    def decorator(func):
        # إنشاء كائن تخزين مؤقت إذا لم يتم توفيره
        nonlocal cache
        if cache is None:
            cache = OptimizedCache()
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # إنشاء مفتاح فريد للتخزين المؤقت
            cache_key = f"{key_prefix}{func.__name__}_{hash(str(args))}_{hash(str(kwargs))}"
            
            # محاولة استرجاع النتيجة من التخزين المؤقت
            result = cache.get(cache_key)
            
            if result is not None:
                return result
            
            # تنفيذ الدالة وتخزين النتيجة
            result = func(*args, **kwargs)
            
            # تخزين النتيجة في التخزين المؤقت
            cache.set(cache_key, result)
            
            return result
        
        return wrapper
    
    return decorator