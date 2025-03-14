import unittest
import json
import os
from pathlib import Path

# استيراد الفئة المستهدفة
from core.lexicon.quranic_lexicon import QuranicLexicon


class TestQuranicLexicon(unittest.TestCase):
    """اختبارات للتأكد من سلامة وفعالية نظام المعجم القرآني."""

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

        # إنشاء كائن المعجم
        self.lexicon = QuranicLexicon(data_path=self.test_data_path)

    def tearDown(self):
        """تنظيف بيئة الاختبار بعد كل اختبار."""
        # حذف ملف البيانات المؤقت
        if os.path.exists(self.test_data_path):
            os.remove(self.test_data_path)

    def test_lexicon_initialization(self):
        """اختبار تهيئة المعجم وتحميل البيانات بشكل صحيح."""
        self.assertEqual(len(self.lexicon.words), 3)
        self.assertTrue("كتب" in self.lexicon.words)
        self.assertTrue("الكتاب" in self.lexicon.words)
        self.assertTrue("يقرأ" in self.lexicon.words)

    def test_get_root(self):
        """اختبار استخراج جذر الكلمة من المعجم."""
        self.assertEqual(self.lexicon.get_root("كتب"), "كتب")
        self.assertEqual(self.lexicon.get_root("الكتاب"), "كتب")
        self.assertEqual(self.lexicon.get_root("يقرأ"), "قرأ")
        self.assertIsNone(self.lexicon.get_root("غير_موجود"))

    def test_get_word_type(self):
        """اختبار استخراج نوع الكلمة من المعجم."""
        self.assertEqual(self.lexicon.get_word_type("كتب"), "verb")
        self.assertEqual(self.lexicon.get_word_type("الكتاب"), "noun")
        self.assertEqual(self.lexicon.get_word_type("يقرأ"), "verb")
        self.assertIsNone(self.lexicon.get_word_type("غير_موجود"))

    def test_get_pattern(self):
        """اختبار استخراج الوزن الصرفي للكلمة من المعجم."""
        self.assertEqual(self.lexicon.get_pattern("كتب"), "فَعَلَ")
        self.assertEqual(self.lexicon.get_pattern("الكتاب"), "فِعَال")
        self.assertEqual(self.lexicon.get_pattern("يقرأ"), "يَفْعَل")
        self.assertIsNone(self.lexicon.get_pattern("غير_موجود"))

    def test_get_all_info(self):
        """اختبار استخراج جميع معلومات الكلمة من المعجم."""
        info = self.lexicon.get_all_info("كتب")
        self.assertEqual(info["root"], "كتب")
        self.assertEqual(info["type"], "verb")
        self.assertEqual(info["pattern"], "فَعَلَ")
        self.assertEqual(info["source"], "لسان العرب")

        self.assertIsNone(self.lexicon.get_all_info("غير_موجود"))

    def test_add_word(self):
        """اختبار إضافة كلمة جديدة إلى المعجم."""
        word_info = {
            "root": "علم",
            "type": "verb",
            "pattern": "فَعِلَ",
            "meaning": "أدرك حقيقة الشيء",
            "source": "المعجم الوسيط",
        }
        self.lexicon.add_word("علم", word_info)

        # التحقق من إضافة الكلمة بنجاح
        self.assertTrue("علم" in self.lexicon.words)
        self.assertEqual(self.lexicon.get_root("علم"), "علم")
        self.assertEqual(self.lexicon.get_word_type("علم"), "verb")

    def test_save_and_load(self):
        """اختبار حفظ المعجم وإعادة تحميله."""
        # إضافة كلمة جديدة
        word_info = {
            "root": "علم",
            "type": "verb",
            "pattern": "فَعِلَ",
            "meaning": "أدرك حقيقة الشيء",
            "source": "المعجم الوسيط",
        }
        self.lexicon.add_word("علم", word_info)

        # حفظ المعجم
        save_path = Path("test_save_lexicon.json")
        self.lexicon.save(save_path)

        # إنشاء معجم جديد من الملف المحفوظ
        new_lexicon = QuranicLexicon(data_path=save_path)

        # التحقق من صحة البيانات المحفوظة
        self.assertEqual(len(new_lexicon.words), 4)  # 3 كلمات أصلية + 1 جديدة
        self.assertTrue("علم" in new_lexicon.words)
        self.assertEqual(new_lexicon.get_root("علم"), "علم")

        # تنظيف
        if os.path.exists(save_path):
            os.remove(save_path)

    def test_search_by_root(self):
        """اختبار البحث عن الكلمات بناءً على الجذر."""
        كلمات_كتب = self.lexicon.search_by_root("كتب")
        self.assertEqual(len(كلمات_كتب), 2)
        self.assertIn("كتب", كلمات_كتب)
        self.assertIn("الكتاب", كلمات_كتب)

        كلمات_قرأ = self.lexicon.search_by_root("قرأ")
        self.assertEqual(len(كلمات_قرأ), 1)
        self.assertIn("يقرأ", كلمات_قرأ)

    def test_verify_word_root(self):
        """اختبار التحقق من صحة جذر كلمة."""
        self.assertTrue(self.lexicon.verify_word_root("كتب", "كتب"))
        self.assertTrue(self.lexicon.verify_word_root("الكتاب", "كتب"))
        self.assertTrue(self.lexicon.verify_word_root("يقرأ", "قرأ"))
        self.assertFalse(self.lexicon.verify_word_root("كتب", "قرأ"))
        self.assertFalse(self.lexicon.verify_word_root("غير_موجود", "كتب"))

    def test_statistics(self):
        """اختبار الحصول على إحصائيات المعجم."""
        stats = self.lexicon.get_statistics()
        self.assertEqual(stats["total_words"], 3)
        self.assertEqual(stats["total_roots"], 2)
        self.assertEqual(stats["word_types"]["verb"], 2)
        self.assertEqual(stats["word_types"]["noun"], 1)


if __name__ == "__main__":
    unittest.main()
