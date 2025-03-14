#!/usr/bin/env python3
"""
مثال لاستخدام المعالج الهجين الذي يدمج بين المعجم والخوارزميات.
"""

import os
import sys
from pathlib import Path
import json

# إضافة مسار المشروع إلى متغير المسار
sys.path.append(str(Path(__file__).parent.parent))

from core.lexicon.hybrid_processor import HybridProcessor


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


def main():
    """الدالة الرئيسية للمثال."""
    # مسار ملف المعجم
    lexicon_path = Path(__file__).parent.parent / "data" / "quran_lexicon_sample.json"

    # التحقق من وجود ملف المعجم
    if not os.path.exists(lexicon_path):
        print(f"❌ ملف المعجم غير موجود في المسار: {lexicon_path}")
        return

    # تهيئة المعالج الهجين
    print(f"🔄 جاري تهيئة المعالج الهجين باستخدام المعجم من: {lexicon_path}")
    processor = HybridProcessor(lexicon_path=lexicon_path)

    # قائمة الكلمات للاختبار
    test_words = ["الله", "الرحمن", "نعبد", "المستقيم", "كلمة_غير_موجودة"]

    print("\n=== معالجة الكلمات ===")
    for word in test_words:
        # معالجة الكلمة واستخراج جميع المعلومات
        result = processor.process_word(word)
        print_word_processing_result(result)

    print("\n=== التحقق من صحة استخراج الجذور ===")
    verification_tests = [
        {"word": "الله", "expected_root": "أله"},
        {"word": "الرحمن", "expected_root": "رحم"},
        {"word": "الرحمن", "expected_root": "رحمن"},  # جذر خاطئ
        {"word": "كلمة_غير_موجودة", "expected_root": "كلم"},
    ]

    for test in verification_tests:
        # التحقق من صحة الجذر
        result = processor.verify_extraction(test["word"], test["expected_root"])
        print_verification_result(result)

    print("\n✅ تم تنفيذ المثال بنجاح.")


if __name__ == "__main__":
    main()
