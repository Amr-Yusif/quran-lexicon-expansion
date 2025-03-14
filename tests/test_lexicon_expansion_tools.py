#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
اختبارات أدوات توسيع المعجم
========================

هذا الملف يحتوي على اختبارات الوحدة للتحقق من صحة أدوات توسيع المعجم
الجديدة، بما في ذلك أداة جمع الكلمات وواجهة توسيع المعجم المحسنة.
"""

import os
import sys
import json
import tempfile
import unittest
import shutil
from pathlib import Path
from typing import Dict, List, Any, Set

# إضافة المسار إلى PYTHONPATH للوصول إلى الوحدات
current_path = Path(os.path.dirname(os.path.abspath(__file__)))
root_path = current_path.parent
sys.path.append(str(root_path))

from tools.word_collector import WordCollector
from tools.lexicon_expansion_interface import LexiconExpansionInterface
from core.lexicon.quranic_lexicon import QuranicLexicon
from core.lexicon.hybrid_processor import HybridProcessor


class TestWordCollector(unittest.TestCase):
    """اختبارات أداة جمع الكلمات العربية"""

    def setUp(self):
        """الإعداد قبل كل اختبار"""
        # إنشاء مجلد مؤقت للاختبارات
        self.temp_dir = tempfile.mkdtemp()

        # إنشاء ملف نصي مؤقت يحتوي على كلمات عربية
        self.text_file = os.path.join(self.temp_dir, "test_text.txt")
        with open(self.text_file, "w", encoding="utf-8") as f:
            f.write("""
            هذا نص عربي للاختبار
            يحتوي على بعض الكلمات العربية
            مثل كتاب، ومدرسة، وقلم، وعلم
            وبعض العبارات المفيدة
            ويمكن استخدامه لجمع الكلمات
            """)

        # إنشاء ملف قاموس مؤقت
        self.dictionary_file = os.path.join(self.temp_dir, "test_dictionary.json")
        dictionary_data = {
            "كتاب": {"root": "كتب", "type": "اسم"},
            "مدرسة": {"root": "درس", "type": "اسم"},
            "قلم": {"root": "قلم", "type": "اسم"},
            "علم": {"root": "علم", "type": "اسم"},
        }
        with open(self.dictionary_file, "w", encoding="utf-8") as f:
            json.dump(dictionary_data, f, ensure_ascii=False, indent=2)

        # إنشاء ملف قائمة سوداء مؤقت
        self.blacklist_file = os.path.join(self.temp_dir, "test_blacklist.txt")
        with open(self.blacklist_file, "w", encoding="utf-8") as f:
            f.write("هذا\nعلى\nمثل\n")

        # تهيئة أداة جمع الكلمات
        self.collector = WordCollector()

    def tearDown(self):
        """التنظيف بعد كل اختبار"""
        # حذف المجلد المؤقت وجميع محتوياته
        shutil.rmtree(self.temp_dir)

    def test_collect_from_text_file(self):
        """اختبار جمع الكلمات من ملف نصي"""
        words = self.collector.collect_from_text_file(self.text_file, min_word_length=3)

        # التحقق من أن مجموعة الكلمات غير فارغة
        self.assertTrue(len(words) > 0)

        # التحقق من وجود بعض الكلمات المتوقعة
        expected_words = {
            "نص",
            "عربي",
            "للاختبار",
            "يحتوي",
            "بعض",
            "الكلمات",
            "العربية",
            "كتاب",
            "مدرسة",
            "قلم",
            "علم",
        }
        for word in expected_words:
            self.assertIn(word, words)

        # التحقق من عدم وجود كلمات قصيرة جدًا
        for word in words:
            self.assertTrue(len(word) >= 3)

    def test_collect_from_dictionary(self):
        """اختبار جمع الكلمات من ملف قاموس"""
        words = self.collector.collect_from_dictionary(self.dictionary_file)

        # التحقق من عدد الكلمات المجمعة
        self.assertEqual(len(words), 4)

        # التحقق من وجود جميع الكلمات المتوقعة
        expected_words = {"كتاب", "مدرسة", "قلم", "علم"}
        self.assertEqual(set(words), expected_words)

    def test_load_blacklist(self):
        """اختبار تحميل القائمة السوداء"""
        # جمع كلمات من ملف نصي أولاً
        self.collector.collect_from_text_file(self.text_file)

        # تحميل القائمة السوداء
        count = self.collector.load_blacklist(self.blacklist_file)

        # التحقق من عدد الكلمات في القائمة السوداء
        self.assertEqual(count, 3)

        # التحقق من عدم وجود كلمات القائمة السوداء في الكلمات المجمعة
        blacklist_words = {"هذا", "على", "مثل"}
        for word in blacklist_words:
            self.assertNotIn(word, self.collector.collected_words)

    def test_save_collected_words(self):
        """اختبار حفظ الكلمات المجمعة في ملف"""
        # جمع كلمات من ملف نصي
        self.collector.collect_from_text_file(self.text_file)

        # حفظ الكلمات في ملف
        output_file = os.path.join(self.temp_dir, "output_words.txt")
        count = self.collector.save_collected_words(output_file)

        # التحقق من عدد الكلمات المحفوظة
        self.assertEqual(count, len(self.collector.collected_words))

        # التحقق من وجود الملف وقراءة محتواه
        self.assertTrue(os.path.exists(output_file))
        with open(output_file, "r", encoding="utf-8") as f:
            saved_words = [line.strip() for line in f if line.strip()]

        # التحقق من تطابق عدد الكلمات
        self.assertEqual(len(saved_words), len(self.collector.collected_words))

        # التحقق من تطابق الكلمات
        for word in saved_words:
            self.assertIn(word, self.collector.collected_words)

    def test_get_statistics(self):
        """اختبار الحصول على إحصائيات عملية جمع الكلمات"""
        # جمع كلمات من مصادر مختلفة
        self.collector.collect_from_text_file(self.text_file)
        self.collector.collect_from_dictionary(self.dictionary_file)

        # الحصول على الإحصائيات
        stats = self.collector.get_statistics()

        # التحقق من وجود جميع المفاتيح المتوقعة
        expected_keys = {
            "total",
            "text_file",
            "dictionary",
            "quran",
            "web",
            "custom",
            "length_distribution",
            "sample",
        }
        for key in expected_keys:
            self.assertIn(key, stats)

        # التحقق من صحة الإحصائيات الأساسية
        self.assertEqual(stats["total"], len(self.collector.collected_words))
        self.assertTrue(stats["text_file"] > 0)
        self.assertEqual(stats["dictionary"], 4)


class TestLexiconExpansionInterface(unittest.TestCase):
    """اختبارات واجهة توسيع المعجم"""

    def setUp(self):
        """الإعداد قبل كل اختبار"""
        # إنشاء مجلد مؤقت للاختبارات
        self.temp_dir = tempfile.mkdtemp()

        # إنشاء معجم مؤقت للاختبار
        self.lexicon_file = os.path.join(self.temp_dir, "test_lexicon.json")
        lexicon_data = {
            "الله": {"root": "الله", "type": "اسم", "pattern": "فَعْل", "meaning": "الذات الإلهية"},
            "يعبد": {"root": "عبد", "type": "فعل", "pattern": "يَفْعُل", "meaning": "يطيع ويخضع"},
        }
        with open(self.lexicon_file, "w", encoding="utf-8") as f:
            json.dump(lexicon_data, f, ensure_ascii=False, indent=2)

        # إنشاء ملف كلمات للاختبار
        self.words_file = os.path.join(self.temp_dir, "test_words.txt")
        with open(self.words_file, "w", encoding="utf-8") as f:
            f.write("كتاب\nمدرسة\nقلم\nعلم\nالعالم\nمكتبة\n")

        # تهيئة واجهة توسيع المعجم
        self.output_path = os.path.join(self.temp_dir, "expanded_lexicon.json")
        self.interface = LexiconExpansionInterface(self.lexicon_file, self.output_path)

    def tearDown(self):
        """التنظيف بعد كل اختبار"""
        # حذف المجلد المؤقت وجميع محتوياته
        shutil.rmtree(self.temp_dir)

    def test_generate_suggestions(self):
        """اختبار توليد اقتراحات للكلمات"""
        suggestions = self.interface.generate_suggestions(self.words_file)

        # التحقق من عدد الاقتراحات
        self.assertTrue(len(suggestions) > 0)

        # التحقق من بنية الاقتراحات
        for suggestion in suggestions:
            self.assertIn("word", suggestion)
            self.assertIn("root", suggestion)
            self.assertIn("type", suggestion)
            self.assertIn("pattern", suggestion)
            self.assertIn("confidence", suggestion)

    def test_export_suggestions_to_csv(self):
        """اختبار تصدير الاقتراحات إلى ملف CSV"""
        # توليد اقتراحات أولاً
        self.interface.generate_suggestions(self.words_file)

        # تصدير الاقتراحات إلى ملف CSV
        csv_file = os.path.join(self.temp_dir, "suggestions.csv")
        self.interface.export_suggestions_to_csv(csv_file)

        # التحقق من وجود الملف
        self.assertTrue(os.path.exists(csv_file))

        # التحقق من محتوى الملف
        with open(csv_file, "r", encoding="utf-8") as f:
            lines = f.readlines()

        # التحقق من وجود عنوان الملف
        self.assertTrue(len(lines) > 1)
        self.assertIn("الكلمة", lines[0])
        self.assertIn("الجذر", lines[0])
        self.assertIn("النوع", lines[0])
        self.assertIn("الوزن", lines[0])

    def test_process_words_in_batches(self):
        """اختبار معالجة الكلمات على دفعات"""
        # معالجة الكلمات على دفعات
        stats = self.interface.process_words_in_batches(
            self.words_file, batch_size=2, auto_approve_threshold=0.8, use_parallel=False
        )

        # التحقق من إحصائيات العملية
        self.assertEqual(stats["total_words"], 6)
        self.assertTrue(stats["processed_words"] > 0)
        self.assertTrue(stats["batches"] > 0)
        self.assertTrue(stats["processing_time"] > 0)

        # التحقق من وجود ملف CSV للاقتراحات التي تحتاج إلى مراجعة
        review_file = f"{os.path.splitext(self.words_file)[0]}_review_required.csv"
        self.assertTrue(os.path.exists(review_file))

    def test_add_to_lexicon(self):
        """اختبار إضافة الاقتراحات إلى المعجم"""
        # توليد اقتراحات
        suggestions = self.interface.generate_suggestions(self.words_file)

        # إضافة الاقتراحات إلى المعجم
        success = self.interface.add_to_lexicon()

        # التحقق من نجاح الإضافة
        self.assertTrue(success)

        # حفظ المعجم
        self.interface.save_lexicon()

        # التحقق من وجود المعجم الموسع
        self.assertTrue(os.path.exists(self.output_path))

        # تحميل المعجم الموسع والتحقق من محتواه
        expanded_lexicon = QuranicLexicon(self.output_path)

        # التحقق من عدد الكلمات
        self.assertTrue(len(expanded_lexicon.words) > 2)  # أكثر من الكلمات الأصلية


class TestLexiconExpansion(unittest.TestCase):
    """اختبارات تكامل توسيع المعجم"""

    def setUp(self):
        """الإعداد قبل كل اختبار"""
        # إنشاء مجلد مؤقت للاختبارات
        self.temp_dir = tempfile.mkdtemp()

        # إنشاء معجم مؤقت للاختبار
        self.lexicon_file = os.path.join(self.temp_dir, "test_lexicon.json")
        lexicon_data = {
            "الله": {"root": "الله", "type": "اسم", "pattern": "فَعْل", "meaning": "الذات الإلهية"},
            "يعبد": {"root": "عبد", "type": "فعل", "pattern": "يَفْعُل", "meaning": "يطيع ويخضع"},
        }
        with open(self.lexicon_file, "w", encoding="utf-8") as f:
            json.dump(lexicon_data, f, ensure_ascii=False, indent=2)

    def tearDown(self):
        """التنظيف بعد كل اختبار"""
        # حذف المجلد المؤقت وجميع محتوياته
        shutil.rmtree(self.temp_dir)

    def test_end_to_end_lexicon_expansion(self):
        """اختبار تكاملي لعملية توسيع المعجم من البداية إلى النهاية"""
        # إنشاء أداة جمع الكلمات
        collector = WordCollector()

        # إنشاء ملف نصي مؤقت
        text_file = os.path.join(self.temp_dir, "test_text.txt")
        with open(text_file, "w", encoding="utf-8") as f:
            f.write("""
            كتاب مدرسة قلم علم
            العالم مكتبة درس محمد
            القرآن الإسلام المسلمين
            """)

        # جمع الكلمات من الملف النصي
        collector.collect_from_text_file(text_file)

        # حفظ الكلمات المجمعة في ملف
        words_file = os.path.join(self.temp_dir, "collected_words.txt")
        collector.save_collected_words(words_file)

        # إنشاء واجهة توسيع المعجم
        output_path = os.path.join(self.temp_dir, "expanded_lexicon.json")
        interface = LexiconExpansionInterface(self.lexicon_file, output_path)

        # معالجة الكلمات وإضافتها إلى المعجم
        stats = interface.process_words_in_batches(
            words_file, batch_size=5, auto_approve_threshold=0.7
        )

        # حفظ المعجم الموسع
        interface.save_lexicon()

        # التحقق من وجود المعجم الموسع
        self.assertTrue(os.path.exists(output_path))

        # تحميل المعجم الموسع والتحقق من محتواه
        original_lexicon = QuranicLexicon(self.lexicon_file)
        expanded_lexicon = QuranicLexicon(output_path)

        # التحقق من أن المعجم الموسع يحتوي على كلمات أكثر من المعجم الأصلي
        self.assertTrue(len(expanded_lexicon.words) > len(original_lexicon.words))


class TestExpandLexiconScript(unittest.TestCase):
    """اختبارات سكربت توسيع المعجم الرئيسي"""

    def setUp(self):
        """الإعداد قبل كل اختبار"""
        # إنشاء مجلد مؤقت للاختبارات
        self.temp_dir = tempfile.mkdtemp()

        # إنشاء معجم مؤقت للاختبار
        self.lexicon_file = os.path.join(self.temp_dir, "test_lexicon.json")
        lexicon_data = {
            "الله": {"root": "الله", "type": "اسم", "pattern": "فَعْل", "meaning": "الذات الإلهية"},
            "يعبد": {"root": "عبد", "type": "فعل", "pattern": "يَفْعُل", "meaning": "يطيع ويخضع"},
            "رحمن": {"root": "رحم", "type": "اسم", "pattern": "فَعْلان", "meaning": "كثير الرحمة"},
        }
        with open(self.lexicon_file, "w", encoding="utf-8") as f:
            json.dump(lexicon_data, f, ensure_ascii=False, indent=2)

        # إنشاء ملفات بيانات مختلفة للاختبار

        # ملف نصي يحاكي نص القرآن
        self.quran_file = os.path.join(self.temp_dir, "quran_sample.txt")
        with open(self.quran_file, "w", encoding="utf-8") as f:
            f.write("""
            بسم الله الرحمن الرحيم
            الحمد لله رب العالمين
            الرحمن الرحيم
            مالك يوم الدين
            إياك نعبد وإياك نستعين
            اهدنا الصراط المستقيم
            صراط الذين أنعمت عليهم غير المغضوب عليهم ولا الضالين
            """)

        # ملف نصي عادي
        self.text_file = os.path.join(self.temp_dir, "text_sample.txt")
        with open(self.text_file, "w", encoding="utf-8") as f:
            f.write("""
            كتاب علم مدرسة
            قلم كاتب مكتبة
            معلم طالب فصل
            دراسة امتحان نجاح
            """)

        # ملف كلمات مخصصة
        self.custom_file = os.path.join(self.temp_dir, "custom_words.txt")
        with open(self.custom_file, "w", encoding="utf-8") as f:
            f.write("حاسوب\nبرمجة\nتقنية\nمعلومات\nتطوير\nذكاء\nاصطناعي\n")

        # ملف قائمة سوداء
        self.blacklist_file = os.path.join(self.temp_dir, "blacklist.txt")
        with open(self.blacklist_file, "w", encoding="utf-8") as f:
            f.write("في\nمن\nعلى\nإلى\nعن\nأو\nثم\nلا\nبل\nإن\nأن\nهو\nهي\n")

        # مسار الخرج
        self.output_path = os.path.join(self.temp_dir, "expanded_lexicon.json")

    def tearDown(self):
        """التنظيف بعد كل اختبار"""
        # حذف المجلد المؤقت وجميع محتوياته
        shutil.rmtree(self.temp_dir)

    def test_expand_lexicon_with_quran_source(self):
        """اختبار توسيع المعجم باستخدام نص القرآن كمصدر"""
        # استدعاء دالة توسيع المعجم من سكربت expand_lexicon
        from tools.expand_lexicon import expand_lexicon

        data_sources = {"quran": self.quran_file}

        result = expand_lexicon(
            lexicon_path=self.lexicon_file,
            data_sources=data_sources,
            output_path=self.output_path,
            auto_approve_threshold=0.85,
            batch_size=5,
            word_limit=20,
            min_word_length=3,
            generate_report=True,
            use_parallel=False,
        )

        # التحقق من وجود المعجم الموسع
        self.assertTrue(os.path.exists(self.output_path))

        # التحقق من عناصر النتيجة
        self.assertEqual(result["original_path"], self.lexicon_file)
        self.assertEqual(result["expanded_path"], self.output_path)
        self.assertTrue(result["expanded_count"] > result["original_count"])
        self.assertTrue(result["added_count"] > 0)

        # التحقق من وجود تقرير
        report_path = f"{os.path.splitext(self.output_path)[0]}_report.md"
        self.assertTrue(os.path.exists(report_path))

    def test_expand_lexicon_with_multiple_sources(self):
        """اختبار توسيع المعجم باستخدام مصادر متعددة"""
        # استدعاء دالة توسيع المعجم من سكربت expand_lexicon
        from tools.expand_lexicon import expand_lexicon

        data_sources = {
            "quran": self.quran_file,
            "text_files": [self.text_file],
            "custom": self.custom_file,
            "blacklist": self.blacklist_file,
        }

        result = expand_lexicon(
            lexicon_path=self.lexicon_file,
            data_sources=data_sources,
            output_path=self.output_path,
            auto_approve_threshold=0.8,
            batch_size=10,
            word_limit=30,
            min_word_length=3,
            generate_report=True,
            use_parallel=False,
        )

        # التحقق من وجود المعجم الموسع
        self.assertTrue(os.path.exists(self.output_path))

        # تحميل المعجم الموسع
        expanded_lexicon = QuranicLexicon(self.output_path)

        # التحقق من عدم وجود كلمات القائمة السوداء
        blacklist_words = ["في", "من", "على", "إلى", "عن"]
        for word in blacklist_words:
            self.assertNotIn(word, expanded_lexicon.words)

        # التحقق من إضافة كلمات من المصادر المختلفة
        combined_words = set()

        # قراءة الملف النصي
        with open(self.text_file, "r", encoding="utf-8") as f:
            for line in f:
                words = line.strip().split()
                combined_words.update(words)

        # قراءة ملف الكلمات المخصصة
        with open(self.custom_file, "r", encoding="utf-8") as f:
            for line in f:
                word = line.strip()
                if word:
                    combined_words.add(word)

        # التحقق من وجود بعض الكلمات في المعجم الموسع
        found_count = 0
        for word in combined_words:
            if word in expanded_lexicon.words:
                found_count += 1

        # يجب أن يكون هناك على الأقل كلمة واحدة من المصادر في المعجم الموسع
        self.assertTrue(found_count > 0)

    def test_expand_lexicon_with_high_threshold(self):
        """اختبار توسيع المعجم باستخدام عتبة ثقة عالية"""
        # استدعاء دالة توسيع المعجم من سكربت expand_lexicon
        from tools.expand_lexicon import expand_lexicon

        data_sources = {"custom": self.custom_file}

        result = expand_lexicon(
            lexicon_path=self.lexicon_file,
            data_sources=data_sources,
            output_path=self.output_path,
            auto_approve_threshold=0.99,  # عتبة عالية جدًا
            batch_size=5,
            word_limit=10,
            min_word_length=3,
            generate_report=True,
            use_parallel=False,
        )

        # التحقق من وجود المعجم الموسع
        self.assertTrue(os.path.exists(self.output_path))

        # يجب أن تكون معظم الكلمات في انتظار المراجعة
        self.assertTrue(result["review_required"] >= result["auto_approved"])


if __name__ == "__main__":
    unittest.main()
