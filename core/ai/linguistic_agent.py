#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
وكيل التحليل اللغوي
يحلل الجوانب اللغوية والبلاغية في الآيات القرآنية ويستخرج خصائصها اللغوية
"""

import logging
from typing import Dict, List, Any, Optional, Union
import re

from core.ai.multi_agent_system import Agent

# إعداد التسجيل
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class LinguisticAgent(Agent):
    """
    وكيل متخصص في التحليل اللغوي للآيات القرآنية

    يقوم هذا الوكيل بالمهام التالية:
    1. تحليل الخصائص اللغوية للآيات
    2. تحديد الأساليب البلاغية
    3. استخراج الاستعارات والتشبيهات والكنايات
    4. تحليل بنية الجمل ودلالاتها
    """

    def __init__(self, name: str = "linguistic_agent"):
        """
        تهيئة وكيل التحليل اللغوي

        Args:
            name: اسم الوكيل
        """
        super().__init__(name)

        # أنواع الأساليب البلاغية التي يتعرف عليها الوكيل
        self.rhetorical_styles = [
            "استعارة",
            "تشبيه",
            "كناية",
            "مجاز",
            "طباق",
            "جناس",
            "سجع",
            "مقابلة",
            "تورية",
            "تقديم وتأخير",
        ]

        # خصائص لغوية للتحليل
        self.linguistic_features = [
            "بناء الجملة",
            "الأساليب الإنشائية",
            "الأساليب الخبرية",
            "التوكيد",
            "النفي",
            "الشرط",
            "الاستفهام",
            "النداء",
            "الأمر",
            "النهي",
        ]

        logger.info(f"تم إنشاء وكيل التحليل اللغوي: {name}")

    def process(self, query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        معالجة الاستعلام وتحليل الجوانب اللغوية للآيات

        Args:
            query: الاستعلام المراد معالجته
            context: سياق إضافي للمعالجة (اختياري)

        Returns:
            نتائج التحليل اللغوي
        """
        logger.info(f"معالجة الاستعلام: {query}")

        # التأكد من وجود سياق
        if context is None:
            context = {}

        # استخراج الآيات من السياق (إذا كانت متاحة)
        verses = context.get("verses", [])

        # تحليل الخصائص اللغوية للآيات
        linguistic_analysis = self._analyze_linguistic_features(verses)

        # تحديد الأساليب البلاغية
        rhetorical_analysis = self._analyze_rhetorical_styles(verses)

        # استخراج البنى اللغوية
        structure_analysis = self._analyze_sentence_structures(verses)

        # تحليل الإيقاع الصوتي والفواصل
        phonetic_analysis = self._analyze_phonetic_patterns(verses)

        # تجميع النتائج
        result = {
            "linguistic_analysis": linguistic_analysis,
            "rhetorical_analysis": rhetorical_analysis,
            "structure_analysis": structure_analysis,
            "phonetic_analysis": phonetic_analysis,
            "confidence": 0.9,  # ثقة افتراضية
            "metadata": {
                "agent": self.name,
                "query": query,
                "num_verses_analyzed": len(verses),
            },
        }

        return result

    def _analyze_linguistic_features(self, verses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        تحليل الخصائص اللغوية للآيات

        Args:
            verses: قائمة الآيات المراد تحليلها

        Returns:
            نتائج تحليل الخصائص اللغوية
        """
        # محاكاة لتحليل الخصائص اللغوية (يمكن تحسينها باستخدام تقنيات NLP)
        analysis = {feature: [] for feature in self.linguistic_features}

        for verse in verses:
            verse_text = verse.get("text", "")
            verse_ref = f"{verse.get('surah_name', '')} ({verse.get('surah_num', 0)}:{verse.get('verse_num', 0)})"

            # تحليل مبسط للخصائص اللغوية
            if "?" in verse_text or "؟" in verse_text:
                analysis["الاستفهام"].append({"verse": verse_ref, "text": verse_text})

            if "يا " in verse_text:
                analysis["النداء"].append({"verse": verse_ref, "text": verse_text})

            if "لا " in verse_text:
                analysis["النهي"].append({"verse": verse_ref, "text": verse_text})

            if "إن " in verse_text or "إذا " in verse_text:
                analysis["الشرط"].append({"verse": verse_ref, "text": verse_text})

            # إضافة المزيد من التحليلات اللغوية حسب الحاجة

        return analysis

    def _analyze_rhetorical_styles(
        self, verses: List[Dict[str, Any]]
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        تحليل الأساليب البلاغية في الآيات

        Args:
            verses: قائمة الآيات المراد تحليلها

        Returns:
            قاموس بالأساليب البلاغية المكتشفة وأمثلتها
        """
        # محاكاة لتحليل الأساليب البلاغية (يمكن تحسينها باستخدام تقنيات NLP)
        rhetorical_styles = {style: [] for style in self.rhetorical_styles}

        # كلمات مفتاحية بسيطة للكشف عن الأساليب البلاغية (نموذج بسيط)
        style_indicators = {
            "تشبيه": ["كأن", "مثل", "كـ", "يشبه"],
            "استعارة": ["استعار", "مستعار", "يستعير"],
            "كناية": ["كناية", "يكني"],
            "طباق": ["طباق", "متضاد"],
            "جناس": ["جناس", "تجانس"],
        }

        for verse in verses:
            verse_text = verse.get("text", "")
            verse_ref = f"{verse.get('surah_name', '')} ({verse.get('surah_num', 0)}:{verse.get('verse_num', 0)})"

            # فحص بسيط للأساليب البلاغية
            for style, indicators in style_indicators.items():
                for indicator in indicators:
                    if indicator in verse_text:
                        rhetorical_styles[style].append(
                            {"verse": verse_ref, "text": verse_text, "indicator": indicator}
                        )
                        break

        return rhetorical_styles

    def _analyze_sentence_structures(self, verses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        تحليل بنية الجمل في الآيات

        Args:
            verses: قائمة الآيات المراد تحليلها

        Returns:
            تحليل بنية الجمل
        """
        # محاكاة لتحليل بنية الجمل (يمكن تحسينها باستخدام تقنيات NLP)
        structure_types = {
            "جملة اسمية": [],
            "جملة فعلية": [],
            "جملة شرطية": [],
            "جملة استفهامية": [],
            "جملة تعجبية": [],
        }

        for verse in verses:
            verse_text = verse.get("text", "")
            verse_ref = f"{verse.get('surah_name', '')} ({verse.get('surah_num', 0)}:{verse.get('verse_num', 0)})"

            # تحليل نوع الجملة (محاكاة بسيطة)
            words = verse_text.split()
            if words and words[0] in ["إن", "إذا", "لو", "لولا"]:
                structure_types["جملة شرطية"].append({"verse": verse_ref, "text": verse_text})
            elif words and (words[0][-1] == "ُ" or words[0][-1] == "ٌ" or words[0][-1] == "ً"):
                structure_types["جملة اسمية"].append({"verse": verse_ref, "text": verse_text})
            elif words and (words[0][-1] == "َ" or words[0][-1] == "ً"):
                structure_types["جملة فعلية"].append({"verse": verse_ref, "text": verse_text})
            elif "؟" in verse_text or "أ" == words[0][0] if words else False:
                structure_types["جملة استفهامية"].append({"verse": verse_ref, "text": verse_text})
            elif "!" in verse_text or "ما أ" in verse_text:
                structure_types["جملة تعجبية"].append({"verse": verse_ref, "text": verse_text})

        return structure_types

    def _analyze_phonetic_patterns(self, verses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        تحليل الأنماط الصوتية والفواصل في الآيات

        Args:
            verses: قائمة الآيات المراد تحليلها

        Returns:
            تحليل الأنماط الصوتية
        """
        # محاكاة لتحليل الأنماط الصوتية (يمكن تحسينها باستخدام تقنيات معالجة الصوت)
        phonetic_patterns = {
            "فواصل متماثلة": [],
            "فواصل متقاربة": [],
            "إيقاع منتظم": [],
            "تكرار حروف": {},
        }

        # تحليل الفواصل ونهايات الآيات
        for i, verse in enumerate(verses):
            verse_text = verse.get("text", "")
            verse_ref = f"{verse.get('surah_name', '')} ({verse.get('surah_num', 0)}:{verse.get('verse_num', 0)})"

            # تحليل نهاية الآية (محاكاة)
            if i > 0 and len(verses) > 1:
                prev_verse_text = verses[i - 1].get("text", "")
                if prev_verse_text and verse_text:
                    prev_ending = prev_verse_text[-2:] if len(prev_verse_text) >= 2 else ""
                    current_ending = verse_text[-2:] if len(verse_text) >= 2 else ""

                    if prev_ending == current_ending:
                        phonetic_patterns["فواصل متماثلة"].append(
                            {
                                "verse": verse_ref,
                                "text": verse_text,
                                "ending": current_ending,
                            }
                        )
                    elif prev_ending[-1:] == current_ending[-1:]:
                        phonetic_patterns["فواصل متقاربة"].append(
                            {
                                "verse": verse_ref,
                                "text": verse_text,
                                "ending": current_ending,
                            }
                        )

            # تحليل تكرار الحروف
            for letter in "ابتثجحخدذرزسشصضطظعغفقكلمنهوي":
                count = verse_text.count(letter)
                if count > 3:  # تكرار ملحوظ
                    if letter not in phonetic_patterns["تكرار حروف"]:
                        phonetic_patterns["تكرار حروف"][letter] = []

                    phonetic_patterns["تكرار حروف"][letter].append(
                        {"verse": verse_ref, "text": verse_text, "count": count}
                    )

        return phonetic_patterns
