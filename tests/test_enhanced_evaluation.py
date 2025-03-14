#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
اختبارات نظام التقييم المحسن للخوارزميات
======================================

هذا الملف يحتوي على اختبارات الوحدة للتحقق من صحة نظام التقييم المحسن
للخوارزميات، بما في ذلك تقييم أداء استخراج الجذور وتحليل الأخطاء وإنشاء التقارير.
"""

import os
import sys
import json
import tempfile
import unittest
import shutil
from pathlib import Path
from typing import Dict, List, Any, Set, Tuple

# إضافة المسار إلى PYTHONPATH للوصول إلى الوحدات
current_path = Path(os.path.dirname(os.path.abspath(__file__)))
root_path = current_path.parent
sys.path.append(str(root_path))

from core.nlp.evaluate_nlp import (
    evaluate_root_extraction,
    evaluate_with_custom_dataset,
    analyze_error_patterns,
    generate_evaluation_report,
    get_evaluation_metrics,
)
from core.nlp.root_extraction import ArabicRootExtractor
from core.nlp.diacritics import DiacriticsProcessor
from core.lexicon.quranic_lexicon import QuranicLexicon
from core.lexicon.hybrid_processor import HybridProcessor


class TestEnhancedEvaluation(unittest.TestCase):
    """اختبارات نظام التقييم المحسن للخوارزميات"""

    def setUp(self):
        """الإعداد قبل كل اختبار"""
        # إنشاء مجلد مؤقت للاختبارات
        self.temp_dir = tempfile.mkdtemp()

        # إنشاء معجم مؤقت للاختبار
        self.lexicon_file = os.path.join(self.temp_dir, "test_lexicon.json")
        lexicon_data = {
            "كتاب": {
                "root": "كتب",
                "type": "اسم",
                "pattern": "فِعال",
                "meaning": "مؤلف من الصفحات المكتوبة",
            },
            "مكتوب": {"root": "كتب", "type": "اسم", "pattern": "مَفْعول", "meaning": "ما كُتب"},
            "يكتب": {"root": "كتب", "type": "فعل", "pattern": "يَفْعُلُ", "meaning": "يخط بالقلم"},
            "علم": {"root": "علم", "type": "اسم", "pattern": "فَعْل", "meaning": "معرفة"},
            "معلوم": {"root": "علم", "type": "اسم", "pattern": "مَفْعول", "meaning": "ما عُلم"},
            "قرأ": {"root": "قرء", "type": "فعل", "pattern": "فَعَلَ", "meaning": "تلا"},
            "قارئ": {"root": "قرء", "type": "اسم", "pattern": "فاعِل", "meaning": "من يقرأ"},
            "دخل": {"root": "دخل", "type": "فعل", "pattern": "فَعَلَ", "meaning": "ولج"},
            "خرج": {"root": "خرج", "type": "فعل", "pattern": "فَعَلَ", "meaning": "برز"},
        }
        with open(self.lexicon_file, "w", encoding="utf-8") as f:
            json.dump(lexicon_data, f, ensure_ascii=False, indent=2)

        # إنشاء مجموعة بيانات مخصصة للتقييم
        self.test_dataset_file = os.path.join(self.temp_dir, "test_dataset.json")
        test_dataset = [
            {"word": "كتاب", "root": "كتب", "type": "اسم"},
            {"word": "يكتب", "root": "كتب", "type": "فعل"},
            {"word": "مكاتبة", "root": "كتب", "type": "اسم"},
            {"word": "كاتب", "root": "كتب", "type": "اسم"},
            {"word": "علم", "root": "علم", "type": "اسم"},
            {"word": "معلم", "root": "علم", "type": "اسم"},
            {"word": "تعليم", "root": "علم", "type": "اسم"},
            {"word": "عالم", "root": "علم", "type": "اسم"},
            {"word": "قرأ", "root": "قرء", "type": "فعل"},
            {"word": "قارئ", "root": "قرء", "type": "اسم"},
            {"word": "قراءة", "root": "قرء", "type": "اسم"},
            {"word": "مقروء", "root": "قرء", "type": "اسم"},
            {"word": "دخل", "root": "دخل", "type": "فعل"},
            {"word": "مدخل", "root": "دخل", "type": "اسم"},
            {"word": "داخل", "root": "دخل", "type": "اسم"},
            {"word": "خرج", "root": "خرج", "type": "فعل"},
            {"word": "مخرج", "root": "خرج", "type": "اسم"},
            {"word": "خارج", "root": "خرج", "type": "اسم"},
            {"word": "استخرج", "root": "خرج", "type": "فعل"},
            {"word": "فهم", "root": "فهم", "type": "فعل"},
        ]
        with open(self.test_dataset_file, "w", encoding="utf-8") as f:
            json.dump(test_dataset, f, ensure_ascii=False, indent=2)

        # تهيئة المعالج الهجين
        self.hybrid_processor = HybridProcessor(self.lexicon_file)

        # تهيئة الأدوات المساعدة
        self.root_extractor = ArabicRootExtractor()
        self.diacritics_processor = DiacriticsProcessor()

        # مسار خرج التقرير
        self.report_path = os.path.join(self.temp_dir, "evaluation_report.md")

    def tearDown(self):
        """التنظيف بعد كل اختبار"""
        # حذف المجلد المؤقت وجميع محتوياته
        shutil.rmtree(self.temp_dir)

    def test_evaluate_root_extraction(self):
        """اختبار تقييم أداء استخراج الجذور باستخدام مجموعة بيانات محددة"""
        # استدعاء دالة تقييم استخراج الجذور
        results = evaluate_root_extraction(
            lexicon_path=self.lexicon_file,
            dataset_path=self.test_dataset_file,
            output_report=None,
        )

        # التحقق من وجود المقاييس المتوقعة في النتائج
        expected_metrics = [
            "total_words",
            "correct_extractions",
            "incorrect_extractions",
            "accuracy",
            "extraction_times",
            "avg_extraction_time",
        ]

        for metric in expected_metrics:
            self.assertIn(metric, results)

        # التحقق من قيم بعض المقاييس
        self.assertEqual(results["total_words"], 20)  # عدد الكلمات في مجموعة البيانات
        self.assertTrue(results["accuracy"] >= 0.0 and results["accuracy"] <= 1.0)  # دقة بين 0 و 1
        self.assertTrue(results["avg_extraction_time"] > 0)  # وقت الاستخراج موجب

    def test_evaluate_with_custom_dataset(self):
        """اختبار تقييم الخوارزميات باستخدام مجموعة بيانات مخصصة"""
        # إنشاء مجموعة بيانات مخصصة
        custom_dataset = [
            {"word": "يكتب", "root": "كتب", "type": "فعل"},
            {"word": "مكاتبة", "root": "كتب", "type": "اسم"},
            {"word": "تعليم", "root": "علم", "type": "اسم"},
            {"word": "مقروء", "root": "قرء", "type": "اسم"},
            {"word": "استخرج", "root": "خرج", "type": "فعل"},
        ]

        # استدعاء دالة التقييم مع مجموعة بيانات مخصصة
        results = evaluate_with_custom_dataset(
            processor=self.hybrid_processor,
            dataset=custom_dataset,
            evaluation_type="root_extraction",
        )

        # التحقق من وجود المقاييس المتوقعة في النتائج
        expected_metrics = [
            "total_words",
            "correct_extractions",
            "incorrect_extractions",
            "accuracy",
            "extraction_sources",
        ]

        for metric in expected_metrics:
            self.assertIn(metric, results)

        # التحقق من قيم بعض المقاييس
        self.assertEqual(results["total_words"], 5)  # عدد الكلمات في مجموعة البيانات المخصصة
        self.assertTrue(results["accuracy"] >= 0.0 and results["accuracy"] <= 1.0)  # دقة بين 0 و 1

        # التحقق من وجود مصادر الاستخراج
        self.assertIn("lexicon", results["extraction_sources"])
        self.assertIn("algorithm", results["extraction_sources"])

    def test_analyze_error_patterns(self):
        """اختبار تحليل أنماط الأخطاء في استخراج الجذور"""
        # إنشاء بيانات النتائج المفصلة لاستخراج الجذور
        detailed_results = [
            {
                "word": "كتاب",
                "expected": "كتب",
                "extracted": "كتب",
                "correct": True,
                "source": "lexicon",
            },
            {
                "word": "مكاتبة",
                "expected": "كتب",
                "extracted": "كتب",
                "correct": True,
                "source": "algorithm",
            },
            {
                "word": "علم",
                "expected": "علم",
                "extracted": "علم",
                "correct": True,
                "source": "lexicon",
            },
            {
                "word": "تعليم",
                "expected": "علم",
                "extracted": "علم",
                "correct": True,
                "source": "algorithm",
            },
            {
                "word": "قرأ",
                "expected": "قرء",
                "extracted": "قرء",
                "correct": True,
                "source": "lexicon",
            },
            {
                "word": "قراءة",
                "expected": "قرء",
                "extracted": "قرأ",
                "correct": False,
                "source": "algorithm",
            },
            {
                "word": "استخرج",
                "expected": "خرج",
                "extracted": "خرج",
                "correct": True,
                "source": "algorithm",
            },
            {
                "word": "فهم",
                "expected": "فهم",
                "extracted": "فهم",
                "correct": True,
                "source": "algorithm",
            },
            {
                "word": "مفهوم",
                "expected": "فهم",
                "extracted": "فهم",
                "correct": True,
                "source": "algorithm",
            },
            {
                "word": "استفهام",
                "expected": "فهم",
                "extracted": "فهم",
                "correct": True,
                "source": "algorithm",
            },
        ]

        # استدعاء دالة تحليل أنماط الأخطاء
        error_patterns = analyze_error_patterns(detailed_results)

        # التحقق من وجود التحليلات المتوقعة
        expected_analysis = [
            "common_error_patterns",
            "error_by_word_length",
            "error_by_word_type",
            "error_by_extraction_source",
            "common_error_substitutions",
        ]

        for analysis in expected_analysis:
            self.assertIn(analysis, error_patterns)

        # التحقق من وجود بعض البيانات التفصيلية
        self.assertIn("lexicon", error_patterns["error_by_extraction_source"])
        self.assertIn("algorithm", error_patterns["error_by_extraction_source"])

    def test_generate_evaluation_report(self):
        """اختبار توليد تقرير التقييم الشامل"""
        # إعداد بيانات التقييم
        evaluation_data = {
            "metrics": {
                "total_words": 20,
                "correct_extractions": 18,
                "incorrect_extractions": 2,
                "accuracy": 0.9,
                "avg_extraction_time": 0.005,
            },
            "detailed_results": [
                {
                    "word": "كتاب",
                    "expected": "كتب",
                    "extracted": "كتب",
                    "correct": True,
                    "source": "lexicon",
                },
                {
                    "word": "مكاتبة",
                    "expected": "كتب",
                    "extracted": "كتب",
                    "correct": True,
                    "source": "algorithm",
                },
                {
                    "word": "قراءة",
                    "expected": "قرء",
                    "extracted": "قرأ",
                    "correct": False,
                    "source": "algorithm",
                },
            ],
            "error_analysis": {
                "common_error_patterns": {"قرء/قرأ": 1},
                "error_by_word_length": {"6": 1},
                "error_by_extraction_source": {"algorithm": 1, "lexicon": 0},
            },
        }

        # استدعاء دالة توليد التقرير
        report_path = generate_evaluation_report(
            evaluation_data=evaluation_data,
            output_path=self.report_path,
            title="تقرير تقييم استخراج الجذور",
            description="تقرير تفصيلي عن أداء خوارزمية استخراج الجذور",
        )

        # التحقق من وجود ملف التقرير
        self.assertTrue(os.path.exists(report_path))

        # التحقق من محتوى التقرير
        with open(report_path, "r", encoding="utf-8") as f:
            report_content = f.read()

        # التحقق من وجود بعض العناصر المتوقعة في التقرير
        self.assertIn("تقرير تقييم استخراج الجذور", report_content)
        self.assertIn("إجمالي الكلمات:", report_content)
        self.assertIn("الدقة:", report_content)
        self.assertIn("تحليل الأخطاء", report_content)

    def test_get_evaluation_metrics(self):
        """اختبار الحصول على مقاييس التقييم المختلفة"""
        # إنشاء بيانات النتائج المفصلة
        detailed_results = [
            {
                "word": "كتاب",
                "expected": "كتب",
                "extracted": "كتب",
                "correct": True,
                "source": "lexicon",
            },
            {
                "word": "مكاتبة",
                "expected": "كتب",
                "extracted": "كتب",
                "correct": True,
                "source": "algorithm",
            },
            {
                "word": "علم",
                "expected": "علم",
                "extracted": "علم",
                "correct": True,
                "source": "lexicon",
            },
            {
                "word": "تعليم",
                "expected": "علم",
                "extracted": "علم",
                "correct": True,
                "source": "algorithm",
            },
            {
                "word": "قرأ",
                "expected": "قرء",
                "extracted": "قرء",
                "correct": True,
                "source": "lexicon",
            },
            {
                "word": "قراءة",
                "expected": "قرء",
                "extracted": "قرأ",
                "correct": False,
                "source": "algorithm",
            },
            {
                "word": "استخرج",
                "expected": "خرج",
                "extracted": "خرج",
                "correct": True,
                "source": "algorithm",
            },
            {
                "word": "فهم",
                "expected": "فهم",
                "extracted": "فهم",
                "correct": True,
                "source": "algorithm",
            },
            {
                "word": "مفهوم",
                "expected": "فهم",
                "extracted": "فهم",
                "correct": True,
                "source": "algorithm",
            },
            {
                "word": "استفهام",
                "expected": "فهم",
                "extracted": "فهم",
                "correct": True,
                "source": "algorithm",
            },
        ]

        # استدعاء دالة الحصول على المقاييس
        metrics = get_evaluation_metrics(detailed_results)

        # التحقق من وجود المقاييس المتوقعة
        expected_metrics = [
            "total_words",
            "correct_extractions",
            "incorrect_extractions",
            "accuracy",
            "precision",
            "recall",
            "f1_score",
            "extraction_sources",
        ]

        for metric in expected_metrics:
            self.assertIn(metric, metrics)

        # التحقق من قيم بعض المقاييس
        self.assertEqual(metrics["total_words"], 10)
        self.assertEqual(metrics["correct_extractions"], 9)
        self.assertEqual(metrics["incorrect_extractions"], 1)
        self.assertEqual(metrics["accuracy"], 0.9)
        self.assertTrue(metrics["precision"] >= 0.0 and metrics["precision"] <= 1.0)
        self.assertTrue(metrics["recall"] >= 0.0 and metrics["recall"] <= 1.0)
        self.assertTrue(metrics["f1_score"] >= 0.0 and metrics["f1_score"] <= 1.0)

        # التحقق من مصادر الاستخراج
        self.assertIn("lexicon", metrics["extraction_sources"])
        self.assertIn("algorithm", metrics["extraction_sources"])


if __name__ == "__main__":
    unittest.main()
