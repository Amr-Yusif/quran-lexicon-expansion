import unittest
from pathlib import Path
import os
import json

from core.lexicon.hybrid_processor import HybridProcessor


class TestHybridProcessor(unittest.TestCase):
    """اختبارات لفئة المعالج الهجين الذي يدمج بين المعجم والخوارزميات."""

    def setUp(self):
        """تهيئة بيئة الاختبار قبل كل اختبار."""
        # إنشاء بيانات اختبار مؤقتة
        self.test_data_path = Path("test_lexicon_data.json")
        self.test_data = {
            "كتب": {
                "root": "كتب",
                "type": "verb",
                "pattern": "فَعَلَ",
                "meaning": "كتب، خط بالقلم",
                "source": "لسان العرب",
            },
            "الكتاب": {
                "root": "كتب",
                "type": "noun",
                "pattern": "فِعَال",
                "meaning": "ما يُكتب فيه",
                "source": "المعجم الوسيط",
            },
            "يقرأ": {
                "root": "قرأ",
                "type": "verb",
                "pattern": "يَفْعَل",
                "meaning": "تلا، نطق بالمكتوب",
                "source": "لسان العرب",
            },
        }

        # حفظ بيانات الاختبار في ملف مؤقت
        with open(self.test_data_path, "w", encoding="utf-8") as f:
            json.dump(self.test_data, f, ensure_ascii=False)

        # إنشاء كائن المعالج الهجين
        self.processor = HybridProcessor(lexicon_path=self.test_data_path)

    def tearDown(self):
        """تنظيف بيئة الاختبار بعد كل اختبار."""
        # حذف ملف البيانات المؤقت
        if os.path.exists(self.test_data_path):
            os.remove(self.test_data_path)

    def test_extract_root_from_lexicon(self):
        """اختبار استخراج جذر الكلمة من المعجم."""
        root, confidence, source = self.processor.extract_root("كتب")
        self.assertEqual(root, "كتب")
        self.assertEqual(confidence, 1.0)
        self.assertEqual(source, "lexicon")

        root, confidence, source = self.processor.extract_root("الكتاب")
        self.assertEqual(root, "كتب")
        self.assertEqual(confidence, 1.0)
        self.assertEqual(source, "lexicon")

    def test_extract_root_unknown_word(self):
        """اختبار استخراج جذر لكلمة غير موجودة في المعجم."""
        root, confidence, source = self.processor.extract_root("كلمة_غير_موجودة")
        self.assertEqual(root, "")
        self.assertEqual(confidence, 0.0)
        self.assertEqual(source, "unknown")

    def test_get_word_type(self):
        """اختبار تحديد نوع الكلمة من المعجم."""
        word_type, confidence, source = self.processor.get_word_type("كتب")
        self.assertEqual(word_type, "verb")
        self.assertEqual(confidence, 1.0)
        self.assertEqual(source, "lexicon")

        word_type, confidence, source = self.processor.get_word_type("الكتاب")
        self.assertEqual(word_type, "noun")
        self.assertEqual(confidence, 1.0)
        self.assertEqual(source, "lexicon")

    def test_process_word_found_in_lexicon(self):
        """اختبار معالجة كلمة موجودة في المعجم."""
        result = self.processor.process_word("كتب")

        self.assertEqual(result["word"], "كتب")
        self.assertEqual(result["root"]["value"], "كتب")
        self.assertEqual(result["root"]["confidence"], 1.0)
        self.assertEqual(result["root"]["source"], "lexicon")
        self.assertEqual(result["type"]["value"], "verb")
        self.assertEqual(result["type"]["confidence"], 1.0)
        self.assertEqual(result["type"]["source"], "lexicon")
        self.assertEqual(result["pattern"]["value"], "فَعَلَ")
        self.assertEqual(result["pattern"]["confidence"], 1.0)
        self.assertEqual(result["pattern"]["source"], "lexicon")
        self.assertEqual(result["meaning"]["value"], "كتب، خط بالقلم")

    def test_process_word_not_found(self):
        """اختبار معالجة كلمة غير موجودة في المعجم."""
        result = self.processor.process_word("كلمة_غير_موجودة")

        self.assertEqual(result["word"], "كلمة_غير_موجودة")
        self.assertEqual(result["root"]["value"], "")
        self.assertEqual(result["root"]["confidence"], 0.0)
        self.assertEqual(result["root"]["source"], "unknown")
        self.assertEqual(result["type"]["value"], "")
        self.assertEqual(result["type"]["confidence"], 0.0)
        self.assertEqual(result["type"]["source"], "unknown")

    def test_verify_extraction(self):
        """اختبار التحقق من صحة استخراج جذر كلمة."""
        # كلمة موجودة في المعجم وجذرها صحيح
        result = self.processor.verify_extraction("كتب", "كتب")
        self.assertTrue(result["is_correct"])
        self.assertEqual(result["confidence"], 1.0)
        self.assertEqual(result["source"], "lexicon")

        # كلمة موجودة في المعجم ولكن الجذر المتوقع خاطئ
        result = self.processor.verify_extraction("كتب", "قرأ")
        self.assertFalse(result["is_correct"])
        self.assertEqual(result["confidence"], 1.0)
        self.assertEqual(result["source"], "lexicon")

        # كلمة غير موجودة في المعجم
        result = self.processor.verify_extraction("كلمة_غير_موجودة", "كتب")
        self.assertFalse(result["is_correct"])
        self.assertEqual(result["confidence"], 0.0)
        self.assertEqual(result["source"], "unknown")


if __name__ == "__main__":
    unittest.main()
