#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
اختبارات وحدة لوكيل استخراج المسارات الموضوعية من القرآن الكريم
"""

import pytest
import os
import sys
from unittest.mock import MagicMock, patch
import json
from pathlib import Path
from typing import Dict, List, Any, Optional

# إضافة المجلد الرئيسي للمشروع إلى مسار Python
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# استيراد الوحدة المراد اختبارها
from core.ai.thematic_path_agent import ThematicPathAgent


class TestThematicPathAgent:
    """اختبارات لوكيل استخراج المسارات الموضوعية من القرآن الكريم"""

    @pytest.fixture
    def mock_quran_data(self):
        """إعداد بيانات قرآنية وهمية للاختبارات"""
        return {
            "surahs": [
                {
                    "number": 1,
                    "name": "الفاتحة",
                    "revelationType": "مكية",
                    "verses": [
                        {"number": 1, "text": "بسم الله الرحمن الرحيم"},
                        {"number": 2, "text": "الحمد لله رب العالمين"},
                        {"number": 3, "text": "الرحمن الرحيم"},
                        {"number": 4, "text": "مالك يوم الدين"},
                        {"number": 5, "text": "إياك نعبد وإياك نستعين"},
                        {"number": 6, "text": "اهدنا الصراط المستقيم"},
                        {"number": 7, "text": "صراط الذين أنعمت عليهم غير المغضوب عليهم ولا الضالين"}
                    ]
                },
                {
                    "number": 2,
                    "name": "البقرة",
                    "revelationType": "مدنية",
                    "verses": [
                        {"number": 1, "text": "الم"},
                        {"number": 2, "text": "ذلك الكتاب لا ريب فيه هدى للمتقين"},
                        {"number": 3, "text": "الذين يؤمنون بالغيب ويقيمون الصلاة ومما رزقناهم ينفقون"},
                        {"number": 4, "text": "والذين يؤمنون بما أنزل إليك وما أنزل من قبلك وبالآخرة هم يوقنون"},
                        {"number": 5, "text": "أولئك على هدى من ربهم وأولئك هم المفلحون"}
                    ]
                },
                {
                    "number": 96,
                    "name": "العلق",
                    "revelationType": "مكية",
                    "verses": [
                        {"number": 1, "text": "اقرأ باسم ربك الذي خلق"},
                        {"number": 2, "text": "خلق الإنسان من علق"},
                        {"number": 3, "text": "اقرأ وربك الأكرم"},
                        {"number": 4, "text": "الذي علم بالقلم"},
                        {"number": 5, "text": "علم الإنسان ما لم يعلم"}
                    ]
                }
            ]
        }

    @pytest.fixture
    def thematic_path_agent(self, mock_quran_data):
        """إعداد وكيل استخراج المسارات الموضوعية للاختبارات"""
        # إنشاء وكيل وهمي مع تجاوز تحميل البيانات من الملف
        with patch('core.ai.thematic_path_agent.ThematicPathAgent._load_quran_data') as mock_load:
            mock_load.return_value = mock_quran_data
            agent = ThematicPathAgent(name="test_thematic_path_agent")
            return agent

    def test_initialization(self, thematic_path_agent, mock_quran_data):
        """اختبار تهيئة وكيل استخراج المسارات الموضوعية"""
        assert thematic_path_agent is not None
        assert thematic_path_agent.name == "test_thematic_path_agent"
        assert thematic_path_agent.quran_data == mock_quran_data
        assert hasattr(thematic_path_agent, 'thematic_paths')
        assert hasattr(thematic_path_agent, 'discovered_patterns')

    def test_determine_analysis_type(self, thematic_path_agent):
        """اختبار تحديد نوع التحليل المطلوب"""
        # اختبار المسارات الموضوعية
        assert thematic_path_agent._determine_analysis_type("ما هي المسارات الموضوعية في القرآن؟") == "thematic_paths"
        assert thematic_path_agent._determine_analysis_type("أريد معرفة المسار التربوي في القرآن") == "thematic_paths"
        
        # اختبار مقارنة السور
        assert thematic_path_agent._determine_analysis_type("قارن بين سورة البقرة وسورة آل عمران") == "surah_comparison"
        
        # اختبار الأنماط العددية
        assert thematic_path_agent._determine_analysis_type("ما هي الأنماط العددية في القرآن؟") == "numerical_patterns"
        
        # اختبار الأنماط الحرفية
        assert thematic_path_agent._determine_analysis_type("ما هي الأنماط الحرفية في القرآن؟") == "letter_patterns"
        
        # اختبار التحليل الشامل (الافتراضي)
        assert thematic_path_agent._determine_analysis_type("حلل القرآن الكريم") == "comprehensive"

    def test_verse_matches_theme(self, thematic_path_agent):
        """اختبار تطابق الآية مع موضوع معين"""
        # آية تحتوي على كلمة مفتاحية للمسار التعليمي
        assert thematic_path_agent._verse_matches_theme("اقرأ باسم ربك الذي خلق", ["اقرأ", "علم", "كتاب"]) == True
        
        # آية لا تحتوي على كلمات مفتاحية للمسار الاقتصادي
        assert thematic_path_agent._verse_matches_theme("بسم الله الرحمن الرحيم", ["مال", "تجارة", "بيع"]) == False

    def test_classify_verses_by_theme(self, thematic_path_agent):
        """اختبار تصنيف الآيات حسب المسارات الموضوعية"""
        # تنفيذ التصنيف
        thematic_path_agent._classify_verses_by_theme()
        
        # التحقق من تصنيف آيات المسار التعليمي
        educational_verses = thematic_path_agent.thematic_paths["educational"]["verses"]
        assert len(educational_verses) > 0
        
        # التحقق من وجود آيات سورة العلق في المسار التعليمي
        educational_surah_names = [verse["surah_name"] for verse in educational_verses]
        assert "العلق" in educational_surah_names

    def test_extract_thematic_paths(self, thematic_path_agent):
        """اختبار استخراج المسارات الموضوعية"""
        # تنفيذ استخراج المسارات الموضوعية
        results = thematic_path_agent.extract_thematic_paths()
        
        # التحقق من النتائج
        assert "thematic_paths" in results
        assert "path_relationships" in results
        assert "summary" in results
        assert isinstance(results["summary"], str)

    def test_process_query(self, thematic_path_agent):
        """اختبار معالجة استعلام"""
        # تجهيز الطرق الوهمية
        thematic_path_agent.extract_thematic_paths = MagicMock(return_value={"result": "thematic_paths_result"})
        thematic_path_agent.compare_surahs = MagicMock(return_value={"result": "surah_comparison_result"})
        thematic_path_agent.discover_numerical_patterns = MagicMock(return_value={"result": "numerical_patterns_result"})
        thematic_path_agent.discover_letter_patterns = MagicMock(return_value={"result": "letter_patterns_result"})
        thematic_path_agent.comprehensive_analysis = MagicMock(return_value={"result": "comprehensive_analysis_result"})
        
        # اختبار المسارات الموضوعية
        result = thematic_path_agent.process("ما هي المسارات الموضوعية في القرآن؟")
        assert result == {"result": "thematic_paths_result"}
        thematic_path_agent.extract_thematic_paths.assert_called_once()
        
        # إعادة تعيين المحاكاة
        thematic_path_agent.extract_thematic_paths.reset_mock()
        
        # اختبار مقارنة السور
        result = thematic_path_agent.process("قارن بين سورة البقرة وسورة آل عمران")
        assert result == {"result": "surah_comparison_result"}
        thematic_path_agent.compare_surahs.assert_called_once()
        
        # اختبار التحليل الشامل
        result = thematic_path_agent.process("حلل القرآن الكريم")
        assert result == {"result": "comprehensive_analysis_result"}
        thematic_path_agent.comprehensive_analysis.assert_called_once()


if __name__ == "__main__":
    pytest.main()