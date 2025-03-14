#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
نظام التقييم والتحقق
=================

نظام متطور لتقييم والتحقق من جودة المعجم العربي وخوارزمياته.
يقوم بإجراء اختبارات شاملة على المعجم وخوارزميات معالجة اللغة العربية
ويقارن النتائج مع المراحل السابقة.
"""

import os
import sys
import json
import csv
import time
import random
import logging
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Tuple, Set, Optional
from collections import defaultdict, Counter

# إضافة المسار إلى PYTHONPATH للوصول إلى الوحدات
current_path = Path(os.path.dirname(os.path.abspath(__file__)))
root_path = current_path.parent
sys.path.append(str(root_path))

from core.lexicon.quranic_lexicon import QuranicLexicon
from core.nlp.root_extraction import ArabicRootExtractor
from core.nlp.morphology import ArabicMorphologyAnalyzer
from core.nlp.diacritics import DiacriticsProcessor

# إعداد التسجيل
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(os.path.join(root_path, "logs", "evaluation_system.log")),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger("evaluation_system")


class LexiconEvaluator:
    """فئة تقييم المعجم وخوارزميات معالجة اللغة العربية."""

    def __init__(
        self,
        lexicon_path: str,
        original_lexicon_path: Optional[str] = None,
        previous_results_path: Optional[str] = None,
    ):
        """
        تهيئة مقيّم المعجم.

        المعلمات:
            lexicon_path: مسار ملف المعجم الموسع
            original_lexicon_path: مسار ملف المعجم الأصلي (اختياري)
            previous_results_path: مسار نتائج التقييم السابقة للمقارنة (اختياري)
        """
        self.lexicon_path = lexicon_path
        self.original_lexicon_path = original_lexicon_path
        self.previous_results_path = previous_results_path

        # تحميل المعجم
        self.lexicon = QuranicLexicon(lexicon_path)
        logger.info(f"تم تحميل المعجم: {lexicon_path} ({len(self.lexicon.words)} كلمة)")

        # تحميل المعجم الأصلي إذا تم توفيره
        self.original_lexicon = None
        if original_lexicon_path:
            self.original_lexicon = QuranicLexicon(original_lexicon_path)
            logger.info(
                f"تم تحميل المعجم الأصلي: {original_lexicon_path} ({len(self.original_lexicon.words)} كلمة)"
            )

        # تحميل نتائج التقييم السابقة إذا تم توفيرها
        self.previous_results = None
        if previous_results_path and os.path.exists(previous_results_path):
            try:
                with open(previous_results_path, "r", encoding="utf-8") as f:
                    self.previous_results = json.load(f)
                logger.info(f"تم تحميل نتائج التقييم السابقة: {previous_results_path}")
            except Exception as e:
                logger.warning(f"فشل تحميل نتائج التقييم السابقة: {str(e)}")

        # تهيئة المعالجات
        self.root_extractor = ArabicRootExtractor()
        self.morphology_analyzer = ArabicMorphologyAnalyzer()
        self.diacritics_processor = DiacriticsProcessor()

        # إحصائيات التقييم
        self.evaluation_stats = {
            "lexicon_stats": self._calculate_lexicon_stats(),
            "algorithm_performance": {},
            "comparison_with_previous": {},
            "test_cases": {},
            "timestamp": datetime.now().isoformat(),
        }

    def _calculate_lexicon_stats(self) -> Dict[str, Any]:
        """
        حساب إحصائيات المعجم الأساسية.

        العوائد:
            قاموس يحتوي على إحصائيات المعجم
        """
        stats = {
            "total_words": len(self.lexicon.words),
            "with_root": sum(1 for word in self.lexicon.words.values() if "root" in word),
            "with_type": sum(1 for word in self.lexicon.words.values() if "type" in word),
            "with_pattern": sum(1 for word in self.lexicon.words.values() if "pattern" in word),
            "with_meaning": sum(1 for word in self.lexicon.words.values() if "meaning" in word),
            "new_words": 0,
            "root_lengths": defaultdict(int),
            "types": defaultdict(int),
            "patterns": defaultdict(int),
        }

        # حساب إحصائيات الجذور والأنواع والأوزان
        for word, properties in self.lexicon.words.items():
            if "root" in properties:
                stats["root_lengths"][len(properties["root"])] += 1
            if "type" in properties:
                stats["types"][properties["type"]] += 1
            if "pattern" in properties:
                stats["patterns"][properties["pattern"]] += 1

        # حساب الكلمات الجديدة المضافة
        if self.original_lexicon:
            new_words = set(self.lexicon.words.keys()) - set(self.original_lexicon.words.keys())
            stats["new_words"] = len(new_words)

        # تحويل الإحصائيات المجمعة إلى قوائم مرتبة
        stats["root_lengths"] = [
            {"length": length, "count": count} for length, count in stats["root_lengths"].items()
        ]
        stats["types"] = [
            {"type": type_, "count": count} for type_, count in stats["types"].items()
        ]
        stats["patterns"] = [
            {"pattern": pattern, "count": count} for pattern, count in stats["patterns"].items()
        ]

        return stats

    def evaluate_algorithm_performance(self) -> Dict[str, Any]:
        """
        تقييم أداء خوارزميات معالجة اللغة العربية.

        العوائد:
            قاموس يحتوي على نتائج تقييم الخوارزميات
        """
        logger.info("بدء تقييم أداء الخوارزميات")

        # إعداد إحصائيات الأداء
        performance = {
            "root_extraction": {"correct": 0, "incorrect": 0, "accuracy": 0, "errors": []},
            "morphology_analysis": {"correct": 0, "incorrect": 0, "accuracy": 0, "errors": []},
        }

        # إنشاء مجموعة اختبار عشوائية من الكلمات
        test_words = self._select_test_words(min(100, len(self.lexicon.words)))
        logger.info(f"تم اختيار {len(test_words)} كلمة للاختبار")

        # تقييم خوارزمية استخراج الجذور
        for word, properties in test_words.items():
            # تجاوز الكلمات بدون جذر مسجل
            if "root" not in properties:
                continue

            # استخراج الجذر باستخدام الخوارزمية
            extracted_root_info = self.root_extractor.extract_root(word)
            extracted_root = extracted_root_info.get("root", "")
            expected_root = properties["root"]

            # تقييم النتيجة
            if extracted_root == expected_root:
                performance["root_extraction"]["correct"] += 1
            else:
                performance["root_extraction"]["incorrect"] += 1
                if len(performance["root_extraction"]["errors"]) < 10:  # حد عدد الأخطاء المحفوظة
                    performance["root_extraction"]["errors"].append(
                        {
                            "word": word,
                            "expected": expected_root,
                            "extracted": extracted_root,
                            "confidence": extracted_root_info.get("confidence", 0),
                        }
                    )

            # تقييم خوارزمية تحليل الصرف
            if "type" in properties:
                morphology_info = self.morphology_analyzer.analyze_word(word)
                extracted_type = morphology_info.get("type", "")
                expected_type = properties["type"]

                if extracted_type == expected_type:
                    performance["morphology_analysis"]["correct"] += 1
                else:
                    performance["morphology_analysis"]["incorrect"] += 1
                    if len(performance["morphology_analysis"]["errors"]) < 10:
                        performance["morphology_analysis"]["errors"].append(
                            {
                                "word": word,
                                "expected": expected_type,
                                "extracted": extracted_type,
                            }
                        )

        # حساب الدقة
        total_root_tests = (
            performance["root_extraction"]["correct"] + performance["root_extraction"]["incorrect"]
        )
        if total_root_tests > 0:
            performance["root_extraction"]["accuracy"] = (
                performance["root_extraction"]["correct"] / total_root_tests
            )

        total_morphology_tests = (
            performance["morphology_analysis"]["correct"]
            + performance["morphology_analysis"]["incorrect"]
        )
        if total_morphology_tests > 0:
            performance["morphology_analysis"]["accuracy"] = (
                performance["morphology_analysis"]["correct"] / total_morphology_tests
            )

        # تحديث إحصائيات التقييم
        self.evaluation_stats["algorithm_performance"] = performance
        self.evaluation_stats["test_cases"]["count"] = len(test_words)

        logger.info(
            f"دقة استخراج الجذور: {performance['root_extraction']['accuracy']:.2%} "
            f"({performance['root_extraction']['correct']}/{total_root_tests})"
        )
        logger.info(
            f"دقة تحليل الصرف: {performance['morphology_analysis']['accuracy']:.2%} "
            f"({performance['morphology_analysis']['correct']}/{total_morphology_tests})"
        )

        return performance

    def _select_test_words(self, count: int) -> Dict[str, Dict[str, Any]]:
        """
        اختيار مجموعة كلمات للاختبار.

        المعلمات:
            count: عدد الكلمات المراد اختيارها

        العوائد:
            قاموس من الكلمات المختارة وخصائصها
        """
        # اختيار الكلمات بشكل عشوائي
        words = list(self.lexicon.words.keys())
        selected_indices = random.sample(range(len(words)), min(count, len(words)))
        selected_words = {words[i]: self.lexicon.words[words[i]] for i in selected_indices}

        return selected_words

    def compare_with_previous_results(self) -> Dict[str, Any]:
        """
        مقارنة نتائج التقييم الحالية مع النتائج السابقة.

        العوائد:
            قاموس يحتوي على نتائج المقارنة
        """
        logger.info("مقارنة نتائج التقييم الحالية مع النتائج السابقة")

        # إذا لم تكن هناك نتائج سابقة، نعود بنتيجة فارغة
        if not self.previous_results:
            logger.warning("لا توجد نتائج سابقة للمقارنة")
            return {}

        comparison = {
            "lexicon_growth": {
                "previous": self.previous_results.get("lexicon_stats", {}).get("total_words", 0),
                "current": self.evaluation_stats["lexicon_stats"]["total_words"],
                "difference": 0,
                "percentage": 0,
            },
            "algorithm_improvement": {
                "root_extraction": {
                    "previous": self.previous_results.get("algorithm_performance", {})
                    .get("root_extraction", {})
                    .get("accuracy", 0),
                    "current": self.evaluation_stats["algorithm_performance"]["root_extraction"][
                        "accuracy"
                    ],
                    "difference": 0,
                    "percentage": 0,
                },
                "morphology_analysis": {
                    "previous": self.previous_results.get("algorithm_performance", {})
                    .get("morphology_analysis", {})
                    .get("accuracy", 0),
                    "current": self.evaluation_stats["algorithm_performance"][
                        "morphology_analysis"
                    ]["accuracy"],
                    "difference": 0,
                    "percentage": 0,
                },
            },
        }

        # حساب الفروقات
        previous_words = self.previous_results.get("lexicon_stats", {}).get("total_words", 0)
        current_words = self.evaluation_stats["lexicon_stats"]["total_words"]
        comparison["lexicon_growth"]["difference"] = current_words - previous_words
        if previous_words > 0:
            comparison["lexicon_growth"]["percentage"] = (
                comparison["lexicon_growth"]["difference"] / previous_words
            ) * 100

        previous_root_accuracy = (
            self.previous_results.get("algorithm_performance", {})
            .get("root_extraction", {})
            .get("accuracy", 0)
        )
        current_root_accuracy = self.evaluation_stats["algorithm_performance"]["root_extraction"][
            "accuracy"
        ]
        comparison["algorithm_improvement"]["root_extraction"]["difference"] = (
            current_root_accuracy - previous_root_accuracy
        )
        if previous_root_accuracy > 0:
            comparison["algorithm_improvement"]["root_extraction"]["percentage"] = (
                comparison["algorithm_improvement"]["root_extraction"]["difference"]
                / previous_root_accuracy
            ) * 100

        previous_morphology_accuracy = (
            self.previous_results.get("algorithm_performance", {})
            .get("morphology_analysis", {})
            .get("accuracy", 0)
        )
        current_morphology_accuracy = self.evaluation_stats["algorithm_performance"][
            "morphology_analysis"
        ]["accuracy"]
        comparison["algorithm_improvement"]["morphology_analysis"]["difference"] = (
            current_morphology_accuracy - previous_morphology_accuracy
        )
        if previous_morphology_accuracy > 0:
            comparison["algorithm_improvement"]["morphology_analysis"]["percentage"] = (
                comparison["algorithm_improvement"]["morphology_analysis"]["difference"]
                / previous_morphology_accuracy
            ) * 100

        # تحديث إحصائيات التقييم
        self.evaluation_stats["comparison_with_previous"] = comparison

        # تسجيل نتائج المقارنة
        logger.info(
            f"نمو المعجم: {comparison['lexicon_growth']['difference']} كلمة "
            f"({comparison['lexicon_growth']['percentage']:.2f}%)"
        )
        logger.info(
            f"تحسين دقة استخراج الجذور: {comparison['algorithm_improvement']['root_extraction']['difference']:.4f} "
            f"({comparison['algorithm_improvement']['root_extraction']['percentage']:.2f}%)"
        )
        logger.info(
            f"تحسين دقة تحليل الصرف: {comparison['algorithm_improvement']['morphology_analysis']['difference']:.4f} "
            f"({comparison['algorithm_improvement']['morphology_analysis']['percentage']:.2f}%)"
        )

        return comparison

    def run_evaluation_tests(self) -> Dict[str, Any]:
        """
        تشغيل اختبارات شاملة للتقييم.

        العوائد:
            قاموس يحتوي على نتائج الاختبارات
        """
        logger.info("بدء تشغيل اختبارات التقييم الشاملة")

        # تقييم أداء الخوارزميات
        self.evaluate_algorithm_performance()

        # مقارنة مع النتائج السابقة
        if self.previous_results:
            self.compare_with_previous_results()

        # إضافة وقت انتهاء التقييم
        self.evaluation_stats["end_time"] = datetime.now().isoformat()

        return self.evaluation_stats

    def generate_report(self, output_path: str) -> None:
        """
        توليد تقرير شامل عن نتائج التقييم.

        المعلمات:
            output_path: مسار ملف التقرير
        """
        logger.info(f"توليد تقرير التقييم: {output_path}")

        # التأكد من وجود نتائج التقييم
        if not self.evaluation_stats.get("algorithm_performance"):
            self.run_evaluation_tests()

        # إنشاء محتوى التقرير بتنسيق Markdown
        report_content = "# تقرير تقييم المعجم والخوارزميات\n\n"
        report_content += f"**تاريخ التقرير:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        report_content += f"**المعجم:** {self.lexicon_path}\n"
        if self.original_lexicon_path:
            report_content += f"**المعجم الأصلي:** {self.original_lexicon_path}\n"
        report_content += "\n"

        # إحصائيات المعجم
        lexicon_stats = self.evaluation_stats["lexicon_stats"]
        report_content += "## إحصائيات المعجم\n\n"
        report_content += f"- **إجمالي الكلمات:** {lexicon_stats['total_words']}\n"
        report_content += f"- **الكلمات بجذور:** {lexicon_stats['with_root']} ({lexicon_stats['with_root'] / lexicon_stats['total_words']:.2%})\n"
        report_content += f"- **الكلمات بأنواع:** {lexicon_stats['with_type']} ({lexicon_stats['with_type'] / lexicon_stats['total_words']:.2%})\n"
        report_content += f"- **الكلمات بأوزان:** {lexicon_stats['with_pattern']} ({lexicon_stats['with_pattern'] / lexicon_stats['total_words']:.2%})\n"
        report_content += f"- **الكلمات بمعاني:** {lexicon_stats['with_meaning']} ({lexicon_stats['with_meaning'] / lexicon_stats['total_words']:.2%})\n"

        if lexicon_stats.get("new_words", 0) > 0:
            report_content += f"- **الكلمات الجديدة المضافة:** {lexicon_stats['new_words']}\n"

        # توزيع أطوال الجذور
        report_content += "\n### توزيع أطوال الجذور\n\n"
        report_content += "| طول الجذر | عدد الكلمات | النسبة المئوية |\n"
        report_content += "| --------- | ----------- | -------------- |\n"

        total_with_roots = lexicon_stats["with_root"]
        for root_length in sorted(lexicon_stats["root_lengths"], key=lambda x: x["length"]):
            percentage = (
                (root_length["count"] / total_with_roots) * 100 if total_with_roots > 0 else 0
            )
            report_content += (
                f"| {root_length['length']} | {root_length['count']} | {percentage:.2f}% |\n"
            )

        # توزيع أنواع الكلمات
        report_content += "\n### توزيع أنواع الكلمات\n\n"
        report_content += "| النوع | عدد الكلمات | النسبة المئوية |\n"
        report_content += "| ---- | ----------- | -------------- |\n"

        total_with_types = lexicon_stats["with_type"]
        for type_info in sorted(lexicon_stats["types"], key=lambda x: x["count"], reverse=True):
            percentage = (
                (type_info["count"] / total_with_types) * 100 if total_with_types > 0 else 0
            )
            report_content += (
                f"| {type_info['type']} | {type_info['count']} | {percentage:.2f}% |\n"
            )

        # أداء الخوارزميات
        algorithm_performance = self.evaluation_stats["algorithm_performance"]
        report_content += "\n## أداء الخوارزميات\n\n"

        # أداء خوارزمية استخراج الجذور
        root_extraction = algorithm_performance["root_extraction"]
        total_root_tests = root_extraction["correct"] + root_extraction["incorrect"]
        report_content += "### خوارزمية استخراج الجذور\n\n"
        report_content += f"- **الدقة:** {root_extraction['accuracy']:.2%}\n"
        report_content += (
            f"- **الإجابات الصحيحة:** {root_extraction['correct']}/{total_root_tests}\n"
        )
        report_content += (
            f"- **الإجابات الخاطئة:** {root_extraction['incorrect']}/{total_root_tests}\n"
        )

        if root_extraction["errors"]:
            report_content += "\n#### أمثلة على الأخطاء\n\n"
            report_content += "| الكلمة | الجذر المتوقع | الجذر المستخرج | الثقة |\n"
            report_content += "| ------ | ------------- | -------------- | ----- |\n"

            for error in root_extraction["errors"]:
                report_content += f"| {error['word']} | {error['expected']} | {error['extracted']} | {error['confidence']:.2f} |\n"

        # أداء خوارزمية تحليل الصرف
        morphology_analysis = algorithm_performance["morphology_analysis"]
        total_morphology_tests = morphology_analysis["correct"] + morphology_analysis["incorrect"]
        report_content += "\n### خوارزمية تحليل الصرف\n\n"
        report_content += f"- **الدقة:** {morphology_analysis['accuracy']:.2%}\n"
        report_content += (
            f"- **الإجابات الصحيحة:** {morphology_analysis['correct']}/{total_morphology_tests}\n"
        )
        report_content += (
            f"- **الإجابات الخاطئة:** {morphology_analysis['incorrect']}/{total_morphology_tests}\n"
        )

        if morphology_analysis["errors"]:
            report_content += "\n#### أمثلة على الأخطاء\n\n"
            report_content += "| الكلمة | النوع المتوقع | النوع المستخرج |\n"
            report_content += "| ------ | ------------- | -------------- |\n"

            for error in morphology_analysis["errors"]:
                report_content += (
                    f"| {error['word']} | {error['expected']} | {error['extracted']} |\n"
                )

        # المقارنة مع النتائج السابقة
        comparison = self.evaluation_stats.get("comparison_with_previous", {})
        if comparison:
            report_content += "\n## المقارنة مع النتائج السابقة\n\n"

            # نمو المعجم
            lexicon_growth = comparison["lexicon_growth"]
            report_content += "### نمو المعجم\n\n"
            report_content += f"- **العدد السابق:** {lexicon_growth['previous']} كلمة\n"
            report_content += f"- **العدد الحالي:** {lexicon_growth['current']} كلمة\n"
            report_content += f"- **الزيادة:** {lexicon_growth['difference']} كلمة ({lexicon_growth['percentage']:.2f}%)\n"

            # تحسين الخوارزميات
            report_content += "\n### تحسين أداء الخوارزميات\n\n"
            report_content += (
                "| الخوارزمية | الدقة السابقة | الدقة الحالية | التغيير | النسبة المئوية |\n"
            )
            report_content += (
                "| --------- | ------------- | ------------ | ------- | -------------- |\n"
            )

            root_improvement = comparison["algorithm_improvement"]["root_extraction"]
            report_content += f"| استخراج الجذور | {root_improvement['previous']:.2%} | {root_improvement['current']:.2%} | {root_improvement['difference']:.4f} | {root_improvement['percentage']:.2f}% |\n"

            morphology_improvement = comparison["algorithm_improvement"]["morphology_analysis"]
            report_content += f"| تحليل الصرف | {morphology_improvement['previous']:.2%} | {morphology_improvement['current']:.2%} | {morphology_improvement['difference']:.4f} | {morphology_improvement['percentage']:.2f}% |\n"

        # خلاصة وتوصيات
        report_content += "\n## الخلاصة والتوصيات\n\n"
        report_content += "### النقاط الإيجابية\n\n"

        # إضافة النقاط الإيجابية تلقائيًا بناءً على النتائج
        positives = []

        if lexicon_stats.get("new_words", 0) > 0:
            positives.append(f"تمت إضافة {lexicon_stats['new_words']} كلمة جديدة إلى المعجم")

        if comparison.get("lexicon_growth", {}).get("percentage", 0) > 5:
            positives.append(
                f"نمو كبير في حجم المعجم بنسبة {comparison['lexicon_growth']['percentage']:.2f}%"
            )

        if (
            comparison.get("algorithm_improvement", {})
            .get("root_extraction", {})
            .get("percentage", 0)
            > 0
        ):
            positives.append(
                f"تحسن في دقة استخراج الجذور بنسبة {comparison['algorithm_improvement']['root_extraction']['percentage']:.2f}%"
            )

        if (
            comparison.get("algorithm_improvement", {})
            .get("morphology_analysis", {})
            .get("percentage", 0)
            > 0
        ):
            positives.append(
                f"تحسن في دقة تحليل الصرف بنسبة {comparison['algorithm_improvement']['morphology_analysis']['percentage']:.2f}%"
            )

        if root_extraction["accuracy"] > 0.7:
            positives.append(f"دقة جيدة في استخراج الجذور ({root_extraction['accuracy']:.2%})")

        if morphology_analysis["accuracy"] > 0.7:
            positives.append(f"دقة جيدة في تحليل الصرف ({morphology_analysis['accuracy']:.2%})")

        if positives:
            for point in positives:
                report_content += f"- {point}\n"
        else:
            report_content += "- لا توجد نقاط إيجابية محددة في هذا التقييم\n"

        report_content += "\n### التحديات والتوصيات\n\n"

        # إضافة التحديات والتوصيات تلقائيًا بناءً على النتائج
        challenges = []

        if root_extraction["accuracy"] < 0.7:
            challenges.append(
                f"دقة خوارزمية استخراج الجذور منخفضة ({root_extraction['accuracy']:.2%}). يوصى بتحسين الخوارزمية."
            )

        if morphology_analysis["accuracy"] < 0.7:
            challenges.append(
                f"دقة خوارزمية تحليل الصرف منخفضة ({morphology_analysis['accuracy']:.2%}). يوصى بتحسين الخوارزمية."
            )

        if (
            comparison.get("algorithm_improvement", {})
            .get("root_extraction", {})
            .get("percentage", 0)
            < 0
        ):
            challenges.append(
                "تراجع في أداء خوارزمية استخراج الجذور مقارنة بالنتائج السابقة. يجب مراجعة التغييرات الأخيرة."
            )

        if (
            comparison.get("algorithm_improvement", {})
            .get("morphology_analysis", {})
            .get("percentage", 0)
            < 0
        ):
            challenges.append(
                "تراجع في أداء خوارزمية تحليل الصرف مقارنة بالنتائج السابقة. يجب مراجعة التغييرات الأخيرة."
            )

        if lexicon_stats["with_root"] / lexicon_stats["total_words"] < 0.9:
            challenges.append(
                f"نسبة الكلمات بدون جذور مرتفعة ({1 - lexicon_stats['with_root'] / lexicon_stats['total_words']:.2%}). يوصى بتحسين تغطية الجذور."
            )

        if lexicon_stats["with_meaning"] / lexicon_stats["total_words"] < 0.9:
            challenges.append(
                f"نسبة الكلمات بدون معاني مرتفعة ({1 - lexicon_stats['with_meaning'] / lexicon_stats['total_words']:.2%}). يوصى بتحسين تغطية المعاني."
            )

        if challenges:
            for point in challenges:
                report_content += f"- {point}\n"
        else:
            report_content += "- لا توجد تحديات محددة في هذا التقييم\n"

        # إنشاء دليل التقرير إذا لم يكن موجودًا
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

        # حفظ التقرير
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(report_content)

        logger.info(f"تم توليد تقرير التقييم بنجاح: {output_path}")

    def save_results(self, output_path: str) -> None:
        """
        حفظ نتائج التقييم إلى ملف JSON.

        المعلمات:
            output_path: مسار ملف النتائج
        """
        logger.info(f"حفظ نتائج التقييم: {output_path}")

        # التأكد من وجود نتائج التقييم
        if not self.evaluation_stats.get("algorithm_performance"):
            self.run_evaluation_tests()

        # إنشاء دليل النتائج إذا لم يكن موجودًا
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

        # حفظ النتائج
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(self.evaluation_stats, f, ensure_ascii=False, indent=4)

        logger.info(f"تم حفظ نتائج التقييم بنجاح: {output_path}")


def main():
    """النقطة الرئيسية لتنفيذ نظام التقييم والتحقق"""
    parser = argparse.ArgumentParser(
        description="نظام تقييم المعجم وخوارزميات معالجة اللغة العربية"
    )
    parser.add_argument("--lexicon", required=True, help="مسار ملف المعجم المراد تقييمه")
    parser.add_argument("--original", help="مسار ملف المعجم الأصلي (اختياري)")
    parser.add_argument("--previous", help="مسار نتائج التقييم السابقة للمقارنة (اختياري)")
    parser.add_argument("--report", help="مسار ملف تقرير التقييم (Markdown)")
    parser.add_argument("--results", help="مسار ملف نتائج التقييم (JSON)")

    args = parser.parse_args()

    try:
        # إنشاء مقيّم المعجم
        evaluator = LexiconEvaluator(
            lexicon_path=args.lexicon,
            original_lexicon_path=args.original,
            previous_results_path=args.previous,
        )

        # تشغيل اختبارات التقييم
        evaluation_results = evaluator.run_evaluation_tests()

        # توليد تقرير التقييم
        if args.report:
            evaluator.generate_report(args.report)

        # حفظ نتائج التقييم
        if args.results:
            evaluator.save_results(args.results)

        return 0

    except Exception as e:
        logger.error(f"خطأ أثناء تنفيذ نظام التقييم: {str(e)}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
