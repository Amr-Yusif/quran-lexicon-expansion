#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
وكيل استخراج المسارات الموضوعية من القرآن الكريم
يقوم بتحليل ومقارنة آيات وسور القرآن لاستخراج الأطر الشاملة والمسارات المختلفة
مثل المسار التربوي والسياسي والتعليمي والاجتماعي
"""

import logging
from typing import Dict, List, Any, Optional, Union, Set
import json
import re
from pathlib import Path
import numpy as np

# استيراد الفئة الأساسية للوكيل
from core.ai.multi_agent_system import Agent

# إعداد التسجيل
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class ThematicPathAgent(Agent):
    """
    وكيل متخصص في استخراج المسارات الموضوعية من القرآن الكريم
    يقوم بتحليل ومقارنة آيات وسور القرآن لاستخراج الأطر الشاملة والمسارات المختلفة
    """

    def __init__(self, name: str = "thematic_path_agent", quran_data_path: str = None):
        """
        تهيئة وكيل استخراج المسارات الموضوعية

        Args:
            name: اسم الوكيل
            quran_data_path: مسار ملف بيانات القرآن الكريم (اختياري)
        """
        super().__init__(name)

        # تحديد مسار ملف بيانات القرآن الكريم
        self.quran_data_path = quran_data_path or Path("data/quran/quran.json")

        # تحميل بيانات القرآن الكريم
        self.quran_data = self._load_quran_data()

        # تعريف المسارات الموضوعية الرئيسية
        self.thematic_paths = {
            "educational": {
                "name": "المسار التعليمي",
                "keywords": ["علم", "تعلم", "اقرأ", "كتاب", "قلم", "فكر", "عقل", "حكمة", "معرفة"],
                "verses": [],
            },
            "social": {
                "name": "المسار الاجتماعي",
                "keywords": [
                    "أسرة",
                    "زواج",
                    "والدين",
                    "أولاد",
                    "مجتمع",
                    "جار",
                    "صلة",
                    "رحم",
                    "تعاون",
                ],
                "verses": [],
            },
            "political": {
                "name": "المسار السياسي",
                "keywords": ["حكم", "شورى", "عدل", "ظلم", "سلطان", "ملك", "أمير", "دولة", "نظام"],
                "verses": [],
            },
            "educational": {
                "name": "المسار التربوي",
                "keywords": ["تربية", "أخلاق", "آداب", "سلوك", "تزكية", "تهذيب", "قدوة", "إصلاح"],
                "verses": [],
            },
            "economic": {
                "name": "المسار الاقتصادي",
                "keywords": ["مال", "تجارة", "بيع", "شراء", "ربا", "زكاة", "صدقة", "إنفاق", "كسب"],
                "verses": [],
            },
            "spiritual": {
                "name": "المسار الروحي",
                "keywords": ["إيمان", "عبادة", "صلاة", "ذكر", "دعاء", "توبة", "استغفار", "خشوع"],
                "verses": [],
            },
        }

        # إنشاء قاموس للعلاقات بين السور والآيات
        self.surah_relationships = {}

        # إنشاء قاموس للأنماط المكتشفة
        self.discovered_patterns = {
            "numerical": [],  # الأنماط العددية
            "letter": [],  # الأنماط الحرفية
            "thematic": [],  # الأنماط الموضوعية
            "structural": [],  # الأنماط البنيوية
        }

        logger.info(f"تم تهيئة وكيل استخراج المسارات الموضوعية: {name}")

    def _load_quran_data(self) -> Dict[str, Any]:
        """
        تحميل بيانات القرآن الكريم من الملف

        Returns:
            بيانات القرآن الكريم
        """
        try:
            with open(self.quran_data_path, "r", encoding="utf-8") as f:
                quran_data = json.load(f)
            logger.info(f"تم تحميل بيانات القرآن الكريم من: {self.quran_data_path}")
            return quran_data
        except Exception as e:
            logger.error(f"خطأ في تحميل بيانات القرآن الكريم: {str(e)}")
            return {}

    def process(self, query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        معالجة استعلام لاستخراج المسارات الموضوعية من القرآن الكريم

        Args:
            query: الاستعلام المراد معالجته
            context: سياق إضافي للمعالجة (اختياري)

        Returns:
            نتائج المعالجة
        """
        logger.info(f"معالجة استعلام: {query}")

        # تحليل الاستعلام لتحديد نوع التحليل المطلوب
        analysis_type = self._determine_analysis_type(query)

        # تنفيذ التحليل المناسب بناءً على نوع التحليل
        if analysis_type == "thematic_paths":
            results = self.extract_thematic_paths()
        elif analysis_type == "surah_comparison":
            results = self.compare_surahs()
        elif analysis_type == "numerical_patterns":
            results = self.discover_numerical_patterns()
        elif analysis_type == "letter_patterns":
            results = self.discover_letter_patterns()
        else:
            # التحليل الشامل (الافتراضي)
            results = self.comprehensive_analysis()

        return results

    def _determine_analysis_type(self, query: str) -> str:
        """
        تحديد نوع التحليل المطلوب بناءً على الاستعلام

        Args:
            query: الاستعلام المراد تحليله

        Returns:
            نوع التحليل المطلوب
        """
        query = query.lower()

        if any(
            keyword in query
            for keyword in [
                "مسار",
                "مسارات",
                "موضوعي",
                "موضوعية",
                "تربوي",
                "سياسي",
                "اجتماعي",
                "تعليمي",
            ]
        ):
            return "thematic_paths"
        elif any(keyword in query for keyword in ["مقارنة", "سورة", "سور", "علاقة", "علاقات"]):
            return "surah_comparison"
        elif any(keyword in query for keyword in ["عدد", "رقم", "أرقام", "إحصاء", "عددي"]):
            return "numerical_patterns"
        elif any(keyword in query for keyword in ["حرف", "حروف", "لفظ", "ألفاظ"]):
            return "letter_patterns"
        else:
            return "comprehensive"

    def extract_thematic_paths(self) -> Dict[str, Any]:
        """
        استخراج المسارات الموضوعية من القرآن الكريم

        Returns:
            المسارات الموضوعية المستخرجة
        """
        logger.info("استخراج المسارات الموضوعية من القرآن الكريم")

        # تصنيف الآيات حسب المسارات الموضوعية
        self._classify_verses_by_theme()

        # تحليل العلاقات بين المسارات
        path_relationships = self._analyze_path_relationships()

        # تجميع النتائج
        results = {
            "thematic_paths": self.thematic_paths,
            "path_relationships": path_relationships,
            "summary": self._generate_thematic_paths_summary(),
        }

        return results

    def _classify_verses_by_theme(self) -> None:
        """
        تصنيف آيات القرآن الكريم حسب المسارات الموضوعية
        """
        logger.info("تصنيف آيات القرآن الكريم حسب المسارات الموضوعية")

        # إعادة تعيين قوائم الآيات
        for path in self.thematic_paths.values():
            path["verses"] = []

        # تحليل كل سورة وآية
        for surah in self.quran_data.get("surahs", []):
            surah_num = surah.get("number", 0)
            surah_name = surah.get("name", "")

            for verse in surah.get("verses", []):
                verse_num = verse.get("number", 0)
                verse_text = verse.get("text", "")

                # تصنيف الآية حسب المسارات الموضوعية
                for path_key, path_info in self.thematic_paths.items():
                    if self._verse_matches_theme(verse_text, path_info["keywords"]):
                        verse_info = {
                            "surah_num": surah_num,
                            "surah_name": surah_name,
                            "verse_num": verse_num,
                            "text": verse_text,
                        }
                        path_info["verses"].append(verse_info)

    def _verse_matches_theme(self, verse_text: str, keywords: List[str]) -> bool:
        """
        التحقق مما إذا كانت الآية تتطابق مع موضوع معين

        Args:
            verse_text: نص الآية
            keywords: الكلمات المفتاحية للموضوع

        Returns:
            نتيجة التطابق
        """
        # تحويل النص إلى أحرف صغيرة للمطابقة
        verse_lower = verse_text.lower()

        # التحقق من وجود أي من الكلمات المفتاحية في الآية
        for keyword in keywords:
            if keyword in verse_lower:
                return True

        return False

    def _analyze_path_relationships(self) -> Dict[str, Any]:
        """
        تحليل العلاقات بين المسارات الموضوعية

        Returns:
            العلاقات بين المسارات
        """
        logger.info("تحليل العلاقات بين المسارات الموضوعية")

        # إنشاء مصفوفة العلاقات
        path_keys = list(self.thematic_paths.keys())
        relationships = {}

        # تحليل التداخل بين المسارات
        for i, path1 in enumerate(path_keys):
            relationships[path1] = {}
            for path2 in path_keys[i + 1 :]:
                # حساب الآيات المشتركة بين المسارين
                path1_verses = {
                    (v["surah_num"], v["verse_num"]) for v in self.thematic_paths[path1]["verses"]
                }
                path2_verses = {
                    (v["surah_num"], v["verse_num"]) for v in self.thematic_paths[path2]["verses"]
                }
                common_verses = path1_verses.intersection(path2_verses)

                # حساب قوة العلاقة
                if path1_verses and path2_verses:  # تجنب القسمة على صفر
                    relationship_strength = len(common_verses) / min(
                        len(path1_verses), len(path2_verses)
                    )
                else:
                    relationship_strength = 0

                # تخزين العلاقة
                relationships[path1][path2] = {
                    "common_verses_count": len(common_verses),
                    "relationship_strength": relationship_strength,
                }
