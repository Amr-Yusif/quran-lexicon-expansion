#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
معالج التشكيل (Diacritics Processor)
يوفر أدوات متقدمة للتعامل مع علامات التشكيل في النصوص العربية
"""

import re
from typing import List, Dict, Tuple, Set, Optional, Union


class DiacriticsProcessor:
    """
    معالج متخصص لعلامات التشكيل في اللغة العربية

    يوفر وظائف متنوعة لإدارة علامات التشكيل في النصوص العربية مثل:
    - إزالة التشكيل بشكل كامل أو جزئي
    - استخراج نمط التشكيل من النص
    - إضافة التشكيل الافتراضي المتوقع للنص
    - مقارنة أنماط التشكيل بين نصوص
    """

    # ======== علامات التشكيل الأساسية ========
    # الحركات الرئيسية
    FATHA = "\u064e"  # فتحة
    DAMMA = "\u064f"  # ضمة
    KASRA = "\u0650"  # كسرة
    SUKUN = "\u0652"  # سكون

    # التنوين
    FATHATAN = "\u064b"  # فتحتان (تنوين فتح)
    DAMMATAN = "\u064c"  # ضمتان (تنوين ضم)
    KASRATAN = "\u064d"  # كسرتان (تنوين كسر)

    # علامات أخرى
    SHADDA = "\u0651"  # شدة
    MADDAH = "\u0653"  # مدة
    HAMZA_ABOVE = "\u0654"  # همزة فوق الألف
    HAMZA_BELOW = "\u0655"  # همزة تحت الألف

    # مجموعات التشكيل
    SHORT_VOWELS = [FATHA, DAMMA, KASRA, SUKUN]
    TANWIN = [FATHATAN, DAMMATAN, KASRATAN]
    SPECIAL_MARKS = [SHADDA, MADDAH, HAMZA_ABOVE, HAMZA_BELOW]

    # جميع علامات التشكيل المدعومة
    ALL_DIACRITICS = SHORT_VOWELS + TANWIN + SPECIAL_MARKS

    # القواعد الصوتية المعروفة للتشكيل التلقائي
    COMMON_PREFIXES = {
        "ال": {"ل": SUKUN},
        "ب": {"ب": KASRA},
        "ل": {"ل": KASRA},
        "و": {"و": FATHA},
        "ف": {"ف": FATHA},
    }

    COMMON_SUFFIXES = {
        "ون": {"و": DAMMA, "ن": FATHA},
        "ين": {"ي": KASRA, "ن": FATHA},
        "ان": {"ا": "", "ن": KASRA},
        "ات": {"ا": "", "ت": DAMMA},
    }

    def __init__(self):
        """تهيئة معالج التشكيل"""
        # يمكن إضافة خيارات تهيئة إضافية هنا في المستقبل
        pass

    @classmethod
    def remove_all_diacritics(cls, text: str) -> str:
        """
        إزالة جميع علامات التشكيل من النص

        Args:
            text: النص المراد معالجته

        Returns:
            النص بعد إزالة جميع علامات التشكيل
        """
        for diacritic in cls.ALL_DIACRITICS:
            text = text.replace(diacritic, "")
        return text

    @classmethod
    def remove_tatweel(cls, text: str) -> str:
        """
        إزالة علامة التطويل (الكشيدة) من النص

        Args:
            text: النص المراد معالجته

        Returns:
            النص بعد إزالة علامة التطويل
        """
        # كود يونيكود لعلامة التطويل (الكشيدة)
        tatweel = "\u0640"
        return text.replace(tatweel, "")

    @classmethod
    def remove_except_shadda(cls, text: str) -> str:
        """
        إزالة جميع علامات التشكيل ما عدا الشدة

        مفيد عندما تكون الشدة مهمة للمعنى ولكن باقي الحركات يمكن حذفها

        Args:
            text: النص المراد معالجته

        Returns:
            النص بعد إزالة جميع علامات التشكيل ما عدا الشدة
        """
        for diacritic in cls.ALL_DIACRITICS:
            if diacritic != cls.SHADDA:
                text = text.replace(diacritic, "")
        return text

    @classmethod
    def extract_diacritics_pattern(cls, text: str) -> str:
        """
        استخراج نمط التشكيل من النص

        يستخرج هذا النمط بحيث يمكن تطبيقه على نص آخر مشابه

        Args:
            text: النص المراد استخراج نمط التشكيل منه

        Returns:
            سلسلة تمثل نمط التشكيل للنص
        """
        pattern = []
        for char in text:
            if char in cls.ALL_DIACRITICS:
                pattern.append(char)
            else:
                pattern.append("_")  # استبدال الحروف برمز خاص

        return "".join(pattern)

    @classmethod
    def apply_diacritics_pattern(cls, text: str, pattern: str) -> str:
        """
        تطبيق نمط تشكيل على نص

        Args:
            text: النص المراد تطبيق التشكيل عليه
            pattern: نمط التشكيل المراد تطبيقه

        Returns:
            النص بعد تطبيق نمط التشكيل
        """
        # أولاً، إزالة أي تشكيل موجود
        text = cls.remove_all_diacritics(text)

        result = []
        text_index = 0

        for pattern_char in pattern:
            if pattern_char == "_" and text_index < len(text):
                # إضافة الحرف من النص الأصلي
                result.append(text[text_index])
                text_index += 1
            elif pattern_char in cls.ALL_DIACRITICS and text_index > 0:
                # إضافة علامة التشكيل بعد الحرف السابق
                result.append(pattern_char)

        # إضافة أي حروف متبقية من النص الأصلي
        if text_index < len(text):
            result.extend(text[text_index:])

        return "".join(result)

    @classmethod
    def has_diacritics(cls, text: str) -> bool:
        """
        التحقق مما إذا كان النص يحتوي على علامات تشكيل

        Args:
            text: النص المراد فحصه

        Returns:
            True إذا كان النص يحتوي على علامات تشكيل، وإلا False
        """
        for char in text:
            if char in cls.ALL_DIACRITICS:
                return True
        return False

    @classmethod
    def get_diacritics_count(cls, text: str) -> Dict[str, int]:
        """
        حساب عدد علامات التشكيل المختلفة في النص

        Args:
            text: النص المراد تحليله

        Returns:
            قاموس يحتوي على عدد كل علامة تشكيل
        """
        counts = {diacritic: 0 for diacritic in cls.ALL_DIACRITICS}

        for char in text:
            if char in cls.ALL_DIACRITICS:
                counts[char] += 1

        return counts

    @classmethod
    def suggest_simple_diacritics(cls, text: str) -> str:
        """
        اقتراح تشكيل بسيط للنص بناءً على القواعد الصوتية الشائعة

        ملاحظة: هذا تشكيل أولي بسيط وقد لا يكون دقيقًا بنسبة 100%

        Args:
            text: النص المراد إضافة التشكيل له

        Returns:
            النص مع التشكيل المقترح
        """
        # إزالة أي تشكيل موجود
        text = cls.remove_all_diacritics(text)

        result = []
        words = text.split()

        for word in words:
            processed_word = word

            # معالجة البادئات المعروفة
            for prefix, rules in cls.COMMON_PREFIXES.items():
                if word.startswith(prefix):
                    for char, diacritic in rules.items():
                        char_index = prefix.index(char)
                        if diacritic:  # بعض الحروف قد لا تحتاج لتشكيل
                            processed_word = (
                                processed_word[: char_index + 1]
                                + diacritic
                                + processed_word[char_index + 1 :]
                            )

            # معالجة اللواحق المعروفة
            for suffix, rules in cls.COMMON_SUFFIXES.items():
                if word.endswith(suffix):
                    suffix_start = len(word) - len(suffix)
                    for char, diacritic in rules.items():
                        char_index = suffix_start + suffix.index(char)
                        if diacritic:  # بعض الحروف قد لا تحتاج لتشكيل
                            processed_word = (
                                processed_word[: char_index + 1]
                                + diacritic
                                + processed_word[char_index + 1 :]
                            )

            # القواعد العامة: وضع فتحة على الأحرف باستثناء الحرف الأخير
            for i in range(len(word) - 1):
                if all(processed_word[i] != d for d in cls.ALL_DIACRITICS) and processed_word[
                    i
                ] not in (" ", "،", "."):
                    # التأكد من أن الحرف لا يحتوي بالفعل على تشكيل
                    has_diacritic = False
                    if i + 1 < len(processed_word) and processed_word[i + 1] in cls.ALL_DIACRITICS:
                        has_diacritic = True

                    if not has_diacritic:
                        processed_word = (
                            processed_word[: i + 1] + cls.FATHA + processed_word[i + 1 :]
                        )

            result.append(processed_word)

        return " ".join(result)

    @classmethod
    def count_diacritics_density(cls, text: str) -> float:
        """
        حساب كثافة التشكيل في النص (نسبة علامات التشكيل إلى عدد الحروف)

        Args:
            text: النص المراد تحليله

        Returns:
            نسبة كثافة التشكيل (0.0 إلى 1.0)
        """
        if not text:
            return 0.0

        diacritics_count = sum(1 for char in text if char in cls.ALL_DIACRITICS)
        # حساب عدد الأحرف العربية (باستثناء المسافات وعلامات الترقيم)
        arabic_letters_count = sum(
            1 for char in text if "\u0600" <= char <= "\u06ff" and char not in cls.ALL_DIACRITICS
        )

        if arabic_letters_count == 0:
            return 0.0

        return diacritics_count / arabic_letters_count

    @classmethod
    def get_last_letter_diacritic(cls, word: str) -> Tuple[Optional[str], str]:
        """
        استخراج تشكيل الحرف الأخير من الكلمة (مهم في الإعراب)

        Args:
            word: الكلمة المراد تحليلها

        Returns:
            زوج من (علامة التشكيل للحرف الأخير، وصف موجز للحركة الإعرابية)
        """
        # إزالة أي مسافات أو علامات ترقيم
        word = word.strip(' ،.؟!:؛""')

        if not word:
            return None, "كلمة فارغة"

        # البحث عن آخر حرف عربي في الكلمة
        last_letter_index = None
        for i in range(len(word) - 1, -1, -1):
            if "\u0600" <= word[i] <= "\u06ff" and word[i] not in cls.ALL_DIACRITICS:
                last_letter_index = i
                break

        if last_letter_index is None:
            return None, "لا توجد حروف عربية"

        # تحقق من تشكيل الحرف الأخير
        if last_letter_index + 1 < len(word) and word[last_letter_index + 1] in cls.ALL_DIACRITICS:
            diacritic = word[last_letter_index + 1]

            # تحديد وصف الحركة الإعرابية
            if diacritic == cls.FATHA or diacritic == cls.FATHATAN:
                return diacritic, "منصوب"
            elif diacritic == cls.DAMMA or diacritic == cls.DAMMATAN:
                return diacritic, "مرفوع"
            elif diacritic == cls.KASRA or diacritic == cls.KASRATAN:
                return diacritic, "مجرور"
            elif diacritic == cls.SUKUN:
                return diacritic, "مبني على السكون"
            else:
                return diacritic, "علامة أخرى"

        return None, "غير مشكّل"
