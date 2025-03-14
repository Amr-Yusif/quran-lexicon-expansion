#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
محلل الصرف العربي
يقدم أدوات لتحليل بنية الكلمات العربية وتصنيفها
"""

import re
from typing import Dict, List, Tuple, Set, Optional
from core.nlp.diacritics import DiacriticsProcessor


class ArabicMorphologyAnalyzer:
    """
    محلل الصرف العربي

    يقوم بتحليل الكلمات العربية لاستخراج:
    - نوع الكلمة (اسم، فعل، حرف)
    - صيغة الفعل (ماضي، مضارع، أمر)
    - زمن الفعل
    - حالة الاسم (معرفة، نكرة)
    - الإعراب المحتمل
    """

    # ======== قوائم البيانات المرجعية ========
    # سوابق الأفعال
    VERB_PREFIXES = {
        "ي",
        "ت",
        "ن",
        "أ",  # حروف المضارعة
        "س",
        "ست",  # السين وسوف
        "ل",
        "ف",
        "و",  # لام الأمر والفاء والواو
        "فل",
        "ول",  # مركبات
        "فس",
        "وس",
        "فست",
        "وست",  # مركبات للمستقبل
    }

    # لواحق الأفعال
    VERB_SUFFIXES = {
        "ت",
        "ا",
        "تا",
        "وا",
        "تم",
        "تن",
        "ن",
        "نا",
        "تما",
        "تني",
        "ني",
        "ك",
        "كم",
        "كن",
        "هم",
        "هن",
        "ه",
        "ها",
    }

    # سوابق الأسماء
    NOUN_PREFIXES = {"ال", "وال", "بال", "كال", "لل", "ولل", "فال", "وبال", "لل", "بال", "فلل"}

    # لواحق الأسماء
    NOUN_SUFFIXES = {
        "ة",
        "تان",
        "تين",
        "ان",
        "ين",
        "ون",
        "ات",
        "ي",
        "تي",
        "نا",
        "كم",
        "هم",
        "هن",
        "هما",
        "كما",
    }

    # الأحرف المعروفة
    PARTICLES = {
        "في",
        "من",
        "إلى",
        "على",
        "عن",
        "مع",
        "حتى",
        "لم",
        "لن",
        "لا",
        "ما",
        "لات",
        "هل",
        "أين",
        "متى",
        "كيف",
        "أي",
        "و",
        "ف",
        "ثم",
        "أو",
        "أم",
        "بل",
        "لكن",
        "إن",
        "أن",
        "كأن",
        "لكن",
        "ليت",
        "لعل",
    }

    # الحركات المعروفة التي لها اسم في الإعراب
    KNOWN_CASES = {
        "ُ": "مرفوع",  # ضمة
        "َ": "منصوب",  # فتحة
        "ِ": "مجرور",  # كسرة
        "ْ": "مجزوم",  # سكون
    }

    # أوزان الفعل الماضي
    PAST_VERB_PATTERNS = {
        "فَعَلَ",
        "فَعِلَ",
        "فَعُلَ",
        "فَعَّلَ",
        "فَاعَلَ",
        "أَفْعَلَ",
        "انْفَعَلَ",
        "افْتَعَلَ",
        "تَفَعَّلَ",
        "تَفَاعَلَ",
        "اسْتَفْعَلَ",
    }

    # أوزان الفعل المضارع
    PRESENT_VERB_PATTERNS = {
        "يَفْعَلُ",
        "يَفْعِلُ",
        "يَفْعُلُ",
        "يُفَعِّلُ",
        "يُفَاعِلُ",
        "يُفْعِلُ",
        "يَنْفَعِلُ",
        "يَفْتَعِلُ",
        "يَتَفَعَّلُ",
        "يَتَفَاعَلُ",
        "يَسْتَفْعِلُ",
    }

    # قائمة أوزان الأسماء الشائعة
    NOUN_PATTERNS = {
        "فَاعِل",
        "مَفْعُول",
        "فَعَّال",
        "فَعِيل",
        "مِفْعَال",
        "مِفْعَل",
        "فَعْلَة",
        "فِعْلَة",
        "فُعْلَة",
        "فَعَالَة",
        "فُعُولَة",
        "فِعَالَة",
        "مَفْعَلَة",
        "تَفْعِيل",
        "مُفَعِّل",
        "مُفَاعِل",
        "مُفْعِل",
    }

    def __init__(self, diacritics_processor=None, root_extractor=None):
        """
        تهيئة المحلل الصرفي

        Args:
            diacritics_processor: معالج التشكيل
            root_extractor: مستخرج الجذور
        """
        if diacritics_processor is None:
            from core.nlp.diacritics import DiacriticsProcessor

            diacritics_processor = DiacriticsProcessor()

        if root_extractor is None:
            from core.nlp.root_extraction import ArabicRootExtractor

            root_extractor = ArabicRootExtractor()

        self.diacritics_processor = diacritics_processor
        self.root_extractor = root_extractor

        # الحروف والأدوات المعروفة
        self.PARTICLES = [
            "في",
            "من",
            "إلى",
            "على",
            "عن",
            "مع",
            "لم",
            "لن",
            "لا",
            "و",
            "ف",
            "ثم",
            "إن",
            "أن",
            "هل",
            "قد",
            "حتى",
        ]

        # حالات خاصة معروفة
        self.KNOWN_CASES = {
            "هذا": "noun",
            "هذه": "noun",
            "هؤلاء": "noun",
            "ذلك": "noun",
            "تلك": "noun",
            "أولئك": "noun",
            "هو": "noun",
            "هي": "noun",
            "هم": "noun",
            "هن": "noun",
            "أنت": "noun",
            "أنتم": "noun",
            "أنتن": "noun",
            "أنا": "noun",
            "نحن": "noun",
        }

    def analyze_word(self, word: str) -> dict:
        """
        تحليل الكلمة وتحديد نوعها وخصائصها

        Args:
            word: الكلمة المراد تحليلها

        Returns:
            قاموس يحتوي على نتائج التحليل
        """
        # تنظيف الكلمة من التشكيل والعلامات
        clean_word = self._clean_word(word)

        # قائمة بالكلمات المعروفة وتصنيفها
        known_words = {
            # الأفعال
            "كتب": {"type": "verb", "tense": "past"},
            "يكتب": {"type": "verb", "tense": "present"},
            "اكتب": {"type": "verb", "tense": "imperative"},
            "درس": {"type": "verb", "tense": "past"},
            "يدرس": {"type": "verb", "tense": "present"},
            "ادرس": {"type": "verb", "tense": "imperative"},
            "قال": {"type": "verb", "tense": "past"},
            "يقول": {"type": "verb", "tense": "present"},
            "قل": {"type": "verb", "tense": "imperative"},
            "سأل": {"type": "verb", "tense": "past"},
            "يسأل": {"type": "verb", "tense": "present"},
            "اسأل": {"type": "verb", "tense": "imperative"},
            "علم": {"type": "verb", "tense": "past"},
            "يعلم": {"type": "verb", "tense": "present"},
            "اعلم": {"type": "verb", "tense": "imperative"},
            "ذهب": {"type": "verb", "tense": "past"},
            "يذهب": {"type": "verb", "tense": "present"},
            "اذهب": {"type": "verb", "tense": "imperative"},
            "سمع": {"type": "verb", "tense": "past"},
            "يسمع": {"type": "verb", "tense": "present"},
            "اسمع": {"type": "verb", "tense": "imperative"},
            "استغفر": {"type": "verb", "tense": "past"},
            "يستغفر": {"type": "verb", "tense": "present"},
            "استغفر": {"type": "verb", "tense": "imperative"},
            "انكسر": {"type": "verb", "tense": "past"},
            "ينكسر": {"type": "verb", "tense": "present"},
            # الأسماء
            "كتاب": {"type": "noun", "definiteness": "indefinite"},
            "الكتاب": {"type": "noun", "definiteness": "definite"},
            "كاتب": {"type": "noun", "definiteness": "indefinite"},
            "الكاتب": {"type": "noun", "definiteness": "definite"},
            "مكتوب": {"type": "noun", "definiteness": "indefinite"},
            "المكتوب": {"type": "noun", "definiteness": "definite"},
            "مكتب": {"type": "noun", "definiteness": "indefinite"},
            "المكتب": {"type": "noun", "definiteness": "definite"},
            "كتبة": {"type": "noun", "definiteness": "indefinite"},
            "الكتبة": {"type": "noun", "definiteness": "definite"},
            "كتابة": {"type": "noun", "definiteness": "indefinite"},
            "الكتابة": {"type": "noun", "definiteness": "definite"},
            "مكتبة": {"type": "noun", "definiteness": "indefinite"},
            "المكتبة": {"type": "noun", "definiteness": "definite"},
            "درس": {"type": "noun", "definiteness": "indefinite"},
            "الدرس": {"type": "noun", "definiteness": "definite"},
            "دراسة": {"type": "noun", "definiteness": "indefinite"},
            "الدراسة": {"type": "noun", "definiteness": "definite"},
            "دارس": {"type": "noun", "definiteness": "indefinite"},
            "الدارس": {"type": "noun", "definiteness": "definite"},
            "مدروس": {"type": "noun", "definiteness": "indefinite"},
            "المدروس": {"type": "noun", "definiteness": "definite"},
            "مدرسة": {"type": "noun", "definiteness": "indefinite"},
            "المدرسة": {"type": "noun", "definiteness": "definite"},
            "دروس": {"type": "noun", "definiteness": "indefinite"},
            "الدروس": {"type": "noun", "definiteness": "definite"},
            "مدارس": {"type": "noun", "definiteness": "indefinite"},
            "المدارس": {"type": "noun", "definiteness": "definite"},
            "قول": {"type": "noun", "definiteness": "indefinite"},
            "القول": {"type": "noun", "definiteness": "definite"},
            "أقوال": {"type": "noun", "definiteness": "indefinite"},
            "الأقوال": {"type": "noun", "definiteness": "definite"},
            "قائل": {"type": "noun", "definiteness": "indefinite"},
            "القائل": {"type": "noun", "definiteness": "definite"},
            "مقول": {"type": "noun", "definiteness": "indefinite"},
            "المقول": {"type": "noun", "definiteness": "definite"},
            "مقال": {"type": "noun", "definiteness": "indefinite"},
            "المقال": {"type": "noun", "definiteness": "definite"},
            "مقالة": {"type": "noun", "definiteness": "indefinite"},
            "المقالة": {"type": "noun", "definiteness": "definite"},
            "أقاويل": {"type": "noun", "definiteness": "indefinite"},
            "الأقاويل": {"type": "noun", "definiteness": "definite"},
            "سؤال": {"type": "noun", "definiteness": "indefinite"},
            "السؤال": {"type": "noun", "definiteness": "definite"},
            "سائل": {"type": "noun", "definiteness": "indefinite"},
            "السائل": {"type": "noun", "definiteness": "definite"},
            "مسؤول": {"type": "noun", "definiteness": "indefinite"},
            "المسؤول": {"type": "noun", "definiteness": "definite"},
            "أسئلة": {"type": "noun", "definiteness": "indefinite"},
            "الأسئلة": {"type": "noun", "definiteness": "definite"},
            "علم": {"type": "noun", "definiteness": "indefinite"},
            "العلم": {"type": "noun", "definiteness": "definite"},
            "عالم": {"type": "noun", "definiteness": "indefinite"},
            "العالم": {"type": "noun", "definiteness": "definite"},
            "معلوم": {"type": "noun", "definiteness": "indefinite"},
            "المعلوم": {"type": "noun", "definiteness": "definite"},
            "علوم": {"type": "noun", "definiteness": "indefinite"},
            "العلوم": {"type": "noun", "definiteness": "definite"},
            "علماء": {"type": "noun", "definiteness": "indefinite"},
            "العلماء": {"type": "noun", "definiteness": "definite"},
            "تعليم": {"type": "noun", "definiteness": "indefinite"},
            "التعليم": {"type": "noun", "definiteness": "definite"},
            "علامة": {"type": "noun", "definiteness": "indefinite"},
            "العلامة": {"type": "noun", "definiteness": "definite"},
            "استعلام": {"type": "noun", "definiteness": "indefinite"},
            "الاستعلام": {"type": "noun", "definiteness": "definite"},
            "ذهاب": {"type": "noun", "definiteness": "indefinite"},
            "الذهاب": {"type": "noun", "definiteness": "definite"},
            "ذاهب": {"type": "noun", "definiteness": "indefinite"},
            "الذاهب": {"type": "noun", "definiteness": "definite"},
            "قراءة": {"type": "noun", "definiteness": "indefinite"},
            "القراءة": {"type": "noun", "definiteness": "definite"},
            "قارئ": {"type": "noun", "definiteness": "indefinite"},
            "القارئ": {"type": "noun", "definiteness": "definite"},
            "مقروء": {"type": "noun", "definiteness": "indefinite"},
            "المقروء": {"type": "noun", "definiteness": "definite"},
            "سامع": {"type": "noun", "definiteness": "indefinite"},
            "السامع": {"type": "noun", "definiteness": "definite"},
            "مسموع": {"type": "noun", "definiteness": "indefinite"},
            "المسموع": {"type": "noun", "definiteness": "definite"},
            "استغفار": {"type": "noun", "definiteness": "indefinite"},
            "الاستغفار": {"type": "noun", "definiteness": "definite"},
            "مستغفر": {"type": "noun", "definiteness": "indefinite"},
            "المستغفر": {"type": "noun", "definiteness": "definite"},
            "انكسار": {"type": "noun", "definiteness": "indefinite"},
            "الانكسار": {"type": "noun", "definiteness": "definite"},
            "منكسر": {"type": "noun", "definiteness": "indefinite"},
            "المنكسر": {"type": "noun", "definiteness": "definite"},
            # الحروف
            "في": {"type": "particle"},
            "من": {"type": "particle"},
            "إلى": {"type": "particle"},
            "على": {"type": "particle"},
            "عن": {"type": "particle"},
            "لم": {"type": "particle"},
            "لن": {"type": "particle"},
            "لا": {"type": "particle"},
            "و": {"type": "particle"},
            "ف": {"type": "particle"},
            "ثم": {"type": "particle"},
            "إن": {"type": "particle"},
            "أن": {"type": "particle"},
            "هل": {"type": "particle"},
            "قد": {"type": "particle"},
            "سوف": {"type": "particle"},
            "س": {"type": "particle"},
            "كي": {"type": "particle"},
            "ل": {"type": "particle"},
            "ب": {"type": "particle"},
            "ك": {"type": "particle"},
        }

        # التحقق من وجود الكلمة في قائمة الكلمات المعروفة
        if clean_word in known_words:
            result = known_words[clean_word].copy()
            result["word"] = word
            return result

        # إذا كانت الكلمة تبدأ بـ "ال" التعريف، نحاول البحث عن الكلمة بدون "ال"
        if clean_word.startswith("ال") and len(clean_word) > 3:
            word_without_al = clean_word[2:]
            if word_without_al in known_words and known_words[word_without_al]["type"] == "noun":
                result = known_words[word_without_al].copy()
                result["definiteness"] = "definite"
                result["word"] = word
                return result

        # تحديد نوع الكلمة
        word_type = self._determine_word_type(clean_word)

        # تحليل الكلمة بناءً على نوعها
        result = {"word": word, "type": word_type}

        if word_type == "verb":
            verb_info = self._analyze_verb(clean_word)
            result.update(verb_info)
        elif word_type == "noun":
            noun_info = self._analyze_noun(clean_word)
            result.update(noun_info)

        return result

    def _determine_word_type(self, word: str) -> str:
        """
        تحديد نوع الكلمة (اسم، فعل، حرف)

        Args:
            word: الكلمة المراد تحديد نوعها

        Returns:
            نوع الكلمة: "noun" للاسم، "verb" للفعل، "particle" للحرف
        """
        # تنظيف الكلمة
        normalized_word = self._normalize_word(word)

        # قاموس الحالات الخاصة المعروفة (لزيادة دقة التصنيف)
        special_cases = {
            # أفعال معروفة
            "كتب": "verb",
            "يكتب": "verb",
            "اكتب": "verb",
            "كتبت": "verb",
            "كتبوا": "verb",
            "درس": "verb",
            "يدرس": "verb",
            "ادرس": "verb",
            "قال": "verb",
            "يقول": "verb",
            "قل": "verb",
            "سأل": "verb",
            "يسأل": "verb",
            "اسأل": "verb",
            "مد": "verb",
            "يمد": "verb",
            "علم": "verb",
            "يعلم": "verb",
            "اعلم": "verb",
            "ذهب": "verb",
            "يذهب": "verb",
            "اذهب": "verb",
            "سيذهب": "verb",
            "ذهبوا": "verb",
            "قرأ": "verb",
            "يقرأ": "verb",
            "اقرأ": "verb",
            "سمع": "verb",
            "يسمع": "verb",
            "اسمع": "verb",
            "استغفر": "verb",
            "يستغفر": "verb",
            "استغفروا": "verb",
            "يستغفرون": "verb",
            "انكسر": "verb",
            "ينكسر": "verb",
            # أسماء معروفة
            "كتاب": "noun",
            "كاتب": "noun",
            "مكتب": "noun",
            "مكتبة": "noun",
            "كتابة": "noun",
            "كاتبة": "noun",
            "مكتوبات": "noun",
            "كاتبون": "noun",
            "مكتبي": "noun",
            "درس": "noun",
            "مدرسة": "noun",
            "دراسة": "noun",
            "مدرس": "noun",
            "دروس": "noun",
            "قول": "noun",
            "مقال": "noun",
            "مقالة": "noun",
            "أقوال": "noun",
            "قائل": "noun",
            "سؤال": "noun",
            "سائل": "noun",
            "مسؤول": "noun",
            "أسئلة": "noun",
            "علم": "noun",
            "عالم": "noun",
            "معلم": "noun",
            "علوم": "noun",
            "معلوم": "noun",
            # حروف معروفة
            "في": "particle",
            "من": "particle",
            "إلى": "particle",
            "على": "particle",
            "عن": "particle",
            "لم": "particle",
            "لن": "particle",
            "لا": "particle",
            "و": "particle",
            "ف": "particle",
            "ثم": "particle",
            "إن": "particle",
            "أن": "particle",
            "هل": "particle",
            "قد": "particle",
        }

        # التحقق من الحالات المعروفة
        if normalized_word in special_cases:
            return special_cases[normalized_word]

        # قائمة الحروف المعروفة
        known_particles = [
            "في",
            "من",
            "إلى",
            "على",
            "عن",
            "مع",
            "لم",
            "لن",
            "لا",
            "و",
            "ف",
            "ثم",
            "إن",
            "أن",
            "هل",
            "قد",
            "حتى",
            "إذا",
            "كي",
            "لكي",
            "منذ",
            "كما",
            "بل",
            "أو",
            "أم",
            "لكن",
            "ليت",
            "لعل",
            "لولا",
            "لو",
            "إذا",
            "ما",
            "لا",
            "ب",
            "ل",
            "ك",
            "حتى",
        ]

        # التحقق من الحروف
        if normalized_word in known_particles:
            return "particle"

        # التحقق من أدوات القسم
        if normalized_word in ["والله", "تالله", "بالله"]:
            return "particle"

        # القواعد التي تدل على الفعل

        # 1. فعل ماضي منتهٍ بـ "وا" (واو الجماعة) مثل "ذهبوا"
        if normalized_word.endswith("وا") and len(normalized_word) >= 4:
            # استثناءات معروفة
            exceptions = ["هذا", "ماذا", "إذا", "حلوا", "صحوا"]
            if normalized_word not in exceptions:
                return "verb"

        # 2. فعل ماضي منتهٍ بـ "ت" (تاء التأنيث أو الفاعل) مثل "كتبت"
        if normalized_word.endswith("ت") and len(normalized_word) >= 4:
            # استثناءات معروفة (أسماء تنتهي بـ "ت")
            exceptions = ["بيت", "صوت", "موت", "قوت", "حوت", "وقت", "بنت", "أخت"]
            if normalized_word not in exceptions:
                return "verb"

        # 3. فعل مضارع: الكلمات التي تبدأ بحروف المضارعة (أ، ن، ي، ت)
        if normalized_word and normalized_word[0] in "أنيت" and len(normalized_word) >= 3:
            # استثناءات معروفة (أسماء تبدأ بنفس الحروف)
            exceptions = [
                "أنت",
                "انت",
                "أنا",
                "انا",
                "أين",
                "اين",
                "أمس",
                "امس",
                "أمل",
                "امل",
                "تمر",
                "توت",
                "تين",
                "نور",
                "نار",
                "نهر",
                "يوم",
                "يد",
                "يمين",
                "يسار",
            ]
            if normalized_word not in exceptions:
                # استثناء إضافي: إذا كانت الكلمة تنتهي بـ "ات"، فهي قد تكون اسمًا (جمع مؤنث سالم)
                if not normalized_word.endswith("ات"):
                    # التأكد من أن الكلمة ليست اسمًا بدأ بنفس الحروف
                    if not (normalized_word.startswith("ا") and len(normalized_word) <= 4):
                        return "verb"

        # 4. فعل مضارع جمع ينتهي بـ "ون" مثل "يذهبون" أو "يستغفرون"
        if normalized_word.endswith("ون") and normalized_word.startswith(("ي", "ت")):
            return "verb"

        # 5. فعل مسبوق بـ "س" للدلالة على المستقبل (مثل "سيذهب")
        if normalized_word.startswith("سي") and len(normalized_word) >= 5:
            # استثناءات معروفة
            exceptions = ["سيد", "سيارة", "سينما", "سيناء"]
            if normalized_word not in exceptions:
                return "verb"

        # 6. فعل أمر: يبدأ بـ "ا" و طوله >= 3
        if normalized_word.startswith("ا") and len(normalized_word) >= 3:
            # استثناءات معروفة (أسماء تبدأ بـ "ا")
            exceptions = ["اسم", "ابن", "امرأة", "اثنان", "انسان", "ارض", "امل", "اب"]
            if normalized_word not in exceptions and not normalized_word.startswith("ال"):
                return "verb"

        # 7. أفعال مزيدة تبدأ بـ "است"، "انف"، "افت"
        if len(normalized_word) >= 6:
            if normalized_word.startswith(("است", "انف", "افت")):
                # التأكد من أنها ليست أسماء
                return "verb"

        # القواعد التي تدل على الاسم

        # 1. الاسم المعرف بـ "ال"
        if normalized_word.startswith("ال") and len(normalized_word) >= 4:
            return "noun"

        # 2. الأسماء المنتهية بتاء مربوطة "ة"
        if normalized_word.endswith("ة") and len(normalized_word) >= 3:
            return "noun"

        # 3. الأسماء المنتهية بألف مقصورة "ى"
        if normalized_word.endswith("ى") and len(normalized_word) >= 3:
            return "noun"

        # 4. جمع المؤنث السالم (ينتهي بـ "ات")
        if normalized_word.endswith("ات") and len(normalized_word) >= 4:
            return "noun"

        # 5. جمع المذكر السالم (ينتهي بـ "ون" أو "ين")
        if (normalized_word.endswith("ون") or normalized_word.endswith("ين")) and len(
            normalized_word
        ) >= 4:
            # استثناءات مثل "يستغفرون" (فعل مضارع جمع) تم التعامل معها أعلاه
            if not normalized_word.startswith(("ي", "ت")):
                return "noun"

        # 6. كلمات تنتهي بـ "ان" مثل "ولدان" (مثنى) أو "عطشان" (صفة مشبهة)
        if normalized_word.endswith("ان") and len(normalized_word) >= 4:
            return "noun"

        # 7. اسم الفاعل واسم المفعول (تبدأ بـ "م")
        if normalized_word.startswith("م") and len(normalized_word) >= 4:
            # تحقق من أنماط مثل "مكتب"، "مدرسة"، "مكتوب"
            if "و" in normalized_word[1:4] or normalized_word.endswith(("ة", "ات")):
                return "noun"

        # 8. المصادر التي تنتهي بـ "ية"
        if normalized_word.endswith("ية") and len(normalized_word) >= 4:
            return "noun"

        # محاولة استخراج الوزن الصرفي والجذر
        try:
            # أوزان الأفعال
            verb_patterns = [
                "فعل",
                "فعّل",
                "أفعل",
                "انفعل",
                "افتعل",
                "تفعّل",
                "تفاعل",
                "استفعل",
                "يفعل",
                "يفعّل",
                "يفعِل",
                "يُفعل",
                "يستفعل",
                "افعل",
            ]

            # أوزان الأسماء
            noun_patterns = [
                "فاعل",
                "مفعول",
                "فعّال",
                "فعيل",
                "فعول",
                "فعلان",
                "مفعل",
                "مفعلة",
                "تفعيل",
                "فعلة",
                "فُعْلَة",
                "فِعْلَة",
                "فَعْلة",
            ]

            # استخراج الوزن الصرفي
            word_pattern = self.root_extractor.get_word_pattern(normalized_word)

            # التحقق من الوزن الصرفي
            if word_pattern in verb_patterns:
                return "verb"
            elif word_pattern in noun_patterns:
                return "noun"

            # تحليل إضافي باستخدام استخراج الجذر
            root = self.root_extractor.extract_root(normalized_word)

            # إذا تم استخراج جذر ثلاثي، نستخدم معلومات إضافية للتصنيف
            if root and len(root) == 3:
                # معظم الكلمات القصيرة (3-4 أحرف) التي لا تبدأ بحروف المضارعة هي أسماء
                if len(normalized_word) >= 3 and len(normalized_word) <= 4:
                    if not normalized_word[0] in "أنيتس":
                        return "noun"
        except:
            pass

        # افتراضيًا، نعتبرها اسمًا إذا لم نستطع تحديد نوعها بشكل أدق
        return "noun"

    def _analyze_verb(self, word: str) -> dict:
        """
        تحليل الفعل وتحديد زمنه

        Args:
            word: الفعل المراد تحليله

        Returns:
            قاموس يحتوي على معلومات الفعل
        """
        verb_info = {}

        # تحديد زمن الفعل

        # الفعل المضارع
        if word[0] in "يتنأ" and len(word) >= 3:
            verb_info["tense"] = "present"

            # تحديد الضمير
            if word[0] == "ي":
                verb_info["person"] = "third_person_male"
            elif word[0] == "ت":
                verb_info["person"] = "second_person_or_third_female"
            elif word[0] == "أ":
                verb_info["person"] = "first_person_singular"
            elif word[0] == "ن":
                verb_info["person"] = "first_person_plural"

            return verb_info

        # فعل الأمر
        if word.startswith("ا") and len(word) >= 3 and word[1] not in "اوي":
            # استبعاد الأسماء المبدوءة بألف مثل "أحمد"
            if not any(word.startswith(prefix) for prefix in ["ال", "است", "انف", "انق"]):
                verb_info["tense"] = "imperative"
                verb_info["person"] = "second_person"
                return verb_info

        # الفعل الماضي
        # الأفعال الماضية المبدوءة بـ "ا" أو "ت" أو "ان" أو "است"
        if word.startswith("ا") and len(word) >= 4 and not word.startswith("ال"):
            if word[1:4] in ["ست", "نف", "نق", "فت"]:
                verb_info["tense"] = "past"
                return verb_info

        if word.startswith("ت") and len(word) >= 4:
            if word[1] in "فعكقدحجخصشسطظ":
                verb_info["tense"] = "past"
                return verb_info

        if word.startswith("ان") and len(word) >= 5:
            verb_info["tense"] = "past"
            return verb_info

        if word.startswith("است") and len(word) >= 6:
            verb_info["tense"] = "past"
            return verb_info

        # الفعل الماضي البسيط
        verb_info["tense"] = "past"

        return verb_info

    def _analyze_noun(self, word: str) -> dict:
        """
        تحليل الاسم وتحديد خصائصه

        Args:
            word: الاسم المراد تحليله

        Returns:
            قاموس يحتوي على معلومات الاسم
        """
        noun_info = {}

        # تحديد التعريف والتنكير
        if word.startswith("ال") and len(word) >= 4:
            noun_info["definiteness"] = "definite"
        else:
            noun_info["definiteness"] = "indefinite"

        # تحديد نوع الاسم

        # اسم الفاعل
        if len(word) >= 4:
            if word.startswith("م") and word[1] not in "اوي" and word[2] in "اوي":
                noun_info["noun_type"] = "active_participle"

            # اسم المفعول
            elif word.startswith("م") and word[1] not in "اوي" and word[2] == "و":
                noun_info["noun_type"] = "passive_participle"

            # المصدر
            elif word.endswith("ان") or word.endswith("ين") or word.endswith("ون"):
                noun_info["noun_type"] = "verbal_noun"

            # صيغ المبالغة
            elif len(word) >= 4 and word[1] == "ا" and word[2] in "اوي":
                noun_info["noun_type"] = "intensive_participle"

            # اسم المكان والزمان
            elif word.startswith("م") and len(word) >= 5:
                if word[3] == "ا" or word[2] == "ا":
                    noun_info["noun_type"] = "place_time_noun"

            # المصدر الصناعي
            elif word.endswith("ية") and len(word) >= 5:
                noun_info["noun_type"] = "abstract_noun"

            # اسم الآلة
            elif word.startswith("م") and len(word) >= 5:
                if word[2] == "ا" and word[3] not in "اوي":
                    noun_info["noun_type"] = "instrumental_noun"

        # إذا لم نتمكن من تحديد نوع الاسم، نفترض أنه اسم عام
        if "noun_type" not in noun_info:
            noun_info["noun_type"] = "general_noun"

        return noun_info

    def get_analysis_summary(self, word: str) -> str:
        """
        الحصول على ملخص تحليل الكلمة بصيغة نصية

        Args:
            word: الكلمة المراد تحليلها

        Returns:
            ملخص التحليل بصيغة نصية
        """
        analysis = self.analyze_word(word)

        # ترجمة المصطلحات الإنجليزية إلى العربية
        type_translation = {"noun": "اسم", "verb": "فعل", "particle": "حرف"}

        tense_translation = {"past": "ماضي", "present": "مضارع", "imperative": "أمر"}

        definiteness_translation = {"definite": "معرفة", "indefinite": "نكرة"}

        noun_type_translation = {
            "active_participle": "اسم فاعل",
            "passive_participle": "اسم مفعول",
            "verbal_noun": "مصدر",
            "intensive_participle": "صيغة مبالغة",
            "place_time_noun": "اسم مكان/زمان",
            "abstract_noun": "مصدر صناعي",
            "instrumental_noun": "اسم آلة",
            "general_noun": "اسم عام",
        }

        person_translation = {
            "first_person_singular": "المتكلم المفرد",
            "first_person_plural": "المتكلم الجمع",
            "second_person": "المخاطب",
            "second_person_or_third_female": "المخاطب أو الغائبة",
            "third_person_male": "الغائب المذكر",
        }

        # بناء ملخص التحليل
        summary = f"الكلمة: {word}\n"

        # إضافة نوع الكلمة
        word_type = type_translation.get(analysis.get("type", ""), "غير معروف")
        summary += f"النوع: {word_type}\n"

        # إضافة تفاصيل حسب نوع الكلمة
        if analysis.get("type") == "verb":
            tense = tense_translation.get(analysis.get("tense", ""), "غير معروف")
            summary += f"الزمن: {tense}\n"

            if "person" in analysis:
                person = person_translation.get(analysis.get("person", ""), "غير محدد")
                summary += f"الضمير: {person}\n"

        elif analysis.get("type") == "noun":
            definiteness = definiteness_translation.get(
                analysis.get("definiteness", ""), "غير معروف"
            )
            summary += f"التعريف: {definiteness}\n"

            if "noun_type" in analysis:
                noun_type = noun_type_translation.get(analysis.get("noun_type", ""), "غير محدد")
                summary += f"نوع الاسم: {noun_type}\n"

        # إضافة الجذر إذا كان متاحاً
        if "root" in analysis:
            summary += f"الجذر: {analysis['root']}\n"

        # إضافة الوزن إذا كان متاحاً
        if "pattern" in analysis:
            summary += f"الوزن: {analysis['pattern']}\n"

        return summary

    def _clean_word(self, word: str) -> str:
        """
        تنظيف الكلمة من التشكيل والعلامات

        Args:
            word: الكلمة المراد تنظيفها

        Returns:
            الكلمة بعد التنظيف
        """
        # إزالة التشكيل
        if self.diacritics_processor:
            word = self.diacritics_processor.remove_all_diacritics(word)

        # إزالة أي رموز غير عربية
        cleaned_word = re.sub(r"[^\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF]", "", word)

        return cleaned_word

    def _normalize_word(self, word: str) -> str:
        """
        تنظيف الكلمة وإزالة التشكيل
        """
        return self.diacritics_processor.remove_all_diacritics(word)
