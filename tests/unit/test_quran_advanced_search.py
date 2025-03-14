#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
اختبارات وحدة للبحث المتقدم في القرآن الكريم
"""

import pytest
import os
import sys
import json
from unittest.mock import MagicMock, patch, mock_open

# إضافة المجلد الرئيسي للمشروع إلى مسار Python
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

# استيراد الوحدة المراد اختبارها
from core.data_loaders.quran_loader import QuranLoader


class TestQuranAdvancedSearch:
    """اختبارات للبحث المتقدم في القرآن الكريم"""

    @pytest.fixture
    def quran_loader(self, tmp_path):
        """إعداد محمل بيانات القرآن للاختبارات"""
        # استخدام مجلد مؤقت للاختبارات
        data_dir = tmp_path / "data"
        data_dir.mkdir()
        return QuranLoader(data_dir=str(data_dir))

    def test_search_by_topic(self, quran_loader):
        """اختبار البحث في القرآن حسب الموضوع"""
        # بيانات القرآن المزيفة
        mock_quran_data = [
            {
                "number": 2,
                "name": "البقرة",
                "ayahs": [
                    {
                        "number": 183,
                        "numberInSurah": 183,
                        "text": "يَا أَيُّهَا الَّذِينَ آمَنُوا كُتِبَ عَلَيْكُمُ الصِّيَامُ كَمَا كُتِبَ عَلَى الَّذِينَ مِن قَبْلِكُمْ لَعَلَّكُمْ تَتَّقُونَ",
                    },
                    {
                        "number": 184,
                        "numberInSurah": 184,
                        "text": "أَيَّامًا مَّعْدُودَاتٍ فَمَن كَانَ مِنكُم مَّرِيضًا أَوْ عَلَى سَفَرٍ فَعِدَّةٌ مِّنْ أَيَّامٍ أُخَرَ",
                    },
                ],
            },
            {
                "number": 4,
                "name": "النساء",
                "ayahs": [
                    {
                        "number": 103,
                        "numberInSurah": 103,
                        "text": "فَإِذَا قَضَيْتُمُ الصَّلَاةَ فَاذْكُرُوا اللَّهَ قِيَامًا وَقُعُودًا وَعَلَى جُنُوبِكُمْ",
                    }
                ],
            },
        ]

        # قاموس المواضيع المزيف
        mock_topics = {"الصيام": ["2:183", "2:184", "2:185"], "الصلاة": ["4:103", "2:238", "17:78"]}

        # تجهيز البيانات المزيفة
        with patch.object(quran_loader, "download_quran_text", return_value=mock_quran_data):
            with patch.object(quran_loader, "_load_topics_index", return_value=mock_topics):
                # البحث عن موضوع الصيام
                results = quran_loader.search_by_topic("الصيام")

                # التحقق من النتائج
                assert len(results) == 2  # آيتان من سورة البقرة
                assert results[0]["surah_name"] == "البقرة"
                assert "الصِّيَامُ" in results[0]["text"]

                # البحث عن موضوع الصلاة
                results = quran_loader.search_by_topic("الصلاة")
                assert len(results) == 1
                assert results[0]["surah_name"] == "النساء"
                assert "الصَّلَاةَ" in results[0]["text"]

                # البحث عن موضوع غير موجود
                results = quran_loader.search_by_topic("موضوع غير موجود")
                assert len(results) == 0

    def test_search_by_root_word(self, quran_loader):
        """اختبار البحث في القرآن حسب الجذر اللغوي"""
        # بيانات القرآن المزيفة
        mock_quran_data = [
            {
                "number": 1,
                "name": "الفاتحة",
                "ayahs": [
                    {"number": 1, "numberInSurah": 1, "text": "بِسْمِ اللَّهِ الرَّحْمَنِ الرَّحِيمِ"},
                    {"number": 3, "numberInSurah": 3, "text": "الرَّحْمَنِ الرَّحِيمِ"},
                ],
            }
        ]

        # قاموس الجذور المزيف
        mock_roots = {"رحم": ["1:1", "1:3", "2:163"], "علم": ["2:31", "2:32", "96:4"]}

        # تجهيز البيانات المزيفة
        with patch.object(quran_loader, "download_quran_text", return_value=mock_quran_data):
            with patch.object(quran_loader, "_load_roots_index", return_value=mock_roots):
                # البحث عن جذر رحم
                results = quran_loader.search_by_root("رحم")

                # التحقق من النتائج
                assert len(results) == 2
                assert results[0]["surah_name"] == "الفاتحة"
                assert "الرَّحْمَنِ" in results[0]["text"]

                # البحث عن جذر غير موجود في البيانات المزيفة
                results = quran_loader.search_by_root("جذر غير موجود")
                assert len(results) == 0

    def test_get_surah_info(self, quran_loader):
        """اختبار الحصول على معلومات سورة"""
        # بيانات القرآن المزيفة
        mock_quran_data = [
            {
                "number": 1,
                "name": "الفاتحة",
                "englishName": "The Opening",
                "englishNameTranslation": "The Opening",
                "revelationType": "Meccan",
                "numberOfAyahs": 7,
                "ayahs": [{"number": 1, "text": "بسم الله الرحمن الرحيم"}],
            },
            {
                "number": 2,
                "name": "البقرة",
                "englishName": "The Cow",
                "englishNameTranslation": "The Cow",
                "revelationType": "Medinan",
                "numberOfAyahs": 286,
                "ayahs": [{"number": 1, "text": "الم"}],
            },
        ]

        # تجهيز البيانات المزيفة
        with patch.object(quran_loader, "download_quran_text", return_value=mock_quran_data):
            # الحصول على معلومات سورة الفاتحة
            surah_info = quran_loader.get_surah_info(1)

            # التحقق من النتائج
            assert surah_info is not None
            assert surah_info["name"] == "الفاتحة"
            assert surah_info["number"] == 1
            assert surah_info["revelationType"] == "Meccan"
            assert surah_info["numberOfAyahs"] == 7

            # الحصول على معلومات سورة البقرة
            surah_info = quran_loader.get_surah_info(2)
            assert surah_info["name"] == "البقرة"
            assert surah_info["numberOfAyahs"] == 286

            # الحصول على معلومات سورة غير موجودة
            surah_info = quran_loader.get_surah_info(999)
            assert surah_info is None

    def test_get_ayah_with_tafseer(self, quran_loader):
        """اختبار الحصول على آية مع تفسيرها"""
        # بيانات القرآن المزيفة
        mock_quran_data = [
            {
                "number": 1,
                "name": "الفاتحة",
                "ayahs": [{"number": 1, "numberInSurah": 1, "text": "بِسْمِ اللَّهِ الرَّحْمَنِ الرَّحِيمِ"}],
            }
        ]

        # بيانات التفسير المزيفة
        mock_tafseer_data = [{"sura": 1, "ayah": 1, "text": "تفسير بسم الله الرحمن الرحيم"}]

        # تجهيز البيانات المزيفة
        with patch.object(quran_loader, "download_quran_text", return_value=mock_quran_data):
            with patch.object(quran_loader, "download_tafseer", return_value=mock_tafseer_data):
                # الحصول على آية مع تفسيرها
                result = quran_loader.get_ayah_with_tafseer(1, 1)

                # التحقق من النتائج
                assert result is not None
                assert result["surah_number"] == 1
                assert result["ayah_number"] == 1
                assert result["ayah_text"] == "بِسْمِ اللَّهِ الرَّحْمَنِ الرَّحِيمِ"
                assert result["tafseer"] == "تفسير بسم الله الرحمن الرحيم"

                # الحصول على آية غير موجودة
                result = quran_loader.get_ayah_with_tafseer(999, 1)
                assert result is None


if __name__ == "__main__":
    pytest.main(["-v", "test_quran_advanced_search.py"])
