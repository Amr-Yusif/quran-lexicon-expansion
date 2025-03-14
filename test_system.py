#!/usr/bin/env python3
"""
سكريبت اختبار النظام للتأكد من عمل جميع المكونات بشكل صحيح
"""

import os
import sys
import time
import logging
import dotenv
import pymongo
import redis
from qdrant_client import QdrantClient
import ollama
import requests

# إعداد التسجيل
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_mongodb():
    """اختبار الاتصال بـ MongoDB"""
    try:
        # محاولة الاتصال
        mongo_uri = os.getenv("MONGO_URI", "mongodb://admin:quranassistantpass@localhost:27017/")
        client = pymongo.MongoClient(mongo_uri)
        
        # اختبار الاتصال
        client.admin.command('ping')
        
        # إنشاء قاعدة بيانات الاختبار
        db = client["quran_assistant_test"]
        test_collection = db["test_collection"]
        
        # إدراج بيانات اختبار
        result = test_collection.insert_one({"test": "data", "timestamp": time.time()})
        
        # التحقق من الإدراج
        assert result.acknowledged
        
        # حذف بيانات الاختبار
        test_collection.delete_one({"_id": result.inserted_id})
        
        logger.info("✅ MongoDB: تم الاتصال والاختبار بنجاح")
        return True
    except Exception as e:
        logger.error(f"❌ MongoDB: خطأ في الاتصال: {str(e)}")
        return False

def test_redis():
    """اختبار الاتصال بـ Redis"""
    try:
        # محاولة الاتصال
        redis_host = os.getenv("REDIS_HOST", "localhost")
        redis_port = int(os.getenv("REDIS_PORT", "6379"))
        client = redis.Redis(host=redis_host, port=redis_port, decode_responses=True)
        
        # اختبار الاتصال
        client.ping()
        
        # اختبار القراءة والكتابة
        test_key = "test:key"
        test_value = f"test_value_{time.time()}"
        
        client.set(test_key, test_value)
        retrieved_value = client.get(test_key)
        
        # التحقق من القيمة
        assert retrieved_value == test_value
        
        # حذف البيانات
        client.delete(test_key)
        
        logger.info("✅ Redis: تم الاتصال والاختبار بنجاح")
        return True
    except Exception as e:
        logger.error(f"❌ Redis: خطأ في الاتصال: {str(e)}")
        return False

def test_qdrant():
    """اختبار الاتصال بـ Qdrant"""
    try:
        # محاولة الاتصال
        qdrant_url = os.getenv("QDRANT_URL", "http://localhost:6333")
        qdrant_api_key = os.getenv("QDRANT_API_KEY", None)
        
        client = QdrantClient(url=qdrant_url, api_key=qdrant_api_key)
        
        # الحصول على قائمة المجموعات
        collections = client.get_collections()
        
        # طباعة المعلومات
        logger.info(f"Qdrant: المجموعات المتاحة: {[c.name for c in collections.collections]}")
        
        # التحقق من وجود المجموعات المطلوبة
        required_collections = ["tafsir_explanations", "scholars_books", "scientific_miracles"]
        existing_collections = [c.name for c in collections.collections]
        
        missing_collections = [c for c in required_collections if c not in existing_collections]
        
        if missing_collections:
            logger.warning(f"⚠️ Qdrant: المجموعات التالية غير موجودة: {missing_collections}")
            
            # إنشاء المجموعات المفقودة
            for collection_name in missing_collections:
                logger.info(f"إنشاء مجموعة {collection_name}...")
                client.create_collection(
                    collection_name=collection_name,
                    vectors_config={
                        "size": 768,
                        "distance": "Cosine"
                    }
                )
                logger.info(f"✅ تم إنشاء مجموعة {collection_name} بنجاح")
        
        logger.info("✅ Qdrant: تم الاتصال والاختبار بنجاح")
        return True
    except Exception as e:
        logger.error(f"❌ Qdrant: خطأ في الاتصال: {str(e)}")
        return False

def test_ollama():
    """اختبار الاتصال بـ Ollama"""
    try:
        # الحصول على قائمة النماذج المتاحة
        models = ollama.list()
        
        # طباعة المعلومات
        logger.info(f"Ollama: النماذج المتاحة: {[m.get('name') for m in models.get('models', [])]}")
        
        # التحقق من وجود نموذج Mistral
        if not any(m.get('name') == 'mistral' for m in models.get('models', [])):
            logger.warning("⚠️ Ollama: نموذج Mistral غير موجود، جاري تحميله...")
            
            # تحميل نموذج Mistral
            ollama.pull("mistral")
            logger.info("✅ تم تحميل نموذج Mistral بنجاح")
        
        # اختبار الدردشة
        response = ollama.chat(model="mistral", messages=[
            {"role": "user", "content": "اكتب آية من القرآن الكريم عن العلم"}
        ])
        
        # طباعة الاستجابة
        logger.info(f"Ollama response: {response['message']['content']}")
        
        logger.info("✅ Ollama: تم الاتصال والاختبار بنجاح")
        return True
    except Exception as e:
        logger.error(f"❌ Ollama: خطأ في الاتصال: {str(e)}")
        return False

def main():
    """الدالة الرئيسية لاختبار النظام"""
    logger.info("بدء اختبار النظام...")
    
    # تحميل متغيرات البيئة
    dotenv.load_dotenv()
    
    # اختبار المكونات
    mongodb_ok = test_mongodb()
    redis_ok = test_redis()
    qdrant_ok = test_qdrant()
    ollama_ok = test_ollama()
    
    # تلخيص النتائج
    logger.info("\n==== نتائج الاختبار ====")
    logger.info(f"MongoDB: {'✅ نجاح' if mongodb_ok else '❌ فشل'}")
    logger.info(f"Redis: {'✅ نجاح' if redis_ok else '❌ فشل'}")
    logger.info(f"Qdrant: {'✅ نجاح' if qdrant_ok else '❌ فشل'}")
    logger.info(f"Ollama: {'✅ نجاح' if ollama_ok else '❌ فشل'}")
    
    # تحديد نتيجة الاختبار النهائية
    all_ok = all([mongodb_ok, redis_ok, qdrant_ok, ollama_ok])
    
    if all_ok:
        logger.info("✅ جميع المكونات تعمل بشكل صحيح. النظام جاهز للاستخدام!")
        return 0
    else:
        logger.error("❌ بعض المكونات لا تعمل بشكل صحيح. يرجى مراجعة السجلات أعلاه.")
        return 1

if __name__ == "__main__":
    sys.exit(main())