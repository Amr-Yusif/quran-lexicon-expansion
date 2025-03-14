"""
مدير Qdrant - إدارة مجموعات البيانات المتجهية والبحث الدلالي
"""
import os
import json
import numpy as np
from typing import List, Dict, Any, Optional, Union
from qdrant_client import QdrantClient
from qdrant_client.http import models
from qdrant_client.http.exceptions import UnexpectedResponse

class QdrantManager:
    """
    مدير Qdrant - يوفر واجهة للتفاعل مع Qdrant للبحث المتجهي
    """
    
    def __init__(self, 
                api_key: str = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIn0.wzZ1xzWs5MjVqV_BhblVOcKbuQrMwFlrnUU9IxxGz60", 
                url: str = "https://9c41ece4-5e7f-4f91-8292-37e234f6c201.us-east4-0.gcp.cloud.qdrant.io:6333",
                client: Optional[QdrantClient] = None):
        """
        تهيئة مدير Qdrant

        Args:
            api_key: مفتاح API لـ Qdrant (افتراضياً من المتغيرات البيئية)
            url: عنوان URL لخدمة Qdrant (افتراضياً من المتغيرات البيئية)
            client: عميل Qdrant مخصص (اختياري)
        """
        self.api_key = api_key
        self.url = url
        
        # استخدام العميل المقدم أو إنشاء عميل جديد
        if client:
            self.client = client
        else:
            try:
                self.client = QdrantClient(
                    url=self.url,
                    api_key=self.api_key
                )
            except Exception as e:
                print(f"خطأ في الاتصال بـ Qdrant: {str(e)}")
                # استخدام الوضع المحلي إذا فشل الاتصال بالسحابة
                print("استخدام وضع الذاكرة المحلي كحل بديل")
                self.client = QdrantClient(":memory:")
    
    def create_collection(self, collection_name: str, vector_size: int) -> bool:
        """
        إنشاء مجموعة جديدة في Qdrant

        Args:
            collection_name: اسم المجموعة
            vector_size: حجم المتجه (بُعد التضمين)

        Returns:
            نجاح العملية
        """
        try:
            # التحقق مما إذا كانت المجموعة موجودة بالفعل
            try:
                self.client.get_collection(collection_name)
                print(f"المجموعة {collection_name} موجودة بالفعل")
                return True
            except (UnexpectedResponse, Exception):
                # إنشاء المجموعة إذا لم تكن موجودة
                self.client.create_collection(
                    collection_name=collection_name,
                    vectors_config=models.VectorParams(
                        size=vector_size,
                        distance=models.Distance.COSINE
                    )
                )
                print(f"تم إنشاء المجموعة {collection_name} بنجاح")
                return True
        
        except Exception as e:
            print(f"خطأ في إنشاء مجموعة Qdrant: {str(e)}")
            return False
    
    def upload_documents(self, collection_name: str, documents: List[Dict[str, Any]]) -> bool:
        """
        تحميل وثائق إلى مجموعة Qdrant

        Args:
            collection_name: اسم المجموعة
            documents: قائمة الوثائق مع التضمينات

        Returns:
            نجاح العملية
        """
        try:
            # تحويل الوثائق إلى نقاط Qdrant
            points = []
            for doc in documents:
                # التحقق من وجود التضمين
                if "embedding" not in doc:
                    print(f"تخطي وثيقة بدون تضمين: {doc.get('id', 'unknown')}")
                    continue
                
                # إنشاء نقطة Qdrant
                point = models.PointStruct(
                    id=doc.get("id"),
                    vector=doc.get("embedding"),
                    payload={
                        "text": doc.get("text", ""),
                        "metadata": doc.get("metadata", {})
                    }
                )
                
                points.append(point)
            
            # تحميل النقاط إلى Qdrant
            if points:
                self.client.upsert(
                    collection_name=collection_name,
                    points=points
                )
                print(f"تم تحميل {len(points)} وثيقة إلى {collection_name}")
                return True
            else:
                print("لا توجد وثائق صالحة للتحميل")
                return False
        
        except Exception as e:
            print(f"خطأ في تحميل الوثائق إلى Qdrant: {str(e)}")
            return False
    
    def search(self, collection_name: str, query: str, embedding_model, limit: int = 5, filter_condition: Optional[Dict] = None) -> List[Dict[str, Any]]:
        """
        البحث في مجموعة Qdrant

        Args:
            collection_name: اسم المجموعة
            query: استعلام البحث
            embedding_model: نموذج التضمين
            limit: عدد النتائج المطلوبة
            filter_condition: شرط تصفية اختياري

        Returns:
            قائمة نتائج البحث
        """
        try:
            # تضمين الاستعلام
            query_vector = embedding_model.embed_text(query)
            
            # إنشاء شرط تصفية Qdrant إذا كان مطلوبًا
            qdrant_filter = None
            if filter_condition:
                qdrant_filter = models.Filter(**filter_condition)
            
            # البحث في Qdrant
            search_results = self.client.search(
                collection_name=collection_name,
                query_vector=query_vector,
                limit=limit,
                query_filter=qdrant_filter
            )
            
            # تحويل النتائج إلى تنسيق سهل الاستخدام
            results = []
            for result in search_results:
                # استخراج البيانات من النتيجة
                payload = result.payload
                score = result.score
                
                # إنشاء كائن النتيجة
                result_object = {
                    "id": result.id,
                    "text": payload.get("text", ""),
                    "metadata": payload.get("metadata", {}),
                    "score": score
                }
                
                results.append(result_object)
            
            return results
        
        except Exception as e:
            print(f"خطأ في البحث في Qdrant: {str(e)}")
            return []
    
    def delete_collection(self, collection_name: str) -> bool:
        """
        حذف مجموعة من Qdrant

        Args:
            collection_name: اسم المجموعة

        Returns:
            نجاح العملية
        """
        try:
            self.client.delete_collection(collection_name=collection_name)
            print(f"تم حذف المجموعة {collection_name} بنجاح")
            return True
        
        except Exception as e:
            print(f"خطأ في حذف مجموعة Qdrant: {str(e)}")
            return False
    
    def get_collections(self) -> List[str]:
        """
        الحصول على قائمة المجموعات الموجودة

        Returns:
            قائمة أسماء المجموعات
        """
        try:
            collections = self.client.get_collections().collections
            return [collection.name for collection in collections]
        
        except Exception as e:
            print(f"خطأ في الحصول على قائمة المجموعات: {str(e)}")
            return []
    
    def create_islamic_collections(self, embedding_model) -> Dict[str, bool]:
        """
        إنشاء مجموعات مخصصة للمحتوى الإسلامي

        Args:
            embedding_model: نموذج التضمين

        Returns:
            قاموس نتائج إنشاء المجموعات
        """
        vector_size = embedding_model.vector_size
        collections = {
            "quran": "مجموعة القرآن الكريم",
            "tafseer": "مجموعة تفاسير القرآن",
            "hadith": "مجموعة الحديث النبوي",
            "fiqh": "مجموعة الفقه الإسلامي",
            "aqeedah": "مجموعة العقيدة الإسلامية",
            "seera": "مجموعة السيرة النبوية",
            "scientific_miracles": "مجموعة الإعجاز العلمي"
        }
        
        results = {}
        for collection_name, description in collections.items():
            print(f"إنشاء {description}...")
            success = self.create_collection(collection_name, vector_size)
            results[collection_name] = success
        
        return results
