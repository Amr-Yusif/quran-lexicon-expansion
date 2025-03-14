"""
وحدة تخزين البيانات المحلية باستخدام MongoDB و Redis
"""

import os
import json
import time
import pymongo
import redis
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union
import logging

# إعداد التسجيل
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LocalStorage:
    """
    فئة لإدارة التخزين المحلي باستخدام MongoDB وRedis
    """

    def __init__(self, mongo_uri="mongodb://localhost:27017/", 
                 redis_host="localhost", redis_port=6379, 
                 db_name="quran_assistant"):
        """
        تهيئة التخزين المحلي
        
        Args:
            mongo_uri: مسار اتصال MongoDB
            redis_host: مضيف Redis
            redis_port: منفذ Redis
            db_name: اسم قاعدة البيانات
        """
        try:
            # اتصال MongoDB
            self.mongo_client = pymongo.MongoClient(mongo_uri)
            self.db = self.mongo_client[db_name]
            logger.info(f"تم الاتصال بقاعدة بيانات MongoDB: {db_name}")
            
            # اتصال Redis
            self.redis_client = redis.Redis(host=redis_host, port=redis_port, decode_responses=True)
            self.redis_client.ping()  # للتحقق من الاتصال
            logger.info(f"تم الاتصال بـ Redis: {redis_host}:{redis_port}")
            
            # إعداد المجموعات
            self.users_collection = self.db["users"]
            self.quran_collection = self.db["quran"]
            self.tafseer_collection = self.db["tafseer"]
            self.miracles_collection = self.db["miracles"]
            self.memory_collection = self.db["memory"]
            
            # إنشاء فهارس
            self._setup_indexes()
            
        except pymongo.errors.ConnectionFailure:
            logger.error("فشل الاتصال بـ MongoDB")
            raise
        except redis.exceptions.ConnectionError:
            logger.error("فشل الاتصال بـ Redis")
            raise
    
    def _setup_indexes(self):
        """إعداد الفهارس لتحسين الأداء"""
        # فهارس المستخدمين
        self.users_collection.create_index("username", unique=True)
        self.users_collection.create_index("email", unique=True)
        
        # فهارس القرآن
        self.quran_collection.create_index([("surah_number", 1), ("ayah_number", 1)])
        self.quran_collection.create_index([("text", "text")])
        
        # فهارس التفسير
        self.tafseer_collection.create_index([("surah_number", 1), ("ayah_number", 1)])
        self.tafseer_collection.create_index([("text", "text")])
        
        # فهارس المعجزات
        self.miracles_collection.create_index("title")
        self.miracles_collection.create_index([("explanation", "text")])
        
        # فهارس الذاكرة
        self.memory_collection.create_index([("user_id", 1), ("timestamp", -1)])
        self.memory_collection.create_index([("content", "text")])
        
        logger.info("تم إنشاء الفهارس في MongoDB")
    
    # ===== وظائف التخزين المؤقت باستخدام Redis =====
    
    def cache_set(self, key: str, value: Any, expiry_seconds: int = 3600):
        """
        تخزين قيمة في التخزين المؤقت
        
        Args:
            key: مفتاح التخزين
            value: القيمة للتخزين (سيتم تحويلها إلى JSON)
            expiry_seconds: فترة الصلاحية بالثواني
        """
        try:
            serialized_value = json.dumps(value, ensure_ascii=False)
            self.redis_client.setex(key, expiry_seconds, serialized_value)
            return True
        except Exception as e:
            logger.error(f"خطأ في تخزين البيانات المؤقتة: {str(e)}")
            return False
    
    def cache_get(self, key: str) -> Optional[Any]:
        """
        استرجاع قيمة من التخزين المؤقت
        
        Args:
            key: مفتاح التخزين
            
        Returns:
            القيمة المخزنة أو None إذا لم توجد
        """
        try:
            value = self.redis_client.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            logger.error(f"خطأ في استرجاع البيانات المؤقتة: {str(e)}")
            return None
    
    def cache_delete(self, key: str) -> bool:
        """حذف مفتاح من التخزين المؤقت"""
        try:
            return bool(self.redis_client.delete(key))
        except Exception as e:
            logger.error(f"خطأ في حذف البيانات المؤقتة: {str(e)}")
            return False
    
    # ===== وظائف إدارة المستخدمين =====
    
    def save_user(self, user_data: Dict[str, Any]) -> bool:
        """
        حفظ أو تحديث بيانات المستخدم
        
        Args:
            user_data: بيانات المستخدم
        
        Returns:
            نجاح العملية
        """
        try:
            # التحقق من وجود المستخدم
            if "_id" in user_data:
                # تحديث مستخدم موجود
                result = self.users_collection.replace_one(
                    {"_id": user_data["_id"]}, 
                    user_data
                )
                return result.modified_count > 0
            else:
                # إضافة مستخدم جديد
                result = self.users_collection.insert_one(user_data)
                return bool(result.inserted_id)
        except Exception as e:
            logger.error(f"خطأ في حفظ المستخدم: {str(e)}")
            return False
    
    def get_user(self, username: str = None, email: str = None, user_id: str = None) -> Optional[Dict[str, Any]]:
        """
        استرجاع بيانات المستخدم
        
        Args:
            username: اسم المستخدم
            email: البريد الإلكتروني
            user_id: معرف المستخدم
        
        Returns:
            بيانات المستخدم أو None إذا لم يوجد
        """
        try:
            query = {}
            if username:
                query["username"] = username
            elif email:
                query["email"] = email
            elif user_id:
                query["_id"] = user_id
            else:
                return None
            
            # محاولة استرجاع من التخزين المؤقت أولاً
            cache_key = f"user:{username or email or user_id}"
            cached_user = self.cache_get(cache_key)
            if cached_user:
                return cached_user
            
            # استرجاع من MongoDB
            user = self.users_collection.find_one(query)
            if user:
                # تخزين في التخزين المؤقت
                self.cache_set(cache_key, user, 300)  # صالح لمدة 5 دقائق
            return user
        except Exception as e:
            logger.error(f"خطأ في استرجاع المستخدم: {str(e)}")
            return None
    
    def delete_user(self, user_id: str) -> bool:
        """حذف مستخدم"""
        try:
            result = self.users_collection.delete_one({"_id": user_id})
            # حذف من التخزين المؤقت
            self.cache_delete(f"user:{user_id}")
            return result.deleted_count > 0
        except Exception as e:
            logger.error(f"خطأ في حذف المستخدم: {str(e)}")
            return False
    
    # ===== وظائف إدارة ذاكرة المحادثات =====
    
    def add_memory(self, user_id: str, content: str, metadata: Dict[str, Any] = None) -> bool:
        """
        إضافة ذاكرة محادثة جديدة
        
        Args:
            user_id: معرف المستخدم
            content: محتوى الذاكرة
            metadata: بيانات وصفية إضافية
        
        Returns:
            نجاح العملية
        """
        try:
            memory = {
                "user_id": user_id,
                "content": content,
                "timestamp": datetime.now(),
                "metadata": metadata or {}
            }
            
            result = self.memory_collection.insert_one(memory)
            
            # مسح التخزين المؤقت ذي الصلة
            self.cache_delete(f"memories:{user_id}")
            
            return bool(result.inserted_id)
        except Exception as e:
            logger.error(f"خطأ في إضافة الذاكرة: {str(e)}")
            return False
    
    def search_memories(self, user_id: str, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        البحث في ذاكرة المحادثات
        
        Args:
            user_id: معرف المستخدم
            query: نص البحث
            limit: عدد النتائج الأقصى
            
        Returns:
            قائمة بالذاكرات المطابقة
        """
        try:
            # مفتاح التخزين المؤقت
            cache_key = f"memories_search:{user_id}:{query}:{limit}"
            cached_results = self.cache_get(cache_key)
            if cached_results:
                return cached_results
            
            # البحث في MongoDB
            results = list(self.memory_collection.find(
                {"user_id": user_id, "$text": {"$search": query}},
                {"score": {"$meta": "textScore"}}
            ).sort([("score", {"$meta": "textScore"})]).limit(limit))
            
            # تخزين النتائج مؤقتًا
            self.cache_set(cache_key, results, 60)  # صالح لمدة دقيقة واحدة
            
            return results
        except Exception as e:
            logger.error(f"خطأ في البحث عن الذاكرات: {str(e)}")
            return []
    
    def get_recent_memories(self, user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """استرجاع آخر الذاكرات"""
        try:
            # مفتاح التخزين المؤقت
            cache_key = f"memories_recent:{user_id}:{limit}"
            cached_results = self.cache_get(cache_key)
            if cached_results:
                return cached_results
            
            # استرجاع من MongoDB
            results = list(self.memory_collection.find(
                {"user_id": user_id}
            ).sort("timestamp", -1).limit(limit))
            
            # تخزين النتائج مؤقتًا
            self.cache_set(cache_key, results, 60)  # صالح لمدة دقيقة واحدة
            
            return results
        except Exception as e:
            logger.error(f"خطأ في استرجاع الذاكرات الحديثة: {str(e)}")
            return []
    
    # ===== وظائف إدارة بيانات القرآن =====
    
    def save_quran_data(self, quran_data: List[Dict[str, Any]]) -> bool:
        """
        حفظ بيانات القرآن
        
        Args:
            quran_data: قائمة بالآيات القرآنية
            
        Returns:
            نجاح العملية
        """
        try:
            if not quran_data:
                return False
            
            # حذف البيانات الموجودة
            self.quran_collection.delete_many({})
            
            # إضافة البيانات الجديدة
            result = self.quran_collection.insert_many(quran_data)
            
            # مسح التخزين المؤقت
            self.redis_client.delete("quran_data_loaded")
            
            return len(result.inserted_ids) > 0
        except Exception as e:
            logger.error(f"خطأ في حفظ بيانات القرآن: {str(e)}")
            return False
    
    def search_quran(self, query: str, limit: int = 20) -> List[Dict[str, Any]]:
        """
        البحث في القرآن الكريم
        
        Args:
            query: نص البحث
            limit: عدد النتائج الأقصى
            
        Returns:
            قائمة بالآيات المطابقة
        """
        try:
            # مفتاح التخزين المؤقت
            cache_key = f"quran_search:{query}:{limit}"
            cached_results = self.cache_get(cache_key)
            if cached_results:
                return cached_results
            
            # البحث في MongoDB
            results = list(self.quran_collection.find(
                {"$text": {"$search": query}},
                {"score": {"$meta": "textScore"}}
            ).sort([("score", {"$meta": "textScore"})]).limit(limit))
            
            # تخزين النتائج مؤقتًا
            self.cache_set(cache_key, results, 300)  # صالح لمدة 5 دقائق
            
            return results
        except Exception as e:
            logger.error(f"خطأ في البحث عن آيات القرآن: {str(e)}")
            return []
    
    # ===== وظائف إدارة بيانات التفسير =====
    
    def save_tafseer_data(self, tafseer_data: List[Dict[str, Any]], tafseer_name: str) -> bool:
        """
        حفظ بيانات التفسير
        
        Args:
            tafseer_data: قائمة بتفاسير الآيات
            tafseer_name: اسم التفسير
            
        Returns:
            نجاح العملية
        """
        try:
            if not tafseer_data:
                return False
            
            # إضافة اسم التفسير لكل سجل
            for item in tafseer_data:
                item["tafseer_name"] = tafseer_name
            
            # حذف بيانات التفسير الموجودة
            self.tafseer_collection.delete_many({"tafseer_name": tafseer_name})
            
            # إضافة البيانات الجديدة
            result = self.tafseer_collection.insert_many(tafseer_data)
            
            # مسح التخزين المؤقت
            self.redis_client.delete(f"tafseer_data_loaded:{tafseer_name}")
            
            return len(result.inserted_ids) > 0
        except Exception as e:
            logger.error(f"خطأ في حفظ بيانات التفسير: {str(e)}")
            return False
    
    def search_tafseer(self, query: str, tafseer_name: str = None, limit: int = 20) -> List[Dict[str, Any]]:
        """
        البحث في التفسير
        
        Args:
            query: نص البحث
            tafseer_name: اسم التفسير (اختياري)
            limit: عدد النتائج الأقصى
            
        Returns:
            قائمة بالتفاسير المطابقة
        """
        try:
            # مفتاح التخزين المؤقت
            cache_key = f"tafseer_search:{query}:{tafseer_name or 'all'}:{limit}"
            cached_results = self.cache_get(cache_key)
            if cached_results:
                return cached_results
            
            # إعداد الاستعلام
            search_query = {"$text": {"$search": query}}
            if tafseer_name:
                search_query["tafseer_name"] = tafseer_name
            
            # البحث في MongoDB
            results = list(self.tafseer_collection.find(
                search_query,
                {"score": {"$meta": "textScore"}}
            ).sort([("score", {"$meta": "textScore"})]).limit(limit))
            
            # تخزين النتائج مؤقتًا
            self.cache_set(cache_key, results, 300)  # صالح لمدة 5 دقائق
            
            return results
        except Exception as e:
            logger.error(f"خطأ في البحث عن التفاسير: {str(e)}")
            return []
    
    # ===== وظائف إدارة بيانات المعجزات العلمية =====
    
    def save_scientific_miracles(self, miracles_data: List[Dict[str, Any]]) -> bool:
        """
        حفظ بيانات المعجزات العلمية
        
        Args:
            miracles_data: قائمة بالمعجزات العلمية
            
        Returns:
            نجاح العملية
        """
        try:
            if not miracles_data:
                return False
            
            # حذف البيانات الموجودة
            self.miracles_collection.delete_many({})
            
            # إضافة البيانات الجديدة
            result = self.miracles_collection.insert_many(miracles_data)
            
            # مسح التخزين المؤقت
            self.redis_client.delete("miracles_data_loaded")
            
            return len(result.inserted_ids) > 0
        except Exception as e:
            logger.error(f"خطأ في حفظ بيانات المعجزات العلمية: {str(e)}")
            return False
    
    def get_all_scientific_miracles(self) -> List[Dict[str, Any]]:
        """
        استرجاع جميع المعجزات العلمية
        
        Returns:
            قائمة بجميع المعجزات العلمية
        """
        try:
            # مفتاح التخزين المؤقت
            cache_key = "all_miracles"
            cached_results = self.cache_get(cache_key)
            if cached_results:
                return cached_results
            
            # استرجاع من MongoDB
            results = list(self.miracles_collection.find())
            
            # تخزين النتائج مؤقتًا
            self.cache_set(cache_key, results, 3600)  # صالح لمدة ساعة
            
            return results
        except Exception as e:
            logger.error(f"خطأ في استرجاع المعجزات العلمية: {str(e)}")
            return []
    
    def search_scientific_miracles(self, query: str, limit: int = 20) -> List[Dict[str, Any]]:
        """
        البحث في المعجزات العلمية
        
        Args:
            query: نص البحث
            limit: عدد النتائج الأقصى
            
        Returns:
            قائمة بالمعجزات المطابقة
        """
        try:
            # مفتاح التخزين المؤقت
            cache_key = f"miracles_search:{query}:{limit}"
            cached_results = self.cache_get(cache_key)
            if cached_results:
                return cached_results
            
            # البحث في MongoDB
            results = list(self.miracles_collection.find(
                {"$text": {"$search": query}},
                {"score": {"$meta": "textScore"}}
            ).sort([("score", {"$meta": "textScore"})]).limit(limit))
            
            # تخزين النتائج مؤقتًا
            self.cache_set(cache_key, results, 300)  # صالح لمدة 5 دقائق
            
            return results
        except Exception as e:
            logger.error(f"خطأ في البحث عن المعجزات العلمية: {str(e)}")
            return []
    
    def add_scientific_miracle(self, miracle_data: Dict[str, Any]) -> bool:
        """
        إضافة معجزة علمية جديدة
        
        Args:
            miracle_data: بيانات المعجزة
            
        Returns:
            نجاح العملية
        """
        try:
            result = self.miracles_collection.insert_one(miracle_data)
            
            # مسح التخزين المؤقت
            self.redis_client.delete("all_miracles")
            
            return bool(result.inserted_id)
        except Exception as e:
            logger.error(f"خطأ في إضافة معجزة علمية: {str(e)}")
            return False