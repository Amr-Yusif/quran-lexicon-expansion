#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
وكيل البحث
يقوم بالبحث عن آيات محددة في القرآن الكريم بناءً على المعايير والكلمات المفتاحية
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


class SearchAgent(Agent):
    """
    وكيل متخصص في البحث عن آيات في القرآن الكريم

    يقوم هذا الوكيل بالمهام التالية:
    1. البحث عن آيات تحتوي على كلمات مفتاحية محددة
    2. البحث بناءً على معايير متعددة (سورة، موضوع، كلمات مفتاحية)
    3. تصنيف نتائج البحث حسب الأهمية
    4. توفير سياق النتائج وشروحات موجزة
    """

    def __init__(self, name: str = "search_agent"):
        """
        تهيئة وكيل البحث

        Args:
            name: اسم الوكيل
        """
        super().__init__(name)

        # معايير البحث المدعومة
        self.search_criteria = [
            "كلمات مفتاحية",
            "سورة",
            "جزء",
            "موضوع",
            "نوع السورة",
            "مكان النزول",
            "زمن النزول",
        ]

        # خيارات تصنيف النتائج
        self.sorting_options = ["الأهمية", "ترتيب المصحف", "ترتيب النزول", "طول الآية"]

        # خيارات تصفية النتائج
        self.filtering_options = ["السورة", "الجزء", "الحزب", "الربع", "الموضوع"]

        # قاموس المواضيع الرئيسية
        self.main_topics = {
            "عقيدة": [
                "الله",
                "الإيمان",
                "التوحيد",
                "الملائكة",
                "الكتب",
                "الرسل",
                "اليوم الآخر",
                "القدر",
            ],
            "عبادات": ["الصلاة", "الزكاة", "الصوم", "الحج", "الذكر", "الدعاء"],
            "أخلاق": ["الصدق", "الأمانة", "الإحسان", "الصبر", "الشكر", "التواضع", "العفو"],
            "معاملات": ["التجارة", "البيع", "الشراء", "الديون", "الميراث", "النكاح", "الطلاق"],
            "قصص": ["الأنبياء", "الأمم السابقة", "قصص القرآن", "سيرة النبي"],
            "علم": ["التفكر", "النظر", "العلم", "المعرفة", "التدبر", "الحكمة"],
            "معجزات": ["معجزات القرآن", "الإعجاز العلمي", "الإعجاز اللغوي", "الإعجاز التشريعي"],
        }

        logger.info(f"تم إنشاء وكيل البحث: {name}")

    def process(self, query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        معالجة الاستعلام والبحث عن آيات تطابق المعايير

        Args:
            query: الاستعلام المراد معالجته
            context: سياق إضافي للمعالجة (اختياري)

        Returns:
            نتائج البحث المطابقة للمعايير
        """
        logger.info(f"معالجة استعلام البحث: {query}")

        # التأكد من وجود سياق
        if context is None:
            context = {}

        # استخراج الآيات من السياق (إذا كانت متاحة)
        verses = context.get("verses", [])

        # استخراج بيانات السور إذا كانت متاحة
        surahs = context.get("surahs", [])

        # استخراج معايير البحث من الاستعلام
        search_criteria = self._extract_search_criteria(query)

        # تنفيذ البحث باستخدام المعايير المستخرجة
        search_results = self._perform_search(verses, surahs, search_criteria)

        # تصنيف نتائج البحث
        sorted_results = self._sort_results(
            search_results, search_criteria.get("sort_by", "الأهمية")
        )

        # تلخيص النتائج
        summary = self._generate_search_summary(sorted_results, search_criteria)

        # تجميع النتائج
        result = {
            "search_criteria": search_criteria,
            "results": sorted_results,
            "total_results": len(sorted_results),
            "summary": summary,
            "confidence": 0.9,  # ثقة افتراضية
            "metadata": {
                "agent": self.name,
                "query": query,
                "total_verses_searched": len(verses),
            },
        }

        return result

    def _extract_search_criteria(self, query: str) -> Dict[str, Any]:
        """
        استخراج معايير البحث من الاستعلام

        Args:
            query: الاستعلام المراد تحليله

        Returns:
            معايير البحث المستخرجة
        """
        # معايير البحث الافتراضية
        criteria = {
            "keywords": [],
            "surah": None,
            "juz": None,
            "topic": None,
            "revelation_type": None,
            "revelation_place": None,
            "sort_by": "الأهمية",
            "limit": 10,
        }

        # استخراج الكلمات المفتاحية
        # نفترض أن الكلمات المفتاحية هي الاستعلام بالكامل ما لم يتم تحديد خلاف ذلك
        keywords = query.split()
        criteria["keywords"] = keywords

        # البحث عن معايير محددة في الاستعلام

        # البحث عن السورة المحددة
        surah_match = re.search(r"(سورة|من سورة) (\w+)", query)
        if surah_match:
            criteria["surah"] = surah_match.group(2)

        # البحث عن الجزء المحدد
        juz_match = re.search(r"(جزء|الجزء) (\d+)", query)
        if juz_match:
            criteria["juz"] = int(juz_match.group(2))

        # البحث عن الموضوع المحدد
        for topic, keywords in self.main_topics.items():
            if topic in query or any(keyword in query for keyword in keywords):
                criteria["topic"] = topic
                break

        # البحث عن نوع السورة (مكية أو مدنية)
        if "مكية" in query or "مكي" in query:
            criteria["revelation_place"] = "مكة"
        elif "مدنية" in query or "مدني" in query:
            criteria["revelation_place"] = "المدينة"

        # البحث عن خيار التصنيف
        for option in self.sorting_options:
            if f"ترتيب حسب {option}" in query or f"مرتبة حسب {option}" in query:
                criteria["sort_by"] = option
                break

        # البحث عن عدد النتائج المطلوب
        limit_match = re.search(r"(أظهر|اعرض) (\d+) (آية|آيات|نتيجة|نتائج)", query)
        if limit_match:
            criteria["limit"] = int(limit_match.group(2))

        return criteria

    def _perform_search(
        self, verses: List[Dict[str, Any]], surahs: List[Dict[str, Any]], criteria: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        تنفيذ البحث باستخدام المعايير المحددة

        Args:
            verses: قائمة الآيات للبحث فيها
            surahs: قائمة السور للبحث فيها
            criteria: معايير البحث

        Returns:
            قائمة الآيات المطابقة للمعايير
        """
        results = []

        # البحث عن الآيات التي تطابق المعايير
        for verse in verses:
            # البحث حسب الكلمات المفتاحية
            keywords_matched = True

            if criteria["keywords"]:
                # التحقق من وجود جميع الكلمات المفتاحية في الآية
                verse_text = verse.get("text", "").lower()
                for keyword in criteria["keywords"]:
                    if keyword.lower() not in verse_text:
                        keywords_matched = False
                        break

            # البحث حسب السورة
            surah_matched = True
            if criteria["surah"] is not None:
                surah_name = verse.get("surah_name", "").lower()
                if criteria["surah"].lower() not in surah_name:
                    surah_matched = False

            # البحث حسب الجزء
            juz_matched = True
            if criteria["juz"] is not None:
                verse_juz = verse.get("juz", 0)
                if verse_juz != criteria["juz"]:
                    juz_matched = False

            # البحث حسب مكان النزول
            revelation_place_matched = True
            if criteria["revelation_place"] is not None:
                # البحث عن السورة المقابلة
                surah_num = verse.get("surah_num", 0)
                surah = next((s for s in surahs if s.get("number") == surah_num), None)

                if surah:
                    revelation_type = surah.get("revelationType", "")
                    if (criteria["revelation_place"] == "مكة" and revelation_type != "Meccan") or (
                        criteria["revelation_place"] == "المدينة" and revelation_type != "Medinan"
                    ):
                        revelation_place_matched = False

            # البحث حسب الموضوع (تبسيط - يحتاج لتحسين)
            topic_matched = True
            if criteria["topic"] is not None:
                topic_keywords = self.main_topics.get(criteria["topic"], [])
                verse_text = verse.get("text", "").lower()

                topic_found = False
                for keyword in topic_keywords:
                    if keyword.lower() in verse_text:
                        topic_found = True
                        break

                if not topic_found:
                    topic_matched = False

            # إضافة الآية إذا تطابقت مع جميع المعايير
            if (
                keywords_matched
                and surah_matched
                and juz_matched
                and revelation_place_matched
                and topic_matched
            ):
                # حساب درجة المطابقة
                match_score = self._calculate_match_score(verse, criteria)

                # إضافة الآية ودرجة المطابقة
                result = verse.copy()
                result["match_score"] = match_score

                results.append(result)

        # تحديد عدد النتائج حسب المعيار
        limit = criteria.get("limit", 10)
        if len(results) > limit:
            results = results[:limit]

        return results

    def _calculate_match_score(self, verse: Dict[str, Any], criteria: Dict[str, Any]) -> float:
        """
        حساب درجة مطابقة الآية للمعايير

        Args:
            verse: بيانات الآية
            criteria: معايير البحث

        Returns:
            درجة المطابقة (0.0 - 1.0)
        """
        score = 0.0
        total_weight = 0.0

        # وزن الكلمات المفتاحية (الأعلى أهمية)
        keyword_weight = 0.6
        if criteria["keywords"]:
            verse_text = verse.get("text", "").lower()
            keyword_matches = sum(
                1 for keyword in criteria["keywords"] if keyword.lower() in verse_text
            )
            keyword_score = (
                keyword_matches / len(criteria["keywords"]) if criteria["keywords"] else 0
            )
            score += keyword_weight * keyword_score
            total_weight += keyword_weight

        # وزن السورة
        surah_weight = 0.2
        if criteria["surah"] is not None:
            surah_name = verse.get("surah_name", "").lower()
            surah_score = 1.0 if criteria["surah"].lower() in surah_name else 0.0
            score += surah_weight * surah_score
            total_weight += surah_weight

        # وزن مكان النزول
        revelation_weight = 0.1
        if criteria["revelation_place"] is not None:
            # (تبسيط - يفترض أن بيانات مكان النزول متوفرة)
            revelation_score = 1.0  # تبسيط
            score += revelation_weight * revelation_score
            total_weight += revelation_weight

        # وزن الموضوع
        topic_weight = 0.1
        if criteria["topic"] is not None:
            topic_keywords = self.main_topics.get(criteria["topic"], [])
            verse_text = verse.get("text", "").lower()

            topic_matches = sum(1 for keyword in topic_keywords if keyword.lower() in verse_text)
            topic_score = topic_matches / len(topic_keywords) if topic_keywords else 0
            score += topic_weight * topic_score
            total_weight += topic_weight

        # تطبيع الدرجة
        normalized_score = score / total_weight if total_weight > 0 else 0.0

        return normalized_score

    def _sort_results(self, results: List[Dict[str, Any]], sort_by: str) -> List[Dict[str, Any]]:
        """
        تصنيف نتائج البحث حسب المعيار المحدد

        Args:
            results: نتائج البحث
            sort_by: معيار التصنيف

        Returns:
            نتائج البحث مصنفة
        """
        if sort_by == "الأهمية":
            # التصنيف حسب درجة المطابقة (تنازلياً)
            sorted_results = sorted(results, key=lambda x: x.get("match_score", 0.0), reverse=True)

        elif sort_by == "ترتيب المصحف":
            # التصنيف حسب ترتيب السورة والآية
            sorted_results = sorted(
                results, key=lambda x: (x.get("surah_num", 0), x.get("verse_num", 0))
            )

        elif sort_by == "ترتيب النزول":
            # التصنيف حسب ترتيب النزول (تبسيط - يفترض أن بيانات ترتيب النزول متوفرة)
            sorted_results = sorted(results, key=lambda x: x.get("revelation_order", 0))

        elif sort_by == "طول الآية":
            # التصنيف حسب طول الآية (تنازلياً)
            sorted_results = sorted(results, key=lambda x: len(x.get("text", "")), reverse=True)

        else:
            # التصنيف الافتراضي حسب درجة المطابقة
            sorted_results = sorted(results, key=lambda x: x.get("match_score", 0.0), reverse=True)

        return sorted_results

    def _generate_search_summary(
        self, results: List[Dict[str, Any]], criteria: Dict[str, Any]
    ) -> str:
        """
        توليد ملخص لنتائج البحث

        Args:
            results: نتائج البحث المصنفة
            criteria: معايير البحث

        Returns:
            ملخص نتائج البحث
        """
        if not results:
            return "لم يتم العثور على نتائج تطابق معايير البحث."

        # توليد ملخص البحث
        summary = f"تم العثور على {len(results)} آية تطابق معايير البحث.\n\n"

        # إضافة معايير البحث
        summary += "معايير البحث:\n"
        if criteria["keywords"]:
            summary += f"- الكلمات المفتاحية: {', '.join(criteria['keywords'])}\n"
        if criteria["surah"]:
            summary += f"- السورة: {criteria['surah']}\n"
        if criteria["juz"]:
            summary += f"- الجزء: {criteria['juz']}\n"
        if criteria["topic"]:
            summary += f"- الموضوع: {criteria['topic']}\n"
        if criteria["revelation_place"]:
            summary += f"- مكان النزول: {criteria['revelation_place']}\n"

        # إضافة ملخص النتائج
        summary += "\nأهم النتائج:\n"

        # عرض أهم 3 نتائج
        for i, result in enumerate(results[:3], 1):
            surah_name = result.get("surah_name", "")
            surah_num = result.get("surah_num", 0)
            verse_num = result.get("verse_num", 0)
            text = result.get("text", "")

            # اختصار النص إذا كان طويلاً
            if len(text) > 100:
                text = text[:97] + "..."

            summary += f"{i}. {surah_name} ({surah_num}:{verse_num}): {text}\n"

        # إضافة معلومات إضافية
        if len(results) > 3:
            summary += f"\nوهناك {len(results) - 3} نتيجة إضافية."

        return summary

    def _highlight_keywords(self, text: str, keywords: List[str]) -> str:
        """
        تمييز الكلمات المفتاحية في النص

        Args:
            text: النص الأصلي
            keywords: الكلمات المفتاحية للتمييز

        Returns:
            النص مع تمييز الكلمات المفتاحية
        """
        highlighted_text = text

        for keyword in keywords:
            # استخدام تعبير منتظم للبحث عن الكلمة مع مراعاة حالة الأحرف
            pattern = re.compile(re.escape(keyword), re.IGNORECASE)

            # استبدال الكلمة بنسخة مميزة (في هذا المثال، نضيف نجمة قبل وبعد الكلمة)
            highlighted_text = pattern.sub(f"*{keyword}*", highlighted_text)

        return highlighted_text
