#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
سكربت تنفيذ توسيع المعجم - المرحلة الثالثة

هذا السكربت يقوم بتنفيذ عملية توسيع المعجم تلقائياً للوصول إلى هدف 1000 كلمة
باستخدام أدوات جمع الكلمات وواجهة توسيع المعجم.
"""

import os
import sys
import json
import time
import logging
import argparse
from datetime import datetime
from pathlib import Path

# إضافة المسار إلى PYTHONPATH للوصول إلى الوحدات
current_path = Path(os.path.dirname(os.path.abspath(__file__)))
root_path = current_path.parent
sys.path.append(str(root_path))

from tools.word_collector import WordCollector
from tools.lexicon_expansion_interface import LexiconExpansionInterface
from tools.expand_lexicon import expand_lexicon
from core.nlp.diacritics import DiacriticsProcessor

# إعداد التسجيل
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(os.path.join(root_path, "logs", "lexicon_expansion.log")),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger("run_lexicon_expansion")


def ensure_directory_exists(path):
    """التأكد من وجود المجلد، وإنشائه إذا لم يكن موجوداً"""
    os.makedirs(path, exist_ok=True)


def count_words_in_lexicon(lexicon_path):
    """حساب عدد الكلمات في المعجم"""
    try:
        with open(lexicon_path, "r", encoding="utf-8") as f:
            lexicon_data = json.load(f)
        return len(lexicon_data)
    except Exception as e:
        logger.error(f"خطأ في قراءة المعجم {lexicon_path}: {e}")
        return 0


def run_expansion_pipeline(
    lexicon_path,
    target_word_count=1000,
    output_path=None,
    sources=None,
    auto_approve_threshold=0.85,
    batch_size=100,
    use_parallel=True,
    word_min_length=3,
    generate_reports=True,
):
    """
    تنفيذ خط أنابيب توسيع المعجم الكامل

    المعلمات:
        lexicon_path: مسار ملف المعجم الأصلي
        target_word_count: عدد الكلمات المستهدف في المعجم النهائي
        output_path: مسار حفظ المعجم الموسع
        sources: مصادر البيانات لجمع الكلمات
        auto_approve_threshold: عتبة الثقة للقبول التلقائي
        batch_size: حجم دفعة معالجة الكلمات
        use_parallel: استخدام المعالجة المتوازية
        word_min_length: الحد الأدنى لطول الكلمة
        generate_reports: توليد تقارير مفصلة
    """
    # التأكد من إعداد المسارات
    if output_path is None:
        output_dir = os.path.dirname(lexicon_path)
        output_filename = f"extended_lexicon_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        output_path = os.path.join(output_dir, output_filename)

    # إنشاء المجلدات اللازمة
    temp_dir = os.path.join(root_path, "temp")
    ensure_directory_exists(temp_dir)
    ensure_directory_exists(os.path.join(root_path, "logs"))
    ensure_directory_exists(os.path.join(root_path, "reports"))

    # إعداد مصادر البيانات الافتراضية إذا لم يتم توفيرها
    if sources is None:
        quran_path = os.path.join(root_path, "data", "quran_text.txt")
        sources = {
            "quran": quran_path,
            "web": [
                "https://ar.wikipedia.org/wiki/اللغة_العربية",
                "https://ar.wikipedia.org/wiki/النحو_العربي",
                "https://ar.wikipedia.org/wiki/صرف_(لغة)",
                "https://islamway.net/ar",
                "https://www.aljazeera.net/",
                "https://www.bbc.com/arabic",
            ],
            "dictionaries": [os.path.join(root_path, "data", "arabic_dictionary.txt")],
        }

    # قياس عدد الكلمات الحالي في المعجم
    current_word_count = count_words_in_lexicon(lexicon_path)
    logger.info(f"عدد الكلمات الحالي في المعجم: {current_word_count}")
    logger.info(f"عدد الكلمات المستهدف: {target_word_count}")

    # حساب عدد الكلمات المطلوب إضافتها
    words_to_add = max(0, target_word_count - current_word_count)
    logger.info(f"عدد الكلمات المطلوب إضافتها: {words_to_add}")

    if words_to_add == 0:
        logger.info("المعجم وصل بالفعل إلى العدد المستهدف من الكلمات.")
        return output_path

    # إنشاء جامع الكلمات
    word_collector = WordCollector(min_length=word_min_length)

    # جمع الكلمات من المصادر المختلفة
    words_collected = set()

    # جمع الكلمات من القرآن
    if "quran" in sources and os.path.exists(sources["quran"]):
        quran_words = word_collector.collect_words_from_quran(sources["quran"])
        logger.info(f"تم جمع {len(quran_words)} كلمة من القرآن")
        words_collected.update(quran_words)

    # جمع الكلمات من مواقع الويب
    if "web" in sources and sources["web"]:
        web_words = word_collector.collect_words_from_websites(sources["web"])
        logger.info(f"تم جمع {len(web_words)} كلمة من مواقع الويب")
        words_collected.update(web_words)

    # جمع الكلمات من القواميس
    if "dictionaries" in sources and sources["dictionaries"]:
        dict_words = []
        for dict_path in sources["dictionaries"]:
            if os.path.exists(dict_path):
                dict_words.extend(word_collector.collect_words_from_text_file(dict_path))
        logger.info(f"تم جمع {len(dict_words)} كلمة من القواميس")
        words_collected.update(dict_words)

    # تنظيف وترشيح الكلمات
    words_collected = word_collector.clean_words(list(words_collected))
    words_collected = word_collector.filter_words(words_collected)

    logger.info(f"إجمالي الكلمات بعد التنظيف والترشيح: {len(words_collected)}")

    # حفظ الكلمات المجمعة في ملف مؤقت
    collected_words_file = os.path.join(temp_dir, "collected_words.txt")
    with open(collected_words_file, "w", encoding="utf-8") as f:
        for word in words_collected:
            f.write(f"{word}\n")

    logger.info(f"تم حفظ الكلمات المجمعة في: {collected_words_file}")

    # تنفيذ توسيع المعجم
    logger.info("بدء عملية توسيع المعجم...")

    # استخدام توسيع المعجم المباشر
    expand_lexicon(
        lexicon_path=lexicon_path,
        data_sources={"words_file": collected_words_file},
        output_path=output_path,
        auto_approve_threshold=auto_approve_threshold,
        batch_size=batch_size,
        word_limit=words_to_add,
        min_word_length=word_min_length,
        generate_report=generate_reports,
        use_parallel=use_parallel,
    )

    # التحقق من عدد الكلمات النهائي
    final_word_count = count_words_in_lexicon(output_path)
    logger.info(f"عدد الكلمات النهائي في المعجم: {final_word_count}")

    # توليد تقرير نهائي
    if generate_reports:
        report_path = os.path.join(
            root_path,
            "reports",
            f"lexicon_expansion_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
        )
        interface = LexiconExpansionInterface(lexicon_path=output_path)
        interface.generate_report(report_path)
        logger.info(f"تم توليد تقرير نهائي في: {report_path}")

    return output_path


def main():
    """النقطة الرئيسية لتنفيذ سكربت توسيع المعجم"""
    parser = argparse.ArgumentParser(description="سكربت تنفيذ توسيع المعجم")
    parser.add_argument("--lexicon", required=True, help="مسار ملف المعجم الأصلي")
    parser.add_argument("--output", help="مسار حفظ المعجم الموسع (اختياري)")
    parser.add_argument(
        "--target", type=int, default=1000, help="عدد الكلمات المستهدف (الافتراضي: 1000)"
    )
    parser.add_argument(
        "--threshold", type=float, default=0.85, help="عتبة الثقة للقبول التلقائي (الافتراضي: 0.85)"
    )
    parser.add_argument(
        "--min-length", type=int, default=3, help="الحد الأدنى لطول الكلمة (الافتراضي: 3)"
    )
    parser.add_argument(
        "--batch-size", type=int, default=100, help="حجم دفعة معالجة الكلمات (الافتراضي: 100)"
    )
    parser.add_argument("--no-parallel", action="store_true", help="تعطيل المعالجة المتوازية")
    parser.add_argument("--no-reports", action="store_true", help="تعطيل توليد التقارير")

    args = parser.parse_args()

    try:
        output_path = run_expansion_pipeline(
            lexicon_path=args.lexicon,
            target_word_count=args.target,
            output_path=args.output,
            auto_approve_threshold=args.threshold,
            batch_size=args.batch_size,
            use_parallel=not args.no_parallel,
            word_min_length=args.min_length,
            generate_reports=not args.no_reports,
        )

        logger.info(f"اكتملت عملية توسيع المعجم بنجاح. المعجم الموسع: {output_path}")
        return 0

    except Exception as e:
        logger.error(f"خطأ أثناء تنفيذ عملية توسيع المعجم: {str(e)}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
