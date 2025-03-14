#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
مثال توضيحي لاستخدام واجهة توسيع المعجم
=======================================

هذا المثال يوضح كيفية استخدام واجهة توسيع المعجم برمجياً.
"""

import os
import sys
import json
import tempfile
from pathlib import Path

# إضافة المسار إلى PYTHONPATH للوصول إلى الوحدات
current_path = Path(os.path.dirname(os.path.abspath(__file__)))
root_path = current_path.parent
sys.path.append(str(root_path))

from core.lexicon.quranic_lexicon import QuranicLexicon
from core.lexicon.hybrid_processor import HybridProcessor
from core.nlp.root_extraction import ArabicRootExtractor
from core.nlp.morphology import ArabicMorphologyAnalyzer
from core.nlp.diacritics import DiacriticsProcessor


def create_sample_words_file():
    """إنشاء ملف مؤقت يحتوي على كلمات للمعالجة"""
    words = ["مدرسة", "طالب", "كتاب", "قلم", "حاسوب"]

    temp_file = tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", delete=False, suffix=".txt")
    for word in words:
        temp_file.write(word + "\n")
    temp_file.close()

    return temp_file.name


def process_words_automatically(lexicon_path, words_file):
    """معالجة الكلمات آلياً وإضافتها إلى المعجم"""
    # تهيئة الخوارزميات
    root_extractor = ArabicRootExtractor()
    morphology_analyzer = ArabicMorphologyAnalyzer()
    diacritics_processor = DiacriticsProcessor()

    # تهيئة المعالج الهجين
    processor = HybridProcessor(
        lexicon_path=lexicon_path,
        root_extractor=root_extractor,
        morphology_analyzer=morphology_analyzer,
    )

    # قراءة الكلمات من الملف
    with open(words_file, "r", encoding="utf-8") as f:
        words = [line.strip() for line in f if line.strip()]

    print(f"معالجة {len(words)} كلمة...")

    # معالجة كل كلمة وإضافتها إلى المعجم
    for word in words:
        # تجاهل الكلمات الموجودة بالفعل في المعجم
        if word in processor.lexicon.words:
            print(f"الكلمة '{word}' موجودة بالفعل في المعجم.")
            continue

        # معالجة الكلمة باستخدام المعالج الهجين
        result = processor.process_word(word)

        # تحقق من وجود جذر للكلمة
        if result["root"]["value"] != "":
            # إضافة معنى افتراضي للكلمة
            meaning = f"معنى كلمة {word}"

            # إعداد معلومات الكلمة
            word_info = {
                "root": result["root"]["value"],
                "type": result["type"]["value"],
                "pattern": result["pattern"]["value"],
                "meaning": meaning,
            }

            # إضافة الكلمة إلى المعجم
            success = processor.add_to_lexicon(word, word_info)

            if success:
                print(f"تمت إضافة الكلمة '{word}' إلى المعجم:")
                print(f"  الجذر: {result['root']['value']}")
                print(f"  النوع: {result['type']['value']}")
                print(f"  الوزن: {result['pattern']['value']}")
                print(f"  المعنى: {meaning}")
                print(f"  درجة الثقة: {result['root']['confidence']:.2f}")
                print("-" * 40)
            else:
                print(f"فشل في إضافة الكلمة '{word}' إلى المعجم.")
        else:
            print(f"لم يتم التعرف على الكلمة '{word}' بشكل صحيح.")

    # حفظ المعجم الموسع
    temp_output = tempfile.NamedTemporaryFile(delete=False, suffix=".json").name
    processor.save_lexicon(temp_output)

    print(f"تم حفظ المعجم الموسع في: {temp_output}")
    return temp_output


def show_lexicon_stats(lexicon_path):
    """عرض إحصائيات المعجم"""
    lexicon = QuranicLexicon(lexicon_path)

    word_count = len(lexicon.words)

    # تصنيف الكلمات حسب النوع
    types = {}
    for word, info in lexicon.words.items():
        word_type = info.get("type", "غير معروف")
        types[word_type] = types.get(word_type, 0) + 1

    print("\n=== إحصائيات المعجم ===")
    print(f"عدد الكلمات الإجمالي: {word_count}")
    print("\nتوزيع أنواع الكلمات:")
    for word_type, count in types.items():
        print(f"  {word_type}: {count} ({count / word_count * 100:.1f}%)")


def main():
    """الدالة الرئيسية للمثال"""
    # مسار ملف المعجم
    lexicon_path = os.path.join(root_path, "data", "quran_lexicon_sample.json")

    # التحقق من وجود ملف المعجم
    if not os.path.exists(lexicon_path):
        print(f"خطأ: ملف المعجم غير موجود في المسار: {lexicon_path}")
        return

    print("=== مثال توضيحي لاستخدام واجهة توسيع المعجم ===")

    # عرض إحصائيات المعجم قبل التوسيع
    print("\n>> إحصائيات المعجم قبل التوسيع:")
    show_lexicon_stats(lexicon_path)

    # إنشاء ملف مؤقت يحتوي على كلمات للمعالجة
    words_file = create_sample_words_file()
    print(f"\n>> تم إنشاء ملف الكلمات في: {words_file}")

    # معالجة الكلمات وإضافتها إلى المعجم
    print("\n>> معالجة الكلمات وإضافتها إلى المعجم:")
    expanded_lexicon = process_words_automatically(lexicon_path, words_file)

    # عرض إحصائيات المعجم بعد التوسيع
    print("\n>> إحصائيات المعجم بعد التوسيع:")
    show_lexicon_stats(expanded_lexicon)

    # تنظيف الملفات المؤقتة
    os.unlink(words_file)
    print(f"\n>> تم حذف ملف الكلمات المؤقت: {words_file}")

    print("\n=== انتهى المثال التوضيحي ===")


if __name__ == "__main__":
    main()
