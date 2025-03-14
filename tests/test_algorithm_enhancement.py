"""
اختبارات لتحسين الخوارزميات بناءً على المعجم (المرحلة 3.2)
"""

import unittest
import tempfile
import json
import os
import shutil
from pathlib import Path

from core.lexicon.quranic_lexicon import QuranicLexicon
from core.lexicon.hybrid_processor import HybridProcessor
from core.nlp.root_extraction import ArabicRootExtractor
from core.nlp.morphology import ArabicMorphologyAnalyzer
from core.nlp.diacritics import DiacriticsProcessor
from core.nlp.evaluate_nlp import evaluate_root_extraction, analyze_error_patterns


class TestAlgorithmEnhancement(unittest.TestCase):
    """اختبارات تحسين الخوارزميات بناءً على المعجم"""

    def setUp(self):
        """تهيئة بيئة الاختبار قبل كل اختبار"""
        # إنشاء دليل مؤقت للاختبار
        self.temp_dir = tempfile.mkdtemp()

        # إنشاء معجم اختبار موسع
        self.test_lexicon_path = Path(self.temp_dir) / "test_enhanced_lexicon.json"
        # نموذج لمعجم موسع يحتوي على كلمات متنوعة لاختبار الخوارزميات
        self.test_lexicon_data = {
            # كلمات بسيطة
            "كتب": {"root": "كتب", "type": "verb", "pattern": "فَعَلَ", "meaning": "كتب، خط بالقلم"},
            "قرأ": {
                "root": "قرأ",
                "type": "verb",
                "pattern": "فَعَلَ",
                "meaning": "تلا، نطق بالمكتوب",
            },
            # كلمات مزيدة
            "استغفر": {
                "root": "غفر",
                "type": "verb",
                "pattern": "اسْتَفْعَلَ",
                "meaning": "طلب المغفرة",
            },
            "انكسر": {"root": "كسر", "type": "verb", "pattern": "انْفَعَلَ", "meaning": "تحطم"},
            # أسماء مشتقة
            "كاتب": {"root": "كتب", "type": "noun", "pattern": "فَاعِل", "meaning": "من يكتب"},
            "مكتوب": {"root": "كتب", "type": "noun", "pattern": "مَفْعُول", "meaning": "ما تم كتابته"},
            "مكتبة": {
                "root": "كتب",
                "type": "noun",
                "pattern": "مَفْعَلَة",
                "meaning": "مكان لحفظ الكتب",
            },
            # كلمات بحروف زائدة
            "الكتاب": {
                "root": "كتب",
                "type": "noun",
                "pattern": "الفِعَال",
                "meaning": "الشيء المكتوب",
            },
            "بالقلم": {
                "root": "قلم",
                "type": "noun",
                "pattern": "بالفَعَل",
                "meaning": "بأداة الكتابة",
            },
            # حالات خاصة
            "قال": {"root": "قول", "type": "verb", "pattern": "فَعَلَ", "meaning": "نطق، تكلم"},
            "باع": {"root": "بيع", "type": "verb", "pattern": "فَعَلَ", "meaning": "تاجر"},
        }

        # حفظ المعجم في ملف مؤقت
        with open(self.test_lexicon_path, "w", encoding="utf-8") as f:
            json.dump(self.test_lexicon_data, f, ensure_ascii=False, indent=2)

        # تهيئة الخوارزميات
        self.root_extractor = ArabicRootExtractor()
        self.diacritics_processor = DiacriticsProcessor()
        self.morphology_analyzer = ArabicMorphologyAnalyzer(
            diacritics_processor=self.diacritics_processor, root_extractor=self.root_extractor
        )

        # تهيئة المعالج الهجين
        self.processor = HybridProcessor(
            lexicon_path=self.test_lexicon_path,
            use_algorithms=True,
            root_extractor=self.root_extractor,
            morphology_analyzer=self.morphology_analyzer,
        )

        # إنشاء مجموعة اختبار للكلمات
        self.test_words = list(self.test_lexicon_data.keys())
        self.test_words.extend(
            ["يكتبون", "اقرأ", "مستغفر", "كتابة", "قلم"]
        )  # كلمات إضافية للاختبار

    def tearDown(self):
        """تنظيف بيئة الاختبار بعد كل اختبار"""
        # حذف الدليل المؤقت
        shutil.rmtree(self.temp_dir)

    def test_root_extraction_evaluation(self):
        """اختبار تقييم دقة استخراج الجذور"""
        # إنشاء قائمة من الكلمات والجذور المتوقعة
        test_pairs = []
        for word, info in self.test_lexicon_data.items():
            test_pairs.append((word, info["root"]))

        # تقييم دقة استخراج الجذور
        results = evaluate_root_extraction(self.root_extractor, test_pairs)

        # التحقق من وجود نتائج التقييم
        self.assertIn("total", results)
        self.assertIn("correct", results)
        self.assertIn("incorrect", results)
        self.assertIn("accuracy", results)

        # حساب الدقة المتوقعة
        expected_accuracy = results["correct"] / results["total"] if results["total"] > 0 else 0
        self.assertAlmostEqual(results["accuracy"], expected_accuracy)

    def test_error_pattern_analysis(self):
        """اختبار تحليل أنماط الأخطاء في استخراج الجذور"""
        # إنشاء قائمة من الكلمات والجذور المتوقعة
        test_pairs = []
        for word, info in self.test_lexicon_data.items():
            test_pairs.append((word, info["root"]))

        # تحليل أنماط الأخطاء
        error_patterns = analyze_error_patterns(self.root_extractor, test_pairs)

        # التحقق من وجود تحليل للأخطاء
        self.assertIsNotNone(error_patterns)

        # التحقق من وجود المعلومات المطلوبة في تحليل الأخطاء
        self.assertIn("error_count", error_patterns)
        self.assertIn("pattern_categories", error_patterns)

    def test_hybrid_processing_with_enhanced_algorithm(self):
        """اختبار المعالج الهجين مع خوارزمية محسنة"""
        # اختبار معالجة كلمات موجودة في المعجم
        for word in self.test_lexicon_data:
            result = self.processor.process_word(word)
            expected_root = self.test_lexicon_data[word]["root"]

            # التحقق من صحة الجذر المستخرج
            self.assertEqual(result["root"]["value"], expected_root)
            self.assertEqual(result["root"]["source"], "lexicon")
            self.assertEqual(result["root"]["confidence"], 1.0)

        # اختبار معالجة كلمات غير موجودة في المعجم
        for word in ["يكتبون", "اقرأ", "مستغفر", "كتابة"]:
            result = self.processor.process_word(word)

            # التحقق من وجود جذر
            self.assertTrue(result["root"]["value"])
            self.assertGreater(result["root"]["confidence"], 0.5)

    def test_special_cases_handling(self):
        """اختبار معالجة الحالات الخاصة"""
        # اختبار الحالات الخاصة مثل الكلمات المعتلة
        special_cases = {"قال": "قول", "باع": "بيع"}

        for word, expected_root in special_cases.items():
            # معالجة الكلمة باستخدام المعالج الهجين
            result = self.processor.process_word(word)

            # التحقق من صحة الجذر المستخرج
            self.assertEqual(result["root"]["value"], expected_root)
            self.assertEqual(result["root"]["source"], "lexicon")

            # التحقق من صحة الجذر المستخرج باستخدام الخوارزمية فقط
            extracted_root = self.root_extractor.extract_root(word)
            self.assertIsNotNone(extracted_root)


if __name__ == "__main__":
    unittest.main()
