#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
وكيل المعجزات العلمية
يحلل الآيات المتعلقة بالظواهر العلمية ويربطها بالاكتشافات العلمية الحديثة
"""

import logging
from typing import Dict, List, Any, Optional, Union
import re
import json

from core.ai.multi_agent_system import Agent

# إعداد التسجيل
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class ScientificMiraclesAgent(Agent):
    """
    وكيل متخصص في تحليل الآيات المتعلقة بالظواهر العلمية

    يقوم هذا الوكيل بالمهام التالية:
    1. تحديد الآيات ذات المحتوى العلمي
    2. ربط الآيات بالاكتشافات العلمية الحديثة
    3. تقييم التوافق بين النص القرآني والمعرفة العلمية
    """

    def __init__(self, name: str = "scientific_miracles_agent"):
        """
        تهيئة وكيل المعجزات العلمية

        Args:
            name: اسم الوكيل
        """
        super().__init__(name)

        # المجالات العلمية التي يتناولها الوكيل
        self.scientific_domains = [
            "astronomy",  # علم الفلك
            "geology",  # علم الأرض
            "oceanography",  # علم المحيطات
            "meteorology",  # علم الأرصاد الجوية
            "biology",  # علم الأحياء
            "embryology",  # علم الأجنة
            "physics",  # علم الفيزياء
            "medicine",  # علم الطب
        ]

        # قائمة بالكلمات المفتاحية لكل مجال علمي
        self.domain_keywords = {
            "astronomy": ["السماء", "النجوم", "الكواكب", "الشمس", "القمر", "الفلك"],
            "geology": ["الأرض", "الجبال", "الصخور", "الزلازل", "البراكين"],
            "oceanography": ["البحر", "البحار", "الأمواج", "المحيط", "الماء"],
            "meteorology": ["الرياح", "المطر", "السحاب", "الغيوم", "الرعد", "البرق"],
            "biology": ["الحيوان", "النبات", "الكائنات", "الحياة"],
            "embryology": ["الجنين", "النطفة", "العلقة", "المضغة", "العظام", "اللحم"],
            "physics": ["الضوء", "الظل", "الحرارة", "الوزن", "الحديد"],
            "medicine": ["الشفاء", "المرض", "القلب", "الدم", "العقل"],
        }

        logger.info(f"تم إنشاء وكيل المعجزات العلمية: {name}")

    def process(self, query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        معالجة الاستعلام وتحليل الآيات العلمية

        Args:
            query: الاستعلام المراد معالجته
            context: سياق إضافي للمعالجة (اختياري)

        Returns:
            نتائج المعالجة والتحليل العلمي
        """
        logger.info(f"معالجة الاستعلام: {query}")

        # التأكد من وجود سياق
        if context is None:
            context = {}

        # تحليل الاستعلام لتحديد المجالات العلمية ذات الصلة
        relevant_domains = self._identify_relevant_domains(query)

        # استخراج الآيات من السياق (إذا كانت متاحة)
        verses = context.get("verses", [])

        # تحديد الآيات ذات المحتوى العلمي
        scientific_verses = self._identify_scientific_verses(verses, relevant_domains)

        # تحليل التوافق العلمي
        scientific_analysis = self._analyze_scientific_content(scientific_verses, relevant_domains)

        # ربط الآيات بالاكتشافات العلمية الحديثة
        scientific_correlations = self._correlate_with_modern_science(
            scientific_verses, relevant_domains
        )

        # تقييم مستوى التوافق
        compatibility_score = self._evaluate_compatibility(scientific_analysis)

        # تجميع النتائج
        result = {
            "relevant_domains": relevant_domains,
            "scientific_verses": scientific_verses,
            "scientific_analysis": scientific_analysis,
            "scientific_correlations": scientific_correlations,
            "compatibility_score": compatibility_score,
            "confidence": 0.85,  # ثقة افتراضية
            "metadata": {
                "agent": self.name,
                "query": query,
                "num_verses_analyzed": len(verses),
                "num_scientific_verses": len(scientific_verses),
            },
        }

        return result

    def _identify_relevant_domains(self, query: str) -> List[str]:
        """
        تحديد المجالات العلمية ذات الصلة بالاستعلام

        Args:
            query: الاستعلام المراد تحليله

        Returns:
            قائمة بالمجالات العلمية ذات الصلة
        """
        relevant_domains = []

        # البحث عن كلمات مفتاحية في الاستعلام
        for domain, keywords in self.domain_keywords.items():
            for keyword in keywords:
                if keyword in query:
                    relevant_domains.append(domain)
                    break

        # إذا لم يتم العثور على مجالات، نستخدم جميع المجالات
        if not relevant_domains:
            relevant_domains = self.scientific_domains

        return relevant_domains

    def _identify_scientific_verses(
        self, verses: List[Dict[str, Any]], relevant_domains: List[str]
    ) -> List[Dict[str, Any]]:
        """
        تحديد الآيات ذات المحتوى العلمي

        Args:
            verses: قائمة الآيات المراد تحليلها
            relevant_domains: المجالات العلمية ذات الصلة

        Returns:
            قائمة بالآيات ذات المحتوى العلمي
        """
        scientific_verses = []

        # جمع الكلمات المفتاحية لجميع المجالات ذات الصلة
        all_keywords = []
        for domain in relevant_domains:
            all_keywords.extend(self.domain_keywords.get(domain, []))

        # البحث عن الآيات التي تحتوي على كلمات مفتاحية
        for verse in verses:
            verse_text = verse.get("text", "")
            for keyword in all_keywords:
                if keyword in verse_text:
                    # إضافة معلومات إضافية للآية
                    scientific_verse = verse.copy()
                    scientific_verse["domain_keywords"] = [keyword]

                    # التحقق من وجود الآية في القائمة
                    existing_verse = next(
                        (v for v in scientific_verses if v.get("id") == verse.get("id")), None
                    )
                    if existing_verse:
                        # إضافة الكلمة المفتاحية إلى الآية الموجودة
                        if keyword not in existing_verse["domain_keywords"]:
                            existing_verse["domain_keywords"].append(keyword)
                    else:
                        # إضافة الآية إلى القائمة
                        scientific_verses.append(scientific_verse)

                    break

        return scientific_verses

    def _analyze_scientific_content(
        self, scientific_verses: List[Dict[str, Any]], relevant_domains: List[str]
    ) -> Dict[str, Any]:
        """
        تحليل المحتوى العلمي للآيات

        Args:
            scientific_verses: قائمة الآيات ذات المحتوى العلمي
            relevant_domains: المجالات العلمية ذات الصلة

        Returns:
            نتائج تحليل المحتوى العلمي
        """
        # تنظيم الآيات حسب المجالات العلمية
        domain_verses = {domain: [] for domain in relevant_domains}

        for verse in scientific_verses:
            verse_domains = []
            for domain in relevant_domains:
                # التحقق من وجود كلمات مفتاحية من المجال في الآية
                keywords = self.domain_keywords.get(domain, [])
                verse_text = verse.get("text", "")

                for keyword in keywords:
                    if keyword in verse_text:
                        verse_domains.append(domain)
                        domain_verses[domain].append(verse)
                        break

        # تحليل المحتوى العلمي لكل مجال
        analysis = {}

        for domain, verses in domain_verses.items():
            if verses:
                analysis[domain] = {
                    "verses_count": len(verses),
                    "verses": verses,
                    "key_concepts": self._extract_key_concepts(verses, domain),
                    "scientific_principles": self._extract_scientific_principles(verses, domain),
                }

        return analysis

    def _extract_key_concepts(self, verses: List[Dict[str, Any]], domain: str) -> List[str]:
        """
        استخراج المفاهيم الرئيسية من الآيات حسب المجال العلمي

        Args:
            verses: قائمة الآيات
            domain: المجال العلمي

        Returns:
            قائمة بالمفاهيم الرئيسية
        """
        # محاكاة لاستخراج المفاهيم (يمكن تحسينها باستخدام تقنيات NLP)
        concepts = []

        domain_concepts = {
            "astronomy": ["توسع الكون", "حركة الأجرام السماوية", "طبيعة النجوم", "المجرات"],
            "geology": ["تكوين الجبال", "طبقات الأرض", "الصفائح التكتونية", "دورة الصخور"],
            "oceanography": [
                "طبقات البحار",
                "أمواج البحر",
                "الحاجز بين البحرين",
                "المياه العذبة والمالحة",
            ],
            "meteorology": ["دورة الماء", "تكون السحب", "الرياح وحركتها", "ظواهر الطقس"],
            "biology": ["أصل الحياة", "تنوع الكائنات", "التوازن البيئي", "تصنيف الكائنات"],
            "embryology": ["مراحل تطور الجنين", "تكوين الأعضاء", "الخلايا الجذعية", "علم الوراثة"],
            "physics": ["الضوء والظل", "العناصر والمعادن", "الطاقة", "الجاذبية"],
            "medicine": ["الشفاء", "صحة الجسم", "الوقاية من الأمراض", "الطب النبوي"],
        }

        # استخراج المفاهيم المناسبة للمجال
        concepts = domain_concepts.get(domain, [])

        return concepts

    def _extract_scientific_principles(
        self, verses: List[Dict[str, Any]], domain: str
    ) -> List[str]:
        """
        استخراج المبادئ العلمية من الآيات حسب المجال

        Args:
            verses: قائمة الآيات
            domain: المجال العلمي

        Returns:
            قائمة بالمبادئ العلمية
        """
        # محاكاة لاستخراج المبادئ العلمية (يمكن تحسينها باستخدام تقنيات NLP)
        principles = []

        domain_principles = {
            "astronomy": [
                "توسع الكون المستمر",
                "دوران الأرض والأجرام السماوية",
                "المدارات الثابتة للكواكب",
            ],
            "geology": ["وظيفة الجبال كأوتاد", "تكوين طبقات الأرض", "الدورة الهيدرولوجية"],
            "oceanography": [
                "طبقات البحار المختلفة",
                "الحاجز المائي بين البحار",
                "الظلمات في أعماق البحار",
            ],
            "meteorology": [
                "دور الرياح في تلقيح النباتات",
                "تكوين السحب وحركتها",
                "دورة الماء في الطبيعة",
            ],
            "biology": ["خلق الكائنات من الماء", "التنوع البيولوجي", "دورة الحياة الطبيعية"],
            "embryology": ["مراحل خلق الإنسان", "تطور الجنين", "الخصائص الوراثية"],
            "physics": ["خصائص الضوء", "تكوين المعادن", "طبيعة الظل"],
            "medicine": ["الصيام وفوائده الصحية", "الوقاية خير من العلاج", "العسل كشفاء"],
        }

        # استخراج المبادئ المناسبة للمجال
        principles = domain_principles.get(domain, [])

        return principles

    def _correlate_with_modern_science(
        self, scientific_verses: List[Dict[str, Any]], relevant_domains: List[str]
    ) -> Dict[str, Any]:
        """
        ربط الآيات بالاكتشافات العلمية الحديثة

        Args:
            scientific_verses: قائمة الآيات ذات المحتوى العلمي
            relevant_domains: المجالات العلمية ذات الصلة

        Returns:
            ربط الآيات بالاكتشافات العلمية
        """
        # محاكاة لربط الآيات بالاكتشافات العلمية الحديثة
        correlations = {}

        # أمثلة للاكتشافات العلمية الحديثة لكل مجال
        modern_discoveries = {
            "astronomy": [
                {"discovery": "توسع الكون", "year": 1929, "scientist": "إدوين هابل"},
                {"discovery": "الانفجار العظيم", "year": 1965, "scientist": "بنزياس وويلسون"},
                {"discovery": "الثقوب السوداء", "year": 1971, "scientist": "ستيفن هوكينج"},
            ],
            "geology": [
                {"discovery": "الصفائح التكتونية", "year": 1960, "scientist": "هاري هيس"},
                {"discovery": "وظيفة الجبال كأوتاد", "year": 1970, "scientist": "مجموعة علماء"},
            ],
            "oceanography": [
                {"discovery": "طبقات البحار المختلفة", "year": 1942, "scientist": "جاك كوستو"},
                {
                    "discovery": "الحاجز بين المياه العذبة والمالحة",
                    "year": 1962,
                    "scientist": "عالم المحيطات",
                },
            ],
            "meteorology": [
                {"discovery": "دورة الماء في الطبيعة", "year": 1931, "scientist": "تشارلز بروكس"},
                {"discovery": "تلقيح الرياح للنباتات", "year": 1928, "scientist": "عالم النبات"},
            ],
            "biology": [
                {
                    "discovery": "أصل الكائنات الحية من الماء",
                    "year": 1953,
                    "scientist": "ميلر وأوري",
                },
                {"discovery": "التنوع البيولوجي", "year": 1980, "scientist": "إدوارد ويلسون"},
            ],
            "embryology": [
                {"discovery": "مراحل تطور الجنين", "year": 1942, "scientist": "برادلي باتن"},
                {"discovery": "تكوين الأعضاء", "year": 1955, "scientist": "عالم الأجنة"},
            ],
            "physics": [
                {"discovery": "تمدد الضوء", "year": 1905, "scientist": "ألبرت أينشتاين"},
                {"discovery": "خصائص الحديد الفريدة", "year": 1940, "scientist": "عالم المعادن"},
            ],
            "medicine": [
                {"discovery": "فوائد الصيام الصحية", "year": 1975, "scientist": "دراسات طبية"},
                {"discovery": "الخصائص العلاجية للعسل", "year": 1980, "scientist": "أبحاث طبية"},
            ],
        }

        for domain in relevant_domains:
            domain_discoveries = modern_discoveries.get(domain, [])
            if domain_discoveries:
                correlations[domain] = domain_discoveries

        return correlations

    def _evaluate_compatibility(self, scientific_analysis: Dict[str, Any]) -> Dict[str, float]:
        """
        تقييم مستوى التوافق بين الآيات والاكتشافات العلمية

        Args:
            scientific_analysis: نتائج التحليل العلمي

        Returns:
            درجات التوافق لكل مجال
        """
        # محاكاة لتقييم التوافق (يمكن تحسينها باستخدام نماذج أكثر تعقيدًا)
        compatibility = {}

        for domain, analysis in scientific_analysis.items():
            # تقييم بسيط للتوافق (محاكاة)
            verses_count = analysis.get("verses_count", 0)
            compatibility[domain] = min(0.95, 0.7 + (verses_count * 0.05))

        # حساب المتوسط العام
        if compatibility:
            compatibility["overall"] = sum(compatibility.values()) / len(compatibility)
        else:
            compatibility["overall"] = 0.0

        return compatibility
