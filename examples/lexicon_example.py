#!/usr/bin/env python3
"""
مثال لاستخدام المعجم القرآني والحصول على معلومات الكلمات وإحصائيات المعجم.
"""

import os
import sys
from pathlib import Path
import json

# إضافة مسار المشروع إلى متغير المسار
sys.path.append(str(Path(__file__).parent.parent))

from core.lexicon.quranic_lexicon import QuranicLexicon


def print_word_info(lexicon, word):
    """طباعة معلومات كلمة محددة من المعجم."""
    info = lexicon.get_all_info(word)
    if info:
        print(f"\n📝 معلومات الكلمة: '{word}':")
        print(f"  - الجذر: {info.get('root', 'غير معروف')}")
        print(f"  - النوع: {info.get('type', 'غير معروف')}")
        print(f"  - الوزن: {info.get('pattern', 'غير معروف')}")
        print(f"  - المعنى: {info.get('meaning', 'غير معروف')}")
        print(f"  - المصدر: {info.get('source', 'غير معروف')}")
    else:
        print(f"\n❌ الكلمة '{word}' غير موجودة في المعجم!")


def print_root_words(lexicon, root):
    """طباعة جميع الكلمات التي تنتمي إلى جذر معين."""
    words = lexicon.search_by_root(root)
    if words:
        print(f"\n🔍 الكلمات المشتقة من الجذر '{root}':")
        for i, word in enumerate(words, 1):
            print(f"  {i}. {word}")
    else:
        print(f"\n❌ لا توجد كلمات للجذر '{root}' في المعجم!")


def print_statistics(lexicon):
    """طباعة إحصائيات عامة عن المعجم."""
    stats = lexicon.get_statistics()

    print("\n📊 إحصائيات المعجم:")
    print(f"  - عدد الكلمات: {stats['total_words']}")
    print(f"  - عدد الجذور: {stats['total_roots']}")

    print("\n📊 توزيع الكلمات حسب النوع:")
    for word_type, count in stats["word_types"].items():
        print(f"  - {word_type}: {count}")

    print(f"\n📊 متوسط عدد الكلمات لكل جذر: {stats['avg_words_per_root']:.2f}")


def main():
    """الدالة الرئيسية للمثال."""
    # مسار ملف المعجم
    lexicon_path = Path(__file__).parent.parent / "data" / "quran_lexicon_sample.json"

    # التحقق من وجود ملف المعجم
    if not os.path.exists(lexicon_path):
        print(f"❌ ملف المعجم غير موجود في المسار: {lexicon_path}")
        return

    # تهيئة المعجم
    print(f"🔄 جاري تحميل المعجم من: {lexicon_path}")
    lexicon = QuranicLexicon(data_path=lexicon_path)

    # طباعة معلومات عامة
    print(f"✅ تم تحميل المعجم بنجاح. عدد الكلمات: {lexicon.get_word_count()}")

    # طباعة معلومات بعض الكلمات
    print_word_info(lexicon, "الله")
    print_word_info(lexicon, "الرحمن")
    print_word_info(lexicon, "نعبد")
    print_word_info(lexicon, "المستقيم")

    # طباعة الكلمات المشتقة من جذور محددة
    print_root_words(lexicon, "رحم")
    print_root_words(lexicon, "عبد")
    print_root_words(lexicon, "قوم")

    # طباعة إحصائيات المعجم
    print_statistics(lexicon)

    print("\n✅ تم تنفيذ المثال بنجاح.")


if __name__ == "__main__":
    main()
