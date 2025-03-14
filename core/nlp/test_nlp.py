#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
اختبار مكتبة معالجة اللغة العربية الطبيعية
"""

from core.nlp.root_extraction import ArabicRootExtractor
from core.nlp.diacritics import DiacriticsProcessor
from core.nlp.morphology import ArabicMorphologyAnalyzer


def test_diacritics():
    """اختبار معالج التشكيل"""
    processor = DiacriticsProcessor()

    # اختبار إزالة التشكيل
    text_with_diacritics = "بِسْمِ اللَّهِ الرَّحْمَنِ الرَّحِيمِ"
    text_without_diacritics = processor.remove_all_diacritics(text_with_diacritics)
    print(f"النص الأصلي: {text_with_diacritics}")
    print(f"النص بدون تشكيل: {text_without_diacritics}")

    # اختبار الإبقاء على الشدة فقط
    text_with_shadda_only = processor.remove_except_shadda(text_with_diacritics)
    print(f"النص مع الإبقاء على الشدة: {text_with_shadda_only}")


def test_root_extraction():
    """اختبار استخراج الجذور"""
    extractor = ArabicRootExtractor()

    # قائمة كلمات للاختبار
    words = [
        "كتاب",
        "مكتبة",
        "كاتب",
        "مكتوب",
        "يكتب",  # من جذر "كتب"
        "مدرسة",
        "مدرس",
        "دارس",
        "يدرس",
        "دروس",  # من جذر "درس"
        "استغفار",
        "يستغفر",
        "غفران",
        "مغفرة",
        "غافر",  # من جذر "غفر"
    ]

    print("اختبار استخراج الجذور:")
    for word in words:
        root = extractor.extract_root(word, algorithm="hybrid")
        print(f"الكلمة: {word} | الجذر: {root}")

    # اختبار تجميع الكلمات حسب الجذر
    grouped = extractor.group_by_root(words)
    print("\nتجميع الكلمات حسب الجذر:")
    for root, word_group in grouped.items():
        print(f"جذر: {root} | الكلمات: {', '.join(word_group)}")


def test_morphology():
    """اختبار التحليل الصرفي"""
    analyzer = ArabicMorphologyAnalyzer()

    # قائمة كلمات للاختبار
    words = [
        "الكتاب",
        "المكتبة",
        "كاتب",
        "يكتبون",
        "كتبت",
        "سيذهب",
        "ذهبوا",
        "اكتب",
        "من",
        "على",
        "في",
    ]

    print("اختبار التحليل الصرفي:")
    for word in words:
        analysis = analyzer.analyze_word(word)
        print(f"\nالكلمة: {word}")
        print(f"  الجذر: {analysis['جذر']}")
        print(f"  النوع: {analysis['نوع']}")
        print(f"  الوزن: {analysis['وزن']}")
        if analysis["سوابق"]:
            print(f"  السوابق: {', '.join(analysis['سوابق'])}")
        if analysis["لواحق"]:
            print(f"  اللواحق: {', '.join(analysis['لواحق'])}")
        if analysis["معلومات_إضافية"]:
            for key, value in analysis["معلومات_إضافية"].items():
                print(f"  {key}: {value}")


def test_quran_example():
    """اختبار على نص من القرآن الكريم"""
    verse = "إِنَّا أَنزَلْنَاهُ قُرْآنًا عَرَبِيًّا لَّعَلَّكُمْ تَعْقِلُونَ"

    print(f"\nاختبار على آية قرآنية: {verse}")

    # إزالة التشكيل
    processor = DiacriticsProcessor()
    normalized_verse = processor.remove_all_diacritics(verse)
    print(f"الآية بدون تشكيل: {normalized_verse}")

    # استخراج جذور الكلمات
    extractor = ArabicRootExtractor()
    roots = extractor.extract_roots_from_text(normalized_verse)
    print("\nجذور كلمات الآية:")
    for word, root in roots.items():
        print(f"  {word}: {root}")

    # التحليل الصرفي
    analyzer = ArabicMorphologyAnalyzer()
    analysis = analyzer.analyze_text(normalized_verse)
    print("\nالتحليل الصرفي للآية:")
    for word_analysis in analysis:
        word = word_analysis["الكلمة"]
        print(f"  {word}: {word_analysis['نوع']} (جذر: {word_analysis['جذر']})")


if __name__ == "__main__":
    print("=== اختبار مكتبة معالجة اللغة العربية الطبيعية ===\n")

    test_diacritics()
    print("\n" + "=" * 50 + "\n")

    test_root_extraction()
    print("\n" + "=" * 50 + "\n")

    test_morphology()
    print("\n" + "=" * 50 + "\n")

    test_quran_example()
    print("\n=== انتهى الاختبار ===")
