#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
سكربت توسيع المعجم
=================

سكربت يدمج بين أداة جمع الكلمات وواجهة توسيع المعجم لتسهيل عملية
توسيع المعجم ببيانات كبيرة (500-1000 كلمة) في خطوة واحدة.
"""

import os
import sys
import json
import time
import datetime
import argparse
from pathlib import Path

# إضافة المسار إلى PYTHONPATH للوصول إلى الوحدات
current_path = Path(os.path.dirname(os.path.abspath(__file__)))
root_path = current_path.parent
sys.path.append(str(root_path))

from tools.word_collector import WordCollector
from tools.lexicon_expansion_interface import LexiconExpansionInterface
from core.lexicon.quranic_lexicon import QuranicLexicon


def expand_lexicon(
    lexicon_path: str,
    data_sources: dict,
    output_path: str = None,
    auto_approve_threshold: float = 0.9,
    batch_size: int = 100,
    word_limit: int = 1000,
    min_word_length: int = 3,
    generate_report: bool = True,
    use_parallel: bool = True,
):
    """
    توسيع المعجم باستخدام مصادر بيانات متعددة

    المعاملات:
        lexicon_path: مسار ملف المعجم الأصلي
        data_sources: قاموس يحتوي على مصادر البيانات
        output_path: مسار ملف المعجم الموسع (اختياري)
        auto_approve_threshold: عتبة القبول التلقائي للكلمات
        batch_size: حجم دفعة معالجة الكلمات
        word_limit: الحد الأقصى لعدد الكلمات المعالجة
        min_word_length: الحد الأدنى لطول الكلمة
        generate_report: توليد تقرير عن عملية التوسيع
        use_parallel: استخدام المعالجة المتوازية
    """
    start_time = time.time()

    # إعداد مسار المعجم الموسع
    if not output_path:
        output_dir = os.path.dirname(lexicon_path)
        filename = os.path.basename(lexicon_path)
        base_name, ext = os.path.splitext(filename)
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = os.path.join(output_dir, f"{base_name}_expanded_{timestamp}{ext}")

    print("\n=== بدء عملية توسيع المعجم ===")
    print(f"المعجم الأصلي: {lexicon_path}")
    print(f"المعجم الموسع: {output_path}")

    # طباعة إحصائيات المعجم الأصلي
    original_lexicon = QuranicLexicon(lexicon_path)
    original_word_count = len(original_lexicon.words)
    print(f"\n>> إحصائيات المعجم الأصلي: {original_word_count} كلمة")

    # جمع الكلمات من المصادر المحددة
    temp_words_file = os.path.join(
        os.path.dirname(output_path),
        f"temp_words_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
    )

    print("\n=== جمع الكلمات من المصادر المحددة ===")
    collector = WordCollector()

    # تحميل القائمة السوداء إذا تم تحديدها
    if "blacklist" in data_sources and os.path.exists(data_sources["blacklist"]):
        collector.load_blacklist(data_sources["blacklist"])

    # جمع الكلمات من المصادر المختلفة
    if "quran" in data_sources and os.path.exists(data_sources["quran"]):
        collector.collect_from_quran(data_sources["quran"], min_word_length)

    if "web" in data_sources and data_sources["web"]:
        collector.collect_from_web(data_sources["web"], min_word_length)

    if "dictionary" in data_sources and os.path.exists(data_sources["dictionary"]):
        collector.collect_from_dictionary(data_sources["dictionary"])

    if "text_files" in data_sources and data_sources["text_files"]:
        for text_file in data_sources["text_files"]:
            if os.path.exists(text_file):
                collector.collect_from_text_file(text_file, min_word_length)

    if "custom" in data_sources and os.path.exists(data_sources["custom"]):
        with open(data_sources["custom"], "r", encoding="utf-8") as f:
            custom_words = [line.strip() for line in f if line.strip()]
        collector.add_custom_words(custom_words)

    # طباعة إحصائيات عملية الجمع
    collection_stats = collector.get_statistics()
    print("\n>> إحصائيات عملية جمع الكلمات:")
    print(f"إجمالي الكلمات المجمعة: {collection_stats['total']}")

    # استبعاد الكلمات الموجودة بالفعل في المعجم
    existing_words = set(original_lexicon.words.keys())
    new_words = collector.collected_words - existing_words

    print(f"\n>> تم جمع {len(new_words)} كلمة جديدة غير موجودة في المعجم.")

    # تطبيق الحد الأقصى لعدد الكلمات
    if word_limit and word_limit > 0 and len(new_words) > word_limit:
        print(f"تقليص عدد الكلمات إلى الحد الأقصى: {word_limit}")
        word_list = list(new_words)
        word_list.sort()  # ترتيب الكلمات أبجديًا
        word_list = word_list[:word_limit]
    else:
        word_list = list(new_words)
        word_list.sort()  # ترتيب الكلمات أبجديًا

    # حفظ الكلمات في ملف مؤقت
    collector.save_collected_words(temp_words_file, len(word_list), False)

    # توسيع المعجم باستخدام واجهة توسيع المعجم
    print("\n=== معالجة الكلمات وإضافتها إلى المعجم ===")
    expansion_interface = LexiconExpansionInterface(lexicon_path, output_path)

    # تعديل إعدادات المعالجة
    expansion_interface.auto_save_interval = batch_size
    expansion_interface.max_threads = 4 if use_parallel else 1

    # معالجة الكلمات على دفعات
    expansion_stats = expansion_interface.process_words_in_batches(
        temp_words_file,
        batch_size=batch_size,
        auto_approve_threshold=auto_approve_threshold,
        use_parallel=use_parallel,
    )

    # حفظ المعجم النهائي
    print("\n=== حفظ المعجم الموسع ===")
    expansion_interface.save_lexicon()

    # طباعة إحصائيات المعجم الموسع
    expanded_lexicon = QuranicLexicon(output_path)
    expanded_word_count = len(expanded_lexicon.words)

    print(f"\n>> إحصائيات المعجم الموسع: {expanded_word_count} كلمة")
    print(f"عدد الكلمات المضافة: {expanded_word_count - original_word_count}")

    # طباعة إحصائيات عملية التوسيع
    end_time = time.time()
    total_time = end_time - start_time

    print("\n>> إحصائيات عملية التوسيع:")
    print(f"إجمالي الوقت المستغرق: {total_time:.2f} ثانية")
    print(f"عدد الكلمات المعالجة: {expansion_stats['processed_words']}")
    print(f"عدد الكلمات المقبولة تلقائيًا: {expansion_stats['auto_approved']}")
    print(f"عدد الكلمات التي تحتاج إلى مراجعة: {expansion_stats['review_required']}")

    # توليد تقرير عن عملية التوسيع
    if generate_report:
        report_path = f"{os.path.splitext(output_path)[0]}_report.md"
        print(f"\n=== توليد تقرير عن عملية التوسيع: {report_path} ===")
        expansion_interface.generate_report(report_path)

    # تنظيف الملفات المؤقتة
    if os.path.exists(temp_words_file):
        os.unlink(temp_words_file)
        print(f"\n>> تم حذف الملف المؤقت: {temp_words_file}")

    print("\n=== اكتملت عملية توسيع المعجم بنجاح ===")

    return {
        "original_path": lexicon_path,
        "expanded_path": output_path,
        "original_count": original_word_count,
        "expanded_count": expanded_word_count,
        "added_count": expanded_word_count - original_word_count,
        "processed_count": expansion_stats["processed_words"],
        "auto_approved": expansion_stats["auto_approved"],
        "review_required": expansion_stats["review_required"],
        "total_time": total_time,
    }


def main():
    """الدالة الرئيسية للسكربت"""
    parser = argparse.ArgumentParser(description="سكربت توسيع المعجم")

    # إضافة خيارات سطر الأوامر
    parser.add_argument("--lexicon", required=True, help="مسار ملف المعجم الأصلي")
    parser.add_argument("--output", help="مسار ملف المعجم الموسع")
    parser.add_argument("--quran", help="مسار ملف نص القرآن لجمع الكلمات منه")
    parser.add_argument("--web", nargs="+", help="قائمة عناوين مواقع الويب لجمع الكلمات منها")
    parser.add_argument("--dictionary", help="مسار ملف قاموس لجمع الكلمات منه")
    parser.add_argument("--text", nargs="+", help="قائمة مسارات ملفات نصية لجمع الكلمات منها")
    parser.add_argument("--custom", help="مسار ملف يحتوي على كلمات مخصصة")
    parser.add_argument("--blacklist", help="مسار ملف القائمة السوداء")
    parser.add_argument("--threshold", type=float, default=0.9, help="عتبة القبول التلقائي للكلمات")
    parser.add_argument("--batch-size", type=int, default=100, help="حجم دفعة معالجة الكلمات")
    parser.add_argument("--limit", type=int, default=1000, help="الحد الأقصى لعدد الكلمات المعالجة")
    parser.add_argument("--min-length", type=int, default=3, help="الحد الأدنى لطول الكلمة")
    parser.add_argument("--no-report", action="store_true", help="عدم توليد تقرير عن عملية التوسيع")
    parser.add_argument("--no-parallel", action="store_true", help="عدم استخدام المعالجة المتوازية")

    args = parser.parse_args()

    # التحقق من وجود ملف المعجم
    if not os.path.exists(args.lexicon):
        print(f"خطأ: ملف المعجم غير موجود في المسار: {args.lexicon}")
        return 1

    # إعداد مصادر البيانات
    data_sources = {}

    if args.quran:
        data_sources["quran"] = args.quran

    if args.web:
        data_sources["web"] = args.web

    if args.dictionary:
        data_sources["dictionary"] = args.dictionary

    if args.text:
        data_sources["text_files"] = args.text

    if args.custom:
        data_sources["custom"] = args.custom

    if args.blacklist:
        data_sources["blacklist"] = args.blacklist

    # التحقق من وجود مصدر بيانات واحد على الأقل
    if not data_sources:
        print("خطأ: يجب تحديد مصدر بيانات واحد على الأقل.")
        return 1

    # توسيع المعجم
    expand_lexicon(
        lexicon_path=args.lexicon,
        data_sources=data_sources,
        output_path=args.output,
        auto_approve_threshold=args.threshold,
        batch_size=args.batch_size,
        word_limit=args.limit,
        min_word_length=args.min_length,
        generate_report=not args.no_report,
        use_parallel=not args.no_parallel,
    )

    return 0


if __name__ == "__main__":
    sys.exit(main())
