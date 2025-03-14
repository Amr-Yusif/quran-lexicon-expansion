#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
وكيل الاستدلال
يقوم بتحليل الآيات القرآنية من منظور منطقي واستدلالي، ويستخرج الحجج والبراهين المنطقية
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


class ReasoningAgent(Agent):
    """
    وكيل متخصص في الاستدلال والتحليل المنطقي للآيات القرآنية

    يقوم هذا الوكيل بالمهام التالية:
    1. تحليل الحجج والبراهين في النص القرآني
    2. تحديد أنواع الاستدلال المستخدمة
    3. استخراج القضايا المنطقية والافتراضات
    4. تحديد الروابط السببية والنتائج
    """

    def __init__(self, name: str = "reasoning_agent"):
        """
        تهيئة وكيل الاستدلال

        Args:
            name: اسم الوكيل
        """
        super().__init__(name)

        # أنواع الاستدلال التي يتعرف عليها الوكيل
        self.reasoning_types = [
            "استدلال استنباطي",
            "استدلال استقرائي",
            "استدلال تمثيلي",
            "استدلال سببي",
            "استدلال شرطي",
            "استدلال بالتناقض",
            "استدلال بالاستبعاد",
            "استدلال بالسلطة",
        ]

        # كلمات مفتاحية للاستدلال في القرآن الكريم
        self.reasoning_keywords = {
            "استدلال استنباطي": ["إذا", "فإن", "لأن", "إذن", "لذلك", "بما أن"],
            "استدلال استقرائي": ["كل", "دائما", "عادة", "غالبا", "معظم", "كثير من"],
            "استدلال تمثيلي": ["كما", "مثل", "شبه", "كذلك", "هكذا"],
            "استدلال سببي": ["لأن", "بسبب", "نتيجة", "لكي", "حتى"],
            "استدلال شرطي": ["إن", "لو", "إذا", "متى", "لولا", "مهما"],
            "استدلال بالتناقض": ["بل", "لكن", "غير", "لا", "ليس"],
            "استدلال بالاستبعاد": ["أو", "إما", "أم"],
            "استدلال بالسلطة": ["قل", "قال", "شهد", "علم"],
        }

        # أنماط الروابط المنطقية
        self.logical_connectives = ["و", "أو", "إذا", "لكن", "لا", "ليس", "كل", "بعض"]

        logger.info(f"تم إنشاء وكيل الاستدلال: {name}")

    def process(self, query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        معالجة الاستعلام وتحليل الجوانب الاستدلالية للآيات

        Args:
            query: الاستعلام المراد معالجته
            context: سياق إضافي للمعالجة (اختياري)

        Returns:
            نتائج التحليل الاستدلالي
        """
        logger.info(f"معالجة الاستعلام: {query}")

        # التأكد من وجود سياق
        if context is None:
            context = {}

        # استخراج الآيات من السياق (إذا كانت متاحة)
        verses = context.get("verses", [])

        # تحليل أنواع الاستدلال في الآيات
        reasoning_types_analysis = self._analyze_reasoning_types(verses)

        # تحليل الحجج والبراهين
        arguments_analysis = self._analyze_arguments(verses)

        # تحليل القضايا المنطقية
        logical_propositions = self._analyze_logical_propositions(verses)

        # تحليل الروابط السببية
        causal_relations = self._analyze_causal_relations(verses)

        # تحليل القياس المنطقي
        syllogisms = self._analyze_syllogisms(verses)

        # تجميع النتائج
        result = {
            "reasoning_types_analysis": reasoning_types_analysis,
            "arguments_analysis": arguments_analysis,
            "logical_propositions": logical_propositions,
            "causal_relations": causal_relations,
            "syllogisms": syllogisms,
            "confidence": 0.85,  # ثقة افتراضية
            "metadata": {
                "agent": self.name,
                "query": query,
                "num_verses_analyzed": len(verses),
            },
        }

        return result

    def _analyze_reasoning_types(
        self, verses: List[Dict[str, Any]]
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        تحليل أنواع الاستدلال في الآيات

        Args:
            verses: قائمة الآيات المراد تحليلها

        Returns:
            قاموس بأنواع الاستدلال المكتشفة وأمثلتها
        """
        # قاموس لتخزين أنواع الاستدلال المكتشفة
        reasoning_types = {reasoning_type: [] for reasoning_type in self.reasoning_types}

        # تحليل كل آية
        for verse in verses:
            verse_text = verse.get("text", "")
            verse_ref = f"{verse.get('surah_name', '')} ({verse.get('surah_num', 0)}:{verse.get('verse_num', 0)})"

            # فحص وجود أنواع الاستدلال
            for reasoning_type, keywords in self.reasoning_keywords.items():
                for keyword in keywords:
                    if keyword in verse_text:
                        # العثور على نوع استدلال
                        reasoning_types[reasoning_type].append(
                            {
                                "verse": verse_ref,
                                "text": verse_text,
                                "keyword": keyword,
                                "context": self._extract_context(verse_text, keyword, 10),
                            }
                        )
                        break  # الانتقال إلى نوع الاستدلال التالي

        return reasoning_types

    def _extract_context(self, text: str, keyword: str, window_size: int) -> str:
        """
        استخراج سياق الكلمة المفتاحية من النص

        Args:
            text: النص الكامل
            keyword: الكلمة المفتاحية
            window_size: حجم النافذة السياقية

        Returns:
            السياق المستخرج
        """
        # البحث عن موقع الكلمة المفتاحية
        index = text.find(keyword)
        if index == -1:
            return ""

        # تحديد بداية ونهاية النافذة السياقية
        start = max(0, index - window_size)
        end = min(len(text), index + len(keyword) + window_size)

        # استخراج السياق
        context = text[start:end]

        # إضافة علامات القطع إذا لزم الأمر
        if start > 0:
            context = "..." + context
        if end < len(text):
            context = context + "..."

        return context

    def _analyze_arguments(self, verses: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        تحليل الحجج والبراهين في الآيات

        Args:
            verses: قائمة الآيات المراد تحليلها

        Returns:
            قائمة بالحجج والبراهين المكتشفة
        """
        arguments = []

        # بنية الحجج
        argument_structures = [
            {
                "premise_indicators": ["لأن", "بما أن", "حيث أن"],
                "conclusion_indicators": ["إذن", "لذلك", "فـ", "إذاً"],
            },
            {"premise_indicators": ["ثم", "و"], "conclusion_indicators": ["هكذا", "بالتالي"]},
            {"premise_indicators": ["منذ", "بعد أن"], "conclusion_indicators": ["يلزم", "يجب"]},
        ]

        # البحث عن الحجج في الآيات
        for verse in verses:
            verse_text = verse.get("text", "")
            verse_ref = f"{verse.get('surah_name', '')} ({verse.get('surah_num', 0)}:{verse.get('verse_num', 0)})"

            # فحص بنية الحجج في الآية
            for structure in argument_structures:
                premise_found = False
                conclusion_found = False
                premise_keyword = ""
                conclusion_keyword = ""

                # البحث عن مؤشرات المقدمة
                for indicator in structure["premise_indicators"]:
                    if indicator in verse_text:
                        premise_found = True
                        premise_keyword = indicator
                        break

                # البحث عن مؤشرات النتيجة
                for indicator in structure["conclusion_indicators"]:
                    if indicator in verse_text:
                        conclusion_found = True
                        conclusion_keyword = indicator
                        break

                # اكتشاف الحجة إذا وجدت المقدمة والنتيجة
                if premise_found and conclusion_found:
                    # محاولة استخراج المقدمة والنتيجة
                    premise_context = self._extract_context(verse_text, premise_keyword, 15)
                    conclusion_context = self._extract_context(verse_text, conclusion_keyword, 15)

                    arguments.append(
                        {
                            "verse": verse_ref,
                            "text": verse_text,
                            "premise": premise_context,
                            "conclusion": conclusion_context,
                            "structure": "مقدمة-نتيجة",
                            "strength": "قوية",  # تبسيط - يمكن تحسين تقييم قوة الحجة
                        }
                    )

        return arguments

    def _analyze_logical_propositions(self, verses: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        تحليل القضايا المنطقية في الآيات

        Args:
            verses: قائمة الآيات المراد تحليلها

        Returns:
            قائمة بالقضايا المنطقية المكتشفة
        """
        propositions = []

        # أنماط القضايا المنطقية
        proposition_patterns = [
            {"type": "شرطية", "indicators": ["إن", "إذا", "لو", "متى", "عندما", "لولا"]},
            {"type": "كلية موجبة", "indicators": ["كل", "جميع", "الناس", "المؤمنون"]},
            {"type": "كلية سالبة", "indicators": ["لا أحد", "ما من", "ليس كل"]},
            {"type": "جزئية موجبة", "indicators": ["بعض", "كثير من", "قليل من"]},
            {"type": "جزئية سالبة", "indicators": ["ليس كل", "لا ... كل", "بعض ... لا"]},
        ]

        # البحث عن القضايا المنطقية في الآيات
        for verse in verses:
            verse_text = verse.get("text", "")
            verse_ref = f"{verse.get('surah_name', '')} ({verse.get('surah_num', 0)}:{verse.get('verse_num', 0)})"

            # فحص أنماط القضايا المنطقية
            for pattern in proposition_patterns:
                for indicator in pattern["indicators"]:
                    if indicator in verse_text:
                        # العثور على قضية منطقية
                        propositions.append(
                            {
                                "verse": verse_ref,
                                "text": verse_text,
                                "type": pattern["type"],
                                "indicator": indicator,
                                "context": self._extract_context(verse_text, indicator, 15),
                            }
                        )
                        break  # الانتقال إلى النمط التالي

        return propositions

    def _analyze_causal_relations(self, verses: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        تحليل الروابط السببية في الآيات

        Args:
            verses: قائمة الآيات المراد تحليلها

        Returns:
            قائمة بالروابط السببية المكتشفة
        """
        causal_relations = []

        # مؤشرات العلاقات السببية
        causal_indicators = {
            "سبب": ["لأن", "بسبب", "بما أن", "من أجل", "لكي", "حتى"],
            "نتيجة": ["فـ", "لذلك", "إذن", "لهذا", "فإن", "بالتالي"],
        }

        # البحث عن الروابط السببية في الآيات
        for verse in verses:
            verse_text = verse.get("text", "")
            verse_ref = f"{verse.get('surah_name', '')} ({verse.get('surah_num', 0)}:{verse.get('verse_num', 0)})"

            # البحث عن مؤشرات السبب
            for indicator in causal_indicators["سبب"]:
                if indicator in verse_text:
                    # البحث عن مؤشرات النتيجة أيضاً
                    for result_indicator in causal_indicators["نتيجة"]:
                        if result_indicator in verse_text:
                            # محاولة استخراج السبب والنتيجة
                            cause_context = self._extract_context(verse_text, indicator, 15)
                            effect_context = self._extract_context(verse_text, result_indicator, 15)

                            causal_relations.append(
                                {
                                    "verse": verse_ref,
                                    "text": verse_text,
                                    "cause": cause_context,
                                    "effect": effect_context,
                                    "cause_indicator": indicator,
                                    "effect_indicator": result_indicator,
                                }
                            )
                            break  # الانتقال إلى الآية التالية

        return causal_relations

    def _analyze_syllogisms(self, verses: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        تحليل القياس المنطقي في الآيات

        Args:
            verses: قائمة الآيات المراد تحليلها

        Returns:
            قائمة بالقياسات المنطقية المكتشفة
        """
        syllogisms = []

        # تبسيط: البحث عن آيات تحتوي على مقدمة كبرى ومقدمة صغرى ونتيجة
        # يحتاج إلى تحليل أكثر تعقيداً للقياس المنطقي

        # محاكاة: تحديد بعض أمثلة القياس المنطقي في القرآن
        syllogism_examples = [
            {
                "description": "قياس منطقي حول المؤمنين",
                "major_premise": "المؤمنون هم الذين يتوكلون على الله",
                "minor_premise": "الذين يتوكلون على الله ينالون رضاه",
                "conclusion": "المؤمنون ينالون رضا الله",
            },
            {
                "description": "قياس منطقي حول الظالمين",
                "major_premise": "الظالمون لا يفلحون",
                "minor_premise": "هؤلاء القوم ظالمون",
                "conclusion": "هؤلاء القوم لا يفلحون",
            },
        ]

        # البحث عن آيات قد تحتوي على قياس منطقي
        for verse in verses:
            verse_text = verse.get("text", "")
            verse_ref = f"{verse.get('surah_name', '')} ({verse.get('surah_num', 0)}:{verse.get('verse_num', 0)})"

            # البحث عن كلمات قد تشير إلى قياس منطقي
            has_major_premise = any(keyword in verse_text for keyword in ["كل", "جميع", "الذين"])
            has_minor_premise = any(keyword in verse_text for keyword in ["هم", "هؤلاء", "أولئك"])
            has_conclusion = any(keyword in verse_text for keyword in ["إذن", "فـ", "لذلك"])

            if has_major_premise and has_minor_premise and has_conclusion:
                # اكتشاف محتمل لقياس منطقي
                syllogisms.append(
                    {
                        "verse": verse_ref,
                        "text": verse_text,
                        "potential_syllogism": True,
                        "needs_further_analysis": True,
                    }
                )

        return syllogisms
