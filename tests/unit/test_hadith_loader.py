#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
اختبارات وحدة لمحمل بيانات الحديث النبوي
"""

import pytest
import os
import sys
import json
from unittest.mock import MagicMock, patch, mock_open

# إضافة المجلد الرئيسي للمشروع إلى مسار Python
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# استيراد الوحدة المراد اختبارها (سيتم إنشاؤها لاحقًا)
from core.data_loaders.hadith_loader import HadithLoader


class TestHadithLoader:
    """اختبارات لمحمل بيانات الحديث النبوي"""

    @pytest.fixture
    def hadith_loader(self, tmp_path):
        """إعداد محمل بيانات الحديث للاختبارات"""
        # استخدام مجلد مؤقت للاختبارات
        data_dir = tmp_path / "data"
        data_dir.mkdir()
        return HadithLoader(data_dir=str(data_dir))

    def test_initialization(self, hadith_loader):
        """اختبار تهيئة محمل بيانات الحديث"""
        assert hadith_loader is not None
        assert os.path.exists(hadith_loader.hadith_dir)
        assert os.path.basename(hadith_loader.bukhari_file) == "bukhari.json"
        assert os.path.basename(hadith_loader.muslim_file) == "muslim.json"
        assert os.path.basename(hadith_loader.abudawood_file) == "abudawood.json"
        assert os.path.basename(hadith_loader.tirmidhi_file) == "tirmidhi.json"
        assert os.path.basename(hadith_loader.nasai_file) == "nasai.json"
        assert os.path.basename(hadith_loader.ibnmajah_file) == "ibnmajah.json"
        assert os.path.basename(hadith_loader.malik_file) == "malik.json"

    def test_download_hadith_collection(self, hadith_loader):
        """اختبار تنزيل مجموعة أحاديث من API"""
        # إنشاء استجابة API مزيفة
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "data": {
                "hadiths": [
                    {
                        "number": 1,
                        "arab": "نص الحديث باللغة العربية",
                        "text": "نص الحديث المترجم",
                        "reference": "البخاري، كتاب الإيمان، باب الإيمان"
                    },
                    {
                        "number": 2,
                        "arab": "نص الحديث الثاني باللغة العربية",
                        "text": "نص الحديث الثاني المترجم",
                        "reference": "البخاري، كتاب الإيمان، باب الإيمان"
                    }
                ]
            }
        }

        # تجهيز الدالة المزيفة لإعادة الاستجابة
        with patch('requests.get', return_value=mock_response):
            with patch('builtins.open', mock_open()) as mocked_file:
                with patch('json.dump') as mocked_json_dump:
                    hadiths = hadith_loader.download_hadith_collection("bukhari")
                    
                    # التحقق من النتائج
                    assert len(hadiths) == 2
                    assert hadiths[0]["number"] == 1
                    assert hadiths[1]["number"] == 2
                    
                    # التحقق من حفظ الملف
                    mocked_file.assert_called_once_with(hadith_loader.bukhari_file, 'w', encoding='utf-8')
                    mocked_json_dump.assert_called_once()

    def test_download_hadith_collection_from_file(self, hadith_loader):
        """اختبار تحميل مجموعة أحاديث من ملف محلي"""
        # بيانات الحديث المزيفة للاختبار
        mock_hadith_data = [
            {
                "number": 1,
                "arab": "نص الحديث باللغة العربية",
                "text": "نص الحديث المترجم",
                "reference": "البخاري، كتاب الإيمان، باب الإيمان"
            }
        ]
        
        # تجهيز ملف موجود مسبقاً
        with patch('os.path.exists', return_value=True):
            with patch('builtins.open', mock_open(read_data=json.dumps(mock_hadith_data))):
                hadiths = hadith_loader.download_hadith_collection("bukhari")
                
                # التحقق من النتائج
                assert len(hadiths) == 1
                assert hadiths[0]["number"] == 1
                assert hadiths[0]["arab"] == "نص الحديث باللغة العربية"

    def test_search_hadith(self, hadith_loader):
        """اختبار البحث في الأحاديث"""
        # بيانات الحديث المزيفة
        mock_bukhari_data = [
            {
                "number": 1,
                "arab": "إنما الأعمال بالنيات",
                "text": "الأعمال تقيم بالنوايا",
                "reference": "البخاري، كتاب الإيمان، باب النية"
            },
            {
                "number": 2,
                "arab": "من حسن إسلام المرء تركه ما لا يعنيه",
                "text": "من علامات حسن إسلام المرء تركه ما لا يعنيه",
                "reference": "البخاري، كتاب الإيمان، باب الإيمان"
            }
        ]
        
        mock_muslim_data = [
            {
                "number": 1,
                "arab": "الطهور شطر الإيمان",
                "text": "الطهارة نصف الإيمان",
                "reference": "مسلم، كتاب الطهارة، باب فضل الوضوء"
            }
        ]
        
        # تجهيز البيانات المزيفة
        with patch.object(hadith_loader, 'load_all_collections', return_value={
            "bukhari": mock_bukhari_data,
            "muslim": mock_muslim_data
        }):
            # البحث عن كلمة موجودة
            results = hadith_loader.search_hadith("الإيمان")
            
            # التحقق من النتائج
            assert len(results) == 3
            
            # البحث في مجموعة محددة
            results = hadith_loader.search_hadith("الطهارة", collections=["muslim"])
            assert len(results) == 1
            assert results[0]["collection"] == "muslim"
            
            # البحث عن كلمة غير موجودة
            results = hadith_loader.search_hadith("كلمة غير موجودة")
            assert len(results) == 0

    def test_get_hadith_by_number(self, hadith_loader):
        """اختبار الحصول على حديث بالرقم"""
        # بيانات الحديث المزيفة
        mock_bukhari_data = [
            {
                "number": 1,
                "arab": "إنما الأعمال بالنيات",
                "text": "الأعمال تقيم بالنوايا",
                "reference": "البخاري، كتاب الإيمان، باب النية"
            },
            {
                "number": 2,
                "arab": "من حسن إسلام المرء تركه ما لا يعنيه",
                "text": "من علامات حسن إسلام المرء تركه ما لا يعنيه",
                "reference": "البخاري، كتاب الإيمان، باب الإيمان"
            }
        ]
        
        # تجهيز البيانات المزيفة
        with patch.object(hadith_loader, 'download_hadith_collection', return_value=mock_bukhari_data):
            # الحصول على حديث موجود
            hadith = hadith_loader.get_hadith_by_number("bukhari", 1)
            
            # التحقق من النتائج
            assert hadith is not None
            assert hadith["number"] == 1
            assert hadith["arab"] == "إنما الأعمال بالنيات"
            
            # الحصول على حديث غير موجود
            hadith = hadith_loader.get_hadith_by_number("bukhari", 999)
            assert hadith is None

    def test_prepare_hadith_embeddings(self, hadith_loader):
        """اختبار إعداد بيانات الحديث للتضمين"""
        # بيانات الحديث المزيفة
        mock_collections = {
            "bukhari": [
                {
                    "number": 1,
                    "arab": "إنما الأعمال بالنيات",
                    "text": "الأعمال تقيم بالنوايا",
                    "reference": "البخاري، كتاب الإيمان، باب النية"
                }
            ],
            "muslim": [
                {
                    "number": 1,
                    "arab": "الطهور شطر الإيمان",
                    "text": "الطهارة نصف الإيمان",
                    "reference": "مسلم، كتاب الطهارة، باب فضل الوضوء"
                }
            ]
        }
        
        # تجهيز البيانات المزيفة
        with patch.object(hadith_loader, 'load_all_collections', return_value=mock_collections):
            # إعداد التضمينات
            embeddings = hadith_loader.prepare_hadith_embeddings()
            
            # التحقق من النتائج
            assert len(embeddings) == 2
            assert embeddings[0]["id"].startswith("hadith_")
            assert "text" in embeddings[0]
            assert "metadata" in embeddings[0]
            assert embeddings[0]["metadata"]["source"] == "hadith"


if __name__ == "__main__":
    pytest.main(["-v", "test_hadith_loader.py"])