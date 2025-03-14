#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
برنامج تقييم أداء مكتبة معالجة اللغة العربية الطبيعية
"""

import re
import json
import os
import csv
import time
import datetime
from typing import Dict, List, Tuple, Any, Optional, Set, Union
from pathlib import Path
import argparse

from core.nlp.root_extraction import ArabicRootExtractor
from core.nlp.diacritics import DiacriticsProcessor
from core.nlp.morphology import ArabicMorphologyAnalyzer
from core.nlp.test_data import get_test_suite, get_problem_cases
from core.lexicon.hybrid_processor import HybridProcessor


# وظائف مستقلة للتقييم يمكن استخدامها من خارج الفئة الرئيسية
def evaluate_root_extraction(
    lexicon_path: str, dataset_path: str, output_report: Optional[str] = None
) -> Dict[str, Any]:
    """
    تقييم أداء استخراج الجذور باستخدام مجموعة بيانات من ملف JSON

    المعاملات:
        lexicon_path: مسار ملف المعجم
        dataset_path: مسار ملف مجموعة البيانات
        output_report: مسار ملف التقرير (اختياري)

    العائد:
        قاموس يحتوي على نتائج التقييم
    """
    # تحميل مجموعة البيانات
    with open(dataset_path, "r", encoding="utf-8") as f:
        dataset = json.load(f)

    # تهيئة المعالج الهجين
    processor = HybridProcessor(lexicon_path)

    # إعداد الإحصائيات
    total_words = len(dataset)
    correct_extractions = 0
    incorrect_extractions = 0
    extraction_times = []
    detailed_results = []

    # معالجة كل كلمة في مجموعة البيانات
    for item in dataset:
        word = item.get("word", "")
        expected_root = item.get("root", "")

        # قياس وقت استخراج الجذر
        start_time = time.time()
        result = processor.extract_root(word)
        end_time = time.time()
        extraction_time = end_time - start_time

        # تحديد مصدر الاستخراج
        source = "algorithm"
        if result.get("source") == "lexicon":
            source = "lexicon"

        # استخراج الجذر والتحقق من صحته
        extracted_root = result.get("root", "")
        is_correct = extracted_root == expected_root

        if is_correct:
            correct_extractions += 1
        else:
            incorrect_extractions += 1

        # تسجيل وقت الاستخراج
        extraction_times.append(extraction_time)

        # حفظ نتائج تفصيلية لهذه الكلمة
        detailed_results.append(
            {
                "word": word,
                "expected": expected_root,
                "extracted": extracted_root,
                "correct": is_correct,
                "source": source,
                "time": extraction_time,
            }
        )

    # حساب دقة الاستخراج ومتوسط الوقت
    accuracy = correct_extractions / total_words if total_words > 0 else 0
    avg_extraction_time = sum(extraction_times) / len(extraction_times) if extraction_times else 0

    # تجميع النتائج
    results = {
        "total_words": total_words,
        "correct_extractions": correct_extractions,
        "incorrect_extractions": incorrect_extractions,
        "accuracy": accuracy,
        "extraction_times": extraction_times,
        "avg_extraction_time": avg_extraction_time,
        "detailed_results": detailed_results,
    }

    # إنشاء تقرير إذا تم تحديد مسار له
    if output_report:
        error_analysis = analyze_error_patterns(detailed_results)
        evaluation_data = {
            "metrics": {
                "total_words": total_words,
                "correct_extractions": correct_extractions,
                "incorrect_extractions": incorrect_extractions,
                "accuracy": accuracy,
                "avg_extraction_time": avg_extraction_time,
            },
            "detailed_results": detailed_results,
            "error_analysis": error_analysis,
        }
        generate_evaluation_report(
            evaluation_data=evaluation_data,
            output_path=output_report,
            title="تقرير تقييم استخراج الجذور",
            description="تقرير تفصيلي عن أداء خوارزمية استخراج الجذور",
        )

    return results


def evaluate_with_custom_dataset(
    processor: HybridProcessor,
    dataset: List[Dict[str, Any]],
    evaluation_type: str = "root_extraction",
) -> Dict[str, Any]:
    """
    تقييم أداء المعالج الهجين باستخدام مجموعة بيانات مخصصة

    المعاملات:
        processor: كائن من فئة المعالج الهجين
        dataset: قائمة تحتوي على عناصر البيانات المخصصة
        evaluation_type: نوع التقييم (استخراج الجذور، تحديد نوع الكلمة، إلخ)

    العائد:
        قاموس يحتوي على نتائج التقييم
    """
    # إعداد الإحصائيات
    total_words = len(dataset)
    correct_extractions = 0
    incorrect_extractions = 0
    detailed_results = []
    extraction_sources = {"lexicon": 0, "algorithm": 0}

    # معالجة كل كلمة في مجموعة البيانات
    for item in dataset:
        word = item.get("word", "")

        if evaluation_type == "root_extraction":
            expected_root = item.get("root", "")
            result = processor.extract_root(word)
            extracted_root = result.get("root", "")
            source = result.get("source", "algorithm")
            is_correct = extracted_root == expected_root

            # تحديث الإحصائيات
            if is_correct:
                correct_extractions += 1
            else:
                incorrect_extractions += 1

            # تحديث عدد الاستخراجات حسب المصدر
            extraction_sources[source] += 1

            # حفظ نتائج تفصيلية لهذه الكلمة
            detailed_results.append(
                {
                    "word": word,
                    "expected": expected_root,
                    "extracted": extracted_root,
                    "correct": is_correct,
                    "source": source,
                }
            )

        elif evaluation_type == "word_type":
            expected_type = item.get("type", "")
            result = processor.process_word(word)
            extracted_type = result.get("type", "")
            source = result.get("source", "algorithm")
            is_correct = extracted_type == expected_type

            # تحديث الإحصائيات
            if is_correct:
                correct_extractions += 1
            else:
                incorrect_extractions += 1

            # تحديث عدد الاستخراجات حسب المصدر
            extraction_sources[source] += 1

            # حفظ نتائج تفصيلية لهذه الكلمة
            detailed_results.append(
                {
                    "word": word,
                    "expected": expected_type,
                    "extracted": extracted_type,
                    "correct": is_correct,
                    "source": source,
                }
            )

    # حساب دقة التقييم
    accuracy = correct_extractions / total_words if total_words > 0 else 0

    # تجميع النتائج
    results = {
        "total_words": total_words,
        "correct_extractions": correct_extractions,
        "incorrect_extractions": incorrect_extractions,
        "accuracy": accuracy,
        "extraction_sources": extraction_sources,
        "detailed_results": detailed_results,
    }

    return results


def analyze_error_patterns(detailed_results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    تحليل أنماط الأخطاء في نتائج التقييم التفصيلية

    المعاملات:
        detailed_results: قائمة تحتوي على النتائج التفصيلية لكل كلمة

    العائد:
        قاموس يحتوي على تحليل أنماط الأخطاء
    """
    # تصنيف الأخطاء
    common_error_patterns = {}
    error_by_word_length = {}
    error_by_word_type = {
        "اسم": {"total": 0, "errors": 0},
        "فعل": {"total": 0, "errors": 0},
        "حرف": {"total": 0, "errors": 0},
        "أخرى": {"total": 0, "errors": 0},
    }
    error_by_extraction_source = {"lexicon": 0, "algorithm": 0}
    common_error_substitutions = {}

    for result in detailed_results:
        word = result.get("word", "")
        expected = result.get("expected", "")
        extracted = result.get("extracted", "")
        is_correct = result.get("correct", False)
        source = result.get("source", "algorithm")
        word_type = result.get("type", "أخرى") if "type" in result else "أخرى"

        # تحديث إحصائيات النوع
        if word_type in error_by_word_type:
            error_by_word_type[word_type]["total"] += 1
            if not is_correct:
                error_by_word_type[word_type]["errors"] += 1
        else:
            error_by_word_type["أخرى"]["total"] += 1
            if not is_correct:
                error_by_word_type["أخرى"]["errors"] += 1

        # إذا كانت النتيجة خاطئة
        if not is_correct:
            # تحليل أخطاء حسب طول الكلمة
            word_length = str(len(word))
            if word_length in error_by_word_length:
                error_by_word_length[word_length] += 1
            else:
                error_by_word_length[word_length] = 1

            # تحليل أخطاء حسب مصدر الاستخراج
            error_by_extraction_source[source] += 1

            # تحليل أنماط استبدال الحروف الشائعة
            error_pattern = f"{expected}/{extracted}"
            if error_pattern in common_error_patterns:
                common_error_patterns[error_pattern] += 1
            else:
                common_error_patterns[error_pattern] = 1

            # تحليل استبدالات الحروف الشائعة
            if len(expected) == len(extracted):
                for i in range(len(expected)):
                    if i < len(extracted) and expected[i] != extracted[i]:
                        substitution = f"{expected[i]}->{extracted[i]}"
                        if substitution in common_error_substitutions:
                            common_error_substitutions[substitution] += 1
                        else:
                            common_error_substitutions[substitution] = 1

    # تحويل البيانات إلى النسب المئوية
    word_type_error_rates = {}
    for type_name, stats in error_by_word_type.items():
        if stats["total"] > 0:
            word_type_error_rates[type_name] = stats["errors"] / stats["total"]
        else:
            word_type_error_rates[type_name] = 0

    # ترتيب النتائج حسب التكرار
    common_error_patterns = dict(
        sorted(common_error_patterns.items(), key=lambda x: x[1], reverse=True)
    )
    error_by_word_length = dict(
        sorted(error_by_word_length.items(), key=lambda x: x[1], reverse=True)
    )
    common_error_substitutions = dict(
        sorted(common_error_substitutions.items(), key=lambda x: x[1], reverse=True)
    )

    return {
        "common_error_patterns": common_error_patterns,
        "error_by_word_length": error_by_word_length,
        "error_by_word_type": word_type_error_rates,
        "error_by_extraction_source": error_by_extraction_source,
        "common_error_substitutions": common_error_substitutions,
    }


def generate_evaluation_report(
    evaluation_data: Dict[str, Any],
    output_path: str,
    title: str = "تقرير تقييم معالجة اللغة العربية",
    description: str = "تقرير تفصيلي عن أداء خوارزميات معالجة اللغة العربية",
) -> str:
    """
    توليد تقرير تقييم شامل بتنسيق Markdown

    المعاملات:
        evaluation_data: بيانات التقييم
        output_path: مسار ملف التقرير
        title: عنوان التقرير
        description: وصف التقرير

    العائد:
        مسار ملف التقرير
    """
    metrics = evaluation_data.get("metrics", {})
    detailed_results = evaluation_data.get("detailed_results", [])
    error_analysis = evaluation_data.get("error_analysis", {})

    # إنشاء محتوى التقرير
    report_content = f"""# {title}

{description}

## ملخص النتائج

- تاريخ التقييم: {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
- إجمالي الكلمات: {metrics.get("total_words", 0)}
- الكلمات الصحيحة: {metrics.get("correct_extractions", 0)}
- الكلمات الخاطئة: {metrics.get("incorrect_extractions", 0)}
- الدقة: {metrics.get("accuracy", 0) * 100:.2f}%
- متوسط وقت المعالجة: {metrics.get("avg_extraction_time", 0) * 1000:.2f} مللي ثانية

## تحليل الأخطاء

### أنماط الخطأ الشائعة

| نمط الخطأ | عدد الحالات |
|-----------|-------------|
"""

    # إضافة أنماط الخطأ الشائعة
    common_error_patterns = error_analysis.get("common_error_patterns", {})
    for pattern, count in list(common_error_patterns.items())[:10]:  # أخذ أول 10 أنماط فقط
        report_content += f"| {pattern} | {count} |\n"

    # إضافة توزيع الأخطاء حسب طول الكلمة
    report_content += """
### توزيع الأخطاء حسب طول الكلمة

| طول الكلمة | عدد الأخطاء |
|------------|-------------|
"""

    error_by_word_length = error_analysis.get("error_by_word_length", {})
    for length, count in error_by_word_length.items():
        report_content += f"| {length} | {count} |\n"

    # إضافة توزيع الأخطاء حسب نوع الكلمة
    report_content += """
### توزيع الأخطاء حسب نوع الكلمة

| نوع الكلمة | معدل الخطأ |
|------------|------------|
"""

    error_by_word_type = error_analysis.get("error_by_word_type", {})
    for type_name, error_rate in error_by_word_type.items():
        report_content += f"| {type_name} | {error_rate * 100:.2f}% |\n"

    # إضافة توزيع الأخطاء حسب مصدر الاستخراج
    report_content += """
### توزيع الأخطاء حسب مصدر الاستخراج

| المصدر | عدد الأخطاء |
|--------|-------------|
"""

    error_by_source = error_analysis.get("error_by_extraction_source", {})
    for source, count in error_by_source.items():
        report_content += f"| {source} | {count} |\n"

    # إضافة أمثلة على الكلمات الخاطئة
    report_content += """
## أمثلة على الكلمات الخاطئة

| الكلمة | الجذر المتوقع | الجذر المستخرج | المصدر |
|--------|---------------|----------------|--------|
"""

    # إضافة أمثلة من النتائج التفصيلية
    error_examples = [result for result in detailed_results if not result.get("correct", True)]
    for example in error_examples[:20]:  # أخذ أول 20 مثال فقط
        word = example.get("word", "")
        expected = example.get("expected", "")
        extracted = example.get("extracted", "")
        source = example.get("source", "")
        report_content += f"| {word} | {expected} | {extracted} | {source} |\n"

    # كتابة التقرير إلى ملف
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(report_content)

    return output_path


def get_evaluation_metrics(detailed_results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    حساب مقاييس تقييم الأداء من النتائج التفصيلية

    المعاملات:
        detailed_results: قائمة تحتوي على النتائج التفصيلية لكل كلمة

    العائد:
        قاموس يحتوي على مقاييس التقييم
    """
    # إعداد المقاييس
    total_words = len(detailed_results)
    correct_extractions = sum(1 for result in detailed_results if result.get("correct", False))
    incorrect_extractions = total_words - correct_extractions

    # حساب الدقة
    accuracy = correct_extractions / total_words if total_words > 0 else 0

    # حساب دقة التصنيف الثنائي (precision, recall, f1)
    true_positives = correct_extractions
    false_positives = incorrect_extractions
    false_negatives = 0  # لا يمكن حسابها مباشرة من البيانات المقدمة

    precision = (
        true_positives / (true_positives + false_positives)
        if (true_positives + false_positives) > 0
        else 0
    )
    recall = (
        true_positives / (true_positives + false_negatives)
        if (true_positives + false_negatives) > 0
        else 1.0
    )
    f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0

    # حساب توزيع مصادر الاستخراج
    extraction_sources = {"lexicon": 0, "algorithm": 0}
    for result in detailed_results:
        source = result.get("source", "algorithm")
        extraction_sources[source] += 1

    return {
        "total_words": total_words,
        "correct_extractions": correct_extractions,
        "incorrect_extractions": incorrect_extractions,
        "accuracy": accuracy,
        "precision": precision,
        "recall": recall,
        "f1_score": f1_score,
        "extraction_sources": extraction_sources,
    }


def load_custom_dataset_from_csv(filepath: str, has_header: bool = True) -> Dict[str, Tuple]:
    """
    تحميل مجموعة بيانات مخصصة من ملف CSV

    المعاملات:
        filepath: مسار ملف البيانات
        has_header: هل يحتوي الملف على صف عناوين

    العائد:
        قاموس يحتوي على بيانات الاختبار بتنسيق {كلمة: (جذر، نوع، وزن، معنى)}
    """
    dataset = {}

    with open(filepath, "r", encoding="utf-8") as f:
        reader = csv.reader(f)

        # تخطي صف العناوين إذا كان موجودًا
        if has_header:
            next(reader)

        for row in reader:
            if len(row) >= 4:  # نتوقع على الأقل الكلمة، الجذر، النوع، الوزن
                word = row[0].strip()
                root = row[1].strip()
                word_type = row[2].strip()
                pattern = row[3].strip()
                meaning = row[4].strip() if len(row) > 4 else ""

                dataset[word] = (root, word_type, pattern, meaning)

    return dataset


def load_custom_dataset_from_json(filepath: str) -> Dict[str, Tuple]:
    """
    تحميل مجموعة بيانات مخصصة من ملف JSON

    المعاملات:
        filepath: مسار ملف البيانات

    العائد:
        قاموس يحتوي على بيانات الاختبار بتنسيق {كلمة: (جذر، نوع، وزن، معنى)}
    """
    dataset = {}

    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

        for word, details in data.items():
            if isinstance(details, dict):
                root = details.get("root", "")
                word_type = details.get("type", "")
                pattern = details.get("pattern", "")
                meaning = details.get("meaning", "")

                dataset[word] = (root, word_type, pattern, meaning)
            elif isinstance(details, list) and len(details) >= 3:
                root = details[0]
                word_type = details[1]
                pattern = details[2]
                meaning = details[3] if len(details) > 3 else ""

                dataset[word] = (root, word_type, pattern, meaning)

    return dataset


def merge_datasets(*datasets) -> Dict[str, Tuple]:
    """
    دمج عدة مجموعات بيانات في مجموعة واحدة

    المعاملات:
        *datasets: مجموعات البيانات المراد دمجها

    العائد:
        مجموعة البيانات المدمجة
    """
    merged = {}

    for dataset in datasets:
        merged.update(dataset)

    return merged


class NLPEvaluator:
    """
    مقيّم أداء مكتبة معالجة اللغة العربية الطبيعية
    """

    def __init__(
        self, custom_dataset: Dict = None, custom_problem_cases: Dict = None, settings: Dict = None
    ):
        """
        تهيئة المقيّم

        المعاملات:
            custom_dataset: مجموعة بيانات مخصصة {كلمة: (جذر، نوع، وزن، معنى)}
            custom_problem_cases: حالات إشكالية مخصصة {كلمة: (وصف المشكلة، نوع المشكلة)}
            settings: إعدادات التقييم
        """
        # إعداد المعالجات
        self.diacritics_processor = DiacriticsProcessor()
        self.root_extractor = ArabicRootExtractor()
        self.morphology_analyzer = ArabicMorphologyAnalyzer()

        # الإعدادات الافتراضية
        self.settings = {
            "verbose": True,  # طباعة تفاصيل التقييم أثناء التنفيذ
            "report_format": "json",  # صيغة التقرير (json, csv, html)
            "save_errors": True,  # حفظ حالات الخطأ في التقييم
            "error_analysis": True,  # تحليل أنماط الأخطاء
            "algorithms_to_evaluate": [
                "light",
                "stem",
                "pattern",
                "hybrid",
            ],  # خوارزميات استخراج الجذور للتقييم
        }

        # تحديث الإعدادات بالقيم المخصصة
        if settings:
            self.settings.update(settings)

        # الحصول على مجموعة البيانات المرجعية
        if custom_dataset:
            self.reference_data = custom_dataset
        else:
            self.reference_data = get_test_suite()

        # الحصول على الحالات الإشكالية
        if custom_problem_cases:
            self.problem_cases = custom_problem_cases
        else:
            self.problem_cases = get_problem_cases()

        # نتائج الاختبار
        self.results = {
            "root_extraction": {
                "correct": 0,
                "incorrect": 0,
                "errors": {},
                "algorithms": {},
            },
            "word_classification": {
                "correct": 0,
                "incorrect": 0,
                "errors": {},
            },
            "pattern_recognition": {
                "correct": 0,
                "incorrect": 0,
                "errors": {},
            },
            "problem_cases": {},
            "dataset_info": {
                "total_words": len(self.reference_data),
                "custom_dataset": custom_dataset is not None,
            },
        }

        # تاريخ التقييم
        self.evaluation_date = datetime.datetime.now().isoformat()

    def evaluate_root_extraction(self, algorithm: str = "hybrid") -> Dict:
        """
        تقييم أداء خوارزمية استخراج الجذور

        Args:
            algorithm: خوارزمية الاستخراج (light, stem, pattern, hybrid)

        Returns:
            نتائج التقييم
        """
        print(f"\n=== تقييم أداء استخراج الجذور (الخوارزمية: {algorithm}) ===\n")
        correct = 0
        incorrect = 0
        errors = {}

        for word, details in self.reference_data.items():
            reference_root, _, _, _ = details

            # إزالة التشكيل للاختبار
            normalized_word = self.diacritics_processor.remove_all_diacritics(word)

            # استخراج الجذر باستخدام الخوارزمية المحددة
            extracted_root = self.root_extractor.extract_root(normalized_word, algorithm=algorithm)

            # مقارنة النتيجة
            if extracted_root == reference_root:
                correct += 1
                result = "✓"
            else:
                incorrect += 1
                errors[normalized_word] = {
                    "extracted": extracted_root,
                    "reference": reference_root,
                }
                result = "✗"

            print(
                f"{result} الكلمة: {normalized_word} | الجذر المتوقع: {reference_root} | الجذر المستخرج: {extracted_root}"
            )

        # حساب دقة الخوارزمية
        total = correct + incorrect
        accuracy = (correct / total) * 100 if total > 0 else 0

        # تحديث النتائج
        self.results["root_extraction"]["correct"] = correct
        self.results["root_extraction"]["incorrect"] = incorrect
        self.results["root_extraction"]["errors"] = errors
        self.results["root_extraction"]["accuracy"] = accuracy
        self.results["root_extraction"]["algorithm"] = algorithm
        self.results["root_extraction"]["timestamp"] = self.evaluation_date

        print(f"\nالنتيجة: {correct} صحيحة من أصل {total} ({accuracy:.2f}%)")
        return self.results["root_extraction"]

    def _load_word_classification_data(self):
        """
        تحميل بيانات اختبار تصنيف الكلمات
        يرجع قائمة من الأزواج (كلمة، نوع) للاختبار
        """
        test_data = [
            # كلمات من مجموعة أفعال
            ("كتب", "فعل"),
            ("يكتب", "فعل"),
            ("درس", "فعل"),
            ("يدرس", "فعل"),
            ("قال", "فعل"),
            ("يقول", "فعل"),
            ("سأل", "فعل"),
            ("يسأل", "فعل"),
            ("ذهب", "فعل"),
            ("يذهب", "فعل"),
            ("سيذهب", "فعل"),
            ("ذهبوا", "فعل"),
            ("اذهب", "فعل"),
            ("استغفر", "فعل"),
            ("يستغفر", "فعل"),
            ("اجتمع", "فعل"),
            ("يجتمع", "فعل"),
            # كلمات من مجموعة الأسماء
            ("كتاب", "اسم"),
            ("كاتب", "اسم"),
            ("مكتب", "اسم"),
            ("مكتبة", "اسم"),
            ("كتابة", "اسم"),
            ("مكتوبات", "اسم"),
            ("درس", "اسم"),
            ("مدرسة", "اسم"),
            ("دراسة", "اسم"),
            ("قول", "اسم"),
            ("مقال", "اسم"),
            ("سؤال", "اسم"),
            ("علم", "اسم"),
            ("عالم", "اسم"),
            ("معلم", "اسم"),
            # كلمات من مجموعة الحروف
            ("في", "حرف"),
            ("من", "حرف"),
            ("إلى", "حرف"),
            ("على", "حرف"),
            ("عن", "حرف"),
            ("لم", "حرف"),
            ("لن", "حرف"),
            ("لا", "حرف"),
            ("و", "حرف"),
            ("ف", "حرف"),
            ("ثم", "حرف"),
            ("إن", "حرف"),
        ]
        return test_data

    def evaluate_word_classification(self):
        """
        تقييم أداء تصنيف الكلمات
        """
        print("\n===== تقييم تصنيف الكلمات =====\n")

        # إعداد الإحصائيات
        correct_count = 0
        total_count = 0
        error_cases = {}

        # تحميل بيانات الاختبار
        test_data = self._load_word_classification_data()

        print("=== تقييم أداء تصنيف الكلمات ===\n")

        # تخطيط لترجمة أنواع الكلمات من الإنجليزية إلى العربية
        type_translation = {"noun": "اسم", "verb": "فعل", "particle": "حرف"}

        # تحليل الكلمات
        for word, expected_type in test_data:
            # تطبيع الكلمة (إزالة التشكيل)
            normalized_word = self.diacritics_processor.remove_all_diacritics(word)

            # تحليل الكلمة
            word_type_en = self.morphology_analyzer._determine_word_type(normalized_word)
            word_type_ar = type_translation.get(word_type_en, word_type_en)

            # مقارنة النتيجة مع المتوقع
            is_correct = word_type_ar == expected_type
            total_count += 1

            if is_correct:
                correct_count += 1
                print(
                    f"✓ الكلمة: {word} | النوع المتوقع: {expected_type} | النوع المستخرج: {word_type_ar}"
                )
            else:
                print(
                    f"✗ الكلمة: {word} | النوع المتوقع: {expected_type} | النوع المستخرج: {word_type_ar}"
                )
                # تخزين حالة الخطأ
                error_cases[word] = {"expected": expected_type, "actual": word_type_ar}

        # حساب الدقة
        accuracy = correct_count / total_count * 100 if total_count > 0 else 0
        print(f"\nالنتيجة: {correct_count} صحيحة من أصل {total_count} ({accuracy:.2f}%)")

        # تخزين النتائج في المتغير الخاص بالكلاس
        self.results["word_classification"] = {
            "correct": correct_count,
            "total": total_count,
            "accuracy": accuracy,
            "errors": error_cases,
            "timestamp": self.evaluation_date,
        }

    def evaluate_pattern_recognition(self) -> Dict:
        """
        تقييم أداء استخراج الوزن الصرفي

        Returns:
            نتائج التقييم
        """
        print("\n=== تقييم أداء استخراج الوزن الصرفي ===\n")
        correct = 0
        incorrect = 0
        errors = {}

        for word, details in self.reference_data.items():
            _, _, reference_pattern, _ = details

            # إزالة التشكيل للاختبار
            normalized_word = self.diacritics_processor.remove_all_diacritics(word)
            normalized_pattern = self.diacritics_processor.remove_all_diacritics(reference_pattern)

            # استخراج الوزن
            extracted_pattern = self.root_extractor.get_word_pattern(normalized_word)
            normalized_extracted = self.diacritics_processor.remove_all_diacritics(
                extracted_pattern
            )

            # مقارنة النتيجة (بدون تشكيل للمقارنة العادلة)
            if normalized_extracted == normalized_pattern:
                correct += 1
                result = "✓"
            else:
                incorrect += 1
                errors[normalized_word] = {
                    "extracted": extracted_pattern,
                    "reference": reference_pattern,
                }
                result = "✗"

            print(
                f"{result} الكلمة: {normalized_word} | الوزن المتوقع: {reference_pattern} | الوزن المستخرج: {extracted_pattern}"
            )

        # حساب دقة استخراج الوزن
        total = correct + incorrect
        accuracy = (correct / total) * 100 if total > 0 else 0

        # تحديث النتائج
        self.results["pattern_recognition"]["correct"] = correct
        self.results["pattern_recognition"]["incorrect"] = incorrect
        self.results["pattern_recognition"]["errors"] = errors
        self.results["pattern_recognition"]["accuracy"] = accuracy
        self.results["pattern_recognition"]["timestamp"] = self.evaluation_date

        print(f"\nالنتيجة: {correct} صحيحة من أصل {total} ({accuracy:.2f}%)")
        return self.results["pattern_recognition"]

    def evaluate_problem_cases(self) -> Dict:
        """
        تقييم أداء المكتبة على الحالات الإشكالية المحددة

        Returns:
            نتائج التقييم
        """
        print("\n=== تقييم أداء المكتبة على الحالات الإشكالية ===\n")
        results = {}

        # تحويل أنواع الكلمات من الإنجليزية إلى العربية للمقارنة
        type_translation = {"noun": "اسم", "verb": "فعل", "particle": "حرف"}

        for word, (expected_issue, issue_type) in self.problem_cases.items():
            print(f"\nاختبار الكلمة: {word} (نوع المشكلة: {issue_type})")

            # استخراج الجذر
            extracted_root = self.root_extractor.extract_root(word, algorithm="hybrid")
            print(f"الجذر المستخرج: {extracted_root}")

            # تحليل الكلمة
            analysis = self.morphology_analyzer.analyze_word(word)
            extracted_type_en = analysis.get("type", "")
            extracted_type = type_translation.get(extracted_type_en, "غير معروف")
            print(f"نوع الكلمة: {extracted_type}")

            # استخراج الوزن
            extracted_pattern = self.root_extractor.get_word_pattern(word)
            print(f"الوزن المستخرج: {extracted_pattern}")

            # تسجيل النتائج
            results[word] = {
                "expected_issue": expected_issue,
                "issue_type": issue_type,
                "extracted_root": extracted_root,
                "extracted_type": extracted_type,
                "extracted_pattern": extracted_pattern,
            }

        # تحديث النتائج
        self.results["problem_cases"] = results
        return results

    def run_complete_evaluation(self) -> Dict:
        """
        تشغيل تقييم شامل لجميع وظائف المكتبة

        Returns:
            نتائج التقييم الشامل
        """
        # تقييم استخراج الجذور بجميع الخوارزميات
        print("\n===== تقييم استخراج الجذور بمختلف الخوارزميات =====")

        # الخوارزميات المطلوب تقييمها
        algorithms = self.settings.get(
            "algorithms_to_evaluate", ["light", "stem", "pattern", "hybrid"]
        )
        self.results["root_extraction"]["algorithms"] = {}

        for algorithm in algorithms:
            print(f"\n--- تقييم خوارزمية استخراج الجذور: {algorithm} ---")
            result = self.evaluate_root_extraction(algorithm)

            # تسجيل نتائج كل خوارزمية بشكل منفصل
            self.results["root_extraction"]["algorithms"][algorithm] = {
                "accuracy": result["accuracy"],
                "correct": result["correct"],
                "incorrect": result["incorrect"],
                "errors": result["errors"] if self.settings.get("save_errors", True) else {},
            }

        # تقييم تصنيف الكلمات
        print("\n===== تقييم تصنيف الكلمات =====")
        self.evaluate_word_classification()

        # تقييم استخراج الوزن الصرفي
        print("\n===== تقييم استخراج الوزن الصرفي =====")
        self.evaluate_pattern_recognition()

        # تقييم الحالات الإشكالية إذا كانت الإعدادات تتطلب ذلك
        if self.settings.get("evaluate_problem_cases", True):
            print("\n===== تقييم الحالات الإشكالية =====")
            self.evaluate_problem_cases()

        # تحليل الأخطاء إذا كانت الإعدادات تتطلب ذلك
        if self.settings.get("error_analysis", True):
            print("\n===== تحليل أنماط الأخطاء =====")
            error_analysis = self.analyze_errors()
            self.results["error_analysis"] = error_analysis

        # تلخيص النتائج
        print("\n===== ملخص نتائج التقييم =====\n")

        print("نتائج استخراج الجذور:")
        for algorithm, result in self.results["root_extraction"]["algorithms"].items():
            print(
                f"- الخوارزمية {algorithm}: {result['accuracy']:.2f}% ({result['correct']} صحيحة من أصل {result['correct'] + result['incorrect']})"
            )

        print(
            f"\nنتائج تصنيف الكلمات: {self.results['word_classification']['accuracy']:.2f}% ({self.results['word_classification']['correct']} صحيحة من أصل {self.results['word_classification']['total']})"
        )

        print(
            f"\nنتائج استخراج الوزن الصرفي: {self.results['pattern_recognition']['accuracy']:.2f}% ({self.results['pattern_recognition']['correct']} صحيحة من أصل {self.results['pattern_recognition']['correct'] + self.results['pattern_recognition']['incorrect']})"
        )

        return self.results

    def save_results(self, filename: str = "nlp_evaluation_results.json") -> None:
        """
        حفظ نتائج التقييم في ملف JSON

        Args:
            filename: اسم الملف لحفظ النتائج
        """
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(self.results, f, ensure_ascii=False, indent=4)

        print(f"\nتم حفظ نتائج التقييم في الملف: {filename}")

    def analyze_errors(self) -> Dict:
        """
        تحليل الأخطاء وتصنيفها لفهم أنماط الضعف في المكتبة

        Returns:
            تحليل الأخطاء حسب النوع
        """
        print("\n===== تحليل الأخطاء =====\n")

        # تحليل أخطاء استخراج الجذور
        root_errors = self.results["root_extraction"]["errors"]
        root_error_patterns = {
            "حذف بعض حروف الجذر": 0,
            "إضافة حروف للجذر": 0,
            "تبديل الحروف": 0,
            "خطأ في التعامل مع السوابق": 0,
            "خطأ في التعامل مع اللواحق": 0,
            "أخطاء أخرى": 0,
        }

        for word, error in root_errors.items():
            extracted = error["extracted"]
            reference = error["reference"]

            if len(extracted) < len(reference):
                if all(char in reference for char in extracted):
                    root_error_patterns["حذف بعض حروف الجذر"] += 1
                elif word.startswith(("م", "ت", "ا", "ي", "س")):
                    root_error_patterns["خطأ في التعامل مع السوابق"] += 1
                else:
                    root_error_patterns["أخطاء أخرى"] += 1
            elif len(extracted) > len(reference):
                if all(char in extracted for char in reference):
                    root_error_patterns["إضافة حروف للجذر"] += 1
                elif word.endswith(("ة", "ات", "ون", "ين", "ان")):
                    root_error_patterns["خطأ في التعامل مع اللواحق"] += 1
                else:
                    root_error_patterns["أخطاء أخرى"] += 1
            else:
                root_error_patterns["تبديل الحروف"] += 1

        # تحليل أخطاء تصنيف الكلمات
        classification_errors = self.results["word_classification"]["errors"]
        classification_error_patterns = {
            "تصنيف فعل كاسم": 0,
            "تصنيف اسم كفعل": 0,
            "تصنيف حرف كاسم/فعل": 0,
            "أخطاء أخرى": 0,
        }

        for word, error in classification_errors.items():
            expected = error["expected"]
            actual = error["actual"]

            if expected == "فعل" and actual == "اسم":
                classification_error_patterns["تصنيف فعل كاسم"] += 1
            elif expected == "اسم" and actual == "فعل":
                classification_error_patterns["تصنيف اسم كفعل"] += 1
            elif expected == "حرف":
                classification_error_patterns["تصنيف حرف كاسم/فعل"] += 1
            else:
                classification_error_patterns["أخطاء أخرى"] += 1

        # طباعة نتائج تحليل الأخطاء
        print("أنماط أخطاء استخراج الجذور:")
        for pattern, count in root_error_patterns.items():
            print(f"- {pattern}: {count} حالة")

        print("\nأنماط أخطاء تصنيف الكلمات:")
        for pattern, count in classification_error_patterns.items():
            print(f"- {pattern}: {count} حالة")

        error_analysis = {
            "root_error_patterns": root_error_patterns,
            "classification_error_patterns": classification_error_patterns,
            "timestamp": self.evaluation_date,
        }

        return error_analysis

    def generate_report(self, format_type: str = None, output_file: str = None) -> str:
        """
        توليد تقرير بتنسيق محدد استنادًا إلى نتائج التقييم

        المعاملات:
            format_type: نوع تنسيق التقرير (json, csv, html)
            output_file: مسار ملف الخرج لحفظ التقرير

        العائد:
            مسار الملف الذي تم إنشاؤه أو محتوى التقرير كنص
        """
        # استخدام التنسيق المحدد في الإعدادات إذا لم يتم تحديده
        if not format_type:
            format_type = self.settings.get("report_format", "json")

        # توليد التقرير بناءً على النوع المطلوب
        if format_type.lower() == "json":
            report = self._generate_json_report()
            default_filename = "nlp_evaluation_results.json"
        elif format_type.lower() == "csv":
            report = self._generate_csv_report()
            default_filename = "nlp_evaluation_results.csv"
        elif format_type.lower() == "html":
            report = self._generate_html_report()
            default_filename = "nlp_evaluation_results.html"
        else:
            raise ValueError(f"تنسيق التقرير غير مدعوم: {format_type}")

        # حفظ التقرير إذا تم تحديد ملف للخرج
        if output_file:
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(report)
            print(f"تم حفظ التقرير بنجاح في: {output_file}")
            return output_file
        else:
            # استخدام اسم الملف الافتراضي إذا لم يتم تحديد اسم
            output_path = default_filename
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(report)
            print(f"تم حفظ التقرير بنجاح في: {output_path}")
            return output_path

    def _generate_json_report(self) -> str:
        """توليد تقرير بتنسيق JSON من نتائج التقييم"""
        # إضافة معلومات إضافية عن التقييم
        report_data = {
            "evaluation_date": self.evaluation_date,
            "summary": self._generate_summary(),
            "results": self.results,
        }

        # إضافة تحليل الأخطاء إذا تم طلب ذلك
        if self.settings.get("error_analysis", True):
            report_data["error_analysis"] = self.analyze_errors()

        return json.dumps(report_data, ensure_ascii=False, indent=4)

    def _generate_csv_report(self) -> str:
        """توليد تقرير بتنسيق CSV من نتائج التقييم"""
        lines = []

        # إضافة رأس الملف
        lines.append("نوع التقييم,عدد الحالات,عدد النجاح,عدد الفشل,دقة التقييم")

        # إضافة نتائج استخراج الجذور
        root_data = self.results["root_extraction"]
        total_root = root_data["correct"] + root_data["incorrect"]
        accuracy_root = (root_data["correct"] / total_root * 100) if total_root > 0 else 0
        lines.append(
            f"استخراج الجذور,{total_root},{root_data['correct']},{root_data['incorrect']},{accuracy_root:.2f}%"
        )

        # إضافة نتائج كل خوارزمية
        for alg, data in self.results["root_extraction"].get("algorithms", {}).items():
            total = data.get("correct", 0) + data.get("incorrect", 0)
            accuracy = (data.get("correct", 0) / total * 100) if total > 0 else 0
            lines.append(
                f"استخراج الجذور ({alg}),{total},{data.get('correct', 0)},{data.get('incorrect', 0)},{accuracy:.2f}%"
            )

        # إضافة نتائج تصنيف الكلمات
        cls_data = self.results["word_classification"]
        total_cls = cls_data.get("total", 0)
        accuracy_cls = cls_data.get("accuracy", 0)
        lines.append(
            f"تصنيف الكلمات,{total_cls},{cls_data.get('correct', 0)},{total_cls - cls_data.get('correct', 0)},{accuracy_cls:.2f}%"
        )

        # إضافة نتائج استخراج الأوزان
        pattern_data = self.results["pattern_recognition"]
        total_pattern = pattern_data["correct"] + pattern_data["incorrect"]
        accuracy_pattern = (
            (pattern_data["correct"] / total_pattern * 100) if total_pattern > 0 else 0
        )
        lines.append(
            f"استخراج الأوزان,{total_pattern},{pattern_data['correct']},{pattern_data['incorrect']},{accuracy_pattern:.2f}%"
        )

        return "\n".join(lines)

    def _generate_html_report(self) -> str:
        """توليد تقرير بتنسيق HTML من نتائج التقييم"""
        # ملخص نتائج التقييم
        summary = self._generate_summary()

        # قالب HTML البسيط
        html = f"""
        <!DOCTYPE html>
        <html dir="rtl">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>تقرير تقييم مكتبة معالجة اللغة العربية</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; }}
                h1, h2, h3 {{ color: #2c3e50; }}
                table {{ border-collapse: collapse; width: 100%; margin-bottom: 20px; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: center; }}
                th {{ background-color: #f2f2f2; }}
                .success {{ color: green; }}
                .error {{ color: red; }}
                .summary {{ background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin-bottom: 20px; }}
                .chart {{ height: 20px; background-color: #e0e0e0; margin-top: 5px; }}
                .chart-fill {{ height: 100%; background-color: #4CAF50; }}
            </style>
        </head>
        <body>
            <h1>تقرير تقييم مكتبة معالجة اللغة العربية الطبيعية</h1>
            <p>تاريخ التقييم: {self.evaluation_date}</p>
            
            <div class="summary">
                <h2>ملخص نتائج التقييم</h2>
                <p>عدد الكلمات في مجموعة البيانات: {self.results["dataset_info"]["total_words"]}</p>
                <p>دقة استخراج الجذور: {summary["root_extraction_accuracy"]:.2f}%</p>
                <p>دقة تصنيف الكلمات: {summary["word_classification_accuracy"]:.2f}%</p>
                <p>دقة استخراج الأوزان: {summary["pattern_recognition_accuracy"]:.2f}%</p>
            </div>
            
            <h2>تفاصيل نتائج استخراج الجذور</h2>
            <table>
                <tr>
                    <th>الخوارزمية</th>
                    <th>عدد الحالات</th>
                    <th>عدد النجاح</th>
                    <th>عدد الفشل</th>
                    <th>الدقة</th>
                    <th>رسم بياني</th>
                </tr>
        """

        # إضافة نتائج استخراج الجذور لكل خوارزمية
        for alg, data in self.results["root_extraction"].get("algorithms", {}).items():
            total = data.get("correct", 0) + data.get("incorrect", 0)
            accuracy = (data.get("correct", 0) / total * 100) if total > 0 else 0
            html += f"""
                <tr>
                    <td>{alg}</td>
                    <td>{total}</td>
                    <td class="success">{data.get("correct", 0)}</td>
                    <td class="error">{data.get("incorrect", 0)}</td>
                    <td>{accuracy:.2f}%</td>
                    <td>
                        <div class="chart">
                            <div class="chart-fill" style="width: {accuracy}%;"></div>
                        </div>
                    </td>
                </tr>
            """

        # إضافة نتائج تصنيف الكلمات واستخراج الأوزان
        html += f"""
            </table>
            
            <h2>تفاصيل نتائج تصنيف الكلمات</h2>
            <table>
                <tr>
                    <th>عدد الحالات</th>
                    <th>عدد النجاح</th>
                    <th>عدد الفشل</th>
                    <th>الدقة</th>
                    <th>رسم بياني</th>
                </tr>
                <tr>
                    <td>{self.results["word_classification"].get("total", 0)}</td>
                    <td class="success">{self.results["word_classification"].get("correct", 0)}</td>
                    <td class="error">{self.results["word_classification"].get("total", 0) - self.results["word_classification"].get("correct", 0)}</td>
                    <td>{self.results["word_classification"].get("accuracy", 0):.2f}%</td>
                    <td>
                        <div class="chart">
                            <div class="chart-fill" style="width: {self.results["word_classification"].get("accuracy", 0)}%;"></div>
                        </div>
                    </td>
                </tr>
            </table>
            
            <h2>تفاصيل نتائج استخراج الأوزان</h2>
            <table>
                <tr>
                    <th>عدد الحالات</th>
                    <th>عدد النجاح</th>
                    <th>عدد الفشل</th>
                    <th>الدقة</th>
                    <th>رسم بياني</th>
                </tr>
        """

        pattern_data = self.results["pattern_recognition"]
        total_pattern = pattern_data["correct"] + pattern_data["incorrect"]
        accuracy_pattern = (
            (pattern_data["correct"] / total_pattern * 100) if total_pattern > 0 else 0
        )

        html += f"""
                <tr>
                    <td>{total_pattern}</td>
                    <td class="success">{pattern_data["correct"]}</td>
                    <td class="error">{pattern_data["incorrect"]}</td>
                    <td>{accuracy_pattern:.2f}%</td>
                    <td>
                        <div class="chart">
                            <div class="chart-fill" style="width: {accuracy_pattern}%;"></div>
                        </div>
                    </td>
                </tr>
            </table>
        """

        # إضافة تحليل الأخطاء إذا تم طلب ذلك
        if self.settings.get("error_analysis", True):
            error_analysis = self.analyze_errors()
            html += """
            <h2>تحليل أنماط الأخطاء</h2>
            <h3>أنماط أخطاء استخراج الجذور</h3>
            <table>
                <tr>
                    <th>نوع الخطأ</th>
                    <th>عدد الحالات</th>
                    <th>النسبة المئوية</th>
                </tr>
            """

            for pattern, count in error_analysis["root_error_patterns"].items():
                percent = error_analysis["classification_error_patterns"].get("percent", 0)
                html += f"""
                <tr>
                    <td>{pattern}</td>
                    <td>{count}</td>
                    <td>{percent:.2f}%</td>
                </tr>
                """

            html += """
            </table>
            
            <h3>أنماط أخطاء تصنيف الكلمات</h3>
            <table>
                <tr>
                    <th>نوع الخطأ</th>
                    <th>عدد الحالات</th>
                    <th>النسبة المئوية</th>
                </tr>
            """

            for pattern, count in error_analysis["classification_error_patterns"].items():
                percent = 0  # حساب النسبة المئوية
                html += f"""
                <tr>
                    <td>{pattern}</td>
                    <td>{count}</td>
                    <td>{percent:.2f}%</td>
                </tr>
                """

        html += """
            </table>
        </body>
        </html>
        """

        return html

    def _generate_summary(self) -> Dict[str, float]:
        """توليد ملخص لنتائج التقييم"""
        # استخراج الجذور
        root_data = self.results["root_extraction"]
        total_root = root_data["correct"] + root_data["incorrect"]
        root_accuracy = (root_data["correct"] / total_root * 100) if total_root > 0 else 0

        # تصنيف الكلمات
        cls_data = self.results["word_classification"]
        cls_accuracy = cls_data.get("accuracy", 0)

        # استخراج الأوزان
        pattern_data = self.results["pattern_recognition"]
        total_pattern = pattern_data["correct"] + pattern_data["incorrect"]
        pattern_accuracy = (
            (pattern_data["correct"] / total_pattern * 100) if total_pattern > 0 else 0
        )

        return {
            "root_extraction_accuracy": root_accuracy,
            "word_classification_accuracy": cls_accuracy,
            "pattern_recognition_accuracy": pattern_accuracy,
            "evaluation_date": self.evaluation_date,
            "dataset_size": self.results["dataset_info"]["total_words"],
        }


def main():
    """تشغيل التقييم الشامل للمكتبة"""
    # إعداد محلل وسائط سطر الأوامر
    parser = argparse.ArgumentParser(description="تقييم أداء مكتبة معالجة اللغة العربية الطبيعية")
    parser.add_argument("--custom-dataset", help="مسار ملف مجموعة البيانات المخصصة (CSV أو JSON)")
    parser.add_argument(
        "--format", choices=["json", "csv", "html"], default="json", help="تنسيق التقرير الناتج"
    )
    parser.add_argument("--output", help="مسار ملف الخرج لحفظ التقرير")
    parser.add_argument(
        "--algorithms",
        nargs="+",
        default=["light", "stem", "pattern", "hybrid"],
        help="خوارزميات استخراج الجذور للتقييم",
    )
    parser.add_argument("--no-error-analysis", action="store_true", help="تعطيل تحليل الأخطاء")
    parser.add_argument(
        "--no-problem-cases", action="store_true", help="تعطيل تقييم الحالات الإشكالية"
    )

    args = parser.parse_args()

    print("=== بدء تقييم مكتبة معالجة اللغة العربية الطبيعية ===\n")

    # تحميل مجموعة البيانات المخصصة إذا تم تحديدها
    custom_dataset = None
    if args.custom_dataset:
        if args.custom_dataset.endswith(".csv"):
            print(f"تحميل مجموعة البيانات المخصصة من ملف CSV: {args.custom_dataset}")
            custom_dataset = load_custom_dataset_from_csv(args.custom_dataset)
        elif args.custom_dataset.endswith(".json"):
            print(f"تحميل مجموعة البيانات المخصصة من ملف JSON: {args.custom_dataset}")
            custom_dataset = load_custom_dataset_from_json(args.custom_dataset)
        else:
            print(f"تنسيق ملف البيانات غير مدعوم: {args.custom_dataset}")
            return

    # إعداد الإعدادات
    settings = {
        "report_format": args.format,
        "algorithms_to_evaluate": args.algorithms,
        "error_analysis": not args.no_error_analysis,
        "evaluate_problem_cases": not args.no_problem_cases,
    }

    # إنشاء المقيّم وتشغيل التقييم
    evaluator = NLPEvaluator(custom_dataset=custom_dataset, settings=settings)
    evaluator.run_complete_evaluation()

    # إنشاء وحفظ التقرير
    output_file = args.output if args.output else f"nlp_evaluation_results.{args.format}"
    evaluator.generate_report(format_type=args.format, output_file=output_file)

    print("\n=== انتهى التقييم الشامل للمكتبة ===")


if __name__ == "__main__":
    main()
