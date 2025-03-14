#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
اختبارات وحدة لمحمل بيانات القرآن
"""

import pytest
import os
import sys
import json
from unittest.mock import MagicMock, patch, mock_open

# إضافة المجلد الرئيسي للمشروع إلى مسار Python
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# استيراد الوحدة المراد اختبارها
from core.data_loaders.quran_loader import QuranLoader


class TestQuranLoader:
    """اختبارات لمحمل بيانات القرآن"""

    @pytest.fixture
    def quran_loader(self, tmp_path):
        """إعداد محمل بيانات القرآن للاختبارات"""
        # استخدام مجلد مؤقت للاختبارات
        data_dir = tmp_path / "data"
        data_dir.mkdir()
        return QuranLoader(data_dir=str(data_dir))

    def test_initialization(self, quran_loader):
        """اختبار تهيئة محمل بيانات القرآن"""
        assert quran_loader is not None
        assert os.path.exists(quran_loader.quran_dir)
        assert os.path.basename(quran_loader.quran_file) == "quran.json"
        assert os.path.basename(quran_loader.tafseer_file) == "tafseer.json"
        assert os.path.basename(quran_loader.scientific_miracles_file) == "scientific_miracles.json"

    def test_download_quran_text_from_api(self, quran_loader):
        """اختبار تنزيل نص القرآن من API"""
        # إنشاء استجابة API مزيفة
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "data": {
                "surahs": [
                    {
                        "number": 1,
                        "name": "الفاتحة",
                        "ayahs": [
                            {"number": 1, "text": "بسم الله الرحمن الرحيم"},
                            {"number": 2, "text": "الحمد لله رب العالمين"}
                        ]
                    }
                ]
            }
        }

        # تجهيز الدالة المزيفة لإعادة الاستجابة
        with patch('requests.get', return_value=mock_response):
            with patch('builtins.open', mock_open()) as mocked_file:
                with patch('json.dump') as mocked_json_dump:
                    surahs = quran_loader.download_quran_text()
                    
                    # التحقق من النتائج
                    assert len(surahs) == 1
                    assert surahs[0]["number"] == 1
                    assert surahs[0]["name"] == "الفاتحة"
                    assert len(surahs[0]["ayahs"]) == 2
                    
                    # التحقق من حفظ الملف
                    mocked_file.assert_called_once_with(quran_loader.quran_file, 'w', encoding='utf-8')
                    mocked_json_dump.assert_called_once()

    def test_download_quran_text_from_file(self, quran_loader):
        """اختبار تحميل نص القرآن من ملف محلي"""
        # بيانات القرآن المزيفة للاختبار
        mock_quran_data = [
            {
                "number": 1,
                "name": "الفاتحة",
                "ayahs": [
                    {"number": 1, "text": "بسم الله الرحمن الرحيم"},
                    {"number": 2, "text": "الحمد لله رب العالمين"}
                ]
            }
        ]
        
        # تجهيز ملف موجود مسبقاً
        with patch('os.path.exists', return_value=True):
            with patch('builtins.open', mock_open(read_data=json.dumps(mock_quran_data))):
                surahs = quran_loader.download_quran_text()
                
                # التحقق من النتائج
                assert len(surahs) == 1
                assert surahs[0]["number"] == 1
                assert surahs[0]["name"] == "الفاتحة"
                assert len(surahs[0]["ayahs"]) == 2

    def test_download_tafseer(self, quran_loader):
        """اختبار تنزيل تفسير القرآن"""
        # إنشاء استجابة API مزيفة للقرآن أولاً
        mock_quran_data = [
            {
                "number": 1,
                "name": "الفاتحة",
                "ayahs": [
                    {"number": 1, "text": "بسم الله الرحمن الرحيم"},
                    {"number": 2, "text": "الحمد لله رب العالمين"}
                ]
            }
        ]
        
        # إنشاء استجابة API مزيفة للتفسير
        mock_tafseer_response = MagicMock()
        mock_tafseer_response.status_code = 200
        mock_tafseer_response.json.return_value = {
            "data": {
                "text": "تفسير الآية",
                "surah": {"number": 1},
                "numberInSurah": 1
            }
        }
        
        # تجهيز الدوال المزيفة
        with patch('os.path.exists', side_effect=[False, False, True]):  # الملفات غير موجودة في البداية
            with patch.object(quran_loader, 'download_quran_text', return_value=mock_quran_data):
                with patch('requests.get', return_value=mock_tafseer_response):
                    with patch('builtins.open', mock_open()) as mocked_file:
                        with patch('json.dump') as mocked_json_dump:
                            # اختبار تنزيل التفسير لسورة واحدة فقط
                            tafseer = quran_loader.download_tafseer(surah_range=(1, 1), ayah_range=(1, 1))
                            
                            # التحقق من النتائج
                            assert len(tafseer) > 0
                            assert tafseer[0]["sura"] == 1
                            assert tafseer[0]["ayah"] == 1
                            assert tafseer[0]["text"] == "تفسير الآية"
                            
                            # التحقق من حفظ الملف
                            mocked_file.assert_called_with(quran_loader.tafseer_file, 'w', encoding='utf-8')
                            mocked_json_dump.assert_called()

    def test_load_scientific_miracles(self, quran_loader):
        """اختبار تحميل المعجزات العلمية"""
        # بيانات المعجزات المزيفة
        mock_miracles = [
            {
                "title": "الإشارة إلى توسع الكون",
                "surah": 51,
                "ayah": 47,
                "text": "وَالسَّمَاءَ بَنَيْنَاهَا بِأَيْدٍ وَإِنَّا لَمُوسِعُونَ",
                "explanation": "تشير الآية إلى توسع الكون المستمر، وهو ما أثبته العلم الحديث"
            }
        ]
        
        # تجهيز ملف موجود مسبقاً
        with patch('os.path.exists', return_value=True):
            with patch('builtins.open', mock_open(read_data=json.dumps(mock_miracles))):
                miracles = quran_loader.load_scientific_miracles()
                
                # التحقق من النتائج
                assert len(miracles) == 1
                assert miracles[0]["title"] == "الإشارة إلى توسع الكون"
                assert miracles[0]["surah"] == 51
                assert miracles[0]["ayah"] == 47

    def test_add_scientific_miracle(self, quran_loader):
        """اختبار إضافة معجزة علمية"""
        # معجزة علمية جديدة
        new_miracle = {
            "title": "دورة المياه في الطبيعة",
            "surah": 24,
            "ayah": 43,
            "text": "أَلَمْ تَرَ أَنَّ اللَّهَ يُزْجِي سَحَابًا ثُمَّ يُؤَلِّفُ بَيْنَهُ...",
            "explanation": "تصف الآية دورة المياه في الطبيعة بدقة علمية"
        }
        
        # قائمة المعجزات الحالية
        existing_miracles = []
        
        # تجهيز الدوال المزيفة
        with patch.object(quran_loader, 'load_scientific_miracles', return_value=existing_miracles):
            with patch('builtins.open', mock_open()) as mocked_file:
                with patch('json.dump') as mocked_json_dump:
                    result = quran_loader.add_scientific_miracle(new_miracle)
                    
                    # التحقق من النتائج
                    assert result is True
                    
                    # التحقق من حفظ الملف
                    mocked_file.assert_called_with(quran_loader.scientific_miracles_file, 'w', encoding='utf-8')
                    
                    # التحقق من المحتوى المحفوظ
                    # الحصول على القائمة المحدثة المرسلة إلى json.dump
                    args, _ = mocked_json_dump.call_args
                    updated_miracles = args[0]
                    assert len(updated_miracles) == 1
                    assert updated_miracles[0]["title"] == "دورة المياه في الطبيعة"

    def test_search_quran(self, quran_loader):
        """اختبار البحث في القرآن"""
        # بيانات القرآن المزيفة
        mock_quran_data = [
            {
                "number": 1,
                "name": "الفاتحة",
                "ayahs": [
                    {"number": 1, "text": "بسم الله الرحمن الرحيم"},
                    {"number": 2, "text": "الحمد لله رب العالمين"}
                ]
            },
            {
                "number": 2,
                "name": "البقرة",
                "ayahs": [
                    {"number": 1, "text": "الم"},
                    {"number": 2, "text": "ذلك الكتاب لا ريب فيه هدى للمتقين"}
                ]
            }
        ]
        
        # تجهيز البيانات المزيفة
        with patch.object(quran_loader, 'download_quran_text', return_value=mock_quran_data):
            # البحث عن كلمة موجودة
            results = quran_loader.search_quran("الحمد")
            
            # التحقق من النتائج
            assert len(results) == 1
            assert results[0]["surah"] == 1
            assert results[0]["ayah"] == 2
            assert "الحمد" in results[0]["text"]
            
            # البحث عن كلمة أخرى
            results = quran_loader.search_quran("هدى")
            
            # التحقق من النتائج
            assert len(results) == 1
            assert results[0]["surah"] == 2
            assert results[0]["ayah"] == 2
            assert "هدى" in results[0]["text"]
            
            # البحث عن كلمة غير موجودة
            results = quran_loader.search_quran("كلمة غير موجودة")
            assert len(results) == 0

    def test_search_tafseer(self, quran_loader):
        """اختبار البحث في التفسير"""
        # بيانات التفسير المزيفة
        mock_tafseer_data = [
            {
                "sura": 1,
                "ayah": 1,
                "text": "تفسير بسم الله الرحمن الرحيم"
            },
            {
                "sura": 1,
                "ayah": 2,
                "text": "تفسير الحمد لله رب العالمين: الثناء على الله"
            }
        ]
        
        # تجهيز البيانات المزيفة
        with patch.object(quran_loader, 'download_tafseer', return_value=mock_tafseer_data):
            # البحث عن كلمة موجودة
            results = quran_loader.search_tafseer("الثناء")
            
            # التحقق من النتائج
            assert len(results) == 1
            assert results[0]["sura"] == 1
            assert results[0]["ayah"] == 2
            assert "الثناء" in results[0]["text"]
            
            # البحث عن كلمة غير موجودة
            results = quran_loader.search_tafseer("كلمة غير موجودة")
            assert len(results) == 0


if __name__ == "__main__":
    pytest.main(["-v", "test_quran_loader.py"])
