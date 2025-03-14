#!/usr/bin/env python3
"""
مثال لاستخدام المعالج الهجين بعد دمج الخوارزميات.
يوضح كيفية معالجة الكلمات القرآنية والكلمات غير القرآنية باستخدام النظام الهجين.
"""

import os
import sys
from pathlib import Path
import json

# إضافة مسار المشروع إلى متغير المسار
sys.path.append(str(Path(__file__).parent.parent))

from core.lexicon.hybrid_processor import HybridProcessor
from core.nlp.root_extraction import ArabicRootExtractor
from core.nlp.morphology import ArabicMorphologyAnalyzer
from core.nlp.diacritics import DiacriticsProcessor


def print_word_processing_result(result):
    """طباعة نتيجة معالجة كلمة بتنسيق جيد."""
    print(f"\n📝 نتيجة معالجة الكلمة: '{result['word']}'")

    # طباعة معلومات الجذر
    root = result["root"]
    print(f"  🔍 الجذر: {root['value'] or 'غير معروف'}")
    print(f"     - درجة الثقة: {root['confidence']:.2f}")
    print(f"     - المصدر: {root['source']}")

    # طباعة معلومات نوع الكلمة
    word_type = result["type"]
    print(f"  🔍 النوع: {word_type['value'] or 'غير معروف'}")
    print(f"     - درجة الثقة: {word_type['confidence']:.2f}")
    print(f"     - المصدر: {word_type['source']}")

    # طباعة معلومات الوزن الصرفي
    pattern = result["pattern"]
    print(f"  🔍 الوزن: {pattern['value'] or 'غير معروف'}")
    print(f"     - درجة الثقة: {pattern['confidence']:.2f}")
    print(f"     - المصدر: {pattern['source']}")

    # طباعة المعنى إذا كان متوفرًا
    if "meaning" in result:
        print(f"  🔍 المعنى: {result['meaning']['value']}")
        print(f"     - المصدر: {result['meaning']['source']}")

    # طباعة معلومات إضافية إذا كانت متوفرة
    if "additional_info" in result:
        print(f"  🔍 معلومات إضافية:")
        for key, info in result["additional_info"].items():
            print(f"     - {key}: {info['value']}")
            print(f"       المصدر: {info['source']}")


def print_verification_result(result):
    """طباعة نتيجة التحقق من صحة استخراج جذر كلمة."""
    print(f"\n🔍 نتيجة التحقق من الكلمة: '{result['word']}'")
    print(f"  - الجذر المتوقع: {result['expected_root']}")
    print(f"  - الجذر المستخرج: {result['extracted_root'] or 'غير معروف'}")
    print(f"  - درجة الثقة: {result['confidence']:.2f}")
    print(f"  - المصدر: {result['source']}")

    if result["is_correct"]:
        print("  ✅ النتيجة: صحيحة")
    else:
        print("  ❌ النتيجة: خاطئة")


def print_expansion_suggestion(suggestion, word):
    """طباعة اقتراح توسيع المعجم."""
    print(f"\n🔍 اقتراح إضافة كلمة: '{word}'")
    print(f"  - الجذر المقترح: {suggestion['root']}")
    print(f"  - النوع المقترح: {suggestion['type']}")
    print(f"  - الوزن المقترح: {suggestion.get('pattern', 'غير معروف')}")
    print(f"  - درجة الثقة: {suggestion['confidence']:.2f}")
    print(f"  - المصدر: {suggestion['source']}")


def process_quranic_words(processor):
    """معالجة كلمات قرآنية من المعجم."""
    print("\n=== معالجة كلمات قرآنية ===")
    quranic_words = ["الله", "الرحمن", "نعبد", "المستقيم"]

    for word in quranic_words:
        result = processor.process_word(word)
        print_word_processing_result(result)


def process_non_quranic_words(processor):
    """معالجة كلمات غير قرآنية باستخدام الخوارزميات."""
    print("\n=== معالجة كلمات غير قرآنية ===")
    non_quranic_words = ["مكتبة", "استغفر", "يستغفرون", "دراسة", "يكتبون"]

    for word in non_quranic_words:
        result = processor.process_word(word)
        print_word_processing_result(result)


def verify_roots(processor):
    """التحقق من صحة استخراج الجذور."""
    print("\n=== التحقق من صحة استخراج الجذور ===")
    verification_tests = [
        {"word": "الله", "expected_root": "أله"},
        {"word": "الرحمن", "expected_root": "رحم"},
        {"word": "مكتبة", "expected_root": "كتب"},
        {"word": "استغفر", "expected_root": "غفر"},
    ]

    for test in verification_tests:
        result = processor.verify_extraction(test["word"], test["expected_root"])
        print_verification_result(result)


def expand_lexicon(processor):
    """توسيع المعجم باستخدام الخوارزميات."""
    print("\n=== توسيع المعجم باستخدام الخوارزميات ===")
    new_words = ["مكتبة", "استغفر", "مدرسة", "دراسة", "كتابة", "قارئ", "مقروء"]

    result = processor.expand_lexicon(new_words)

    print(f"عدد الكلمات المعالجة: {result['total_words']}")
    print(f"عدد الاقتراحات: {result['suggestions_count']}")

    if result["suggestions_count"] > 0:
        print("\n🔍 اقتراحات توسيع المعجم:")
        for word, suggestion in result["suggestions"].items():
            print_expansion_suggestion(suggestion, word)


def add_words_to_lexicon(processor):
    """إضافة كلمات جديدة إلى المعجم."""
    print("\n=== إضافة كلمات جديدة إلى المعجم ===")

    # إضافة كلمة مع معلوماتها
    word_info = {
        "root": "كتب",
        "type": "noun",
        "pattern": "مَفْعَلَة",
        "meaning": "مكان لحفظ الكتب والقراءة فيها",
        "source": "المعجم الوسيط",
    }

    success = processor.add_to_lexicon("مكتبة", word_info, is_verified=True)
    if success:
        print(f"✅ تمت إضافة كلمة 'مكتبة' بنجاح.")
    else:
        print(f"❌ فشلت عملية إضافة كلمة 'مكتبة'.")

    # التحقق من إضافة الكلمة بنجاح
    result = processor.process_word("مكتبة")
    print_word_processing_result(result)


def main():
    """الدالة الرئيسية للمثال."""
    # مسار ملف المعجم
    lexicon_path = Path(__file__).parent.parent / "data" / "quran_lexicon_sample.json"

    # التحقق من وجود ملف المعجم
    if not os.path.exists(lexicon_path):
        print(f"❌ ملف المعجم غير موجود في المسار: {lexicon_path}")
        return

    # تهيئة الخوارزميات المطلوبة
    root_extractor = ArabicRootExtractor()
    diacritics_processor = DiacriticsProcessor()
    morphology_analyzer = ArabicMorphologyAnalyzer(
        diacritics_processor=diacritics_processor, root_extractor=root_extractor
    )

    # تهيئة المعالج الهجين
    print(f"🔄 جاري تهيئة المعالج الهجين باستخدام المعجم من: {lexicon_path}")
    processor = HybridProcessor(
        lexicon_path=lexicon_path,
        use_algorithms=True,
        morphology_analyzer=morphology_analyzer,
        root_extractor=root_extractor,
    )

    # معالجة كلمات قرآنية من المعجم
    process_quranic_words(processor)

    # معالجة كلمات غير قرآنية باستخدام الخوارزميات
    process_non_quranic_words(processor)

    # التحقق من صحة استخراج الجذور
    verify_roots(processor)

    # إضافة كلمات جديدة إلى المعجم
    add_words_to_lexicon(processor)

    # توسيع المعجم باستخدام الخوارزميات
    expand_lexicon(processor)

    # حفظ المعجم بعد التعديل
    temp_output_path = Path(__file__).parent.parent / "data" / "temp_extended_lexicon.json"
    processor.save_lexicon(temp_output_path)
    print(f"\n✅ تم حفظ المعجم بعد التعديل في: {temp_output_path}")

    print("\n✅ تم تنفيذ المثال بنجاح.")


if __name__ == "__main__":
    main()
