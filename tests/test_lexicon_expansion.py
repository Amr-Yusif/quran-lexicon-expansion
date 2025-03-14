"""
اختبارات لتوسيع قاعدة البيانات المعجمية (المرحلة 3.1)
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
from tools.lexicon_expansion_interface import LexiconExpansionInterface


class TestLexiconExpansion(unittest.TestCase):
    """اختبارات توسيع قاعدة البيانات المعجمية"""

    def setUp(self):
        """تهيئة بيئة الاختبار قبل كل اختبار"""
        # إنشاء دليل مؤقت للاختبار
        self.temp_dir = tempfile.mkdtemp()

        # إنشاء معجم اختبار صغير
        self.test_lexicon_path = Path(self.temp_dir) / "test_lexicon.json"
        self.test_lexicon_data = {
            "كتب": {
                "root": "كتب",
                "type": "verb",
                "pattern": "فَعَلَ",
                "meaning": "كتب، خط بالقلم",
                "source": "اختبار",
            },
            "قرأ": {
                "root": "قرأ",
                "type": "verb",
                "pattern": "فَعَلَ",
                "meaning": "تلا، نطق بالمكتوب",
                "source": "اختبار",
            },
            "علم": {
                "root": "علم",
                "type": "noun",
                "pattern": "فَعْل",
                "meaning": "معرفة، إدراك",
                "source": "اختبار",
            },
        }

        # حفظ المعجم في ملف مؤقت
        with open(self.test_lexicon_path, "w", encoding="utf-8") as f:
            json.dump(self.test_lexicon_data, f, ensure_ascii=False, indent=2)

        # إنشاء ملف كلمات للاختبار
        self.test_words_path = Path(self.temp_dir) / "test_words.txt"
        test_words = ["مكتبة", "قارئ", "معلم", "دراسة", "كتاب"]
        with open(self.test_words_path, "w", encoding="utf-8") as f:
            f.write("\n".join(test_words))

        # تهيئة المعالج الهجين
        self.processor = HybridProcessor(lexicon_path=self.test_lexicon_path)

        # تهيئة واجهة توسيع المعجم
        self.output_path = Path(self.temp_dir) / "expanded_lexicon.json"
        self.interface = LexiconExpansionInterface(
            str(self.test_lexicon_path), str(self.output_path)
        )

    def tearDown(self):
        """تنظيف بيئة الاختبار بعد كل اختبار"""
        # حذف الدليل المؤقت
        shutil.rmtree(self.temp_dir)

    def test_initial_lexicon_size(self):
        """اختبار حجم المعجم الأولي"""
        lexicon = QuranicLexicon(self.test_lexicon_path)
        self.assertEqual(len(lexicon.words), 3)
        self.assertIn("كتب", lexicon.words)
        self.assertIn("قرأ", lexicon.words)
        self.assertIn("علم", lexicon.words)

    def test_generate_suggestions(self):
        """اختبار توليد اقتراحات لتوسيع المعجم"""
        suggestions = self.interface.generate_suggestions(str(self.test_words_path))

        # التحقق من وجود اقتراحات
        self.assertGreater(len(suggestions), 0)

        # التحقق من بنية الاقتراحات
        for suggestion in suggestions:
            self.assertIn("word", suggestion)
            self.assertIn("root", suggestion)
            self.assertIn("type", suggestion)
            self.assertIn("pattern", suggestion)
            self.assertIn("confidence", suggestion)

    def test_add_to_lexicon(self):
        """اختبار إضافة كلمات جديدة إلى المعجم"""
        # إضافة كلمة جديدة
        word_info = {
            "root": "كتب",
            "type": "noun",
            "pattern": "مَفْعَلَة",
            "meaning": "مكان لحفظ الكتب",
        }
        result = self.processor.add_to_lexicon("مكتبة", word_info, is_verified=True)

        # التحقق من نجاح الإضافة
        self.assertTrue(result)

        # التحقق من وجود الكلمة في المعجم
        lexicon = QuranicLexicon(self.test_lexicon_path)
        self.assertIn("مكتبة", lexicon.words)
        self.assertEqual(lexicon.words["مكتبة"]["root"], "كتب")
        self.assertEqual(lexicon.words["مكتبة"]["type"], "noun")

    def test_save_expanded_lexicon(self):
        """اختبار حفظ المعجم بعد التوسيع"""
        # إضافة عدة كلمات
        words_to_add = {
            "مكتبة": {
                "root": "كتب",
                "type": "noun",
                "pattern": "مَفْعَلَة",
                "meaning": "مكان لحفظ الكتب",
            },
            "قارئ": {
                "root": "قرأ",
                "type": "noun",
                "pattern": "فَاعِل",
                "meaning": "من يقوم بالقراءة",
            },
            "معلم": {
                "root": "علم",
                "type": "noun",
                "pattern": "مُفَعِّل",
                "meaning": "من يقوم بالتعليم",
            },
        }

        for word, info in words_to_add.items():
            self.processor.add_to_lexicon(word, info, is_verified=True)

        # حفظ المعجم
        result = self.processor.save_lexicon(self.output_path)
        self.assertTrue(result)

        # التحقق من وجود الملف
        self.assertTrue(os.path.exists(self.output_path))

        # التحقق من محتوى الملف
        with open(self.output_path, "r", encoding="utf-8") as f:
            expanded_lexicon = json.load(f)

        self.assertEqual(len(expanded_lexicon), 6)  # 3 كلمات أصلية + 3 كلمات مضافة
        for word in words_to_add:
            self.assertIn(word, expanded_lexicon)

    def test_bulk_lexicon_expansion(self):
        """اختبار توسيع المعجم بشكل جماعي"""
        # توليد اقتراحات
        self.interface.generate_suggestions(str(self.test_words_path))

        # تعديل الاقتراحات لتكون جميعها موثوقة
        for suggestion in self.interface.suggestions:
            suggestion["source"] = "human_verified"
            suggestion["meaning"] = f"معنى {suggestion['word']}"
            suggestion["confidence"] = 1.0

        # إضافة الاقتراحات إلى المعجم
        self.interface.add_to_lexicon()

        # حفظ المعجم
        self.interface.save_lexicon()

        # التحقق من حجم المعجم بعد التوسيع
        expanded_lexicon = QuranicLexicon(self.output_path)
        self.assertGreater(len(expanded_lexicon.words), 3)  # أكبر من حجم المعجم الأصلي


if __name__ == "__main__":
    unittest.main()
