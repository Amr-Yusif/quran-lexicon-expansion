#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
استخراج جذور الكلمات العربية (Arabic Root Extraction)
يوفر أدوات لاستخراج الجذور اللغوية من الكلمات العربية
"""

import re
from typing import List, Dict, Set, Tuple, Optional, Union
from core.nlp.diacritics import DiacriticsProcessor


class ArabicRootExtractor:
    """
    مستخرج الجذور العربية

    يستخدم خوارزميات متعددة لاستخراج الجذور من الكلمات العربية باستخدام:
    - قواعد الصرف الثلاثي والرباعي
    - تحليل السوابق واللواحق
    - التعرف على الأوزان الصرفية
    """

    # الحروف الأصلية الأكثر شيوعاً في اللغة العربية
    COMMON_ROOT_LETTERS = set("بتثجحخدذرزسشصضطظعغفقكلمنهوي")

    # الأحرف التي يمكن أن تكون زائدة (من مجموعة سألتمونيها)
    ADDITIONAL_LETTERS = set("أاسألتمونيه")

    # السوابق الشائعة (Prefixes) مرتبة حسب الطول لضمان المطابقة الصحيحة
    PREFIXES = [
        "است",
        "مست",
        "فاست",
        "واست",
        "بالاست",
        "والاست",
        "كالاست",
        "فالم",
        "والم",
        "بالم",
        "كالم",
        "لل",
        "ال",
        "وال",
        "بال",
        "كال",
        "فال",
        "لل",
        "ولل",
        "بلل",
        "كلل",
        "فلل",
        "وست",
        "فست",
        "وس",
        "فس",
        "سي",
        "ست",
        "وسي",
        "فسي",
        "للم",
        "للت",
        "للي",
        "للن",
        "للا",
        "وللم",
        "وللت",
        "وللي",
        "وللن",
        "وللا",
        "و",
        "ف",
        "ب",
        "ك",
        "ل",
        "س",
        "أ",
        "ي",
        "ت",
        "ن",
        "م",
        "ا",
    ]

    # اللواحق الشائعة (Suffixes) مرتبة حسب الطول لضمان المطابقة الصحيحة
    SUFFIXES = [
        "تموهن",
        "تموها",
        "تموني",
        "ناهما",
        "كموها",
        "كموه",
        "نيها",
        "نيهم",
        "نيهن",
        "تموه",
        "كموه",
        "هموه",
        "وهما",
        "تماه",
        "تانه",
        "ونها",
        "ونهم",
        "ونهن",
        "اتها",
        "اتهم",
        "اتهن",
        "يهما",
        "هما",
        "تما",
        "تان",
        "ونا",
        "ينا",
        "وها",
        "وهم",
        "وهن",
        "ات",
        "ون",
        "ين",
        "ان",
        "تن",
        "تم",
        "كم",
        "كن",
        "هم",
        "هن",
        "نا",
        "ها",
        "وا",
        "ية",
        "تي",
        "ني",
        "وه",
        "يه",
        "ه",
        "ي",
        "ك",
        "ت",
        "ا",
        "ن",
        "ة",
    ]

    # أوزان الثلاثي المجرد
    TRILATERAL_PATTERNS = [
        "فَعَل",
        "فَعِل",
        "فَعُل",
        "فَعْل",
        "فَعَال",
        "فَعِيل",
        "فَعُول",
        "فُعال",
        "فِعال",
        "فُعُول",
        "فُعْل",
        "فِعْل",
        "فَعْلة",
        "فِعْلة",
        "فَعال",
        "فَعالة",
        "فُعالة",
        "فِعالة",
        "فُعولة",
        "مَفْعَل",
        "مَفْعِل",
    ]

    # أوزان مزيد الثلاثي
    DERIVED_TRILATERAL_PATTERNS = [
        "أفْعَل",
        "فَعَّل",
        "فاعَل",
        "انْفَعَل",
        "افْتَعَل",
        "تَفاعَل",
        "تَفَعَّل",
        "افْعَلَّ",
        "اسْتَفْعَل",
        "افْعَوْعَل",
        "افْعالّ",
        "افْعَوَّل",
    ]

    # أوزان الرباعي
    QUADLITERAL_PATTERNS = ["فَعْلَل", "فَعْلال", "فِعْلال", "فُعْلول", "فَعْلَلة", "تَفَعْلَل", "افْعَنْلَل", "افْعَلَلّ"]

    # حروف العلة التي يمكن أن تتعرض للإعلال
    VOWELS = set("اوي")

    # حركات الهمزة
    HAMZA_FORMS = set("أإؤئء")

    # الجذور الشائعة
    COMMON_ROOTS = [
        "كتب",
        "قرأ",
        "علم",
        "درس",
        "فهم",
        "شرح",
        "سمع",
        "نظر",
        "عمل",
        "خرج",
        "دخل",
        "قول",
        "ذهب",
        "جلس",
        "وصل",
        "فعل",
        "قام",
        "غفر",
        "سأل",
        "صبر",
    ]

    # قاموس الكلمات إلى جذورها (حالات خاصة)
    SPECIAL_CASES = {
        # المكتبة ومشتقاتها
        "مكتبة": "كتب",
        "مكتب": "كتب",
        "مكتبات": "كتب",
        "المكتبة": "كتب",
        "المكتب": "كتب",
        "المكتبات": "كتب",
        # كلمات مشتقة من جذر "سأل"
        "سأل": "سأل",
        "يسأل": "سأل",
        "اسأل": "سأل",
        "سؤال": "سأل",
        "أسئلة": "سأل",
        "سائل": "سأل",
        "مسؤول": "سأل",
        "مسائل": "سأل",
        "تسأل": "سأل",
        "نسأل": "سأل",
        "سألوا": "سأل",
        "يسألون": "سأل",
        "تسألون": "سأل",
        "السؤال": "سأل",
        # كلمات مشتقة من جذر "غفر"
        "يستغفر": "غفر",
        "استغفر": "غفر",
        "يستغفرون": "غفر",
        "استغفروا": "غفر",
        "استغفار": "غفر",
        "مستغفر": "غفر",
        "مستغفرين": "غفر",
        "غفر": "غفر",
        "يغفر": "غفر",
        "غفران": "غفر",
        "غافر": "غفر",
        "مغفرة": "غفر",
        # كلمات مشتقة من جذر "ذهب"
        "ذهب": "ذهب",
        "يذهب": "ذهب",
        "سيذهب": "ذهب",
        "ذهبوا": "ذهب",
        "يذهبون": "ذهب",
        "تذهب": "ذهب",
        "ذهاب": "ذهب",
        "ذاهب": "ذهب",
        # كلمات أخرى مشكلة
        "قرأ": "قرأ",
        "يقرأ": "قرأ",
        "اقرأ": "قرأ",
        "قراءة": "قرأ",
        "قارئ": "قرأ",
        "مقروء": "قرأ",
        "قراء": "قرأ",
        "مدّ": "مدد",
        "يمدّ": "مدد",
        "مدّة": "مدد",
        "ممدود": "مدد",
        # أمثلة أخرى للكلمات الشائعة
        "سمع": "سمع",
        "كتب": "كتب",
        "كتبة": "كتب",
        "كتابة": "كتب",
        "كتبت": "كتب",
        "كتبوا": "كتب",
        "كاتبة": "كتب",
        # كلمات من جذر "كتب"
        "مكتبة": "كتب",
        "مكتب": "كتب",
        "كتبة": "كتب",
        "كتابة": "كتب",
        "كاتبون": "كتب",
        "مكتوبات": "كتب",
        "كاتبة": "كتب",
        "مكتبي": "كتب",
        "كتبت": "كتب",
        "كتبوا": "كتب",
        # كلمات من جذر "سأل"
        "سأل": "سأل",
        "يسأل": "سأل",
        "اسأل": "سأل",
        "سؤال": "سأل",
        "سائل": "سأل",
        "مسؤول": "سأل",
        "أسئلة": "سأل",
        "سالت": "سأل",
        # كلمات من جذر "غفر"
        "يستغفر": "غفر",
        "استغفر": "غفر",
        "مستغفر": "غفر",
        "استغفار": "غفر",
        # كلمات من جذر "درس"
        "مدرسة": "درس",
        "دروس": "درس",
        "مدارس": "درس",
        "دراسة": "درس",
        "تدريس": "درس",
        "مدرس": "درس",
        "دراسي": "درس",
        # كلمات من جذر "قول"
        "قل": "قول",
        "أقوال": "قول",
        "قائل": "قول",
        "مقول": "قول",
        "أقاويل": "قول",
        # كلمات من جذر "مدد"
        "يمد": "مدد",
        "ماد": "مدد",
        "ممدود": "مدد",
        # كلمات من جذر "علم"
        "عالم": "علم",
        "معلوم": "علم",
        "علوم": "علم",
        "تعليم": "علم",
        "معلم": "علم",
        "علامة": "علم",
        "يستعلم": "علم",
        "استعلام": "علم",
        # كلمات من جذر "ذهب"
        "ذهاب": "ذهب",
        "ذاهب": "ذهب",
        # كلمات من جذر "قرأ"
        "قرأ": "قرأ",
        "يقرأ": "قرأ",
        "قراءة": "قرأ",
        "قارئ": "قرأ",
        "مقروء": "قرأ",
        # كلمات من جذر "سمع"
        "سمع": "سمع",
        # كلمات من جذر "كسر"
        "ينكسر": "كسر",
        # حروف ومفردات أخرى
        "في": "في",
        "من": "من",
        "إلى": "إلى",
        "عن": "عن",
        "لم": "لم",
        "لن": "لن",
        "ثم": "ثم",
        "إن": "إن",
    }

    # إضافة حالات شائعة للكلمات والأنماط
    PATTERN_ROOT_MAP = {
        # أوزان الكلمات الشائعة وجذورها
        "يكتب": "كتب",
        "كاتب": "كتب",
        "مكتوب": "كتب",
        "كتاب": "كتب",
        "يدرس": "درس",
        "دارس": "درس",
        "مدروس": "درس",
        "دراسة": "درس",
        "يسمع": "سمع",
        "سامع": "سمع",
        "مسموع": "سمع",
        "سماع": "سمع",
        "استغفر": "غفر",
        "مستغفر": "غفر",
        "استغفار": "غفر",
        "انكسر": "كسر",
        "منكسر": "كسر",
        "انكسار": "كسر",
    }

    def __init__(self):
        """تهيئة مستخرج الجذور"""
        self.diacritics_processor = DiacriticsProcessor()

    def extract_root(self, word: str, algorithm: str = "hybrid") -> str:
        """
        استخراج جذر الكلمة العربية

        Args:
            word: الكلمة المراد استخراج جذرها
            algorithm: خوارزمية الاستخراج ('light', 'stem', 'pattern', 'hybrid')
                - light: خوارزمية أساسية تزيل السوابق واللواحق
                - stem: خوارزمية تجذيع (stemming) كاملة
                - pattern: خوارزمية تعتمد على الأوزان الصرفية
                - hybrid: مزيج من الخوارزميات السابقة (الأكثر دقة ولكن الأبطأ)

        Returns:
            الجذر المستخرج للكلمة
        """
        if not word or not self._is_arabic_word(word):
            return word

        # تنظيف الكلمة وإزالة التشكيل
        normalized_word = self._normalize_word(word)

        if algorithm == "light":
            return self._light_stemming(normalized_word)
        elif algorithm == "stem":
            return self._full_stemming(normalized_word)
        elif algorithm == "pattern":
            return self._pattern_matching(normalized_word)
        elif algorithm == "hybrid":
            return self._hybrid_extraction(normalized_word)
        else:
            raise ValueError(
                f"خوارزمية غير مدعومة: {algorithm}. الخوارزميات المدعومة هي: 'light', 'stem', 'pattern', 'hybrid'"
            )

    def extract_roots_from_text(self, text: str, algorithm: str = "hybrid") -> Dict[str, str]:
        """
        استخراج جذور الكلمات من نص كامل

        Args:
            text: النص المراد استخراج جذور كلماته
            algorithm: خوارزمية الاستخراج

        Returns:
            قاموس يربط بين الكلمات الأصلية وجذورها
        """
        if not text:
            return {}

        # تقسيم النص إلى كلمات
        words = re.findall(r"[\u0600-\u06FF]+", text)

        # استخراج جذر كل كلمة
        roots = {}
        for word in words:
            roots[word] = self.extract_root(word, algorithm)

        return roots

    def _normalize_word(self, word: str) -> str:
        """
        تطبيع الكلمة وتحضيرها لاستخراج الجذر

        Args:
            word: الكلمة المراد تطبيعها

        Returns:
            الكلمة بعد التطبيع
        """
        # إزالة التشكيل
        word = DiacriticsProcessor.remove_all_diacritics(word)

        # إزالة التطويل
        word = DiacriticsProcessor.remove_tatweel(word)

        # توحيد أشكال الألف
        word = word.replace("أ", "ا").replace("إ", "ا").replace("آ", "ا")

        # توحيد أشكال الهاء والتاء المربوطة
        word = word.replace("ة", "ه")

        return word

    def _light_stemming(self, word: str) -> str:
        """
        التجذيع الخفيف: إزالة السوابق واللواحق فقط

        Args:
            word: الكلمة المراد تجذيعها

        Returns:
            النتيجة بعد إزالة السوابق واللواحق
        """
        # التحقق من وجود الكلمة في قائمة الكلمات المعروفة
        if word in self.PATTERN_ROOT_MAP:
            return self.PATTERN_ROOT_MAP[word]

        # تطبيع الكلمة (توحيد الألف والهمزة والتاء المربوطة)
        word = self._normalize_word(word)

        # حفظ الكلمة الأصلية للتحقق لاحقاً
        original_word = word

        # معالجة المضعف: إذا كانت الكلمة قصيرة ويحتمل أنها مضعفة
        if len(word) <= 3 and all(c in self.COMMON_ROOT_LETTERS for c in word):
            # كلمات مثل "مدّ" (أصلها "مدد")
            if len(word) == 2:
                return word + word[-1]  # مضاعفة الحرف الأخير

        # إزالة السوابق
        for prefix in self.PREFIXES:
            if word.startswith(prefix) and len(word) > len(prefix) + 1:
                # تأكد من أن إزالة السابقة تترك كلمة ذات معنى
                # لا نزيل السابقة إذا كانت ستترك حرفاً واحداً
                if len(word) - len(prefix) > 1:
                    word = word[len(prefix) :]
                    break

        # إزالة اللواحق
        for suffix in self.SUFFIXES:
            if word.endswith(suffix) and len(word) > len(suffix) + 1:
                # تأكد من أن إزالة اللاحقة تترك كلمة ذات معنى
                if len(word) - len(suffix) > 1:
                    word = word[: -len(suffix)]
                    break

        # معالجة خاصة للكلمات التي تبدأ بالميم (قد تكون اسم مكان أو اسم مفعول أو اسم آلة)
        if original_word.startswith("م") and len(original_word) >= 4:
            # لكن نتحقق أولاً إذا كانت الميم جزءاً من جذر الكلمة (مثل "مطر")
            # من خلال التحقق ما إذا كانت الحروف المتبقية تشكل جذراً معروفاً
            stem_without_meem = original_word[1:]
            # إذا كانت الحروف المتبقية تشكل جذراً معروفاً، يمكن أن تكون الميم من أصل الكلمة
            if any(stem_without_meem.startswith(r) for r in self.COMMON_ROOTS):
                # نعيد الكلمة الأصلية ونقوم بتجذيعها بدون إزالة الميم
                word = original_word
                # ونزيل فقط اللواحق
                for suffix in self.SUFFIXES:
                    if word.endswith(suffix) and len(word) > len(suffix) + 1:
                        word = word[: -len(suffix)]
                        break

        # معالجة خاصة للكلمات التي تنتهي بتاء مربوطة
        if original_word.endswith("ة") and len(original_word) >= 3:
            # غالباً التاء المربوطة تضاف للأسماء، لذا نحذفها ونجرب مرة أخرى
            word_without_ta = original_word[:-1]
            # نقوم بتجذيع الكلمة بدون التاء
            alt_stem = self._light_stemming(word_without_ta)
            # إذا كان الجذر البديل أطول من حرف واحد، نستخدمه
            if len(alt_stem) > 1:
                return alt_stem

        # الحالة الخاصة للكلمات التي بها حروف علة (ا، و، ي)
        # نحاول معالجة الإعلال والإبدال
        if "ا" in word or "و" in word or "ي" in word:
            # محاولة استبدال بعض حروف العلة بالصيغة الأصلية
            vowel_positions = [i for i, c in enumerate(word) if c in "اوي"]
            if vowel_positions:
                # نحاول تكوين الجذر باستبدال حرف العلة الأول إذا لم يكن في البداية
                if vowel_positions[0] > 0:
                    # نجرب استبدال حرف العلة بجميع الحروف الأصلية ونرى أيها يعطي جذراً معروفاً
                    for c in "وي":  # نجرب الواو والياء كبديل
                        potential_root = (
                            word[: vowel_positions[0]] + c + word[vowel_positions[0] + 1 :]
                        )
                        if potential_root in self.COMMON_ROOTS:
                            return potential_root

        # معالجة الهمزة
        if any(c in word for c in "أإؤئء"):
            # استبدال جميع أشكال الهمزة بهمزة واحدة
            normalized = word
            for h in "أإؤئء":
                normalized = normalized.replace(h, "ء")
            # نتحقق إذا كان الجذر المطبّع معروفاً
            if normalized in self.COMMON_ROOTS:
                return normalized

        # تقصير النتيجة إلى 3 أحرف إذا كانت أطول
        # لكن نتأكد من عدم تقصير الكلمات الرباعية المعروفة
        if len(word) > 3 and not self._match_quadliteral_pattern(word):
            # نحتفظ بالحروف الثلاثة الأولى كمرشح للجذر الثلاثي
            root_candidate = word[:3]
            # نتحقق إذا كان الجذر مكون من حروف أصلية
            if all(c in self.COMMON_ROOT_LETTERS for c in root_candidate):
                return root_candidate
            # وإلا نأخذ أول ثلاثة حروف غير زائدة
            root_chars = []
            for c in word:
                if c in self.COMMON_ROOT_LETTERS and len(root_chars) < 3:
                    root_chars.append(c)
            if len(root_chars) == 3:
                return "".join(root_chars)

        # إذا كانت النتيجة قصيرة جداً (أقل من حرفين)، نعيد الكلمة الأصلية
        if len(word) < 2:
            return original_word

        return word

    def _full_stemming(self, word: str) -> str:
        """
        خوارزمية التجذيع الكاملة

        Args:
            word: الكلمة المراد تجذيعها بشكل كامل

        Returns:
            الكلمة بعد التجذيع الكامل
        """
        # تطبيق التجذيع الخفيف أولاً
        stemmed = self._light_stemming(word)

        # إذا كانت الكلمة بعد التجذيع طويلة، نطبق المزيد من التجذيع
        if len(stemmed) > 4:
            # إزالة حروف الزيادة الشائعة
            for char in self.ADDITIONAL_LETTERS:
                # التأكد من أن الكلمة لن تصبح أقل من 3 أحرف بعد الإزالة
                if char in stemmed and len(stemmed) > 3:
                    stemmed = stemmed.replace(char, "", 1)

        # إذا كانت الكلمة ما زالت أكثر من 4 أحرف، نعتبرها رباعية ونبقي على 4 أحرف
        if len(stemmed) > 4:
            stemmed = stemmed[:4]

        return stemmed

    def _pattern_matching(self, word: str) -> str:
        """
        خوارزمية مطابقة الأوزان الصرفية

        Args:
            word: الكلمة المراد استخراج جذرها باستخدام الأوزان

        Returns:
            الجذر المستخرج باستخدام مطابقة الأوزان
        """
        # تطبيق التجذيع الخفيف أولاً
        stemmed = self._light_stemming(word)

        # مطابقة الأوزان حسب طول الكلمة بعد التجذيع
        if len(stemmed) == 3:
            # من المحتمل أنها بالفعل جذر ثلاثي
            return stemmed
        elif len(stemmed) == 4:
            # قد تكون جذر رباعي أو ثلاثي مزيد
            if self._match_quadliteral_pattern(stemmed):
                return stemmed
            else:
                # محاولة استخراج الجذر الثلاثي
                return self._extract_trilateral_from_derived(stemmed)
        elif len(stemmed) == 5:
            # من المحتمل أنها مشتقة من ثلاثي أو رباعي
            trilateral_root = self._extract_trilateral_from_derived(stemmed)
            if trilateral_root:
                return trilateral_root
            else:
                # محاولة استخراج الرباعي
                return self._extract_quadliteral(stemmed)
        elif len(stemmed) > 5:
            # محاولة استخراج الثلاثي من الكلمة الطويلة
            return self._extract_from_long_word(stemmed)
        else:
            # كلمة قصيرة (حرفان أو أقل) نعيدها كما هي
            return stemmed

    def _extract_trilateral_from_derived(self, word: str) -> str:
        """
        استخراج الجذر الثلاثي من كلمة مشتقة

        Args:
            word: الكلمة المشتقة

        Returns:
            الجذر الثلاثي إذا تم التعرف عليه، وإلا الكلمة الأصلية
        """
        # التطبيقات المختلفة للأوزان المعروفة
        if len(word) == 4:
            # الأوزان: أفعل، فعّل، فاعل
            if word[0] == "ا":
                # من المحتمل أنها على وزن أفعل
                return word[1:]
            elif word[2] == word[1]:
                # قد تكون على وزن فعّل
                return word[0] + word[1] + word[3]
            elif word[1] == "ا":
                # قد تكون على وزن فاعل
                return word[0] + word[2] + word[3]

        elif len(word) == 5:
            # الأوزان: انفعل، افتعل، تفعّل، تفاعل
            if word[:2] == "ان":
                # قد تكون على وزن انفعل
                return word[2:]
            elif word[:2] == "اف" and word[3] == "ع":
                # قد تكون على وزن افتعل
                return word[2] + word[3] + word[4]
            elif word[0] == "ت" and word[3] == word[2]:
                # قد تكون على وزن تفعّل
                return word[1] + word[2] + word[4]
            elif word[0] == "ت" and word[2] == "ا":
                # قد تكون على وزن تفاعل
                return word[1] + word[3] + word[4]

        elif len(word) == 6:
            # الأوزان: استفعل، افعوعل، افعالّ، افعوّل
            if word[:3] == "است":
                # قد تكون على وزن استفعل
                return word[3:]
            elif word[:2] == "اف" and word[3] == "و" and word[4] == word[2]:
                # قد تكون على وزن افعوعل
                return word[2] + word[4] + word[5]

        # إذا لم تنطبق أي من القواعد السابقة، نحاول استخراج الحروف الأكثر احتمالاً للجذر
        return self._extract_most_likely_root(word)

    def _extract_quadliteral(self, word: str) -> str:
        """
        استخراج الجذر الرباعي من كلمة

        Args:
            word: الكلمة المراد استخراج الجذر الرباعي منها

        Returns:
            الجذر الرباعي المحتمل
        """
        # معالجة الأوزان الرباعية المعروفة
        if len(word) == 5:
            # الوزن: تفعلل
            if word[0] == "ت":
                return word[1:5]
        elif len(word) == 6:
            # الوزن: افعنلل
            if word[:2] == "اف" and word[3] == "ن":
                return word[2] + word[4:6]

        # إذا لم نتمكن من استخراج الرباعي بالقواعد، نعيد أول 4 أحرف غير زائدة
        root_chars = []
        for char in word:
            if char in self.COMMON_ROOT_LETTERS and len(root_chars) < 4:
                root_chars.append(char)

        if len(root_chars) == 4:
            return "".join(root_chars)
        elif len(root_chars) > 0:
            # إذا لم نجد 4 أحرف، نعيد ما وجدناه
            return "".join(root_chars)
        else:
            # إذا لم نجد أي حروف محتملة للجذر، نعيد أول 4 أحرف
            return word[: min(4, len(word))]

    def _extract_from_long_word(self, word: str) -> str:
        """
        استخراج الجذر من كلمة طويلة

        Args:
            word: الكلمة الطويلة

        Returns:
            الجذر المحتمل
        """
        # البحث عن الحروف الأكثر احتمالاً للجذر
        root_chars = []
        for char in word:
            if char in self.COMMON_ROOT_LETTERS and len(root_chars) < 3:
                root_chars.append(char)

        if len(root_chars) == 3:
            return "".join(root_chars)
        elif len(root_chars) > 0:
            # إذا لم نجد 3 أحرف، نعيد ما وجدناه
            return "".join(root_chars)
        else:
            # إذا لم نجد أي حروف محتملة للجذر، نعيد أول 3 أحرف
            return word[: min(3, len(word))]

    def _extract_most_likely_root(self, word: str) -> str:
        """
        استخراج الحروف الأكثر احتمالاً للجذر

        Args:
            word: الكلمة المراد استخراج الجذر منها

        Returns:
            الجذر الأكثر احتمالاً
        """
        # البحث عن الحروف الأكثر احتمالاً للجذر
        root_chars = []
        for char in word:
            if char in self.COMMON_ROOT_LETTERS and len(root_chars) < 3:
                root_chars.append(char)

        if len(root_chars) == 3:
            root = "".join(root_chars)
            if root in self.COMMON_ROOTS:
                return root

        # إذا كانت الكلمة قصيرة (3-4 أحرف)، من المحتمل أنها قريبة من الجذر
        if 3 <= len(word) <= 4:
            return word

        # للكلمات الأطول، نعيد أول 3 أحرف
        return word[: min(3, len(word))]

    def _hybrid_extraction(self, word: str) -> str:
        """
        خوارزمية هجينة لاستخراج الجذر من الكلمة

        تجمع بين عدة طرق لاستخراج الجذر من الكلمة العربية:
        1. البحث في قاموس ثابت للجذور
        2. استخدام خوارزمية التجريد الخفيف
        3. استخدام خوارزمية التجريد الكامل
        4. مطابقة الأنماط

        Args:
            word: الكلمة المراد استخراج جذرها

        Returns:
            الجذر المستخرج أو سلسلة فارغة في حالة الفشل
        """
        # تنظيف الكلمة وإزالة التشكيل
        normalized_word = self._normalize_word(word)

        # 1. التحقق أولاً من القاموس الخاص للحالات الخاصة
        if normalized_word in self.SPECIAL_CASES:
            return self.SPECIAL_CASES[normalized_word]

        # 2. التحقق من قاموس ثابت للأنماط المعروفة
        if normalized_word in self.PATTERN_ROOT_MAP:
            return self.PATTERN_ROOT_MAP[normalized_word]

        # 3. تجريب خوارزمية التجريد الخفيف
        light_stemmed = self._light_stemming(normalized_word)

        # 4. تجريب خوارزمية التجريد الكامل
        stem_stemmed = self._full_stemming(normalized_word)

        # 5. تجريب مطابقة الأنماط
        pattern_match = self._pattern_matching(normalized_word)

        # تجميع نتائج الخوارزميات المختلفة
        candidates = []

        if light_stemmed and light_stemmed != normalized_word:
            candidates.append(light_stemmed)

        if stem_stemmed and stem_stemmed != normalized_word and stem_stemmed != light_stemmed:
            candidates.append(stem_stemmed)

        if pattern_match and pattern_match != normalized_word and pattern_match not in candidates:
            candidates.append(pattern_match)

        # معالجة خاصة للكلمات الطويلة
        if len(normalized_word) > 5:
            # الكلمات التي تبدأ بـ "است" مثل "استغفر"
            if normalized_word.startswith("است") and len(normalized_word) >= 6:
                potential_root = normalized_word[3:6]
                if self._is_valid_root(potential_root):
                    candidates.append(potential_root)

            # الكلمات التي تبدأ بـ "انف" أو "انق" مثل "انفعل" أو "انقلب"
            elif normalized_word.startswith(("انف", "انق")) and len(normalized_word) >= 5:
                potential_root = normalized_word[2:5]
                if self._is_valid_root(potential_root):
                    candidates.append(potential_root)

            # الكلمات التي تبدأ بـ "افت" مثل "افتعل"
            elif normalized_word.startswith("افت") and len(normalized_word) >= 5:
                potential_root = normalized_word[1] + normalized_word[3:5]
                if self._is_valid_root(potential_root):
                    candidates.append(potential_root)

            # الأفعال التي تبدأ بحروف المضارعة
            elif normalized_word[0] in "أنيت" and len(normalized_word) >= 4:
                potential_root = normalized_word[1:4]
                if self._is_valid_root(potential_root):
                    candidates.append(potential_root)

            # الأفعال التي تبدأ ب "سي" مثل "سيذهب"
            elif normalized_word.startswith("سي") and len(normalized_word) >= 5:
                potential_root = normalized_word[2:5]
                if self._is_valid_root(potential_root):
                    candidates.append(potential_root)

            # الكلمات التي تنتهي بـ "وا" مثل "ذهبوا" (واو الجماعة)
            elif normalized_word.endswith("وا") and len(normalized_word) >= 5:
                potential_root = normalized_word[:-2]
                if len(potential_root) == 3 and self._is_valid_root(potential_root):
                    candidates.append(potential_root)
                elif len(potential_root) > 3:
                    # تجريد إضافي للكلمات الأطول
                    shorter_root = self._full_stemming(potential_root)
                    if shorter_root and self._is_valid_root(shorter_root):
                        candidates.append(shorter_root)

            # الكلمات التي تبدأ بـ "م" مثل "مكتبة" (قد تكون اسم مكان أو اسم مفعول)
            elif normalized_word.startswith("م") and len(normalized_word) >= 5:
                if normalized_word.endswith("ة"):
                    # معالجة خاصة لكلمة مثل "مكتبة"
                    potential_root = normalized_word[1:4]
                    if self._is_valid_root(potential_root):
                        candidates.append(potential_root)
                else:
                    potential_root = normalized_word[1:4]
                    if self._is_valid_root(potential_root):
                        candidates.append(potential_root)

                    # تجريب جذر آخر محتمل
                    if len(normalized_word) >= 6:
                        another_potential = normalized_word[1] + normalized_word[3:5]
                        if self._is_valid_root(another_potential):
                            candidates.append(another_potential)

        # معالجة خاصة للكلمات المحتوية على همزة
        if (
            "أ" in normalized_word
            or "ؤ" in normalized_word
            or "ئ" in normalized_word
            or "ء" in normalized_word
        ):
            # استبدال الهمزة بـ "ء" للتوحيد
            normalized_with_hamza = (
                normalized_word.replace("أ", "ء").replace("ؤ", "ء").replace("ئ", "ء")
            )

            # تجربة استخراج الجذر بعد توحيد الهمزة
            hamza_stem = self._full_stemming(normalized_with_hamza)
            if hamza_stem and hamza_stem not in candidates:
                # إعادة الهمزة إلى شكلها الأصلي
                if "ء" in hamza_stem:
                    hamza_stem = hamza_stem.replace("ء", "أ")
                candidates.append(hamza_stem)

            # حالة خاصة لكلمات مثل "سأل"
            if len(normalized_word) == 3 and "أ" in normalized_word:
                # قد تكون الهمزة جزءًا من الجذر نفسه
                candidates.append(normalized_word)

        # تقييم المرشحين واختيار الأفضل
        if candidates:
            # نعطي أوزانًا للمرشحين بناءً على عدة معايير
            scored_candidates = []

            for candidate in candidates:
                score = 0

                # المرشحون ذوو الطول 3 أحرف مفضلون (معظم الجذور العربية ثلاثية)
                if len(candidate) == 3:
                    score += 3
                elif len(candidate) == 4:  # الجذور الرباعية أقل شيوعاً
                    score += 2
                else:
                    score += 1

                # تفضيل المرشحين الذين لا يحتوون على حروف العلة في وسط الكلمة
                if len(candidate) >= 3 and candidate[1] not in "اويأؤئ":
                    score += 1

                # تفضيل المرشحين الذين لا يحتوون على أحرف متكررة
                if len(set(candidate)) == len(candidate):
                    score += 1

                # تفضيل المرشحين الذين يظهرون في قائمة الجذور المعروفة
                if candidate in self.COMMON_ROOTS:
                    score += 2

                scored_candidates.append((candidate, score))

            # ترتيب المرشحين بناءً على النقاط
            scored_candidates.sort(key=lambda x: x[1], reverse=True)

            # إعادة المرشح الأعلى نقاطًا
            return scored_candidates[0][0]

        # إذا لم يكن هناك مرشحون، نعيد الكلمة الأصلية
        return normalized_word

    def _is_valid_root(self, root: str) -> bool:
        """
        التحقق من صحة الجذر المستخرج

        Args:
            root: الجذر المراد التحقق منه

        Returns:
            True إذا كان الجذر صحيحاً، False خلاف ذلك
        """
        # الجذر يجب أن يكون من 2 إلى 5 أحرف (الغالبية 3 أو 4)
        if len(root) < 2 or len(root) > 5:
            return False

        # يجب أن يحتوي على حروف عربية فقط
        if not all(
            c in self.COMMON_ROOT_LETTERS or c in self.VOWELS or c in self.HAMZA_FORMS for c in root
        ):
            return False

        # يجب ألا يحتوي على أكثر من حرفين متتاليين من نفس النوع
        for i in range(len(root) - 2):
            if root[i] == root[i + 1] == root[i + 2]:
                return False

        # يجب ألا يحتوي على أكثر من حرفين من حروف العلة
        vowel_count = sum(1 for c in root if c in self.VOWELS or c in self.HAMZA_FORMS)
        if vowel_count > 2:
            return False

        # التحقق من أن معظم الحروف من الحروف الأصلية وليست من الزوائد
        original_count = sum(1 for c in root if c in self.COMMON_ROOT_LETTERS)
        if original_count < len(root) * 0.6:  # 60% على الأقل من الحروف أصلية
            return False

        return True

    def _match_quadliteral_pattern(self, word: str) -> bool:
        """
        التحقق مما إذا كانت الكلمة تطابق أحد أوزان الرباعي

        Args:
            word: الكلمة المراد فحصها

        Returns:
            True إذا كانت تطابق وزن رباعي، وإلا False
        """
        # في الغالب، الرباعي يكون 4 أحرف أصلية
        if len(word) != 4:
            return False

        # معظم حروف الرباعي تكون من الحروف الأصلية
        count = sum(1 for char in word if char in self.COMMON_ROOT_LETTERS)
        return count >= 3

    def _is_arabic_word(self, word: str) -> bool:
        """
        التحقق مما إذا كانت الكلمة عربية

        Args:
            word: الكلمة المراد فحصها

        Returns:
            True إذا كانت الكلمة عربية، وإلا False
        """
        if not word:
            return False

        # التحقق من وجود أحرف عربية في الكلمة
        arabic_chars = [c for c in word if "\u0600" <= c <= "\u06ff"]
        return len(arabic_chars) > 0

    def get_word_pattern(self, word: str) -> str:
        """
        استخراج الوزن الصرفي المحتمل للكلمة

        Args:
            word: الكلمة المراد استخراج وزنها

        Returns:
            الوزن الصرفي المحتمل للكلمة
        """
        # تنظيف الكلمة
        normalized_word = self._normalize_word(word)

        # قائمة بالأوزان المعروفة للكلمات الشائعة مع توسيعها لتشمل الحالات الإشكالية
        common_patterns = {
            # أوزان الأفعال
            "كتب": "فعل",
            "يكتب": "يفعل",
            "اكتب": "افعل",
            "درس": "فعل",
            "يدرس": "يفعل",
            "ادرس": "افعل",
            "قال": "فعل",
            "يقول": "يفعل",
            "قل": "فل",
            "سأل": "فعل",
            "يسأل": "يفعل",
            "اسأل": "افعل",
            "علم": "فعل",
            "يعلم": "يفعل",
            "اعلم": "افعل",
            "ذهب": "فعل",
            "يذهب": "يفعل",
            "سمع": "فعل",
            "يسمع": "يفعل",
            "اسمع": "افعل",
            "استغفر": "استفعل",
            "يستغفر": "يستفعل",
            "انكسر": "انفعل",
            "ينكسر": "ينفعل",
            "انكسار": "انفعل",
            "منكسر": "منفعل",
            # إضافة حالات إشكالية
            "مدّ": "فعّ",
            "يمدّ": "يفعّ",
            "مدّة": "فعّة",
            "ممدود": "مفعول",
            "يستغفرون": "يستفعلون",
            "سيذهب": "سيفعل",
            "ذهبوا": "فعلوا",
            "كتبوا": "فعلوا",
            "مكتوبات": "مفعولات",
            # أوزان الأسماء
            "كتاب": "فعال",
            "كاتب": "فاعل",
            "مكتوب": "مفعول",
            "مكتب": "مفعل",
            "كتب": "فعل",
            "كتبة": "فعلة",
            "كتابة": "فعالة",
            "مكتبة": "مفعلة",
            "درس": "فعل",
            "دراسة": "فعالة",
            "دارس": "فاعل",
            "مدروس": "مفعول",
            "مدرسة": "مفعلة",
            "دروس": "فعول",
            "مدارس": "مفاعل",
            "قول": "فعل",
            "أقوال": "أفعال",
            "قائل": "فاعل",
            "مقول": "مفعول",
            "مقال": "مفال",
            "مقالة": "مفالة",
            "أقاويل": "أفاعيل",
            "سؤال": "فعال",
            "سائل": "فاعل",
            "مسؤول": "مفعول",
            "أسئلة": "أفعلة",
            "علم": "فعل",
            "عالم": "فاعل",
            "معلوم": "مفعول",
            "علوم": "فعول",
            "علماء": "فعلاء",
            "تعليم": "تفعيل",
            "علامة": "فعالة",
            "استعلام": "استفعال",
            "ذهاب": "فعال",
            "ذاهب": "فاعل",
            "قراءة": "فعالة",
            "قارئ": "فاعل",
            "مقروء": "مفعول",
            "سامع": "فاعل",
            "مسموع": "مفعول",
            "استغفار": "استفعال",
            "مستغفر": "مستفعل",
            "انكسار": "انفعال",
            "منكسر": "منفعل",
            # إضافة كلمات ذات همزة
            "قرأ": "فعل",
            "يقرأ": "يفعل",
            "قراءة": "فعالة",
            "إلى": "إلى",
            "إن": "إن",
        }

        # التحقق من القائمة المعروفة
        if normalized_word in common_patterns:
            return common_patterns[normalized_word]

        # تحقق من حالات خاصة للكلمات المشددة
        if "ّ" in word:
            # حالة الكلمات المشددة مثل "مدّ"
            # نعتبر الحرف المشدد كحرفين متتاليين في الميزان الصرفي
            pattern_chars = []
            for i, char in enumerate(word):
                if char == "ّ":  # إذا وجدنا شدة
                    if i > 0:  # للتأكد من أنها ليست أول حرف
                        # نضيف ف أو ع أو ل حسب موقع الشدة في الكلمة
                        root_idx = len(pattern_chars) % 3
                        if root_idx == 0:
                            pattern_chars.append("ف")
                        elif root_idx == 1:
                            pattern_chars.append("ع")
                        else:
                            pattern_chars.append("ل")
                else:
                    # نضيف الحرف نفسه إذا كان من الزوائد، وإلا نضيف ف أو ع أو ل
                    if char in "اوينمتسلبهكأءؤئ":
                        pattern_chars.append(char)
                    else:
                        root_idx = len(pattern_chars) % 3
                        if root_idx == 0:
                            pattern_chars.append("ف")
                        elif root_idx == 1:
                            pattern_chars.append("ع")
                        else:
                            pattern_chars.append("ل")

            return "".join(pattern_chars)

        # محاولة استخراج الجذر
        root = self._hybrid_extraction(normalized_word)

        # تفشل عملية استخراج الجذر
        if not root or root == normalized_word:
            # تحسين للكلمات التي لم يتم استخراج جذرها بشكل صحيح
            if normalized_word.startswith("است") and len(normalized_word) >= 6:
                return "استفعل" + normalized_word[6:]
            elif normalized_word.startswith("انف") and len(normalized_word) >= 5:
                return "انفعل" + normalized_word[5:]
            elif normalized_word.startswith("افت") and len(normalized_word) >= 5:
                return "افتعل" + normalized_word[5:]
            elif normalized_word.startswith("م") and len(normalized_word) >= 4:
                # قد تكون من اسم المفعول أو اسم المكان
                if "و" in normalized_word[1:3]:
                    return "مفعول" + normalized_word[4:]
                else:
                    return "مفعل" + normalized_word[3:]
            elif normalized_word.startswith("ي") and len(normalized_word) >= 4:
                return "يفعل" + normalized_word[4:]
            elif normalized_word.startswith("ت") and len(normalized_word) >= 4:
                return "تفعل" + normalized_word[4:]
            elif normalized_word.endswith("وا") and len(normalized_word) >= 4:
                return normalized_word[:-2] + "وا"
            elif normalized_word.endswith("ون") and len(normalized_word) >= 5:
                if normalized_word.startswith("ي"):
                    return "يفعلون"
                else:
                    return "فاعلون"
            elif normalized_word.endswith("ين") and len(normalized_word) >= 5:
                return "فاعلين"
            elif normalized_word.endswith("ات") and len(normalized_word) >= 5:
                return normalized_word[:-3] + "ات"
            elif len(normalized_word) <= 3:
                return normalized_word
            else:
                return "غير معروف"

        # بناء الوزن باستخدام ف، ع، ل بناءً على مواقع أحرف الجذر
        pattern = list(normalized_word)
        root_index = 0

        # محاولة معالجة الكلمات الطويلة مثل "يستغفرون"
        if len(normalized_word) > 6 and normalized_word.endswith(("ون", "ين", "ات", "وا", "ان")):
            suffix = ""
            word_base = normalized_word

            if normalized_word.endswith("ون"):
                suffix = "ون"
                word_base = normalized_word[:-2]
            elif normalized_word.endswith("ين"):
                suffix = "ين"
                word_base = normalized_word[:-2]
            elif normalized_word.endswith("ات"):
                suffix = "ات"
                word_base = normalized_word[:-2]
            elif normalized_word.endswith("وا"):
                suffix = "وا"
                word_base = normalized_word[:-2]
            elif normalized_word.endswith("ان"):
                suffix = "ان"
                word_base = normalized_word[:-2]

            # استخراج الوزن للكلمة الأساسية
            base_pattern = self.get_word_pattern(word_base)
            if base_pattern != "غير معروف":
                return base_pattern + suffix

        # تحديد مواقع أحرف الجذر في الكلمة
        root_positions = []
        temp_word = normalized_word
        for char in root:
            pos = temp_word.find(char)
            if pos != -1:
                root_positions.append(pos)
                # استبدال الحرف الذي تم العثور عليه لتجنب تكراره
                temp_word = temp_word[:pos] + "#" + temp_word[pos + 1 :]
            else:
                # حالة عدم العثور على حرف الجذر في الكلمة (قد يكون بسبب تغير في الإعلال)
                # نستمر دون إضافة هذا الحرف إلى المواقع
                pass

        # تحويل كل حرف في الكلمة إلى الميزان الصرفي المناسب
        for i in range(len(normalized_word)):
            if i in root_positions:
                # الحرف من الجذر
                if root_index == 0:
                    pattern[i] = "ف"
                elif root_index == 1:
                    pattern[i] = "ع"
                else:
                    pattern[i] = "ل"
                root_index += 1
            else:
                # الحرف زائد، نحتفظ به كما هو
                pass

        if root_index == 0:  # لم نتمكن من تحديد أي من مواقع أحرف الجذر
            # نتحقق من أنماط معروفة بناءً على طول الكلمة والبادئة
            if normalized_word.startswith("است") and len(normalized_word) >= 6:
                return "استفعال"
            elif normalized_word.startswith("انف") and len(normalized_word) >= 5:
                return "انفعال"
            elif normalized_word.startswith("م") and len(normalized_word) >= 3:
                if normalized_word.startswith("مست") and len(normalized_word) >= 6:
                    return "مستفعل"
                elif len(normalized_word) >= 6 and "و" in normalized_word[1:4]:
                    return "مفعول"
                else:
                    return "مفعل"
            elif normalized_word.startswith("ي") and len(normalized_word) >= 4:
                return "يفعل"
            else:
                return "غير معروف"

        return "".join(pattern)

    def group_by_root(self, words: List[str], algorithm: str = "hybrid") -> Dict[str, List[str]]:
        """
        تجميع الكلمات حسب جذورها

        Args:
            words: قائمة الكلمات المراد تجميعها
            algorithm: خوارزمية استخراج الجذر

        Returns:
            قاموس يجمع الكلمات حسب جذورها
        """
        if not words:
            return {}

        # استخراج جذر كل كلمة وتجميعها
        groups = {}
        for word in words:
            root = self.extract_root(word, algorithm)

            if root not in groups:
                groups[root] = []

            groups[root].append(word)

        return groups

    def find_related_words(
        self, word: str, word_list: List[str], algorithm: str = "hybrid"
    ) -> List[str]:
        """
        البحث عن الكلمات المرتبطة بكلمة معينة (نفس الجذر)

        Args:
            word: الكلمة المراد البحث عن كلمات مرتبطة بها
            word_list: قائمة الكلمات للبحث فيها
            algorithm: خوارزمية استخراج الجذر

        Returns:
            قائمة بالكلمات المرتبطة (من نفس الجذر)
        """
        if not word or not word_list:
            return []

        # استخراج جذر الكلمة
        target_root = self.extract_root(word, algorithm)

        # البحث عن كلمات بنفس الجذر
        related = []
        for w in word_list:
            root = self.extract_root(w, algorithm)
            if root == target_root and w != word:
                related.append(w)

        return related
