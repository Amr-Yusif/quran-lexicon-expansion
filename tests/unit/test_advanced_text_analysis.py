#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
اختبارات وحدة لنظام التحليل النصي المتقدم
"""

import pytest
import sys
import os
from pathlib import Path
import json
from typing import Dict, Any

# إضافة المسار الرئيسي للمشروع إلى مسارات البحث
sys.path.append(str(Path(__file__).parent.parent.parent))

from core.analysis.advanced_text_analysis import AdvancedTextAnalysis


@pytest.fixture
def text_analyzer():
    """
    إنشاء محلل نصي للاختبارات
    """
    return AdvancedTextAnalysis()


@pytest.fixture
def test_texts():
    """
    توفير نصوص اختبار نموذجية
    """
    return {
        "simple": "هذا نص بسيط للاختبار.",
        "complex": """إن في خلق السماوات والأرض واختلاف الليل والنهار لآيات لأولي الألباب. 
        الذين يذكرون الله قياماً وقعوداً وعلى جنوبهم ويتفكرون في خلق السماوات والأرض.""",
        "discourse": """الحمد لله رب العالمين. الرحمن الرحيم. مالك يوم الدين. 
        إياك نعبد وإياك نستعين. اهدنا الصراط المستقيم. صراط الذين أنعمت عليهم غير المغضوب عليهم ولا الضالين."""
    }
    
def test_analyze_linguistic_relations(text_analyzer, test_texts):
    """
    اختبار تحليل العلاقات اللغوية
    """
    result = text_analyzer.analyze_linguistic_relations(test_texts["simple"])
    
    # التحقق من وجود التحليل الأساسي
    assert "sentence_analysis" in result
    assert "coherence_analysis" in result
    
    # التحقق من تحليل الجملة
    sentence_analysis = result["sentence_analysis"][0]
    assert "sentence" in sentence_analysis
    assert "pos_tags" in sentence_analysis
    assert "syntax_relations" in sentence_analysis
    assert "references" in sentence_analysis
    
    # التحقق من وجود تحليل للضمائر
    assert isinstance(sentence_analysis["references"], list)
    
    # اختبار النص المعقد
    complex_result = text_analyzer.analyze_linguistic_relations(test_texts["complex"])
    assert len(complex_result["sentence_analysis"]) > 1
    
@pytest.mark.parametrize(
    "text_type,expected_fields,expected_types",
    [
        # اختبار نص الخطاب
        (
            "discourse",
            ["discourse_type", "paragraph_analysis", "rhetorical_analysis", "discourse_structure"],
            {"paragraph_analysis": list, "rhetorical_analysis": dict}
        ),
        # اختبار النص المعقد
        (
            "complex",
            ["discourse_type", "paragraph_analysis", "rhetorical_analysis"],
            {"paragraph_analysis": list, "rhetorical_analysis": dict}
        )
    ]
)
def test_analyze_discourse(text_analyzer, test_texts, text_type, expected_fields, expected_types):
    """
    اختبار تحليل الخطاب باستخدام parametrization
    """
    result = text_analyzer.analyze_discourse(test_texts[text_type])
    
    # التحقق من وجود الحقول المتوقعة
    for field in expected_fields:
        assert field in result
    
    # التحقق من أنواع البيانات المتوقعة
    for field, expected_type in expected_types.items():
        assert isinstance(result[field], expected_type)
    
    # التحقق من تحليل الفقرات
    assert len(result["paragraph_analysis"]) > 0
    
    # التحقق من تحليل البلاغة
    assert "devices" in result["rhetorical_analysis"]
    
    def test_analyze_deep_semantics(self):
        """
        اختبار التحليل الدلالي العميق
        """
        result = self.analyzer.analyze_deep_semantics(self.complex_text)
        
        # التحقق من وجود التحليل الأساسي
        self.assertIn("semantic_fields", result)
        self.assertIn("concept_relations", result)
        self.assertIn("semantic_network", result)
        
        # التحقق من تحليل الحقول الدلالية
        self.assertIsInstance(result["semantic_fields"], dict)
        self.assertGreater(len(result["semantic_fields"]), 0)
        
        # التحقق من تحليل العلاقات المفاهيمية
        self.assertIsInstance(result["concept_relations"], list)
    
    def test_integrated_analysis(self):
        """
        اختبار التحليل المتكامل
        """
        result = self.analyzer.analyze_text(self.complex_text)
        
        # التحقق من وجود جميع أنواع التحليل
        self.assertIn("linguistic_analysis", result)
        self.assertIn("discourse_analysis", result)
        self.assertIn("semantic_analysis", result)
        self.assertIn("integrated_insights", result)
        
        # التحقق من وجود رؤى متكاملة
        self.assertIsInstance(result["integrated_insights"], dict)
        self.assertIn("key_concepts", result["integrated_insights"])
        self.assertIn("thematic_structure", result["integrated_insights"])
        self.assertIn("contextual_relations", result["integrated_insights"])


if __name__ == "__main__":
    unittest.main()