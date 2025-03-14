"""
مكتبة إدارة ذاكرة المحادثات المحلية - بديل لـ Mem0
"""

from typing import List, Dict, Any, Optional, Union
import json
import logging
from datetime import datetime
from pymongo import MongoClient, DESCENDING
from sentence_transformers import SentenceTransformer
import numpy as np
import redis

# إعداد التسجيل
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LocalMemoryClient:
    """
    فئة لإدارة ذاكرة المحادثات المحلية كبديل لـ Mem0
    """
    
    def __init__(self, 
                 mongo_uri="mongodb://localhost:27017/", 
                 redis_host="localhost", 
                 redis_port=6379, 
                 db_name="quran_assistant",
                 embedding_model_name="paraphrase-multilingual-mpnet-base-v2"):
        """
        تهيئة ذاكرة المحادثات المحلية
        
        Args:
            mongo_uri: مسار اتصال MongoDB
            redis_host: مضيف Redis
            redis_port: منفذ Redis
            db_name: اسم قاعدة البيانات
            embedding_model_name: اسم نموذج التضمين
        """
        try:
            # اتصال MongoDB
            self.mongo_client = MongoClient(mongo_uri)
            self.db = self.mongo_client[db_name]
            self.memory_collection = self.db["memory"]
            self.embeddings_collection = self.db["memory_embeddings"]
            
            # إعداد الفهارس
            self.memory_collection.create_index([("user_id", 1), ("timestamp", -1)])
            self.embeddings_collection.create_index([("memory_id", 1)], unique=True)
            self.embeddings_collection.create_index([("user_id", 1)])
            
            # اتصال Redis
            self.redis_client = redis.Redis(host=redis_host, port=redis_port, decode_responses=True)
            
            # تحميل نموذج التضمين
            self.embedding_model = SentenceTransformer(embedding_model_name)
            
            logger.info("تم تهيئة ذاكرة المحادثات المحلية")
            
        except Exception as e:
            logger.error(f"خطأ في تهيئة ذاكرة المحادثات المحلية: {str(e)}")
            raise
    
    def _create_embedding(self, text: str) -> List[float]:
        """
        إنشاء تضمين للنص
        
        Args:
            text: النص المراد تضمينه
            
        Returns:
            مصفوفة تضمين
        """
        try:
            if not text:
                return []
            
            embedding = self.embedding_model.encode(text)
            return embedding.tolist()
        except Exception as e:
            logger.error(f"خطأ في إنشاء التضمين: {str(e)}")
            return []
    
    def _calculate_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """
        حساب التشابه بين تضمينين
        
        Args:
            embedding1: التضمين الأول
            embedding2: التضمين الثاني
            
        Returns:
            درجة التشابه (0-1)
        """
        try:
            # تحويل المصفوفات إلى نوع numpy
            vec1 = np.array(embedding1)
            vec2 = np.array(embedding2)
            
            # حساب تشابه جيب التمام (cosine similarity)
            dot_product = np.dot(vec1, vec2)
            norm1 = np.linalg.norm(vec1)
            norm2 = np.linalg.norm(vec2)
            
            similarity = dot_product / (norm1 * norm2)
            
            return float(similarity)
        except Exception as e:
            logger.error(f"خطأ في حساب التشابه: {str(e)}")
            return 0.0
    
    def add(self, messages: Union[str, List[Dict[str, str]]], user_id: str) -> bool:
        """
        إضافة ذاكرة جديدة للمستخدم
        
        Args:
            messages: محتوى الذاكرة (نص أو قائمة رسائل)
            user_id: معرف المستخدم
            
        Returns:
            نجاح العملية
        """
        try:
            # معالجة المحتوى
            if isinstance(messages, list):
                # تحويل قائمة الرسائل إلى نص
                content = "\n".join([f"{msg.get('role', 'unknown')}: {msg.get('content', '')}" for msg in messages])
                raw_messages = messages
            else:
                # استخدام النص مباشرة
                content = messages
                raw_messages = [{"role": "system", "content": content}]
            
            # إنشاء سجل الذاكرة
            timestamp = datetime.now()
            memory_record = {
                "user_id": user_id,
                "content": content,
                "raw_messages": raw_messages,
                "timestamp": timestamp,
                "added_at": timestamp.isoformat()
            }
            
            # حفظ الذاكرة
            result = self.memory_collection.insert_one(memory_record)
            memory_id = result.inserted_id
            
            # إنشاء وحفظ التضمين
            embedding = self._create_embedding(content)
            if embedding:
                embedding_record = {
                    "memory_id": memory_id,
                    "user_id": user_id,
                    "embedding": embedding,
                    "timestamp": timestamp
                }
                self.embeddings_collection.insert_one(embedding_record)
            
            # تنظيف ذاكرة التخزين المؤقت
            cache_key = f"memory_search:{user_id}:*"
            for key in self.redis_client.keys(cache_key):
                self.redis_client.delete(key)
            
            return True
        except Exception as e:
            logger.error(f"خطأ في إضافة الذاكرة: {str(e)}")
            return False
    
    def search(self, query: str, user_id: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        البحث في ذاكرة المستخدم
        
        Args:
            query: نص البحث
            user_id: معرف المستخدم
            limit: عدد النتائج الأقصى
            
        Returns:
            قائمة بالذاكرات المطابقة مع درجة التطابق
        """
        try:
            # التحقق من التخزين المؤقت أولاً
            cache_key = f"memory_search:{user_id}:{query}:{limit}"
            cached_results = self.redis_client.get(cache_key)
            if cached_results:
                return json.loads(cached_results)
            
            # إنشاء تضمين لنص البحث
            query_embedding = self._create_embedding(query)
            if not query_embedding:
                return []
            
            # الحصول على تضمينات المستخدم
            embeddings = list(self.embeddings_collection.find({"user_id": user_id}))
            
            # حساب التشابه وترتيب النتائج
            similarities = []
            for emb in embeddings:
                memory_id = emb["memory_id"]
                memory = self.memory_collection.find_one({"_id": memory_id})
                if memory:
                    similarity = self._calculate_similarity(query_embedding, emb["embedding"])
                    similarities.append({
                        "memory": memory["content"],
                        "score": similarity,
                        "memory_id": str(memory_id),
                        "created_at": memory.get("added_at"),
                        "raw_messages": memory.get("raw_messages", [])
                    })
            
            # ترتيب النتائج حسب درجة التشابه
            similarities.sort(key=lambda x: x["score"], reverse=True)
            results = similarities[:limit]
            
            # تخزين النتائج مؤقتًا
            self.redis_client.setex(cache_key, 300, json.dumps(results))  # صالح لمدة 5 دقائق
            
            return results
        except Exception as e:
            logger.error(f"خطأ في البحث عن الذاكرات: {str(e)}")
            return []
    
    def get_recent(self, user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        الحصول على أحدث الذاكرات للمستخدم
        
        Args:
            user_id: معرف المستخدم
            limit: عدد النتائج الأقصى
            
        Returns:
            قائمة بأحدث الذاكرات للمستخدم
        """
        try:
            # التحقق من التخزين المؤقت أولاً
            cache_key = f"memory_recent:{user_id}:{limit}"
            cached_results = self.redis_client.get(cache_key)
            if cached_results:
                return json.loads(cached_results)
            
            # الحصول على أحدث الذاكرات
            memories = list(self.memory_collection.find(
                {"user_id": user_id}
            ).sort("timestamp", DESCENDING).limit(limit))
            
            # تنسيق النتائج
            results = []
            for memory in memories:
                results.append({
                    "memory": memory["content"],
                    "memory_id": str(memory["_id"]),
                    "created_at": memory.get("added_at"),
                    "raw_messages": memory.get("raw_messages", [])
                })
            
            # تخزين النتائج مؤقتًا
            self.redis_client.setex(cache_key, 300, json.dumps(results))  # صالح لمدة 5 دقائق
            
            return results
        except Exception as e:
            logger.error(f"خطأ في الحصول على أحدث الذاكرات: {str(e)}")
            return []
    
    def delete(self, memory_id: str, user_id: str) -> bool:
        """
        حذف ذاكرة
        
        Args:
            memory_id: معرف الذاكرة
            user_id: معرف المستخدم
            
        Returns:
            نجاح العملية
        """
        try:
            # حذف الذاكرة
            result = self.memory_collection.delete_one({"_id": memory_id, "user_id": user_id})
            
            # حذف التضمين المرتبط
            self.embeddings_collection.delete_one({"memory_id": memory_id})
            
            # تنظيف ذاكرة التخزين المؤقت
            cache_key = f"memory_*:{user_id}:*"
            for key in self.redis_client.keys(cache_key):
                self.redis_client.delete(key)
            
            return result.deleted_count > 0
        except Exception as e:
            logger.error(f"خطأ في حذف الذاكرة: {str(e)}")
            return False
    
    def clear_all(self, user_id: str) -> bool:
        """
        حذف جميع الذاكرات للمستخدم
        
        Args:
            user_id: معرف المستخدم
            
        Returns:
            نجاح العملية
        """
        try:
            # حذف جميع الذاكرات
            self.memory_collection.delete_many({"user_id": user_id})
            
            # حذف جميع التضمينات
            self.embeddings_collection.delete_many({"user_id": user_id})
            
            # تنظيف ذاكرة التخزين المؤقت
            cache_key = f"memory_*:{user_id}:*"
            for key in self.redis_client.keys(cache_key):
                self.redis_client.delete(key)
            
            return True
        except Exception as e:
            logger.error(f"خطأ في حذف جميع الذاكرات: {str(e)}")
            return False