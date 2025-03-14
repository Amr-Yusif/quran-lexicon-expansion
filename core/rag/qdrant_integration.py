#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
نظام تكامل Qdrant - تخزين واسترجاع التضمينات بكفاءة
يوفر واجهة متقدمة للتفاعل مع Qdrant للبحث المتجهي
"""

import os
import logging
import numpy as np
from typing import List, Dict, Any, Optional, Union, Tuple
from pathlib import Path
import json
import time
from datetime import datetime

from qdrant_client import QdrantClient
from qdrant_client.http import models
from qdrant_client.http.exceptions import UnexpectedResponse

# إعداد التسجيل
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class QdrantIntegration:
    """
    نظام تكامل Qdrant - يوفر واجهة متقدمة للتفاعل مع Qdrant للبحث المتجهي
    """
    
    def __init__(self, url: str = None, api_key: str = None):
        """
        تهيئة نظام تكامل Qdrant
        
        Args:
            url: عنوان URL لخدمة Qdrant
            api_key: مفتاح API لـ Qdrant
        """
        logger.info("تهيئة نظام تكامل Qdrant...")
        
        # استخدام القيم الافتراضية من متغيرات البيئة إذا لم يتم تحديدها
        self.url = url or os.getenv("QDRANT_URL", "http://localhost:6333")
        self.api_key = api_key or os.getenv("QDRANT_API_KEY", "")
        
        # تهيئة عميل Qdrant
        try:
            self.client = QdrantClient(
                url=self.url,
                api_key=self.api_key
            )
            logger.info(f"تم الاتصال بـ Qdrant على {self.url}")
        except Exception as e:
            logger.error(f"خطأ في الاتصال بـ Qdrant: {str(e)}")
            logger.info("استخدام وضع الذاكرة المحلي كحل بديل")
            self.client = QdrantClient(":memory:")
        
        # تخزين مؤقت للمجموعات
        self.collections_cache = {}
        self.cache_timestamp = 0
        self.cache_ttl = 300  # 5 دقائق
        
        logger.info("تم تهيئة نظام تكامل Qdrant بنجاح")
    
    def create_collection(self, collection_name: str, vector_size: int, 
                         distance: str = "Cosine", metadata_schema: Dict[str, Any] = None) -> bool:
        """
        إنشاء مجموعة جديدة في Qdrant
        
        Args:
            collection_name: اسم المجموعة
            vector_size: حجم المتجه (بُعد التضمين)
            distance: مقياس المسافة (Cosine, Euclid, Dot)
            metadata_schema: مخطط البيانات الوصفية (اختياري)
            
        Returns:
            نجاح العملية
        """
        try:
            # تحويل مقياس المسافة إلى النوع المناسب
            distance_type = models.Distance.COSINE
            if distance.lower() == "euclid":
                distance_type = models.Distance.EUCLID
            elif distance.lower() == "dot":
                distance_type = models.Distance.DOT
            
            # التحقق مما إذا كانت المجموعة موجودة بالفعل
            collections = self.list_collections()
            if collection_name in collections:
                logger.info(f"المجموعة {collection_name} موجودة بالفعل")
                return True
            
            # إنشاء المجموعة
            vector_config = models.VectorParams(
                size=vector_size,
                distance=distance_type
            )
            
            # إعداد مخطط البيانات الوصفية إذا تم تحديده
            schema = None
            if metadata_schema:
                schema = {}
                for field_name, field_type in metadata_schema.items():
                    if field_type == "keyword":
                        schema[field_name] = models.KeywordIndexParams()
                    elif field_type == "integer":
                        schema[field_name] = models.IntegerIndexParams()
                    elif field_type == "float":
                        schema[field_name] = models.FloatIndexParams()
                    elif field_type == "geo":
                        schema[field_name] = models.GeoIndexParams()
                    elif field_type == "text":
                        schema[field_name] = models.TextIndexParams()
            
            # إنشاء المجموعة
            self.client.create_collection(
                collection_name=collection_name,
                vectors_config=vector_config,
                optimizers_config=models.OptimizersConfigDiff(
                    indexing_threshold=20000,  # عتبة الفهرسة
                    memmap_threshold=100000  # عتبة استخدام ملفات الذاكرة
                ),
                timeout=60  # مهلة أطول للعمليات الكبيرة
            )
            
            # إضافة مخطط البيانات الوصفية إذا تم تحديده
            if schema:
                self.client.create_payload_index(
                    collection_name=collection_name,
                    field_name="*",
                    field_schema=schema
                )
            
            logger.info(f"تم إنشاء المجموعة {collection_name} بنجاح")
            return True
            
        except Exception as e:
            logger.error(f"خطأ في إنشاء مجموعة Qdrant: {str(e)}")
            return False
    
    def list_collections(self, force_refresh: bool = False) -> List[str]:
        """
        الحصول على قائمة المجموعات
        
        Args:
            force_refresh: إجبار تحديث التخزين المؤقت
            
        Returns:
            قائمة أسماء المجموعات
        """
        current_time = time.time()
        
        # استخدام التخزين المؤقت إذا كان حديثًا
        if not force_refresh and current_time - self.cache_timestamp < self.cache_ttl:
            return list(self.collections_cache.keys())
        
        try:
            # الحصول على قائمة المجموعات من Qdrant
            collections_list = self.client.get_collections().collections
            
            # تحديث التخزين المؤقت
            self.collections_cache = {collection.name: collection for collection in collections_list}
            self.cache_timestamp = current_time
            
            return list(self.collections_cache.keys())
            
        except Exception as e:
            logger.error(f"خطأ في الحصول على قائمة المجموعات: {str(e)}")
            return []
    
    def get_collection_info(self, collection_name: str) -> Dict[str, Any]:
        """
        الحصول على معلومات مجموعة
        
        Args:
            collection_name: اسم المجموعة
            
        Returns:
            معلومات المجموعة
        """
        try:
            # الحصول على معلومات المجموعة من Qdrant
            collection_info = self.client.get_collection(collection_name=collection_name)
            
            # تحويل المعلومات إلى قاموس
            info = {
                "name": collection_name,
                "vector_size": collection_info.config.params.vectors.size,
                "distance": str(collection_info.config.params.vectors.distance),
                "points_count": collection_info.vectors_count,
                "indexed_vectors_count": collection_info.indexed_vectors_count,
                "status": collection_info.status
            }
            
            return info
            
        except Exception as e:
            logger.error(f"خطأ في الحصول على معلومات المجموعة {collection_name}: {str(e)}")
            return {"error": str(e)}
    
    def delete_collection(self, collection_name: str) -> bool:
        """
        حذف مجموعة
        
        Args:
            collection_name: اسم المجموعة
            
        Returns:
            نجاح العملية
        """
        try:
            # حذف المجموعة من Qdrant
            self.client.delete_collection(collection_name=collection_name)
            
            # تحديث التخزين المؤقت
            if collection_name in self.collections_cache:
                del self.collections_cache[collection_name]
            
            logger.info(f"تم حذف المجموعة {collection_name} بنجاح")
            return True
            
        except Exception as e:
            logger.error(f"خطأ في حذف المجموعة {collection_name}: {str(e)}")
            return False
    
    def upload_vectors(self, collection_name: str, vectors: List[List[float]], 
                      metadata: List[Dict[str, Any]], ids: List[str] = None, 
                      batch_size: int = 100) -> bool:
        """
        تحميل متجهات إلى مجموعة
        
        Args:
            collection_name: اسم المجموعة
            vectors: قائمة المتجهات
            metadata: قائمة البيانات الوصفية
            ids: قائمة المعرفات (اختياري)
            batch_size: حجم الدفعة
            
        Returns:
            نجاح العملية
        """
        try:
            # التحقق من تطابق الأطوال
            if len(vectors) != len(metadata):
                logger.error("عدم تطابق أطوال المتجهات والبيانات الوصفية")
                return False
            
            # إنشاء معرفات إذا لم يتم تحديدها
            if ids is None:
                ids = [str(i) for i in range(len(vectors))]
            elif len(ids) != len(vectors):
                logger.error("عدم تطابق أطوال المتجهات والمعرفات")
                return False
            
            # تحميل المتجهات على دفعات
            total_vectors = len(vectors)
            for i in range(0, total_vectors, batch_size):
                end_idx = min(i + batch_size, total_vectors)
                batch_vectors = vectors[i:end_idx]
                batch_metadata = metadata[i:end_idx]
                batch_ids = ids[i:end_idx]
                
                # إنشاء نقاط Qdrant
                points = [
                    models.PointStruct(
                        id=id,
                        vector=vector,
                        payload=meta
                    ) for id, vector, meta in zip(batch_ids, batch_vectors, batch_metadata)
                ]
                
                # تحميل النقاط
                self.client.upsert(
                    collection_name=collection_name,
                    points=points
                )
                
                logger.info(f"تم تحميل دفعة {i//batch_size + 1}/{(total_vectors-1)//batch_size + 1} ({end_idx - i} نقطة)")
            
            logger.info(f"تم تحميل {total_vectors} متجه إلى المجموعة {collection_name} بنجاح")
            return True
            
        except Exception as e:
            logger.error(f"خطأ في تحميل المتجهات إلى المجموعة {collection_name}: {str(e)}")
            return False
    
    def search(self, collection_name: str, query_vector: List[float], limit: int = 10, 
              filter_query: Dict[str, Any] = None, with_payload: bool = True, 
              with_vectors: bool = False) -> List[Dict[str, Any]]:
        """
        البحث في مجموعة
        
        Args:
            collection_name: اسم المجموعة
            query_vector: متجه الاستعلام
            limit: عدد النتائج
            filter_query: استعلام التصفية (اختياري)
            with_payload: إرجاع البيانات الوصفية
            with_vectors: إرجاع المتجهات
            
        Returns:
            قائمة النتائج
        """
        try:
            # إنشاء استعلام التصفية إذا تم تحديده
            filter_condition = None
            if filter_query:
                filter_condition = self._build_filter_condition(filter_query)
            
            # البحث في المجموعة
            search_result = self.client.search(
                collection_name=collection_name,
                query_vector=query_vector,
                limit=limit,
                query_filter=filter_condition,
                with_payload=with_payload,
                with_vectors=with_vectors
            )
            
            # تحويل النتائج إلى قائمة
            return search_result
        except Exception as e:
            logger.error(f"خطأ أثناء البحث في المجموعة: {str(e)}")
            return []