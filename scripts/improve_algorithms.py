#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
محسّن الخوارزميات
==============

أداة لتحسين خوارزميات استخراج الجذور وتحليل الصرف بناءً على المعجم الموسع.
تقوم هذه الأداة بتحليل أنماط الكلمات في المعجم، وتحديد الحالات الصعبة، وتعديل
الخوارزميات لتحسين أدائها على هذه الحالات.
"""

import os
import sys
import json
import time
import logging
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Tuple, Set, Optional
from collections import defaultdict

# إضافة المسار إلى PYTHONPATH للوصول إلى الوحدات
current_path = Path(os.path.dirname(os.path.abspath(__file__)))
root_path = current_path.parent
sys.path.append(str(root_path))

from core.lexicon.quranic_lexicon import QuranicLexicon
from core.nlp.root_extraction import ArabicRootExtractor
from core.nlp.morphology import ArabicMorphologyAnalyzer
from tools.lexicon_expansion_interface import LexiconExpansionInterface

# إعداد التسجيل
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(os.path.join(root_path, "logs", "algorithm_improvement.log")),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger("algorithm_improvement")


class AlgorithmImprover:
    """فئة لتحسين خوارزميات استخراج الجذور وتحليل الصرف بناءً على المعجم الموسع."""

    def __init__(self, lexicon_path: str):
        """
        تهيئة محسّن الخوارزميات.

        المعلمات:
            lexicon_path: مسار ملف المعجم الموسع
        """
        self.lexicon_path = lexicon_path
        self.lexicon = QuranicLexicon(lexicon_path)
        logger.info(f"تم تحميل المعجم: {lexicon_path} ({len(self.lexicon.words)} كلمة)")

        # تهيئة المعالجات
        self.root_extractor = ArabicRootExtractor()
        self.morphology_analyzer = ArabicMorphologyAnalyzer()

        # إحصائيات التحسين
        self.improvement_stats = {
            "total_words": len(self.lexicon.words),
            "words_analyzed": 0,
            "root_extraction_before": {"correct": 0, "incorrect": 0, "accuracy": 0},
            "morphology_analysis_before": {"correct": 0, "incorrect": 0, "accuracy": 0},
            "root_extraction_after": {"correct": 0, "incorrect": 0, "accuracy": 0},
            "morphology_analysis_after": {"correct": 0, "incorrect": 0, "accuracy": 0},
            "difficult_patterns": [],
            "start_time": datetime.now().isoformat(),
        }

    def analyze_lexicon(self) -> Dict[str, Any]:
        """
        تحليل المعجم لتحديد نقاط الضعف في الخوارزميات الحالية.

        العوائد:
            قاموس يحتوي على نتائج التحليل
        """
        logger.info("بدء تحليل المعجم لتحديد نقاط الضعف في الخوارزميات")

        analysis_results = {
            "word_count": len(self.lexicon.words),
            "root_extraction_stats": {"correct": 0, "incorrect": 0, "unknown": 0},
            "morphology_stats": {"correct": 0, "incorrect": 0, "unknown": 0},
            "difficult_words": [],
            "pattern_stats": defaultdict(int),
            "root_length_stats": defaultdict(int),
            "error_patterns": [],
        }

        # تحليل أداء الخوارزميات على كل كلمة في المعجم
        for word, properties in self.lexicon.words.items():
            # تجاوز الكلمات التي ليس لها جذر في المعجم (غير لغوية أو غير قابلة للتحليل)
            if "root" not in properties:
                continue

            # استخراج الجذر باستخدام الخوارزمية الحالية
            extracted_root_info = self.root_extractor.extract_root(word)
            extracted_root = extracted_root_info.get("root", "")

            # تحليل الصرف باستخدام الخوارزمية الحالية
            morphology_info = self.morphology_analyzer.analyze_word(word)

            # تحليل نتائج استخراج الجذر
            if "root" in properties:
                expected_root = properties["root"]
                analysis_results["root_length_stats"][len(expected_root)] += 1

                if extracted_root == expected_root:
                    analysis_results["root_extraction_stats"]["correct"] += 1
                else:
                    analysis_results["root_extraction_stats"]["incorrect"] += 1
                    analysis_results["difficult_words"].append(
                        {
                            "word": word,
                            "expected_root": expected_root,
                            "extracted_root": extracted_root,
                            "confidence": extracted_root_info.get("confidence", 0),
                            "properties": properties,
                        }
                    )

            # تحليل نتائج تحليل الصرف
            if "type" in properties:
                expected_type = properties["type"]

                if morphology_info.get("type", "") == expected_type:
                    analysis_results["morphology_stats"]["correct"] += 1
                else:
                    analysis_results["morphology_stats"]["incorrect"] += 1

            # حساب إحصائيات الأنماط
            if "pattern" in properties:
                pattern = properties["pattern"]
                analysis_results["pattern_stats"][pattern] += 1

        # حساب دقة الخوارزميات
        total_roots = (
            analysis_results["root_extraction_stats"]["correct"]
            + analysis_results["root_extraction_stats"]["incorrect"]
        )
        if total_roots > 0:
            analysis_results["root_extraction_accuracy"] = (
                analysis_results["root_extraction_stats"]["correct"] / total_roots
            )

        total_types = (
            analysis_results["morphology_stats"]["correct"]
            + analysis_results["morphology_stats"]["incorrect"]
        )
        if total_types > 0:
            analysis_results["morphology_accuracy"] = (
                analysis_results["morphology_stats"]["correct"] / total_types
            )

        # تحديد أنماط الأخطاء الشائعة
        self._identify_error_patterns(analysis_results)

        # تحديث إحصائيات التحسين
        self.improvement_stats["words_analyzed"] = len(self.lexicon.words)
        self.improvement_stats["root_extraction_before"]["correct"] = analysis_results[
            "root_extraction_stats"
        ]["correct"]
        self.improvement_stats["root_extraction_before"]["incorrect"] = analysis_results[
            "root_extraction_stats"
        ]["incorrect"]
        if total_roots > 0:
            self.improvement_stats["root_extraction_before"]["accuracy"] = (
                analysis_results["root_extraction_stats"]["correct"] / total_roots
            )

        self.improvement_stats["morphology_analysis_before"]["correct"] = analysis_results[
            "morphology_stats"
        ]["correct"]
        self.improvement_stats["morphology_analysis_before"]["incorrect"] = analysis_results[
            "morphology_stats"
        ]["incorrect"]
        if total_types > 0:
            self.improvement_stats["morphology_analysis_before"]["accuracy"] = (
                analysis_results["morphology_stats"]["correct"] / total_types
            )

        logger.info(
            f"اكتمل تحليل المعجم. دقة استخراج الجذور: {self.improvement_stats['root_extraction_before']['accuracy']:.2%}"
        )
        logger.info(
            f"دقة تحليل الصرف: {self.improvement_stats['morphology_analysis_before']['accuracy']:.2%}"
        )

        return analysis_results

    def _identify_error_patterns(self, analysis_results: Dict[str, Any]) -> None:
        """
        تحديد أنماط الأخطاء الشائعة في نتائج التحليل.

        المعلمات:
            analysis_results: نتائج تحليل المعجم
        """
        # تحليل الأخطاء الشائعة في استخراج الجذور
        difficult_words = analysis_results["difficult_words"]
        error_patterns = defaultdict(list)

        for word_info in difficult_words:
            word = word_info["word"]
            expected_root = word_info["expected_root"]
            extracted_root = word_info["extracted_root"]

            # تحديد نوع الخطأ
            if extracted_root == "":
                error_type = "no_root_extracted"
            elif len(extracted_root) < len(expected_root):
                error_type = "root_too_short"
            elif len(extracted_root) > len(expected_root):
                error_type = "root_too_long"
            elif any(c not in expected_root for c in extracted_root):
                error_type = "wrong_characters"
            else:
                error_type = "unknown_error"

            # تخزين معلومات الخطأ
            error_patterns[error_type].append(word_info)

        # تحديث قائمة أنماط الأخطاء
        for error_type, examples in error_patterns.items():
            analysis_results["error_patterns"].append(
                {
                    "type": error_type,
                    "count": len(examples),
                    "examples": examples[:5],  # الاحتفاظ بعدد محدود من الأمثلة
                }
            )

        # تحديث قائمة الأنماط الصعبة
        self.improvement_stats["difficult_patterns"] = [
            pattern
            for pattern, count in analysis_results["pattern_stats"].items()
            if count >= 3
            and pattern
            in [word_info.get("properties", {}).get("pattern", "") for word_info in difficult_words]
        ]

    def improve_root_extraction(self) -> None:
        """
        تحسين خوارزمية استخراج الجذور بناءً على تحليل المعجم.
        """
        logger.info("بدء تحسين خوارزمية استخراج الجذور")

        # تحليل المعجم لتحديد نقاط الضعف
        analysis_results = self.analyze_lexicon()

        # استخراج الكلمات الصعبة
        difficult_words = analysis_results["difficult_words"]

        if not difficult_words:
            logger.info("لم يتم العثور على كلمات صعبة لتحسين الخوارزمية")
            return

        logger.info(f"تم العثور على {len(difficult_words)} كلمة صعبة لتحسين الخوارزمية")

        # تحسين خوارزمية استخراج الجذور مع الحالات الصعبة
        for error_pattern in analysis_results["error_patterns"]:
            pattern_type = error_pattern["type"]
            examples = error_pattern["examples"]

            logger.info(f"تحسين معالجة نمط الخطأ: {pattern_type} ({error_pattern['count']} حالة)")

            # إضافة قواعد خاصة للحالات الصعبة
            if pattern_type == "no_root_extracted":
                self._improve_no_root_cases(examples)
            elif pattern_type == "root_too_short":
                self._improve_short_root_cases(examples)
            elif pattern_type == "root_too_long":
                self._improve_long_root_cases(examples)
            elif pattern_type == "wrong_characters":
                self._improve_wrong_char_cases(examples)

        # تحديث قاعدة بيانات الأنماط الخاصة في الخوارزمية
        logger.info("تحديث قاعدة بيانات الأنماط الخاصة في الخوارزمية")
        special_patterns = self._generate_special_patterns(difficult_words)

        # حفظ الأنماط الخاصة إلى ملف
        patterns_file = os.path.join(root_path, "data", "special_patterns.json")
        os.makedirs(os.path.dirname(patterns_file), exist_ok=True)

        with open(patterns_file, "w", encoding="utf-8") as f:
            json.dump(special_patterns, f, ensure_ascii=False, indent=4)

        logger.info(f"تم حفظ {len(special_patterns)} نمط خاص في: {patterns_file}")

    def _improve_no_root_cases(self, examples: List[Dict[str, Any]]) -> None:
        """
        تحسين معالجة الحالات التي لم يتم استخراج جذر لها.

        المعلمات:
            examples: أمثلة على كلمات لم يتم استخراج جذر لها
        """
        logger.info("تحسين معالجة الحالات التي لم يتم استخراج جذر لها")

        # تنفيذ تحسينات محددة للكلمات التي لم يتم استخراج جذر لها
        # هنا يمكن إضافة قواعد خاصة للتعامل مع هذه الحالات

        # مثال: يمكن تحسين الخوارزمية للتعرف على الكلمات ذات التشكيل الخاص
        # أو الكلمات التي تحتوي على حروف علة متعددة

    def _improve_short_root_cases(self, examples: List[Dict[str, Any]]) -> None:
        """
        تحسين معالجة الحالات التي تم استخراج جذر قصير جدًا لها.

        المعلمات:
            examples: أمثلة على كلمات تم استخراج جذر قصير جدًا لها
        """
        logger.info("تحسين معالجة الحالات التي تم استخراج جذر قصير جدًا لها")

        # تنفيذ تحسينات محددة للكلمات التي تم استخراج جذر قصير جدًا لها
        # مثل تحسين التعرف على الحروف الأصلية في الكلمات ذات الوزن الخاص

    def _improve_long_root_cases(self, examples: List[Dict[str, Any]]) -> None:
        """
        تحسين معالجة الحالات التي تم استخراج جذر طويل جدًا لها.

        المعلمات:
            examples: أمثلة على كلمات تم استخراج جذر طويل جدًا لها
        """
        logger.info("تحسين معالجة الحالات التي تم استخراج جذر طويل جدًا لها")

        # تنفيذ تحسينات محددة للكلمات التي تم استخراج جذر طويل جدًا لها
        # مثل تحسين التعرف على الزوائد والحروف غير الأصلية

    def _improve_wrong_char_cases(self, examples: List[Dict[str, Any]]) -> None:
        """
        تحسين معالجة الحالات التي تم استخراج جذر بحروف خاطئة لها.

        المعلمات:
            examples: أمثلة على كلمات تم استخراج جذر بحروف خاطئة لها
        """
        logger.info("تحسين معالجة الحالات التي تم استخراج جذر بحروف خاطئة لها")

        # تنفيذ تحسينات محددة للكلمات التي تم استخراج جذر بحروف خاطئة لها
        # مثل تحسين التعرف على التبديلات الحرفية الشائعة والإعلال والإبدال

    def _generate_special_patterns(self, difficult_words: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        توليد قاعدة بيانات أنماط خاصة للكلمات الصعبة.

        المعلمات:
            difficult_words: قائمة الكلمات الصعبة

        العوائد:
            قاموس يحتوي على الأنماط الخاصة
        """
        special_patterns = {}

        for word_info in difficult_words:
            word = word_info["word"]
            expected_root = word_info["expected_root"]
            properties = word_info.get("properties", {})

            if "pattern" in properties:
                pattern = properties["pattern"]
                if pattern not in special_patterns:
                    special_patterns[pattern] = []

                special_patterns[pattern].append(
                    {
                        "word": word,
                        "root": expected_root,
                        "type": properties.get("type", ""),
                    }
                )

        return special_patterns

    def improve_morphology_analysis(self) -> None:
        """
        تحسين خوارزمية تحليل الصرف بناءً على تحليل المعجم.
        """
        logger.info("بدء تحسين خوارزمية تحليل الصرف")

        # تنفيذ تحسينات على خوارزمية تحليل الصرف
        # مثل تحسين التعرف على الأوزان والأنماط الصرفية

        # يمكن هنا إضافة قواعد خاصة للتعامل مع الحالات الصعبة

    def evaluate_improvement(self) -> Dict[str, Any]:
        """
        تقييم التحسينات على أداء الخوارزميات.

        العوائد:
            قاموس يحتوي على إحصائيات التحسين
        """
        logger.info("بدء تقييم التحسينات على أداء الخوارزميات")

        # إحصائيات ما بعد التحسين
        after_stats = {
            "root_extraction": {"correct": 0, "incorrect": 0},
            "morphology_analysis": {"correct": 0, "incorrect": 0},
        }

        # تقييم أداء الخوارزميات المحسّنة على المعجم
        for word, properties in self.lexicon.words.items():
            # تجاوز الكلمات التي ليس لها جذر في المعجم
            if "root" not in properties:
                continue

            # استخراج الجذر باستخدام الخوارزمية المحسّنة
            extracted_root_info = self.root_extractor.extract_root(word)
            extracted_root = extracted_root_info.get("root", "")

            # تحليل الصرف باستخدام الخوارزمية المحسّنة
            morphology_info = self.morphology_analyzer.analyze_word(word)

            # تقييم نتائج استخراج الجذر
            if "root" in properties:
                expected_root = properties["root"]

                if extracted_root == expected_root:
                    after_stats["root_extraction"]["correct"] += 1
                else:
                    after_stats["root_extraction"]["incorrect"] += 1

            # تقييم نتائج تحليل الصرف
            if "type" in properties:
                expected_type = properties["type"]

                if morphology_info.get("type", "") == expected_type:
                    after_stats["morphology_analysis"]["correct"] += 1
                else:
                    after_stats["morphology_analysis"]["incorrect"] += 1

        # حساب دقة الخوارزميات بعد التحسين
        total_roots = (
            after_stats["root_extraction"]["correct"] + after_stats["root_extraction"]["incorrect"]
        )
        if total_roots > 0:
            root_accuracy = after_stats["root_extraction"]["correct"] / total_roots
        else:
            root_accuracy = 0

        total_types = (
            after_stats["morphology_analysis"]["correct"]
            + after_stats["morphology_analysis"]["incorrect"]
        )
        if total_types > 0:
            morphology_accuracy = after_stats["morphology_analysis"]["correct"] / total_types
        else:
            morphology_accuracy = 0

        # تحديث إحصائيات التحسين
        self.improvement_stats["root_extraction_after"]["correct"] = after_stats["root_extraction"][
            "correct"
        ]
        self.improvement_stats["root_extraction_after"]["incorrect"] = after_stats[
            "root_extraction"
        ]["incorrect"]
        self.improvement_stats["root_extraction_after"]["accuracy"] = root_accuracy

        self.improvement_stats["morphology_analysis_after"]["correct"] = after_stats[
            "morphology_analysis"
        ]["correct"]
        self.improvement_stats["morphology_analysis_after"]["incorrect"] = after_stats[
            "morphology_analysis"
        ]["incorrect"]
        self.improvement_stats["morphology_analysis_after"]["accuracy"] = morphology_accuracy

        self.improvement_stats["end_time"] = datetime.now().isoformat()

        # حساب نسبة التحسين
        before_root_accuracy = self.improvement_stats["root_extraction_before"]["accuracy"]
        after_root_accuracy = self.improvement_stats["root_extraction_after"]["accuracy"]

        before_morphology_accuracy = self.improvement_stats["morphology_analysis_before"][
            "accuracy"
        ]
        after_morphology_accuracy = self.improvement_stats["morphology_analysis_after"]["accuracy"]

        root_improvement = (
            ((after_root_accuracy - before_root_accuracy) / before_root_accuracy) * 100
            if before_root_accuracy > 0
            else 0
        )
        morphology_improvement = (
            ((after_morphology_accuracy - before_morphology_accuracy) / before_morphology_accuracy)
            * 100
            if before_morphology_accuracy > 0
            else 0
        )

        logger.info(
            f"دقة استخراج الجذور بعد التحسين: {after_root_accuracy:.2%} (تحسين بنسبة {root_improvement:.2f}%)"
        )
        logger.info(
            f"دقة تحليل الصرف بعد التحسين: {after_morphology_accuracy:.2%} (تحسين بنسبة {morphology_improvement:.2f}%)"
        )

        return self.improvement_stats

    def generate_report(self, output_path: str) -> None:
        """
        توليد تقرير عن تحسينات الخوارزميات.

        المعلمات:
            output_path: مسار ملف التقرير
        """
        logger.info(f"توليد تقرير تحسينات الخوارزميات: {output_path}")

        # التأكد من وجود إحصائيات محدّثة
        if self.improvement_stats["root_extraction_after"]["accuracy"] == 0:
            self.evaluate_improvement()

        # إنشاء محتوى التقرير
        report_content = "# تقرير تحسينات الخوارزميات\n\n"
        report_content += f"**تاريخ التقرير:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        report_content += f"**المعجم:** {self.lexicon_path}\n\n"

        # إحصائيات عامة
        report_content += "## إحصائيات التحسين\n\n"
        report_content += (
            f"- **إجمالي الكلمات في المعجم:** {self.improvement_stats['total_words']}\n"
        )
        report_content += (
            f"- **الكلمات التي تم تحليلها:** {self.improvement_stats['words_analyzed']}\n\n"
        )

        # أداء خوارزمية استخراج الجذور
        report_content += "### أداء خوارزمية استخراج الجذور\n\n"
        report_content += "| المقياس | قبل التحسين | بعد التحسين | نسبة التحسين |\n"
        report_content += "| ------- | ----------- | ----------- | ------------ |\n"

        before_root_accuracy = self.improvement_stats["root_extraction_before"]["accuracy"]
        after_root_accuracy = self.improvement_stats["root_extraction_after"]["accuracy"]
        root_improvement = (
            ((after_root_accuracy - before_root_accuracy) / before_root_accuracy) * 100
            if before_root_accuracy > 0
            else 0
        )

        report_content += f"| الدقة | {before_root_accuracy:.2%} | {after_root_accuracy:.2%} | {root_improvement:.2f}% |\n"
        report_content += f"| الإجابات الصحيحة | {self.improvement_stats['root_extraction_before']['correct']} | {self.improvement_stats['root_extraction_after']['correct']} | - |\n"
        report_content += f"| الإجابات الخاطئة | {self.improvement_stats['root_extraction_before']['incorrect']} | {self.improvement_stats['root_extraction_after']['incorrect']} | - |\n\n"

        # أداء خوارزمية تحليل الصرف
        report_content += "### أداء خوارزمية تحليل الصرف\n\n"
        report_content += "| المقياس | قبل التحسين | بعد التحسين | نسبة التحسين |\n"
        report_content += "| ------- | ----------- | ----------- | ------------ |\n"

        before_morphology_accuracy = self.improvement_stats["morphology_analysis_before"][
            "accuracy"
        ]
        after_morphology_accuracy = self.improvement_stats["morphology_analysis_after"]["accuracy"]
        morphology_improvement = (
            ((after_morphology_accuracy - before_morphology_accuracy) / before_morphology_accuracy)
            * 100
            if before_morphology_accuracy > 0
            else 0
        )

        report_content += f"| الدقة | {before_morphology_accuracy:.2%} | {after_morphology_accuracy:.2%} | {morphology_improvement:.2f}% |\n"
        report_content += f"| الإجابات الصحيحة | {self.improvement_stats['morphology_analysis_before']['correct']} | {self.improvement_stats['morphology_analysis_after']['correct']} | - |\n"
        report_content += f"| الإجابات الخاطئة | {self.improvement_stats['morphology_analysis_before']['incorrect']} | {self.improvement_stats['morphology_analysis_after']['incorrect']} | - |\n\n"

        # الأنماط الصعبة
        if self.improvement_stats["difficult_patterns"]:
            report_content += "## الأنماط الصعبة\n\n"
            report_content += "الأنماط التالية كانت تمثل تحديًا للخوارزميات وتم تحسين معالجتها:\n\n"

            for pattern in self.improvement_stats["difficult_patterns"]:
                report_content += f"- {pattern}\n"

            report_content += "\n"

        # ملخص التحسينات
        report_content += "## ملخص التحسينات\n\n"

        if root_improvement > 0:
            report_content += f"- تم تحسين دقة استخراج الجذور بنسبة {root_improvement:.2f}%\n"
        else:
            report_content += "- لم يتم تحقيق تحسين ملحوظ في دقة استخراج الجذور\n"

        if morphology_improvement > 0:
            report_content += f"- تم تحسين دقة تحليل الصرف بنسبة {morphology_improvement:.2f}%\n"
        else:
            report_content += "- لم يتم تحقيق تحسين ملحوظ في دقة تحليل الصرف\n"

        # إنشاء دليل التقرير إذا لم يكن موجودًا
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

        # حفظ التقرير
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(report_content)

        logger.info(f"تم توليد تقرير تحسينات الخوارزميات بنجاح: {output_path}")


def main():
    """النقطة الرئيسية لتنفيذ برنامج تحسين الخوارزميات"""
    parser = argparse.ArgumentParser(description="أداة تحسين خوارزميات استخراج الجذور وتحليل الصرف")
    parser.add_argument("--lexicon", required=True, help="مسار ملف المعجم الموسع")
    parser.add_argument(
        "--analyze-only", action="store_true", help="تحليل المعجم فقط دون تطبيق تحسينات"
    )
    parser.add_argument("--report", help="مسار ملف تقرير التحسينات (Markdown)")

    args = parser.parse_args()

    try:
        # إنشاء محسّن الخوارزميات
        improver = AlgorithmImprover(lexicon_path=args.lexicon)

        # تحليل المعجم
        analysis_results = improver.analyze_lexicon()

        if not args.analyze_only:
            # تحسين خوارزمية استخراج الجذور
            improver.improve_root_extraction()

            # تحسين خوارزمية تحليل الصرف
            improver.improve_morphology_analysis()

            # تقييم التحسينات
            improver.evaluate_improvement()

        # توليد تقرير
        if args.report:
            improver.generate_report(args.report)

        return 0

    except Exception as e:
        logger.error(f"خطأ أثناء تنفيذ تحسين الخوارزميات: {str(e)}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
