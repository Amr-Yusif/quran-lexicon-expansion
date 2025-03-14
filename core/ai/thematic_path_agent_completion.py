#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
إكمال طرق وكيل استخراج المسارات الموضوعية من القرآن الكريم
تتضمن طرق اكتشاف الأنماط الحرفية والتحليل الشامل
"""

from typing import Dict, Any, List, Tuple

# هذا الملف يحتوي على طرق إضافية سيتم دمجها مع فئة ThematicPathAgent


def _analyze_letter_frequencies(self) -> Dict[str, int]:
    """
    تحليل تكرار الحروف في القرآن الكريم

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
    for surah in self.quran_data.get("surahs", []):
        for verse in surah.get("verses", []):
            verse_text = verse.get("text", "")

            for letter in verse_text:
                if letter in letter_frequencies:
                    letter_frequencies[letter] += 1

    return letter_frequencies


def _analyze_disconnected_letters(self) -> Dict[str, Any]:
    """
    تحليل الحروف المقطعة في أوائل السور

    Returns:
        تحليل الحروف المقطعة
    """
    # قائمة السور التي تبدأ بحروف مقطعة
    disconnected_letters_surahs = []

    # الحروف المقطعة المعروفة
    known_disconnected_letters = [
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

    # تحليل أوائل السور
    for surah in self.quran_data.get("surahs", []):
        surah_num = surah.get("number", 0)
        surah_name = surah.get("name", "")

        # التحقق من وجود آيات في السورة
        if not surah.get("verses", []):
            continue

        # الحصول على الآية الأولى
        first_verse = surah["verses"][0]
        first_verse_text = first_verse.get("text", "")

        # التحقق مما إذا كانت الآية تبدأ بحروف مقطعة
        for letters in known_disconnected_letters:
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


def _analyze_important_word_frequencies(self) -> Dict[str, int]:
    """
    تحليل تكرار الكلمات المهمة في القرآن الكريم

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
    for surah in self.quran_data.get("surahs", []):
        for verse in surah.get("verses", []):
            verse_text = verse.get("text", "")

            for word in important_words:
                word_frequencies[word] += verse_text.count(word)

    return word_frequencies


def _analyze_surah_letter_patterns(self) -> List[Dict[str, Any]]:
    """
    تحليل الأنماط الحرفية في السور

    Returns:
        الأنماط الحرفية في السور
    """
    patterns = []

    # تحليل كل سورة
    for surah in self.quran_data.get("surahs", []):
        surah_num = surah.get("number", 0)
        surah_name = surah.get("name", "")

        # تجميع نص السورة
        surah_text = ""
        for verse in surah.get("verses", []):
            surah_text += verse.get("text", "")

        # تحليل تكرار الحروف في السورة
        letter_frequencies = {}
        for letter in surah_text:
            if letter.isalpha():  # التحقق من أن الحرف ليس علامة ترقيم
                letter_frequencies[letter] = letter_frequencies.get(letter, 0) + 1

        # ترتيب الحروف حسب التكرار
        sorted_letters = sorted(letter_frequencies.items(), key=lambda x: x[1], reverse=True)

        # إضافة النمط إذا كان مثيراً للاهتمام
        if self._is_interesting_letter_pattern(sorted_letters, surah_num, surah_name):
            patterns.append(
                {
                    "surah_number": surah_num,
                    "surah_name": surah_name,
                    "most_frequent_letters": sorted_letters[:5],  # أكثر 5 حروف تكراراً
                    "least_frequent_letters": sorted_letters[-5:],  # أقل 5 حروف تكراراً
                    "total_letters": len(surah_text),
                }
            )

    return patterns


def _is_interesting_letter_pattern(
    self, sorted_letters: List[Tuple[str, int]], surah_num: int, surah_name: str
) -> bool:
    """
    تحديد ما إذا كان النمط الحرفي مثيراً للاهتمام

    Args:
        sorted_letters: الحروف مرتبة حسب التكرار
        surah_num: رقم السورة
        surah_name: اسم السورة

    Returns:
        ما إذا كان النمط مثيراً للاهتمام
    """
    # يمكن تطوير معايير أكثر تعقيداً هنا
    # حالياً، نعتبر أي سورة بها نمط حرفي مثيراً للاهتمام
    return True


def _generate_letter_patterns_summary(self) -> str:
    """
    توليد ملخص للأنماط الحرفية المكتشفة

    Returns:
        ملخص الأنماط الحرفية
    """
    summary = "ملخص الأنماط الحرفية في القرآن الكريم:\n\n"

    # إضافة تكرار الحروف
    letter_frequencies = self._analyze_letter_frequencies()
    if letter_frequencies:
        summary += "الحروف الأكثر تكراراً في القرآن:\n"
        sorted_letters = sorted(letter_frequencies.items(), key=lambda x: x[1], reverse=True)[:10]
        for letter, count in sorted_letters:
            summary += f"- الحرف {letter}: {count} مرة\n"

    # إضافة الحروف المقطعة
    disconnected_letters = self._analyze_disconnected_letters()
    if disconnected_letters["surahs_with_disconnected_letters"]:
        summary += "\nالسور التي تبدأ بحروف مقطعة:\n"
        for surah_info in disconnected_letters["surahs_with_disconnected_letters"][:5]:
            summary += f"- سورة {surah_info['surah_name']}: {surah_info['disconnected_letters']}\n"

    # إضافة الأنماط المكتشفة
    if self.discovered_patterns["letter"]:
        summary += "\nالأنماط الحرفية المكتشفة:\n"
        for i, pattern in enumerate(self.discovered_patterns["letter"][:5], 1):
            summary += f"{i}. {pattern['description']}\n"

    return summary


def comprehensive_analysis(self) -> Dict[str, Any]:
    """
    إجراء تحليل شامل للقرآن الكريم يتضمن جميع أنواع التحليل

    Returns:
        نتائج التحليل الشامل
    """
    logger.info("إجراء تحليل شامل للقرآن الكريم")

    # استخراج المسارات الموضوعية
    thematic_paths_results = self.extract_thematic_paths()

    # اكتشاف الأنماط العددية
    numerical_patterns_results = self.discover_numerical_patterns()

    # اكتشاف الأنماط الحرفية
    letter_patterns_results = self.discover_letter_patterns()

    # تحليل العلاقات بين السور
    surah_relationships_results = self._analyze_all_surah_relationships()

    # تجميع النتائج
    results = {
        "thematic_paths": thematic_paths_results,
        "numerical_patterns": numerical_patterns_results,
        "letter_patterns": letter_patterns_results,
        "surah_relationships": surah_relationships_results,
        "summary": self._generate_comprehensive_analysis_summary(
            thematic_paths_results,
            numerical_patterns_results,
            letter_patterns_results,
            surah_relationships_results,
        ),
    }

    return results


def _generate_comprehensive_analysis_summary(
    self,
    thematic_paths_results: Dict[str, Any],
    numerical_patterns_results: Dict[str, Any],
    letter_patterns_results: Dict[str, Any],
    surah_relationships_results: Dict[str, Any],
) -> str:
    """
    توليد ملخص للتحليل الشامل

    Args:
        thematic_paths_results: نتائج المسارات الموضوعية
        numerical_patterns_results: نتائج الأنماط العددية
        letter_patterns_results: نتائج الأنماط الحرفية
        surah_relationships_results: نتائج العلاقات بين السور

    Returns:
        ملخص التحليل الشامل
    """
    summary = "ملخص التحليل الشامل للقرآن الكريم:\n\n"

    # إضافة ملخص المسارات الموضوعية
    if "summary" in thematic_paths_results:
        summary += "المسارات الموضوعية:\n"
        summary += "----------------\n"
        summary += thematic_paths_results["summary"] + "\n\n"

    # إضافة ملخص الأنماط العددية
    if "summary" in numerical_patterns_results:
        summary += "الأنماط العددية:\n"
        summary += "-------------\n"
        summary += numerical_patterns_results["summary"] + "\n\n"

    # إضافة ملخص الأنماط الحرفية
    if "summary" in letter_patterns_results:
        summary += "الأنماط الحرفية:\n"
        summary += "-------------\n"
        summary += letter_patterns_results["summary"] + "\n\n"

    # إضافة ملخص العلاقات بين السور
    if "summary" in surah_relationships_results:
        summary += "العلاقات بين السور:\n"
        summary += "----------------\n"
