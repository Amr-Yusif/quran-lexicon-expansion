"""
اختبارات لتحسين نظام التقييم والتدقيق (المرحلة 3.3)
"""

import unittest
import tempfile
import json
import os
import shutil
from pathlib import Path
import csv

from core.lexicon.quranic_lexicon import QuranicLexicon
from core.lexicon.hybrid_processor import HybridProcessor
from core.nlp.root_extraction import ArabicRootExtractor
from core.nlp.morphology import ArabicMorphologyAnalyzer
from core.nlp.diacritics import DiacriticsProcessor
from core.nlp.evaluate_nlp import evaluate_root_extraction


class TestEvaluationSystem(unittest.TestCase):
    """اختبارات تحسين نظام التقييم والتدقيق"""

    def setUp(self):
        """تهيئة بيئة الاختبار قبل كل اختبار"""
        # إنشاء دليل مؤقت للاختبار
        self.temp_dir = tempfile.mkdtemp()

        # إنشاء معجم اختبار
        self.test_lexicon_path = Path(self.temp_dir) / "test_lexicon.json"
        self.test_lexicon_data = {
            "كتب": {"root": "كتب", "type": "verb", "pattern": "فَعَلَ", "meaning": "كتب، خط بالقلم"},
            "قرأ": {
                "root": "قرأ",
                "type": "verb",
                "pattern": "فَعَلَ",
                "meaning": "تلا، نطق بالمكتوب",
            },
            "علم": {"root": "علم", "type": "noun", "pattern": "فَعْل", "meaning": "معرفة، إدراك"},
            "استغفر": {
                "root": "غفر",
                "type": "verb",
                "pattern": "اسْتَفْعَلَ",
                "meaning": "طلب المغفرة",
            },
            "كاتب": {"root": "كتب", "type": "noun", "pattern": "فَاعِل", "meaning": "من يكتب"},
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

        # إنشاء دليل لنتائج التقييم
        self.evaluation_dir = Path(self.temp_dir) / "evaluation_results"
        os.makedirs(self.evaluation_dir, exist_ok=True)

    def tearDown(self):
        """تنظيف بيئة الاختبار بعد كل اختبار"""
        # حذف الدليل المؤقت
        shutil.rmtree(self.temp_dir)

    def create_evaluation_dataset(self):
        """إنشاء مجموعة بيانات للتقييم"""
        dataset_path = self.evaluation_dir / "evaluation_dataset.csv"

        # إنشاء بيانات التقييم
        evaluation_data = [
            ["word", "expected_root", "expected_type", "expected_pattern"],
            ["كتب", "كتب", "verb", "فَعَلَ"],
            ["كاتب", "كتب", "noun", "فَاعِل"],
            ["مكتبة", "كتب", "noun", "مَفْعَلَة"],
            ["قرأ", "قرأ", "verb", "فَعَلَ"],
            ["قارئ", "قرأ", "noun", "فَاعِل"],
            ["استغفر", "غفر", "verb", "اسْتَفْعَلَ"],
            ["يستغفرون", "غفر", "verb", "يَسْتَفْعِلُون"],
            ["علم", "علم", "noun", "فَعْل"],
            ["معلم", "علم", "noun", "مُفَعِّل"],
            ["علماء", "علم", "noun", "فُعَلَاء"],
        ]

        # حفظ البيانات في ملف CSV
        with open(dataset_path, "w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerows(evaluation_data)

        return dataset_path

    def test_create_evaluation_dataset(self):
        """اختبار إنشاء مجموعة بيانات للتقييم"""
        dataset_path = self.create_evaluation_dataset()

        # التحقق من وجود ملف البيانات
        self.assertTrue(os.path.exists(dataset_path))

        # قراءة الملف والتحقق من محتواه
        with open(dataset_path, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            rows = list(reader)

        # التحقق من عدد الصفوف
        self.assertEqual(len(rows), 11)  # العنوان + 10 كلمات

        # التحقق من بنية البيانات
        self.assertEqual(rows[0], ["word", "expected_root", "expected_type", "expected_pattern"])
        self.assertEqual(rows[1], ["كتب", "كتب", "verb", "فَعَلَ"])

    def test_evaluate_root_extraction_with_dataset(self):
        """اختبار تقييم استخراج الجذور باستخدام مجموعة بيانات"""
        # إنشاء مجموعة بيانات للتقييم
        dataset_path = self.create_evaluation_dataset()

        # قراءة البيانات
        with open(dataset_path, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            next(reader)  # تخطي الصف الأول (العنوان)
            test_pairs = [(row[0], row[1]) for row in reader]

        # تقييم دقة استخراج الجذور
        results = evaluate_root_extraction(self.root_extractor, test_pairs)

        # التحقق من وجود نتائج التقييم
        self.assertIn("total", results)
        self.assertIn("correct", results)
        self.assertIn("incorrect", results)
        self.assertIn("accuracy", results)

        # التحقق من صحة النتائج
        self.assertEqual(results["total"], len(test_pairs))
        self.assertGreaterEqual(results["correct"], 0)
        self.assertEqual(results["total"], results["correct"] + results["incorrect"])

    def test_save_evaluation_results(self):
        """اختبار حفظ نتائج التقييم"""
        # إنشاء مجموعة بيانات للتقييم
        dataset_path = self.create_evaluation_dataset()

        # قراءة البيانات
        with open(dataset_path, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            next(reader)  # تخطي الصف الأول (العنوان)
            test_pairs = [(row[0], row[1]) for row in reader]

        # تقييم دقة استخراج الجذور
        results = evaluate_root_extraction(self.root_extractor, test_pairs)

        # حفظ نتائج التقييم
        results_path = self.evaluation_dir / "evaluation_results.json"
        with open(results_path, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)

        # التحقق من وجود ملف النتائج
        self.assertTrue(os.path.exists(results_path))

        # قراءة النتائج والتحقق من صحتها
        with open(results_path, "r", encoding="utf-8") as f:
            loaded_results = json.load(f)

        self.assertEqual(loaded_results, results)

    def test_evaluation_tracking(self):
        """اختبار تتبع نتائج التقييم عبر الزمن"""
        # إنشاء عدة نسخ من نتائج التقييم
        results_1 = {
            "timestamp": "2023-01-01",
            "algorithm_version": "1.0",
            "total": 10,
            "correct": 6,
            "incorrect": 4,
            "accuracy": 0.6,
        }

        results_2 = {
            "timestamp": "2023-01-15",
            "algorithm_version": "1.1",
            "total": 10,
            "correct": 7,
            "incorrect": 3,
            "accuracy": 0.7,
        }

        results_3 = {
            "timestamp": "2023-02-01",
            "algorithm_version": "1.2",
            "total": 10,
            "correct": 8,
            "incorrect": 2,
            "accuracy": 0.8,
        }

        # حفظ نتائج التقييم
        history_path = self.evaluation_dir / "evaluation_history.json"
        evaluation_history = [results_1, results_2, results_3]

        with open(history_path, "w", encoding="utf-8") as f:
            json.dump(evaluation_history, f, ensure_ascii=False, indent=2)

        # التحقق من وجود ملف المحفوظات
        self.assertTrue(os.path.exists(history_path))

        # قراءة المحفوظات والتحقق من صحتها
        with open(history_path, "r", encoding="utf-8") as f:
            loaded_history = json.load(f)

        self.assertEqual(len(loaded_history), 3)
        self.assertEqual(loaded_history[0]["timestamp"], "2023-01-01")
        self.assertEqual(loaded_history[1]["timestamp"], "2023-01-15")
        self.assertEqual(loaded_history[2]["timestamp"], "2023-02-01")

        # التحقق من التحسن في الدقة
        self.assertLess(loaded_history[0]["accuracy"], loaded_history[1]["accuracy"])
        self.assertLess(loaded_history[1]["accuracy"], loaded_history[2]["accuracy"])

    def test_detailed_error_reporting(self):
        """اختبار تقارير الأخطاء المفصلة"""
        # إنشاء مجموعة بيانات للتقييم
        dataset_path = self.create_evaluation_dataset()

        # قراءة البيانات
        with open(dataset_path, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            next(reader)  # تخطي الصف الأول (العنوان)
            test_data = list(reader)

        # إنشاء تقرير مفصل للأخطاء
        error_report = []

        for word, expected_root, expected_type, expected_pattern in test_data:
            # استخراج الجذر باستخدام الخوارزمية
            extracted_root = self.root_extractor.extract_root(word)

            # استخراج النوع والوزن باستخدام المحلل الصرفي
            analysis = self.morphology_analyzer.analyze_word(word)
            extracted_type = (
                self.processor._map_arabic_type_to_english(analysis.get("نوع", ""))
                if analysis
                else ""
            )
            extracted_pattern = analysis.get("وزن", "") if analysis else ""

            # معالجة الكلمة باستخدام المعالج الهجين
            result = self.processor.process_word(word)

            # إنشاء تقرير للكلمة
            word_report = {
                "word": word,
                "root": {
                    "expected": expected_root,
                    "extracted": extracted_root,
                    "hybrid": result["root"]["value"],
                    "correct": extracted_root == expected_root,
                },
                "type": {
                    "expected": expected_type,
                    "extracted": extracted_type,
                    "hybrid": result["type"]["value"],
                    "correct": extracted_type == expected_type,
                },
                "pattern": {
                    "expected": expected_pattern,
                    "extracted": extracted_pattern,
                    "hybrid": result["pattern"]["value"],
                    "correct": extracted_pattern == expected_pattern,
                },
            }

            # إضافة التقرير إلى قائمة التقارير
            error_report.append(word_report)

        # حفظ تقرير الأخطاء
        report_path = self.evaluation_dir / "detailed_error_report.json"
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(error_report, f, ensure_ascii=False, indent=2)

        # التحقق من وجود ملف التقرير
        self.assertTrue(os.path.exists(report_path))

        # قراءة التقرير والتحقق من بنيته
        with open(report_path, "r", encoding="utf-8") as f:
            loaded_report = json.load(f)

        self.assertEqual(len(loaded_report), len(test_data))
        for item in loaded_report:
            self.assertIn("word", item)
            self.assertIn("root", item)
            self.assertIn("type", item)
            self.assertIn("pattern", item)


if __name__ == "__main__":
    unittest.main()
