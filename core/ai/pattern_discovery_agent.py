#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
وكيل اكتشاف الأنماط
يكتشف الأنماط العددية والحرفية في القرآن الكريم ويحللها
"""

import logging
from typing import Dict, List, Any, Optional, Union
import re
import math

from core.ai.multi_agent_system import Agent

# إعداد التسجيل
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class PatternDiscoveryAgent(Agent):
    """
    وكيل متخصص في اكتشاف الأنماط في القرآن الكريم

    يقوم هذا الوكيل بالمهام التالية:
    1. اكتشاف الأنماط العددية في القرآن
    2. تحليل تكرار الحروف والكلمات
    3. اكتشاف التناظر والعلاقات الهيكلية
    4. تحليل الحروف المقطعة في أوائل السور
    """

    def __init__(self, name: str = "pattern_discovery_agent"):
        """
        تهيئة وكيل اكتشاف الأنماط

        Args:
            name: اسم الوكيل
        """
        super().__init__(name)

        # أنواع الأنماط التي يكتشفها الوكيل
        self.pattern_types = [
            "أنماط عددية",
            "أنماط حرفية",
            "أنماط هيكلية",
            "تناظرات",
            "تكرارات",
        ]

        # الحروف المقطعة في أوائل السور
        self.disconnected_letters = [
            "الم",
            "المص",
            "الر",
            "المر",
            "كهيعص",
            "طه",
            "طسم",
            "طس",
            "يس",
            "ص",
            "حم",
            "حم عسق",
            "ق",
            "ن",
        ]

        # الأرقام المذكورة في القرآن للتحليل
        self.mentioned_numbers = [
            1,
            2,
            3,
            4,
            5,
            7,
            9,
            10,
            11,
            12,
            19,
            30,
            40,
            70,
            99,
            300,
            309,
            950,
            1000,
            50000,
        ]

        logger.info(f"تم إنشاء وكيل اكتشاف الأنماط: {name}")

    def process(self, query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        معالجة الاستعلام واكتشاف الأنماط في القرآن

        Args:
            query: الاستعلام المراد معالجته
            context: سياق إضافي للمعالجة (اختياري)

        Returns:
            نتائج اكتشاف الأنماط
        """
        logger.info(f"معالجة الاستعلام: {query}")

        # التأكد من وجود سياق
        if context is None:
            context = {}

        # استخراج الآيات من السياق (إذا كانت متاحة)
        verses = context.get("verses", [])

        # استخراج بيانات السور إذا كانت متاحة
        surahs = context.get("surahs", [])

        # اكتشاف الأنماط العددية
        numerical_patterns = self._discover_numerical_patterns(verses, surahs)

        # اكتشاف الأنماط الحرفية
        letter_patterns = self._discover_letter_patterns(verses, surahs)

        # اكتشاف التناظرات والعلاقات الهيكلية
        structural_patterns = self._discover_structural_patterns(verses, surahs)

        # تحليل الحروف المقطعة
        disconnected_letters_analysis = self._analyze_disconnected_letters(surahs)

        # تجميع النتائج
        result = {
            "numerical_patterns": numerical_patterns,
            "letter_patterns": letter_patterns,
            "structural_patterns": structural_patterns,
            "disconnected_letters_analysis": disconnected_letters_analysis,
            "confidence": 0.85,  # ثقة افتراضية
            "metadata": {
                "agent": self.name,
                "query": query,
                "num_verses_analyzed": len(verses),
                "num_surahs_analyzed": len(surahs),
            },
        }

        return result

    def _discover_numerical_patterns(
        self, verses: List[Dict[str, Any]], surahs: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        اكتشاف الأنماط العددية في القرآن

        Args:
            verses: قائمة الآيات
            surahs: قائمة السور

        Returns:
            الأنماط العددية المكتشفة
        """
        # استخراج الأعداد المذكورة في الآيات
        mentioned_numbers = self._extract_mentioned_numbers(verses)

        # تحليل العلاقات العددية بين السور
        surah_relationships = self._analyze_surah_numerical_relationships(surahs)

        # تحليل تكرار الكلمات الدالة على الأعداد
        number_word_frequencies = self._analyze_number_word_frequencies(verses)

        # البحث عن أنماط عددية خاصة (مثل الرقم 19)
        special_patterns = self._discover_special_numerical_patterns(verses, surahs)

        return {
            "mentioned_numbers": mentioned_numbers,
            "surah_relationships": surah_relationships,
            "number_word_frequencies": number_word_frequencies,
            "special_patterns": special_patterns,
        }

    def _extract_mentioned_numbers(self, verses: List[Dict[str, Any]]) -> Dict[int, int]:
        """
        استخراج الأعداد المذكورة في الآيات وعدد مرات ذكرها

        Args:
            verses: قائمة الآيات

        Returns:
            قاموس بالأعداد المذكورة وعدد مرات ذكرها
        """
        # قاموس لتخزين الأعداد المذكورة وعدد مرات ذكرها
        number_counts = {num: 0 for num in self.mentioned_numbers}

        # قاموس لتحويل الكلمات العربية إلى أرقام
        number_words = {
            "واحد": 1,
            "اثنان": 2,
            "ثلاثة": 3,
            "أربعة": 4,
            "خمسة": 5,
            "ستة": 6,
            "سبعة": 7,
            "ثمانية": 8,
            "تسعة": 9,
            "عشرة": 10,
            "أحد عشر": 11,
            "اثنا عشر": 12,
            "سبعة عشر": 17,
            "تسعة عشر": 19,
            "عشرون": 20,
            "ثلاثون": 30,
            "أربعون": 40,
            "خمسون": 50,
            "ستون": 60,
            "سبعون": 70,
            "ثمانون": 80,
            "تسعون": 90,
            "مائة": 100,
            "ألف": 1000,
        }

        # استخراج الأعداد من نصوص الآيات
        for verse in verses:
            text = verse.get("text", "")

            # البحث عن الأرقام المذكورة بالأرقام
            for number in self.mentioned_numbers:
                # تحويل العدد إلى نص عربي
                number_str = str(number)
                # البحث عن العدد في النص
                if number_str in text:
                    number_counts[number] += 1

            # البحث عن الأعداد المذكورة بالكلمات
            for word, number in number_words.items():
                if word in text and number in self.mentioned_numbers:
                    number_counts[number] += 1

        # إزالة الأعداد التي لم تُذكر
        mentioned_numbers = {k: v for k, v in number_counts.items() if v > 0}

        return mentioned_numbers

    def _analyze_surah_numerical_relationships(
        self, surahs: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        تحليل العلاقات العددية بين السور

        Args:
            surahs: قائمة السور

        Returns:
            العلاقات العددية المكتشفة
        """
        relationships = []

        # فحص العلاقات بين أرقام السور وعدد آياتها
        for i, surah in enumerate(surahs):
            surah_number = surah.get("number", i + 1)
            verses_count = len(surah.get("verses", []))

            # فحص العلاقات الرياضية البسيطة
            if surah_number == verses_count:
                relationships.append(
                    {
                        "type": "تساوي",
                        "surah": surah.get("name", ""),
                        "surah_number": surah_number,
                        "verses_count": verses_count,
                        "description": f"عدد آيات سورة {surah.get('name', '')} يساوي رقم السورة ({surah_number})",
                    }
                )

            if verses_count % surah_number == 0:
                relationships.append(
                    {
                        "type": "قسمة",
                        "surah": surah.get("name", ""),
                        "surah_number": surah_number,
                        "verses_count": verses_count,
                        "description": f"عدد آيات سورة {surah.get('name', '')} ({verses_count}) هو مضاعف لرقم السورة ({surah_number})",
                    }
                )

            if math.gcd(surah_number, verses_count) > 1:
                relationships.append(
                    {
                        "type": "قاسم مشترك",
                        "surah": surah.get("name", ""),
                        "surah_number": surah_number,
                        "verses_count": verses_count,
                        "gcd": math.gcd(surah_number, verses_count),
                        "description": f"رقم سورة {surah.get('name', '')} ({surah_number}) وعدد آياتها ({verses_count}) لهما قاسم مشترك ({math.gcd(surah_number, verses_count)})",
                    }
                )

        # فحص العلاقات بين السور المتتالية
        for i in range(len(surahs) - 1):
            surah1 = surahs[i]
            surah2 = surahs[i + 1]

            surah1_number = surah1.get("number", i + 1)
            surah2_number = surah2.get("number", i + 2)

            surah1_verses = len(surah1.get("verses", []))
            surah2_verses = len(surah2.get("verses", []))

            # البحث عن أنماط مثيرة للاهتمام
            if self._is_interesting_numerical_relationship(
                surah1_number, surah2_number, surah1_verses, surah2_verses
            ):
                relationships.append(
                    {
                        "type": "علاقة متتالية",
                        "surah1": surah1.get("name", ""),
                        "surah2": surah2.get("name", ""),
                        "surah1_number": surah1_number,
                        "surah2_number": surah2_number,
                        "surah1_verses": surah1_verses,
                        "surah2_verses": surah2_verses,
                        "description": self._describe_numerical_relationship(surah1, surah2),
                    }
                )

        return relationships

    def _is_interesting_numerical_relationship(
        self, surah1_num: int, surah2_num: int, surah1_verses: int, surah2_verses: int
    ) -> bool:
        """
        تحديد ما إذا كانت العلاقة العددية بين سورتين مثيرة للاهتمام

        Args:
            surah1_num: رقم السورة الأولى
            surah2_num: رقم السورة الثانية
            surah1_verses: عدد آيات السورة الأولى
            surah2_verses: عدد آيات السورة الثانية

        Returns:
            ما إذا كانت العلاقة مثيرة للاهتمام
        """
        # فحص بعض العلاقات المثيرة للاهتمام
        if surah1_verses == surah2_verses:
            return True

        if surah1_verses + surah2_verses == surah1_num + surah2_num:
            return True

        if abs(surah1_verses - surah2_verses) == abs(surah1_num - surah2_num):
            return True

        if surah1_verses * surah2_num == surah2_verses * surah1_num:
            return True

        if math.gcd(surah1_verses, surah2_verses) > 1:
            return True

        return False

    def _describe_numerical_relationship(
        self, surah1: Dict[str, Any], surah2: Dict[str, Any]
    ) -> str:
        """
        وصف العلاقة العددية بين سورتين

        Args:
            surah1: معلومات السورة الأولى
            surah2: معلومات السورة الثانية

        Returns:
            وصف العلاقة العددية
        """
        surah1_name = surah1.get("name", "")
        surah2_name = surah2.get("name", "")

        surah1_num = surah1.get("number", 0)
        surah2_num = surah2.get("number", 0)

        surah1_verses = len(surah1.get("verses", []))
        surah2_verses = len(surah2.get("verses", []))

        # تحديد نوع العلاقة
        if surah1_verses == surah2_verses:
            return f"سورة {surah1_name} وسورة {surah2_name} لهما نفس عدد الآيات ({surah1_verses})"

        if surah1_verses + surah2_verses == surah1_num + surah2_num:
            return f"مجموع آيات سورة {surah1_name} ({surah1_verses}) وسورة {surah2_name} ({surah2_verses}) يساوي مجموع رقمي السورتين ({surah1_num + surah2_num})"

        if abs(surah1_verses - surah2_verses) == abs(surah1_num - surah2_num):
            return f"الفرق بين عدد آيات سورة {surah1_name} ({surah1_verses}) وسورة {surah2_name} ({surah2_verses}) يساوي الفرق بين رقمي السورتين ({abs(surah1_num - surah2_num)})"

        if surah1_verses * surah2_num == surah2_verses * surah1_num:
            return f"حاصل ضرب عدد آيات سورة {surah1_name} ({surah1_verses}) في رقم سورة {surah2_name} ({surah2_num}) يساوي حاصل ضرب عدد آيات سورة {surah2_name} ({surah2_verses}) في رقم سورة {surah1_name} ({surah1_num})"

        if math.gcd(surah1_verses, surah2_verses) > 1:
            return f"عدد آيات سورة {surah1_name} ({surah1_verses}) وسورة {surah2_name} ({surah2_verses}) لهما قاسم مشترك ({math.gcd(surah1_verses, surah2_verses)})"

        return f"توجد علاقة عددية بين سورة {surah1_name} وسورة {surah2_name}"

    def _analyze_number_word_frequencies(self, verses: List[Dict[str, Any]]) -> Dict[str, int]:
        """
        تحليل تكرار الكلمات الدالة على الأعداد

        Args:
            verses: قائمة الآيات

        Returns:
            تكرار الكلمات الدالة على الأعداد
        """
        # قائمة بالكلمات الدالة على الأعداد
        number_words = [
            "واحد",
            "اثنان",
            "ثلاثة",
            "أربعة",
            "خمسة",
            "ستة",
            "سبعة",
            "ثمانية",
            "تسعة",
            "عشرة",
            "أحد عشر",
            "اثنا عشر",
            "سبعة عشر",
            "تسعة عشر",
            "عشرون",
            "ثلاثون",
            "أربعون",
            "خمسون",
            "ستون",
            "سبعون",
            "ثمانون",
            "تسعون",
            "مائة",
            "ألف",
        ]

        # قاموس لتخزين تكرار الكلمات
        word_frequencies = {word: 0 for word in number_words}

        # حساب تكرار الكلمات في كل آية
        for verse in verses:
            text = verse.get("text", "")

            for word in number_words:
                word_frequencies[word] += text.count(word)

        # إزالة الكلمات التي لم تُذكر
        mentioned_words = {k: v for k, v in word_frequencies.items() if v > 0}

        return mentioned_words

    def _discover_special_numerical_patterns(
        self, verses: List[Dict[str, Any]], surahs: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        اكتشاف أنماط عددية خاصة

        Args:
            verses: قائمة الآيات
            surahs: قائمة السور

        Returns:
            الأنماط العددية الخاصة المكتشفة
        """
        special_patterns = []

        # مثال: البحث عن أنماط متعلقة بالرقم 19
        pattern_19 = self._analyze_pattern_19(verses, surahs)
        if pattern_19:
            special_patterns.append(pattern_19)

        # مثال: البحث عن أنماط متعلقة بالرقم 7
        pattern_7 = self._analyze_pattern_7(verses, surahs)
        if pattern_7:
            special_patterns.append(pattern_7)

        return special_patterns

    def _analyze_pattern_19(
        self, verses: List[Dict[str, Any]], surahs: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        تحليل الأنماط المتعلقة بالرقم 19

        Args:
            verses: قائمة الآيات
            surahs: قائمة السور

        Returns:
            الأنماط المتعلقة بالرقم 19
        """
        # محاكاة لتحليل نمط الرقم 19
        return {
            "number": 19,
            "description": "الرقم 19 له دلالات عددية في القرآن الكريم",
            "occurrences": [
                "مجموع السور في القرآن الكريم هو 114 (19 × 6)",
                "عدد الحروف المقطعة المختلفة في القرآن الكريم هو 14 حرفًا",
                "سورة القيامة هي السورة رقم 75 (19 × 5 - 20)",
            ],
        }

    def _analyze_pattern_7(
        self, verses: List[Dict[str, Any]], surahs: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        تحليل الأنماط المتعلقة بالرقم 7

        Args:
            verses: قائمة الآيات
            surahs: قائمة السور

        Returns:
            الأنماط المتعلقة بالرقم 7
        """
        # محاكاة لتحليل نمط الرقم 7
        return {
            "number": 7,
            "description": "الرقم 7 له دلالات عددية في القرآن الكريم",
            "occurrences": [
                "سبع سموات",
                "سبع آيات في سورة الفاتحة",
                "سبعة أحرف في البسملة لا تتكرر",
            ],
        }

    def _discover_letter_patterns(
        self, verses: List[Dict[str, Any]], surahs: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        اكتشاف الأنماط الحرفية في القرآن

        Args:
            verses: قائمة الآيات
            surahs: قائمة السور

        Returns:
            الأنماط الحرفية المكتشفة
        """
        # تحليل تكرار الحروف
        letter_frequencies = self._analyze_letter_frequencies(verses)

        # تحليل الحروف المقطعة
        disconnected_letters = self._analyze_disconnected_letters(surahs)

        # تحليل تكرار الكلمات المهمة
        word_frequencies = self._analyze_important_word_frequencies(verses)

        return {
            "letter_frequencies": letter_frequencies,
            "disconnected_letters": disconnected_letters,
            "word_frequencies": word_frequencies,
        }

    def _analyze_letter_frequencies(self, verses: List[Dict[str, Any]]) -> Dict[str, int]:
        """
        تحليل تكرار الحروف في القرآن

        Args:
            verses: قائمة الآيات

        Returns:
            تكرار الحروف
        """
        # قاموس لتخزين تكرار الحروف
        letter_frequencies = {}

        # الحروف العربية
        arabic_letters = "أبتثجحخدذرزسشصضطظعغفقكلمنهوي"
        for letter in arabic_letters:
            letter_frequencies[letter] = 0

        # حساب تكرار الحروف في كل آية
        for verse in verses:
            text = verse.get("text", "")

            for letter in text:
                if letter in letter_frequencies:
                    letter_frequencies[letter] += 1

        return letter_frequencies

    def _analyze_disconnected_letters(self, surahs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        تحليل الحروف المقطعة في أوائل السور

        Args:
            surahs: قائمة السور

        Returns:
            تحليل الحروف المقطعة
        """
        # قائمة السور التي تبدأ بحروف مقطعة
        disconnected_letters_surahs = []

        # تحليل أوائل السور
        for surah in surahs:
            surah_num = surah.get("number", 0)
            surah_name = surah.get("name", "")

            # التحقق من وجود آيات في السورة
            verses = surah.get("verses", [])
            if not verses:
                continue

            # الحصول على الآية الأولى
            first_verse = verses[0]
            first_verse_text = first_verse.get("text", "")

            # التحقق مما إذا كانت الآية تبدأ بحروف مقطعة
            for letters in self.disconnected_letters:
                if first_verse_text.startswith(letters):
                    disconnected_letters_surahs.append(
                        {
                            "surah_number": surah_num,
                            "surah_name": surah_name,
                            "disconnected_letters": letters,
                            "first_verse": first_verse_text,
                        }
                    )
                    break

        # تحليل تكرار الحروف المقطعة
        letter_counts = {}
        for surah_info in disconnected_letters_surahs:
            letters = surah_info["disconnected_letters"]
            for letter in letters:
                if letter != " ":
                    letter_counts[letter] = letter_counts.get(letter, 0) + 1

        return {
            "surahs_with_disconnected_letters": disconnected_letters_surahs,
            "letter_counts": letter_counts,
        }

    def _analyze_important_word_frequencies(self, verses: List[Dict[str, Any]]) -> Dict[str, int]:
        """
        تحليل تكرار الكلمات المهمة في القرآن

        Args:
            verses: قائمة الآيات

        Returns:
            تكرار الكلمات المهمة
        """
        # قائمة الكلمات المهمة
        important_words = [
            "الله",
            "الرحمن",
            "الرحيم",
            "الإسلام",
            "الإيمان",
            "الصلاة",
            "الزكاة",
            "الصوم",
            "الحج",
            "الجنة",
            "النار",
            "القيامة",
            "الموت",
            "الحياة",
            "الدنيا",
            "الآخرة",
            "الخير",
            "الشر",
            "الحق",
            "الباطل",
            "العدل",
            "الظلم",
            "التقوى",
            "الفسق",
            "الهدى",
            "الضلال",
        ]

        # قاموس لتخزين تكرار الكلمات
        word_frequencies = {word: 0 for word in important_words}

        # حساب تكرار الكلمات في كل آية
        for verse in verses:
            text = verse.get("text", "")

            for word in important_words:
                word_frequencies[word] += text.count(word)

        return word_frequencies

    def _discover_structural_patterns(
        self, verses: List[Dict[str, Any]], surahs: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        اكتشاف التناظرات والعلاقات الهيكلية في القرآن

        Args:
            verses: قائمة الآيات
            surahs: قائمة السور

        Returns:
            التناظرات والعلاقات الهيكلية المكتشفة
        """
        # تحليل التناظر بين السور
        surah_symmetry = self._analyze_surah_symmetry(surahs)

        # تحليل البنية الهيكلية للقرآن
        quran_structure = self._analyze_quran_structure(surahs)

        # تحليل التناظر في الآيات
        verse_symmetry = self._analyze_verse_symmetry(verses)

        return {
            "surah_symmetry": surah_symmetry,
            "quran_structure": quran_structure,
            "verse_symmetry": verse_symmetry,
        }

    def _analyze_surah_symmetry(self, surahs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        تحليل التناظر بين السور

        Args:
            surahs: قائمة السور

        Returns:
            التناظرات المكتشفة بين السور
        """
        # محاكاة لتحليل التناظر بين السور
        symmetries = [
            {
                "type": "تناظر عددي",
                "description": "سورة البقرة (السورة 2) هي أطول سورة، وسورة الكوثر (السورة 108) هي أقصر سورة، ومجموع رقميهما هو 110 (قريب من 114 وهو عدد السور)",
            },
            {
                "type": "تناظر موضوعي",
                "description": "سورة الفاتحة تتضمن دعاء، وسورة الناس تتضمن دعاء، وهما أول وآخر سورة في المصحف",
            },
        ]

        return symmetries

    def _analyze_quran_structure(self, surahs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        تحليل البنية الهيكلية للقرآن

        Args:
            surahs: قائمة السور

        Returns:
            تحليل البنية الهيكلية
        """
        # محاكاة لتحليل البنية الهيكلية
        structure = {
            "total_surahs": len(surahs),
            "makki_surahs": sum(1 for surah in surahs if surah.get("revelationType") == "Meccan"),
            "madani_surahs": sum(1 for surah in surahs if surah.get("revelationType") == "Medinan"),
            "structural_features": [
                "تبدأ معظم السور بالبسملة",
                "ترتيب السور في المصحف ليس حسب النزول الزمني",
                "السور المكية عمومًا أقصر من السور المدنية",
            ],
        }

        return structure

    def _analyze_verse_symmetry(self, verses: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        تحليل التناظر في الآيات

        Args:
            verses: قائمة الآيات

        Returns:
            التناظرات المكتشفة في الآيات
        """
        # محاكاة لتحليل التناظر في الآيات
        symmetries = []

        # فحص الآيات المتشابهة في البداية والنهاية
        if len(verses) >= 2:
            for i in range(len(verses) - 1):
                verse1 = verses[i]
                verse2 = verses[i + 1]

                text1 = verse1.get("text", "")
                text2 = verse2.get("text", "")

                # التحقق من التشابه في البداية
                if len(text1) > 5 and len(text2) > 5 and text1[:5] == text2[:5]:
                    symmetries.append(
                        {
                            "type": "تناظر في بداية الآيات",
                            "verse1": f"{verse1.get('surah_name', '')} ({verse1.get('surah_num', 0)}:{verse1.get('verse_num', 0)})",
                            "verse2": f"{verse2.get('surah_name', '')} ({verse2.get('surah_num', 0)}:{verse2.get('verse_num', 0)})",
                            "description": f"الآيتان تبدآن بنفس الكلمات: {text1[:5]}...",
                        }
                    )

                # التحقق من التشابه في النهاية
                if len(text1) > 5 and len(text2) > 5 and text1[-5:] == text2[-5:]:
                    symmetries.append(
                        {
                            "type": "تناظر في نهاية الآيات",
                            "verse1": f"{verse1.get('surah_name', '')} ({verse1.get('surah_num', 0)}:{verse1.get('verse_num', 0)})",
                            "verse2": f"{verse2.get('surah_name', '')} ({verse2.get('surah_num', 0)}:{verse2.get('verse_num', 0)})",
                            "description": f"الآيتان تنتهيان بنفس الكلمات: ...{text1[-5:]}",
                        }
                    )

        return symmetries
