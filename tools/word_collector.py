#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
أداة جمع الكلمات العربية من مصادر متنوعة.

تستخدم هذه الأداة لجمع الكلمات العربية من مصادر مختلفة مثل:
- نص القرآن الكريم
- مواقع الويب
- القواميس والمعاجم
- ملفات نصية عامة

تتميز الأداة بالقدرة على تنظيف وترشيح الكلمات حسب معايير محددة.
"""

import os
import re
import json
import random
import argparse
import codecs
import logging
from pathlib import Path
from typing import Set, List, Dict, Optional, Union
from concurrent.futures import ThreadPoolExecutor
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

# إعداد التسجيل
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("word_collector")

# التعبيرات النمطية للعثور على الكلمات العربية
ARABIC_WORD_PATTERN = re.compile(r"[\u0621-\u064A\u0671-\u06FF]+")
DIACRITICS_PATTERN = re.compile(r"[\u064B-\u0652\u0670]")
TATWEEL_PATTERN = re.compile(r"\u0640")
ALEF_LAM_PATTERN = re.compile(r"^ال")


class WordCollector:
    """فئة لجمع وترشيح الكلمات العربية من مصادر متنوعة."""

    def __init__(self, blacklist: Optional[List[str]] = None, min_length: int = 2):
        """
        تهيئة جامع الكلمات.

        المعلمات:
            blacklist: قائمة الكلمات المراد استبعادها
            min_length: الحد الأدنى لطول الكلمة المقبولة
        """
        self.blacklist = set(blacklist) if blacklist else set()
        self.min_length = min_length
        self.words = set()

    def clean_word(self, word: str) -> str:
        """
        تنظيف الكلمة من التشكيل والتطويل وغيرها.

        المعلمات:
            word: الكلمة المراد تنظيفها

        العوائد:
            الكلمة بعد التنظيف
        """
        # إزالة التشكيل
        word = DIACRITICS_PATTERN.sub("", word)
        # إزالة التطويل
        word = TATWEEL_PATTERN.sub("", word)
        # تحويل إلى أحرف صغيرة (ليس له تأثير فعلي في العربية)
        word = word.strip().lower()
        return word

    def filter_word(self, word: str) -> bool:
        """
        التحقق مما إذا كانت الكلمة تلبي معايير القبول.

        المعلمات:
            word: الكلمة المراد فحصها

        العوائد:
            True إذا كانت الكلمة مقبولة، False خلاف ذلك
        """
        # التحقق من الحد الأدنى للطول
        if len(word) < self.min_length:
            return False

        # التحقق من القائمة السوداء
        if word in self.blacklist:
            return False

        # التحقق من أن الكلمة تحتوي على أحرف عربية فقط
        if not ARABIC_WORD_PATTERN.fullmatch(word):
            return False

        return True

    def extract_words_from_text(self, text: str) -> Set[str]:
        """
        استخراج الكلمات العربية من نص.

        المعلمات:
            text: النص المراد استخراج الكلمات منه

        العوائد:
            مجموعة من الكلمات العربية المستخرجة والمنظفة
        """
        # العثور على جميع الكلمات العربية في النص
        all_words = ARABIC_WORD_PATTERN.findall(text)

        # تنظيف وترشيح الكلمات
        cleaned_words = set()
        for word in all_words:
            cleaned = self.clean_word(word)
            if self.filter_word(cleaned):
                cleaned_words.add(cleaned)

        return cleaned_words

    def collect_from_quran(self, quran_path: str) -> Set[str]:
        """
        جمع الكلمات من ملف نص قرآني.

        المعلمات:
            quran_path: مسار ملف القرآن الكريم

        العوائد:
            مجموعة من الكلمات المستخرجة
        """
        logger.info(f"جمع الكلمات من القرآن الكريم: {quran_path}")
        try:
            with codecs.open(quran_path, "r", encoding="utf-8") as f:
                text = f.read()
            words = self.extract_words_from_text(text)
            logger.info(f"تم استخراج {len(words)} كلمة فريدة من القرآن الكريم")
            return words
        except FileNotFoundError:
            logger.error(f"لم يتم العثور على ملف القرآن: {quran_path}")
            return set()
        except Exception as e:
            logger.error(f"خطأ أثناء معالجة ملف القرآن: {str(e)}")
            return set()

    def collect_from_web(self, urls: List[str], max_workers: int = 5) -> Set[str]:
        """
        جمع الكلمات من مواقع الويب.

        المعلمات:
            urls: قائمة عناوين URL للمواقع
            max_workers: عدد العمال للمعالجة المتوازية

        العوائد:
            مجموعة من الكلمات المستخرجة
        """
        logger.info(f"جمع الكلمات من {len(urls)} موقع ويب")
        all_words = set()

        def fetch_url(url):
            try:
                # إضافة رأس وكيل المستخدم لتجنب الحظر
                req = Request(
                    url, headers={"User-Agent": "Mozilla/5.0 (compatible; WordCollector/1.0)"}
                )
                with urlopen(req, timeout=30) as response:
                    html = response.read().decode("utf-8", errors="ignore")
                # إزالة علامات HTML البسيطة (يمكن استخدام BeautifulSoup لتحليل أكثر تقدمًا)
                text = re.sub(r"<[^>]+>", " ", html)
                words = self.extract_words_from_text(text)
                logger.info(f"تم استخراج {len(words)} كلمة فريدة من {url}")
                return words
            except (URLError, HTTPError) as e:
                logger.error(f"خطأ في الاتصال بـ {url}: {str(e)}")
                return set()
            except Exception as e:
                logger.error(f"خطأ أثناء معالجة {url}: {str(e)}")
                return set()

        # استخدام مجمع المواضيع لزيادة السرعة
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            results = list(executor.map(fetch_url, urls))

        # دمج النتائج
        for words in results:
            all_words.update(words)

        logger.info(f"تم استخراج إجمالي {len(all_words)} كلمة فريدة من مواقع الويب")
        return all_words

    def collect_from_dictionary(self, dictionary_path: str) -> Set[str]:
        """
        جمع الكلمات من ملف قاموس.

        المعلمات:
            dictionary_path: مسار ملف القاموس

        العوائد:
            مجموعة من الكلمات المستخرجة
        """
        logger.info(f"جمع الكلمات من القاموس: {dictionary_path}")
        try:
            with codecs.open(dictionary_path, "r", encoding="utf-8") as f:
                # يمكن أن تكون ملفات القاموس بتنسيقات مختلفة، نفترض أن كل سطر يحتوي على كلمة
                words = set()
                for line in f:
                    line = line.strip()
                    if line:
                        # يمكن أن تحتوي أسطر القاموس على كلمات متعددة أو شروحات
                        extracted = self.extract_words_from_text(line)
                        words.update(extracted)

            logger.info(f"تم استخراج {len(words)} كلمة فريدة من القاموس")
            return words
        except FileNotFoundError:
            logger.error(f"لم يتم العثور على ملف القاموس: {dictionary_path}")
            return set()
        except Exception as e:
            logger.error(f"خطأ أثناء معالجة ملف القاموس: {str(e)}")
            return set()

    def collect_from_text_files(self, file_paths: List[str]) -> Set[str]:
        """
        جمع الكلمات من ملفات نصية متعددة.

        المعلمات:
            file_paths: قائمة مسارات الملفات النصية

        العوائد:
            مجموعة من الكلمات المستخرجة
        """
        logger.info(f"جمع الكلمات من {len(file_paths)} ملف نصي")
        all_words = set()

        for file_path in file_paths:
            try:
                with codecs.open(file_path, "r", encoding="utf-8") as f:
                    text = f.read()
                words = self.extract_words_from_text(text)
                logger.info(f"تم استخراج {len(words)} كلمة فريدة من {file_path}")
                all_words.update(words)
            except FileNotFoundError:
                logger.error(f"لم يتم العثور على الملف: {file_path}")
            except Exception as e:
                logger.error(f"خطأ أثناء معالجة الملف {file_path}: {str(e)}")

        logger.info(f"تم استخراج إجمالي {len(all_words)} كلمة فريدة من الملفات النصية")
        return all_words

    def collect_from_custom_words(self, words: List[str]) -> Set[str]:
        """
        جمع الكلمات من قائمة كلمات مخصصة.

        المعلمات:
            words: قائمة الكلمات المخصصة

        العوائد:
            مجموعة من الكلمات المقبولة بعد التنظيف والترشيح
        """
        logger.info(f"معالجة {len(words)} كلمة مخصصة")
        cleaned_words = set()

        for word in words:
            cleaned = self.clean_word(word)
            if self.filter_word(cleaned):
                cleaned_words.add(cleaned)

        logger.info(f"تم قبول {len(cleaned_words)} كلمة مخصصة بعد التنظيف والترشيح")
        return cleaned_words

    def add_words(self, words: Set[str]) -> int:
        """
        إضافة مجموعة من الكلمات إلى مجموعة الكلمات المجمعة.

        المعلمات:
            words: مجموعة الكلمات المراد إضافتها

        العوائد:
            عدد الكلمات الجديدة التي تمت إضافتها
        """
        initial_size = len(self.words)
        self.words.update(words)
        return len(self.words) - initial_size

    def save_words(
        self, output_path: str, randomize: bool = False, limit: Optional[int] = None
    ) -> int:
        """
        حفظ الكلمات المجمعة إلى ملف.

        المعلمات:
            output_path: مسار ملف الإخراج
            randomize: ما إذا كان يجب ترتيب الكلمات بشكل عشوائي
            limit: الحد الأقصى لعدد الكلمات للحفظ (اختياري)

        العوائد:
            عدد الكلمات التي تم حفظها
        """
        # تحويل مجموعة الكلمات إلى قائمة
        word_list = list(self.words)

        # ترتيب عشوائي إذا تم تحديده
        if randomize:
            random.shuffle(word_list)

        # تطبيق الحد إذا تم تحديده
        if limit is not None and limit < len(word_list):
            word_list = word_list[:limit]

        try:
            # التأكد من وجود الدليل الأم
            os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

            # حفظ الكلمات
            with codecs.open(output_path, "w", encoding="utf-8") as f:
                for word in word_list:
                    f.write(f"{word}\n")

            logger.info(f"تم حفظ {len(word_list)} كلمة إلى {output_path}")
            return len(word_list)
        except Exception as e:
            logger.error(f"خطأ أثناء حفظ الكلمات: {str(e)}")
            return 0

    def get_words(self, randomize: bool = False, limit: Optional[int] = None) -> List[str]:
        """
        الحصول على الكلمات المجمعة كقائمة.

        المعلمات:
            randomize: ما إذا كان يجب ترتيب الكلمات بشكل عشوائي
            limit: الحد الأقصى لعدد الكلمات للعودة (اختياري)

        العوائد:
            قائمة الكلمات المجمعة
        """
        # تحويل مجموعة الكلمات إلى قائمة
        word_list = list(self.words)

        # ترتيب عشوائي إذا تم تحديده
        if randomize:
            random.shuffle(word_list)

        # تطبيق الحد إذا تم تحديده
        if limit is not None and limit < len(word_list):
            word_list = word_list[:limit]

        return word_list


def read_blacklist(file_path: str) -> List[str]:
    """
    قراءة قائمة الكلمات المحظورة من ملف.

    المعلمات:
        file_path: مسار ملف القائمة السوداء

    العوائد:
        قائمة الكلمات المحظورة
    """
    try:
        with codecs.open(file_path, "r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        logger.warning(f"لم يتم العثور على ملف القائمة السوداء: {file_path}")
        return []
    except Exception as e:
        logger.error(f"خطأ أثناء قراءة ملف القائمة السوداء: {str(e)}")
        return []


def parse_args():
    """تحليل وسيطات سطر الأوامر."""
    parser = argparse.ArgumentParser(description="أداة لجمع الكلمات العربية من مصادر متنوعة")

    parser.add_argument(
        "--output", "-o", required=True, help="مسار ملف الإخراج لحفظ الكلمات المجمعة"
    )

    # معلمات المصادر
    parser.add_argument("--quran", help="مسار ملف نص القرآن الكريم")

    parser.add_argument("--web", nargs="+", help="قائمة عناوين URL لمواقع الويب لجمع الكلمات منها")

    parser.add_argument("--dictionary", help="مسار ملف قاموس الكلمات العربية")

    parser.add_argument("--text", nargs="+", help="قائمة مسارات الملفات النصية لجمع الكلمات منها")

    parser.add_argument("--custom", nargs="+", help="قائمة كلمات مخصصة لإضافتها مباشرة")

    # معلمات الترشيح والمعالجة
    parser.add_argument("--blacklist", help="مسار ملف يحتوي على قائمة الكلمات المحظورة")

    parser.add_argument(
        "--min-length", type=int, default=2, help="الحد الأدنى لطول الكلمة المقبولة (الافتراضي: 2)"
    )

    parser.add_argument("--limit", type=int, help="الحد الأقصى لعدد الكلمات للإخراج")

    parser.add_argument(
        "--randomize", action="store_true", help="ترتيب الكلمات بشكل عشوائي قبل الحفظ"
    )

    return parser.parse_args()


def main():
    """النقطة الرئيسية لتنفيذ البرنامج."""
    args = parse_args()

    # التحقق من تحديد مصدر واحد على الأقل
    if not any([args.quran, args.web, args.dictionary, args.text, args.custom]):
        logger.error(
            "يجب تحديد مصدر واحد على الأقل للكلمات (--quran و/أو --web و/أو --dictionary و/أو --text و/أو --custom)"
        )
        return 1

    # قراءة القائمة السوداء إذا تم تحديدها
    blacklist = []
    if args.blacklist:
        blacklist = read_blacklist(args.blacklist)
        logger.info(f"تم تحميل {len(blacklist)} كلمة محظورة من القائمة السوداء")

    # إنشاء جامع الكلمات
    collector = WordCollector(blacklist=blacklist, min_length=args.min_length)

    # جمع الكلمات من المصادر المختلفة
    if args.quran:
        words = collector.collect_from_quran(args.quran)
        added = collector.add_words(words)
        logger.info(f"تمت إضافة {added} كلمة جديدة من القرآن الكريم")

    if args.web:
        words = collector.collect_from_web(args.web)
        added = collector.add_words(words)
        logger.info(f"تمت إضافة {added} كلمة جديدة من مواقع الويب")

    if args.dictionary:
        words = collector.collect_from_dictionary(args.dictionary)
        added = collector.add_words(words)
        logger.info(f"تمت إضافة {added} كلمة جديدة من القاموس")

    if args.text:
        words = collector.collect_from_text_files(args.text)
        added = collector.add_words(words)
        logger.info(f"تمت إضافة {added} كلمة جديدة من الملفات النصية")

    if args.custom:
        words = collector.collect_from_custom_words(args.custom)
        added = collector.add_words(words)
        logger.info(f"تمت إضافة {added} كلمة جديدة من القائمة المخصصة")

    # حفظ الكلمات المجمعة
    saved_count = collector.save_words(args.output, randomize=args.randomize, limit=args.limit)

    if saved_count > 0:
        logger.info(f"تم حفظ {saved_count} كلمة بنجاح إلى {args.output}")
        return 0
    else:
        logger.error("فشل في حفظ الكلمات أو لم يتم جمع أي كلمات")
        return 1


if __name__ == "__main__":
    exit(main())
