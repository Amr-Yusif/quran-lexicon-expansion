#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
محمل بيانات الحديث النبوي - يوفر وظائف لتحميل وإدارة بيانات الأحاديث النبوية من مختلف المصادر
"""

import os
import json
import requests
from typing import List, Dict, Any, Optional, Union


class HadithLoader:
    """
    محمل بيانات الحديث النبوي - يقوم بإدارة تنزيل وتخزين وتحميل وتجهيز بيانات الأحاديث
    """
    
    def __init__(self, data_dir: str = None):
        """
        تهيئة محمل بيانات الحديث

        Args:
            data_dir: مسار مجلد البيانات (اختياري)
        """
        if data_dir is None:
            # استخدام المجلد الافتراضي إذا لم يتم تحديد مجلد
            self.data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data")
        else:
            self.data_dir = data_dir
        
        # التأكد من وجود مجلد البيانات
        self.hadith_dir = os.path.join(self.data_dir, "hadith")
        os.makedirs(self.hadith_dir, exist_ok=True)
        
        # تحديد مسارات ملفات مجموعات الأحاديث
        self.bukhari_file = os.path.join(self.hadith_dir, "bukhari.json")
        self.muslim_file = os.path.join(self.hadith_dir, "muslim.json")
        self.abudawood_file = os.path.join(self.hadith_dir, "abudawood.json")
        self.tirmidhi_file = os.path.join(self.hadith_dir, "tirmidhi.json")
        self.nasai_file = os.path.join(self.hadith_dir, "nasai.json")
        self.ibnmajah_file = os.path.join(self.hadith_dir, "ibnmajah.json")
        self.malik_file = os.path.join(self.hadith_dir, "malik.json")
        
        # قاموس يربط بين اسم المجموعة ومسار الملف
        self.collection_files = {
            "bukhari": self.bukhari_file,
            "muslim": self.muslim_file,
            "abudawood": self.abudawood_file,
            "tirmidhi": self.tirmidhi_file,
            "nasai": self.nasai_file,
            "ibnmajah": self.ibnmajah_file,
            "malik": self.malik_file
        }
    
    def download_hadith_collection(self, collection_name: str) -> List[Dict[str, Any]]:
        """
        تنزيل مجموعة أحاديث من API

        Args:
            collection_name: اسم مجموعة الأحاديث (bukhari, muslim, etc.)

        Returns:
            قائمة من الأحاديث
        """
        try:
            # التحقق من صحة اسم المجموعة
            if collection_name not in self.collection_files:
                print(f"اسم مجموعة غير صالح: {collection_name}")
                return []
            
            file_path = self.collection_files[collection_name]
            
            # التحقق مما إذا كان الملف موجودًا بالفعل
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            
            # تنزيل البيانات من API
            url = f"https://api.sunnah.com/v1/collections/{collection_name}/hadiths"
            headers = {
                "X-API-KEY": "SqD712P3E82xnwOAEOkGd5JZH8s9wRR24TqNFzjk",  # مفتاح API افتراضي، يجب استبداله بمفتاح حقيقي
                "Content-Type": "application/json"
            }
            
            response = requests.get(url, headers=headers)
            response.raise_for_status()  # رفع استثناء إذا فشل الطلب
            
            data = response.json()
            hadiths = data.get("data", {}).get("hadiths", [])
            
            # حفظ البيانات في ملف
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(hadiths, f, ensure_ascii=False, indent=4)
            
            return hadiths
        
        except Exception as e:
            print(f"خطأ في تنزيل مجموعة الأحاديث {collection_name}: {str(e)}")
            # إذا حدث خطأ ولكن الملف موجود، قم بتحميله
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return []
    
    def load_all_collections(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        تحميل جميع مجموعات الأحاديث المتاحة

        Returns:
            قاموس يحتوي على جميع مجموعات الأحاديث
        """
        collections = {}
        
        for collection_name in self.collection_files.keys():
            collections[collection_name] = self.download_hadith_collection(collection_name)
        
        return collections
    
    def search_hadith(self, query: str, collections: List[str] = None) -> List[Dict[str, Any]]:
        """
        البحث في الأحاديث عن نص معين

        Args:
            query: نص البحث
            collections: قائمة مجموعات الأحاديث للبحث فيها (اختياري)

        Returns:
            قائمة الأحاديث المطابقة
        """
        results = []
        
        try:
            # تحميل جميع المجموعات
            all_collections = self.load_all_collections()
            
            # تحديد المجموعات للبحث
            if collections is None:
                collections_to_search = all_collections.keys()
            else:
                collections_to_search = [c for c in collections if c in all_collections]
            
            # البحث في كل مجموعة
            for collection_name in collections_to_search:
                hadiths = all_collections[collection_name]
                
                for hadith in hadiths:
                    # البحث في النص العربي والمترجم والمرجع
                    arab_text = hadith.get("arab", "")
                    translated_text = hadith.get("text", "")
                    reference = hadith.get("reference", "")
                    
                    if (query in arab_text or query in translated_text or query in reference):
                        # إضافة اسم المجموعة إلى نتيجة البحث
                        result = hadith.copy()
                        result["collection"] = collection_name
                        results.append(result)
            
            return results
        
        except Exception as e:
            print(f"خطأ في البحث في الأحاديث: {str(e)}")
            return []
    
    def get_hadith_by_number(self, collection_name: str, hadith_number: int) -> Optional[Dict[str, Any]]:
        """
        الحصول على حديث بالرقم من مجموعة محددة

        Args:
            collection_name: اسم مجموعة الأحاديث
            hadith_number: رقم الحديث

        Returns:
            بيانات الحديث أو None إذا لم يتم العثور عليه
        """
        try:
            # تحميل مجموعة الأحاديث
            hadiths = self.download_hadith_collection(collection_name)
            
            # البحث عن الحديث بالرقم
            for hadith in hadiths:
                if hadith.get("number") == hadith_number:
                    return hadith
            
            return None
        
        except Exception as e:
            print(f"خطأ في الحصول على الحديث: {str(e)}")
            return None
    
    def prepare_hadith_embeddings(self) -> List[Dict[str, Any]]:
        """
        إعداد بيانات الأحاديث للتضمين
        
        Returns:
            قائمة من بيانات الأحاديث المعدة للتضمين
        """
        embedding_data = []
        
        try:
            # تحميل جميع مجموعات الأحاديث
            collections = self.load_all_collections()
            
            # إعداد كل حديث للتضمين
            for collection_name, hadiths in collections.items():
                for hadith in hadiths:
                    hadith_number = hadith.get("number", 0)
                    arab_text = hadith.get("arab", "")
                    translated_text = hadith.get("text", "")
                    reference = hadith.get("reference", "")
                    
                    # إنشاء سجل للتضمين
                    embedding_record = {
                        "id": f"hadith_{collection_name}_{hadith_number}",
                        "text": arab_text,  # استخدام النص العربي للتضمين
                        "metadata": {
                            "source": "hadith",
                            "collection": collection_name,
                            "number": hadith_number,
                            "translated_text": translated_text,
                            "reference": reference
                        }
                    }
                    
                    embedding_data.append(embedding_record)
            
            return embedding_data
        
        except Exception as e:
            print(f"خطأ في إعداد تضمينات الأحاديث: {str(e)}")
            return []