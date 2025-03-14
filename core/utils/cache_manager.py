#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
مدير التخزين المؤقت - نظام متكامل لإدارة التخزين المؤقت متعدد المستويات

يوفر هذا النظام واجهة موحدة للتعامل مع التخزين المؤقت في التطبيق، ويدعم:
1. تخزين مؤقت متعدد المستويات (ذاكرة + ملفات)
2. إدارة دورة حياة البيانات المخزنة مؤقتًا
3. تنظيف تلقائي للبيانات منتهية الصلاحية
4. إحصائيات أداء مفصلة
5. تكامل مع نظام التسجيل
"""

import time
import logging
import json
import os
import functools
import hashlib
from typing import Dict, Any, Optional, List, Callable, Union, Tuple
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import threading

# استيراد نظام التخزين المؤقت المحسن
from core.data_processing.optimized_cache import OptimizedCache, cached

# إعداد التسجيل
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class CacheManager:
    """مدير متكامل للتخزين المؤقت متعدد المستويات"""
    
    _instance = None  # نمط Singleton للتأكد من وجود نسخة واحدة فقط
    
    def __new__(cls, *args, **kwargs):
        """تنفيذ نمط Singleton"""
        if cls._instance is None:
            cls._instance = super(CacheManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self, cache_dir: str = "data/cache", 
                 memory_ttl: int = 3600, 
                 disk_ttl: int = 86400,
                 max_memory_items: int = 1000,
                 enable_stats: bool = True,
                 auto_cleanup_interval: int = 3600):
        """تهيئة مدير التخزين المؤقت
        
        Args:
            cache_dir: مسار دليل التخزين المؤقت
            memory_ttl: مدة صلاحية التخزين المؤقت في الذاكرة بالثواني (ساعة واحدة افتراضيًا)
            disk_ttl: مدة صلاحية التخزين المؤقت في الملفات بالثواني (يوم واحد افتراضيًا)
            max_memory_items: الحد الأقصى لعدد العناصر في ذاكرة التخزين المؤقت
            enable_stats: تمكين إحصائيات الأداء
            auto_cleanup_interval: الفاصل الزمني للتنظيف التلقائي بالثواني
        """
        # تجنب إعادة التهيئة في نمط Singleton
        if self._initialized:
            return
            
        # إنشاء نظام التخزين المؤقت المحسن
        self.cache = OptimizedCache(
            cache_dir=cache_dir,
            memory_ttl=memory_ttl,
            disk_ttl=disk_ttl,
            max_memory_items=max_memory_items,
            enable_stats=enable_stats
        )
        
        # إعدادات إضافية
        self.auto_cleanup_interval = auto_cleanup_interval
        self.cache_enabled = True
        self.cache_dir = Path(cache_dir)
        
        # بدء عملية التنظيف التلقائي
        self._start_auto_cleanup()
        
        # تسجيل التهيئة
        logger.info(f"تم تهيئة مدير التخزين المؤقت بنجاح (ذاكرة TTL: {memory_ttl}ث، ملفات TTL: {disk_ttl}ث)")
        self._initialized = True
    
    def get(self, key: str) -> Any:
        """استرجاع قيمة من التخزين المؤقت
        
        Args:
            key: مفتاح القيمة
            
        Returns:
            القيمة المخزنة أو None إذا لم تكن موجودة
        """
        if not self.cache_enabled:
            return None
        
        return self.cache.get(key)
    
    def set(self, key: str, data: Any, memory_only: bool = False) -> None:
        """تخزين قيمة في التخزين المؤقت
        
        Args:
            key: مفتاح القيمة
            data: القيمة المراد تخزينها
            memory_only: تخزين في الذاكرة فقط دون الملفات
        """
        if not self.cache_enabled:
            return
        
        self.cache.set(key, data, memory_only)
    
    def clear(self, key: str = None) -> None:
        """مسح التخزين المؤقت
        
        Args:
            key: مفتاح القيمة (إذا كان None، يتم مسح كل التخزين المؤقت)
        """
        if not self.cache_enabled:
            return
        
        self.cache.clear(key)
        logger.info(f"تم مسح التخزين المؤقت: {key if key else 'الكل'}")
    
    def clear_expired(self) -> int:
        """مسح العناصر منتهية الصلاحية من التخزين المؤقت
        
        Returns:
            عدد العناصر التي تم مسحها
        """
        if not self.cache_enabled:
            return 0
        
        return self.cache.clear_expired()
    
    def get_stats(self) -> Dict[str, Any]:
        """الحصول على إحصائيات أداء التخزين المؤقت
        
        Returns:
            قاموس بإحصائيات الأداء
        """
        if not self.cache_enabled:
            return {"cache_disabled": True}
        
        stats = self.cache.get_stats()
        
        # إضافة معلومات إضافية
        stats["cache_dir"] = str(self.cache_dir)
        stats["auto_cleanup_interval"] = self.auto_cleanup_interval
        
        return stats
    
    def optimize(self) -> Dict[str, Any]:
        """تحسين أداء التخزين المؤقت
        
        Returns:
            إحصائيات التحسين
        """
        if not self.cache_enabled:
            return {"cache_disabled": True}
        
        # مسح العناصر منتهية الصلاحية
        cleared_count = self.clear_expired()
        
        # الحصول على إحصائيات التخزين المؤقت بعد التحسين
        stats = self.get_stats()
        stats["cleared_count"] = cleared_count
        
        logger.info(f"تم تحسين أداء التخزين المؤقت، تم مسح {cleared_count} عنصر منتهي الصلاحية")
        return stats
    
    def enable(self) -> None:
        """تمكين التخزين المؤقت"""
        self.cache_enabled = True
        logger.info("تم تمكين التخزين المؤقت")
    
    def disable(self) -> None:
        """تعطيل التخزين المؤقت"""
        self.cache_enabled = False
        logger.info("تم تعطيل التخزين المؤقت")
    
    def update_settings(self, memory_ttl: int = None, disk_ttl: int = None, 
                       max_memory_items: int = None) -> None:
        """تحديث إعدادات التخزين المؤقت
        
        Args:
            memory_ttl: مدة صلاحية التخزين المؤقت في الذاكرة بالثواني
            disk_ttl: مدة صلاحية التخزين المؤقت في الملفات بالثواني
            max_memory_items: الحد الأقصى لعدد العناصر في ذاكرة التخزين المؤقت
        """
        if memory_ttl is not None:
            self.cache.memory_ttl = memory_ttl
        
        if disk_ttl is not None:
            self.cache.disk_ttl = disk_ttl
        
        if max_memory_items is not None:
            self.cache.max_memory_items = max_memory_items
        
        logger.info(f"تم تحديث إعدادات التخزين المؤقت (ذاكرة TTL: {self.cache.memory_ttl}ث، ملفات TTL: {self.cache.disk_ttl}ث)")
    
    def _start_auto_cleanup(self) -> None:
        """بدء عملية تنظيف تلقائي للتخزين المؤقت"""
        def cleanup_task():
            while True:
                try:
                    # تنظيف دوري حسب الفاصل الزمني المحدد
                    time.sleep(self.auto_cleanup_interval)
                    if self.cache_enabled:
                        cleared_count = self.clear_expired()
                        if cleared_count > 0:
                            logger.info(f"التنظيف التلقائي: تم مسح {cleared_count} عنصر منتهي الصلاحية")
                except Exception as e:
                    logger.error(f"خطأ في عملية التنظيف التلقائي: {str(e)}")
        
        # بدء العملية في خلفية منفصلة
        cleanup_thread = threading.Thread(target=cleanup_task, daemon=True)
        cleanup_thread.start()
        logger.debug("تم بدء عملية التنظيف التلقائي للتخزين المؤقت")

# دالة مساعدة للحصول على مدير التخزين المؤقت
def get_cache_manager() -> CacheManager:
    """الحصول على نسخة من مدير التخزين المؤقت
    
    Returns:
        نسخة من مدير التخزين المؤقت
    """
    return CacheManager()

# مزخرف للتخزين المؤقت باستخدام مدير التخزين المؤقت
def cache_with_manager(ttl: int = None, key_prefix: str = "", memory_only: bool = False):
    """مزخرف للتخزين المؤقت للدوال باستخدام مدير التخزين المؤقت
    
    Args:
        ttl: مدة صلاحية التخزين المؤقت بالثواني (يستخدم القيمة الافتراضية إذا كان None)
        key_prefix: بادئة مفتاح التخزين المؤقت
        memory_only: تخزين في الذاكرة فقط دون الملفات
        
    Returns:
        دالة مغلفة
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # الحصول على مدير التخزين المؤقت
            cache_manager = get_cache_manager()
            
            # التحقق من تمكين التخزين المؤقت
            if not cache_manager.cache_enabled:
                return func(*args, **kwargs)
            
            # إنشاء مفتاح فريد للتخزين المؤقت
            cache_key = f"{key_prefix}{func.__name__}_{hash(str(args))}_{hash(str(kwargs))}"
            
            # محاولة استرجاع النتيجة من التخزين المؤقت
            result = cache_manager.get(cache_key)
            
            if result is not None:
                return result
            
            # تنفيذ الدالة وتخزين النتيجة
            result = func(*args, **kwargs)
            
            # تخزين النتيجة في التخزين المؤقت
            cache_manager.set(cache_key, result, memory_only=memory_only)
            
            return result
        
        return wrapper
    
    return decorator