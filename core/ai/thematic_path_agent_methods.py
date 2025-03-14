#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
طرق إضافية لوكيل استخراج المسارات الموضوعية من القرآن الكريم
تتضمن طرق مقارنة السور واكتشاف الأنماط العددية والحرفية والتحليل الشامل
"""

from typing import Dict, Any, List
import re
import logging

# إعداد التسجيل
logger = logging.getLogger(__name__)

# هذا الملف يحتوي على طرق إضافية سيتم دمجها مع فئة ThematicPathAgent


def _generate_thematic_paths_summary(self) -> str:
    """
    توليد ملخص للمسارات الموضوعية المستخرجة

    Returns:
        ملخص المسارات الموضوعية
    """
    summary = "ملخص المسارات الموضوعية في القرآن الكريم:\n\n"

    for path_key, path_info in self.thematic_paths.items():
        verse_count = len(path_info["verses"])
        summary += f"- {path_info['name']}: {verse_count} آية\n"

        # إضافة أمثلة للآيات (بحد أقصى 3 آيات)
        if verse_count > 0:
            summary += "  أمثلة:\n"
            for verse in path_info["verses"][:3]:
                summary += f"  * سورة {verse['surah_name']} ({verse['surah_num']}): {verse['verse_num']} - {verse['text'][:100]}...\n"

    return summary


def compare_surahs(self, surah1_num: int = None, surah2_num: int = None) -> Dict[str, Any]:
    """
    مقارنة سورتين من القرآن الكريم

    Args:
        surah1_num: رقم السورة الأولى (اختياري)
        surah2_num: رقم السورة الثانية (اختياري)

    Returns:
        نتائج المقارنة
    """
    logger.info(f"مقارنة السور: {surah1_num} و {surah2_num}")

    # إذا لم يتم تحديد السور، قم بمقارنة جميع السور
    if surah1_num is None or surah2_num is None:
        return self._analyze_all_surah_relationships()

    # البحث عن السورتين
    surah1 = None
    surah2 = None

    for surah in self.quran_data.get("surahs", []):
        if surah.get("number") == surah1_num:
            surah1 = surah
        elif surah.get("number") == surah2_num:
            surah2 = surah

    # التحقق من وجود السورتين
    if not surah1 or not surah2:
        logger.warning(f"لم يتم العثور على إحدى السورتين أو كلتيهما: {surah1_num}, {surah2_num}")
        return {"error": "لم يتم العثور على إحدى السورتين أو كلتيهما"}

    # استخراج معلومات السورتين
    surah1_info = {
        "number": surah1.get("number"),
        "name": surah1.get("name"),
        "verses_count": len(surah1.get("verses", [])),
        "revelation_type": surah1.get("revelationType", ""),
        "themes": self._extract_surah_themes(surah1),
    }

    surah2_info = {
        "number": surah2.get("number"),
        "name": surah2.get("name"),
        "verses_count": len(surah2.get("verses", [])),
        "revelation_type": surah2.get("revelationType", ""),
        "themes": self._extract_surah_themes(surah2),
    }

    # تحليل العلاقات بين السورتين
    relationship = self._analyze_surah_relationship(surah1, surah2)

    # تجميع النتائج
    results = {
        "surah1": surah1_info,
        "surah2": surah2_info,
        "relationship": relationship,
        "summary": self._generate_surah_comparison_summary(surah1_info, surah2_info, relationship),
    }

    return results


def _extract_surah_themes(self, surah: Dict[str, Any]) -> Dict[str, int]:
    """
    استخراج المواضيع الرئيسية في سورة

    Args:
        surah: بيانات السورة

    Returns:
        المواضيع الرئيسية وعدد الآيات لكل موضوع
    """
    themes = {}

    # تحليل كل آية في السورة
    for verse in surah.get("verses", []):
        verse_text = verse.get("text", "")

        # تصنيف الآية حسب المسارات الموضوعية
        for path_key, path_info in self.thematic_paths.items():
            if self._verse_matches_theme(verse_text, path_info["keywords"]):
                themes[path_info["name"]] = themes.get(path_info["name"], 0) + 1

    return themes


def _analyze_surah_relationship(
    self, surah1: Dict[str, Any], surah2: Dict[str, Any]
) -> Dict[str, Any]:
    """
    تحليل العلاقة بين سورتين

    Args:
        surah1: بيانات السورة الأولى
        surah2: بيانات السورة الثانية

    Returns:
        تحليل العلاقة بين السورتين
    """
    # استخراج نصوص الآيات
    surah1_texts = [verse.get("text", "") for verse in surah1.get("verses", [])]
    surah2_texts = [verse.get("text", "") for verse in surah2.get("verses", [])]

    # تحليل التشابه في المواضيع
    surah1_themes = self._extract_surah_themes(surah1)
    surah2_themes = self._extract_surah_themes(surah2)

    # تحديد المواضيع المشتركة
    common_themes = {}
    for theme, count in surah1_themes.items():
        if theme in surah2_themes:
            common_themes[theme] = (count, surah2_themes[theme])

    # تحليل التشابه في الكلمات المفتاحية
    common_keywords = self._find_common_keywords(surah1_texts, surah2_texts)

    # تحليل التسلسل الزمني
    chronological_relationship = "غير معروف"
    if surah1.get("number") < surah2.get("number"):
        chronological_relationship = "السورة الأولى قبل الثانية في ترتيب المصحف"
    else:
        chronological_relationship = "السورة الثانية قبل الأولى في ترتيب المصحف"

    # تحليل نوع الوحي
    revelation_relationship = "مختلف"
    if surah1.get("revelationType") == surah2.get("revelationType"):
        revelation_relationship = f"كلتا السورتين {surah1.get('revelationType')}"
    else:
        revelation_relationship = (
            f"السورة الأولى {surah1.get('revelationType')} والثانية {surah2.get('revelationType')}"
        )

    # تجميع النتائج
    relationship = {
        "common_themes": common_themes,
        "common_keywords": common_keywords,
        "chronological_relationship": chronological_relationship,
        "revelation_relationship": revelation_relationship,
    }

    return relationship


def _find_common_keywords(self, texts1: List[str], texts2: List[str]) -> List[str]:
    """
    البحث عن الكلمات المفتاحية المشتركة بين مجموعتين من النصوص

    Args:
        texts1: المجموعة الأولى من النصوص
        texts2: المجموعة الثانية من النصوص

    Returns:
        الكلمات المفتاحية المشتركة
    """
    # تجميع النصوص
    text1 = " ".join(texts1)
    text2 = " ".join(texts2)

    # تقسيم النصوص إلى كلمات
    words1 = set(re.findall(r"\b\w+\b", text1))
    words2 = set(re.findall(r"\b\w+\b", text2))

    # استبعاد الكلمات الشائعة (حروف الجر، الضمائر، إلخ)
    common_words = [
        "في",
        "من",
        "إلى",
        "على",
        "عن",
        "مع",
        "هو",
        "هي",
        "هم",
        "أنت",
        "أنا",
        "نحن",
        "الذي",
        "التي",
        "الذين",
    ]
    words1 = words1 - set(common_words)
    words2 = words2 - set(common_words)

    # إيجاد الكلمات المشتركة
    common_keywords = words1.intersection(words2)

    # ترتيب الكلمات حسب الأهمية (الطول هنا كمؤشر بسيط للأهمية)
    return sorted(list(common_keywords), key=len, reverse=True)[:20]  # أهم 20 كلمة


def _generate_surah_comparison_summary(
    self, surah1_info: Dict[str, Any], surah2_info: Dict[str, Any], relationship: Dict[str, Any]
) -> str:
    """
    توليد ملخص لمقارنة السورتين

    Args:
        surah1_info: معلومات السورة الأولى
        surah2_info: معلومات السورة الثانية
        relationship: تحليل العلاقة بين السورتين

    Returns:
        ملخص المقارنة
    """
    summary = f"مقارنة بين سورة {surah1_info['name']} وسورة {surah2_info['name']}:\n\n"

    # معلومات أساسية
    summary += "معلومات أساسية:\n"
    summary += f"- سورة {surah1_info['name']}: {surah1_info['verses_count']} آية، {surah1_info['revelation_type']}\n"
    summary += f"- سورة {surah2_info['name']}: {surah2_info['verses_count']} آية، {surah2_info['revelation_type']}\n\n"

    # المواضيع المشتركة
    summary += "المواضيع المشتركة:\n"
    if relationship["common_themes"]:
        for theme, (count1, count2) in relationship["common_themes"].items():
            summary += f"- {theme}: {count1} آية في سورة {surah1_info['name']} و {count2} آية في سورة {surah2_info['name']}\n"
    else:
        summary += "- لا توجد مواضيع مشتركة بارزة\n"

    # الكلمات المفتاحية المشتركة
    summary += "\nالكلمات المفتاحية المشتركة:\n"
    if relationship["common_keywords"]:
        summary += "- " + "، ".join(relationship["common_keywords"][:10]) + "\n"
    else:
        summary += "- لا توجد كلمات مفتاحية مشتركة بارزة\n"

    # العلاقات الأخرى
    summary += f"\nالعلاقة الزمنية: {relationship['chronological_relationship']}\n"
    summary += f"نوع الوحي: {relationship['revelation_relationship']}\n"

    return summary


def _analyze_all_surah_relationships(self) -> Dict[str, Any]:
    """
    تحليل العلاقات بين جميع سور القرآن الكريم

    Returns:
        تحليل العلاقات بين السور
    """
    logger.info("تحليل العلاقات بين جميع سور القرآن الكريم")

    # تحليل العلاقات بين السور المتتالية
    sequential_relationships = []

    surahs = self.quran_data.get("surahs", [])
    for i in range(len(surahs) - 1):
        surah1 = surahs[i]
        surah2 = surahs[i + 1]

        relationship = self._analyze_surah_relationship(surah1, surah2)

        sequential_relationships.append(
            {
                "surah1": {
                    "number": surah1.get("number"),
                    "name": surah1.get("name"),
                    "verses_count": len(surah1.get("verses", [])),
                },
                "surah2": {
                    "number": surah2.get("number"),
                    "name": surah2.get("name"),
                    "verses_count": len(surah2.get("verses", [])),
                },
                "relationship": relationship,
                "summary": self._generate_surah_comparison_summary(
                    {
                        "number": surah1.get("number"),
                        "name": surah1.get("name"),
                        "verses_count": len(surah1.get("verses", [])),
                        "revelation_type": surah1.get("revelationType", ""),
                        "themes": self._extract_surah_themes(surah1),
                    },
                    {
                        "number": surah2.get("number"),
                        "name": surah2.get("name"),
                        "verses_count": len(surah2.get("verses", [])),
                        "revelation_type": surah2.get("revelationType", ""),
                        "themes": self._extract_surah_themes(surah2),
                    },
                    relationship,
                ),
            }
        )

    return {"sequential_relationships": sequential_relationships}
