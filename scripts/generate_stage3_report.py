#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
مولد تقرير المرحلة الثالثة
=====================

أداة لتوليد التقرير النهائي للمرحلة الثالثة من مشروع توسيع المعجم القرآني.
يجمع التقرير نتائج جميع الأدوات والتحليلات ويضع ملخصاً شاملاً عن المرحلة
مع الدروس المستفادة والخطوات المستقبلية.
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
import matplotlib.pyplot as plt
import matplotlib

matplotlib.use("Agg")  # Backend for non-interactive plots

# إضافة المسار إلى PYTHONPATH للوصول إلى الوحدات
current_path = Path(os.path.dirname(os.path.abspath(__file__)))
root_path = current_path.parent
sys.path.append(str(root_path))

from core.lexicon.quranic_lexicon import QuranicLexicon

# إعداد التسجيل
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(os.path.join(root_path, "logs", "stage3_report.log")),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger("stage3_report")


class Stage3ReportGenerator:
    """فئة توليد التقرير النهائي للمرحلة الثالثة من مشروع توسيع المعجم القرآني."""

    def __init__(
        self,
        lexicon_path: str,
        original_lexicon_path: str,
        evaluation_results_path: Optional[str] = None,
        algorithm_results_path: Optional[str] = None,
        audit_report_path: Optional[str] = None,
        output_path: str = "reports/stage3_final_report.md",
    ):
        """
        تهيئة مولد التقرير.

        المعلمات:
            lexicon_path: مسار ملف المعجم الموسع
            original_lexicon_path: مسار ملف المعجم الأصلي
            evaluation_results_path: مسار نتائج التقييم (اختياري)
            algorithm_results_path: مسار نتائج تحسين الخوارزميات (اختياري)
            audit_report_path: مسار تقرير تدقيق المعجم (اختياري)
            output_path: مسار ملف التقرير النهائي
        """
        self.lexicon_path = lexicon_path
        self.original_lexicon_path = original_lexicon_path
        self.evaluation_results_path = evaluation_results_path
        self.algorithm_results_path = algorithm_results_path
        self.audit_report_path = audit_report_path
        self.output_path = output_path

        # تحميل المعجم
        self.lexicon = QuranicLexicon(lexicon_path)
        logger.info(f"تم تحميل المعجم الموسع: {lexicon_path} ({len(self.lexicon.words)} كلمة)")

        # تحميل المعجم الأصلي
        self.original_lexicon = QuranicLexicon(original_lexicon_path)
        logger.info(
            f"تم تحميل المعجم الأصلي: {original_lexicon_path} ({len(self.original_lexicon.words)} كلمة)"
        )

        # تحميل نتائج التقييم إذا كانت متوفرة
        self.evaluation_results = None
        if evaluation_results_path and os.path.exists(evaluation_results_path):
            try:
                with open(evaluation_results_path, "r", encoding="utf-8") as f:
                    self.evaluation_results = json.load(f)
                logger.info(f"تم تحميل نتائج التقييم: {evaluation_results_path}")
            except Exception as e:
                logger.warning(f"فشل تحميل نتائج التقييم: {str(e)}")

        # تحميل نتائج تحسين الخوارزميات إذا كانت متوفرة
        self.algorithm_results = None
        if algorithm_results_path and os.path.exists(algorithm_results_path):
            try:
                with open(algorithm_results_path, "r", encoding="utf-8") as f:
                    self.algorithm_results = json.load(f)
                logger.info(f"تم تحميل نتائج تحسين الخوارزميات: {algorithm_results_path}")
            except Exception as e:
                logger.warning(f"فشل تحميل نتائج تحسين الخوارزميات: {str(e)}")

        # تحميل تقرير التدقيق إذا كان متوفراً
        self.audit_report = None
        if audit_report_path and os.path.exists(audit_report_path):
            try:
                with open(audit_report_path, "r", encoding="utf-8") as f:
                    self.audit_report = f.read()
                logger.info(f"تم تحميل تقرير التدقيق: {audit_report_path}")
            except Exception as e:
                logger.warning(f"فشل تحميل تقرير التدقيق: {str(e)}")

        # إعداد بيانات التقرير
        self.report_data = {
            "lexicon_growth": self._calculate_lexicon_growth(),
            "date": datetime.now().strftime("%Y-%m-%d"),
            "stage": "المرحلة الثالثة: توسيع المعجم وتحسين الخوارزميات",
        }

    def _calculate_lexicon_growth(self) -> Dict[str, Any]:
        """
        حساب نمو المعجم والإحصائيات الأساسية.

        العوائد:
            قاموس يحتوي على إحصائيات نمو المعجم
        """
        growth = {
            "original_count": len(self.original_lexicon.words),
            "current_count": len(self.lexicon.words),
            "new_words_count": 0,
            "new_words_percentage": 0,
            "with_root_percentage": 0,
            "with_type_percentage": 0,
            "with_pattern_percentage": 0,
            "with_meaning_percentage": 0,
        }

        # حساب الكلمات الجديدة
        new_words = set(self.lexicon.words.keys()) - set(self.original_lexicon.words.keys())
        growth["new_words_count"] = len(new_words)
        growth["new_words_percentage"] = (
            growth["new_words_count"] / growth["original_count"] * 100
            if growth["original_count"] > 0
            else 0
        )

        # حساب نسب الاكتمال
        growth["with_root_percentage"] = (
            sum(1 for word in self.lexicon.words.values() if "root" in word)
            / growth["current_count"]
            * 100
            if growth["current_count"] > 0
            else 0
        )
        growth["with_type_percentage"] = (
            sum(1 for word in self.lexicon.words.values() if "type" in word)
            / growth["current_count"]
            * 100
            if growth["current_count"] > 0
            else 0
        )
        growth["with_pattern_percentage"] = (
            sum(1 for word in self.lexicon.words.values() if "pattern" in word)
            / growth["current_count"]
            * 100
            if growth["current_count"] > 0
            else 0
        )
        growth["with_meaning_percentage"] = (
            sum(1 for word in self.lexicon.words.values() if "meaning" in word)
            / growth["current_count"]
            * 100
            if growth["current_count"] > 0
            else 0
        )

        return growth

    def generate_visualizations(self, output_dir: str = "reports/images") -> Dict[str, str]:
        """
        توليد الرسوم التوضيحية للتقرير.

        المعلمات:
            output_dir: دليل حفظ الرسوم التوضيحية

        العوائد:
            قاموس يحتوي على مسارات الرسوم التوضيحية
        """
        logger.info("توليد الرسوم التوضيحية للتقرير")

        # إنشاء دليل الرسوم التوضيحية إذا لم يكن موجوداً
        os.makedirs(output_dir, exist_ok=True)

        # قاموس لتخزين مسارات الرسوم التوضيحية
        visualization_paths = {}

        # رسم نمو المعجم
        fig, ax = plt.subplots(figsize=(10, 6))
        stages = ["المعجم الأصلي", "المعجم الموسع"]
        counts = [
            self.report_data["lexicon_growth"]["original_count"],
            self.report_data["lexicon_growth"]["current_count"],
        ]

        ax.bar(stages, counts, color=["#3498db", "#2ecc71"])
        ax.set_title("نمو المعجم", fontsize=16, fontweight="bold")
        ax.set_ylabel("عدد الكلمات", fontsize=12)

        # إضافة الأرقام فوق الأعمدة
        for i, count in enumerate(counts):
            ax.text(i, count + 5, str(count), ha="center", fontsize=12, fontweight="bold")

        plt.tight_layout()
        lexicon_growth_path = os.path.join(output_dir, "lexicon_growth.png")
        plt.savefig(lexicon_growth_path)
        plt.close()

        visualization_paths["lexicon_growth"] = lexicon_growth_path

        # رسم نسب اكتمال خصائص الكلمات
        if self.evaluation_results and "lexicon_stats" in self.evaluation_results:
            fig, ax = plt.subplots(figsize=(10, 6))
            properties = ["الجذر", "النوع", "الوزن", "المعنى"]
            percentages = [
                self.report_data["lexicon_growth"]["with_root_percentage"],
                self.report_data["lexicon_growth"]["with_type_percentage"],
                self.report_data["lexicon_growth"]["with_pattern_percentage"],
                self.report_data["lexicon_growth"]["with_meaning_percentage"],
            ]

            ax.bar(properties, percentages, color=["#e74c3c", "#f39c12", "#9b59b6", "#1abc9c"])
            ax.set_title("نسب اكتمال خصائص الكلمات", fontsize=16, fontweight="bold")
            ax.set_ylabel("النسبة المئوية", fontsize=12)
            ax.set_ylim(0, 100)

            # إضافة النسب فوق الأعمدة
            for i, percentage in enumerate(percentages):
                ax.text(
                    i,
                    percentage + 2,
                    f"{percentage:.1f}%",
                    ha="center",
                    fontsize=12,
                    fontweight="bold",
                )

            plt.tight_layout()
            properties_completion_path = os.path.join(output_dir, "properties_completion.png")
            plt.savefig(properties_completion_path)
            plt.close()

            visualization_paths["properties_completion"] = properties_completion_path

        # رسم دقة الخوارزميات
        if self.evaluation_results and "algorithm_performance" in self.evaluation_results:
            performance = self.evaluation_results["algorithm_performance"]

            if "root_extraction" in performance and "morphology_analysis" in performance:
                fig, ax = plt.subplots(figsize=(10, 6))
                algorithms = ["استخراج الجذور", "تحليل الصرف"]
                accuracies = [
                    performance["root_extraction"]["accuracy"] * 100,
                    performance["morphology_analysis"]["accuracy"] * 100,
                ]

                ax.bar(algorithms, accuracies, color=["#3498db", "#f1c40f"])
                ax.set_title("دقة الخوارزميات", fontsize=16, fontweight="bold")
                ax.set_ylabel("الدقة (%)", fontsize=12)
                ax.set_ylim(0, 100)

                # إضافة النسب فوق الأعمدة
                for i, accuracy in enumerate(accuracies):
                    ax.text(
                        i,
                        accuracy + 2,
                        f"{accuracy:.1f}%",
                        ha="center",
                        fontsize=12,
                        fontweight="bold",
                    )

                plt.tight_layout()
                algorithm_accuracy_path = os.path.join(output_dir, "algorithm_accuracy.png")
                plt.savefig(algorithm_accuracy_path)
                plt.close()

                visualization_paths["algorithm_accuracy"] = algorithm_accuracy_path

        # رسم مقارنة التحسينات في الخوارزميات إذا كانت متوفرة
        if (
            self.algorithm_results
            and "root_extraction_before" in self.algorithm_results
            and "root_extraction_after" in self.algorithm_results
        ):
            fig, ax = plt.subplots(figsize=(10, 6))

            before_after = ["قبل التحسين", "بعد التحسين"]
            root_accuracies = [
                self.algorithm_results["root_extraction_before"].get("accuracy", 0) * 100,
                self.algorithm_results["root_extraction_after"].get("accuracy", 0) * 100,
            ]
            morphology_accuracies = [
                self.algorithm_results["morphology_analysis_before"].get("accuracy", 0) * 100,
                self.algorithm_results["morphology_analysis_after"].get("accuracy", 0) * 100,
            ]

            x = range(len(before_after))
            width = 0.35

            ax.bar(
                [i - width / 2 for i in x],
                root_accuracies,
                width,
                label="استخراج الجذور",
                color="#3498db",
            )
            ax.bar(
                [i + width / 2 for i in x],
                morphology_accuracies,
                width,
                label="تحليل الصرف",
                color="#f1c40f",
            )

            ax.set_title("تحسين أداء الخوارزميات", fontsize=16, fontweight="bold")
            ax.set_xticks(x)
            ax.set_xticklabels(before_after)
            ax.set_ylabel("الدقة (%)", fontsize=12)
            ax.set_ylim(0, 100)
            ax.legend()

            # إضافة النسب فوق الأعمدة
            for i, accuracy in enumerate(root_accuracies):
                ax.text(i - width / 2, accuracy + 2, f"{accuracy:.1f}%", ha="center", fontsize=10)

            for i, accuracy in enumerate(morphology_accuracies):
                ax.text(i + width / 2, accuracy + 2, f"{accuracy:.1f}%", ha="center", fontsize=10)

            plt.tight_layout()
            algorithm_improvement_path = os.path.join(output_dir, "algorithm_improvement.png")
            plt.savefig(algorithm_improvement_path)
            plt.close()

            visualization_paths["algorithm_improvement"] = algorithm_improvement_path

        return visualization_paths

    def generate_report(self, visualizations: Optional[Dict[str, str]] = None) -> None:
        """
        توليد التقرير النهائي للمرحلة الثالثة.

        المعلمات:
            visualizations: قاموس يحتوي على مسارات الرسوم التوضيحية (اختياري)
        """
        logger.info(f"توليد التقرير النهائي للمرحلة الثالثة: {self.output_path}")

        # إنشاء دليل التقرير إذا لم يكن موجوداً
        os.makedirs(os.path.dirname(os.path.abspath(self.output_path)), exist_ok=True)

        # إعداد محتوى التقرير
        report_content = f"""# تقرير المرحلة الثالثة: توسيع المعجم وتحسين الخوارزميات

**تاريخ التقرير:** {datetime.now().strftime("%Y-%m-%d")}

## 1. ملخص تنفيذي

استكملت المرحلة الثالثة من مشروع توسيع المعجم القرآني والتي ركزت على:

1. **توسيع قاعدة بيانات المعجم** من {self.report_data["lexicon_growth"]["original_count"]} كلمة إلى {self.report_data["lexicon_growth"]["current_count"]} كلمة، بزيادة قدرها {self.report_data["lexicon_growth"]["new_words_count"]} كلمة ({self.report_data["lexicon_growth"]["new_words_percentage"]:.2f}%).
2. **تحسين خوارزميات معالجة اللغة العربية** لزيادة دقة استخراج الجذور وتحليل الصرف.
3. **تطوير نظام تقييم وتحقق** متطور لضمان جودة المعجم والتأكد من صحة البيانات.
4. **توثيق الدروس المستفادة والخطوات المستقبلية** لضمان استمرارية المشروع وتحسينه.

## 2. توسيع المعجم

### 2.1 إحصائيات النمو
"""

        # إضافة رسم نمو المعجم إذا كان متوفراً
        if visualizations and "lexicon_growth" in visualizations:
            rel_path = os.path.relpath(
                visualizations["lexicon_growth"], os.path.dirname(self.output_path)
            )
            report_content += f"\n![نمو المعجم]({rel_path})\n\n"

        report_content += f"""
- **المعجم الأصلي:** {self.report_data["lexicon_growth"]["original_count"]} كلمة
- **المعجم الموسع:** {self.report_data["lexicon_growth"]["current_count"]} كلمة
- **الكلمات الجديدة المضافة:** {self.report_data["lexicon_growth"]["new_words_count"]} كلمة
- **نسبة النمو:** {self.report_data["lexicon_growth"]["new_words_percentage"]:.2f}%

### 2.2 اكتمال خصائص الكلمات
"""

        # إضافة رسم نسب اكتمال خصائص الكلمات إذا كان متوفراً
        if visualizations and "properties_completion" in visualizations:
            rel_path = os.path.relpath(
                visualizations["properties_completion"], os.path.dirname(self.output_path)
            )
            report_content += f"\n![نسب اكتمال خصائص الكلمات]({rel_path})\n\n"

        report_content += f"""
- **الكلمات بجذور:** {self.report_data["lexicon_growth"]["with_root_percentage"]:.2f}%
- **الكلمات بأنواع:** {self.report_data["lexicon_growth"]["with_type_percentage"]:.2f}%
- **الكلمات بأوزان:** {self.report_data["lexicon_growth"]["with_pattern_percentage"]:.2f}%
- **الكلمات بمعاني:** {self.report_data["lexicon_growth"]["with_meaning_percentage"]:.2f}%

### 2.3 مصادر الكلمات الجديدة

تم جمع الكلمات الجديدة من المصادر التالية:

1. **النص القرآني:** استخراج كلمات جديدة لم تكن موجودة في المعجم الأصلي.
2. **المعاجم العربية:** استخراج كلمات من معاجم عربية مختلفة مثل لسان العرب والصحاح.
3. **مواقع إلكترونية:** جمع كلمات من مواقع متخصصة في اللغة العربية والقرآن الكريم.
4. **كتب التفسير:** استخراج كلمات من كتب تفسير القرآن الكريم.

### 2.4 تقييم جودة الكلمات المضافة

تم تطوير أداة تدقيق المعجم للتأكد من جودة الكلمات المضافة، وتشمل التدقيق:

- التحقق من صحة الجذور المستخرجة.
- التأكد من دقة تصنيف نوع الكلمة.
- مراجعة أوزان الكلمات.
- التحقق من اكتمال معاني الكلمات.

## 3. تحسين الخوارزميات

### 3.1 خوارزمية استخراج الجذور
"""

        # إضافة معلومات من نتائج تحسين الخوارزميات إذا كانت متوفرة
        if self.algorithm_results:
            # إضافة رسم تحسين أداء الخوارزميات إذا كان متوفراً
            if visualizations and "algorithm_improvement" in visualizations:
                rel_path = os.path.relpath(
                    visualizations["algorithm_improvement"], os.path.dirname(self.output_path)
                )
                report_content += f"\n![تحسين أداء الخوارزميات]({rel_path})\n\n"

            before_acc = (
                self.algorithm_results.get("root_extraction_before", {}).get("accuracy", 0) * 100
            )
            after_acc = (
                self.algorithm_results.get("root_extraction_after", {}).get("accuracy", 0) * 100
            )
            improvement = after_acc - before_acc

            report_content += f"""
#### التحسينات الرئيسية:

- **الدقة قبل التحسين:** {before_acc:.2f}%
- **الدقة بعد التحسين:** {after_acc:.2f}%
- **نسبة التحسن:** {improvement:.2f}%

#### الأساليب المستخدمة في التحسين:

1. **تحديد الأنماط الصعبة** التي تسبب مشاكل في استخراج الجذور.
2. **إضافة قواعد خاصة** للتعامل مع الحالات الاستثنائية.
3. **تحسين التعامل مع الإعلال والإبدال** في الكلمات العربية.
4. **تطوير قاعدة بيانات للأنماط الخاصة** للكلمات غير القياسية.
"""

        report_content += """
### 3.2 خوارزمية تحليل الصرف
"""

        # إضافة معلومات من نتائج تحسين الخوارزميات إذا كانت متوفرة
        if self.algorithm_results:
            before_acc = (
                self.algorithm_results.get("morphology_analysis_before", {}).get("accuracy", 0)
                * 100
            )
            after_acc = (
                self.algorithm_results.get("morphology_analysis_after", {}).get("accuracy", 0) * 100
            )
            improvement = after_acc - before_acc

            report_content += f"""
#### التحسينات الرئيسية:

- **الدقة قبل التحسين:** {before_acc:.2f}%
- **الدقة بعد التحسين:** {after_acc:.2f}%
- **نسبة التحسن:** {improvement:.2f}%

#### الأساليب المستخدمة في التحسين:

1. **تحسين التعرف على الأوزان الصرفية** للكلمات العربية.
2. **تطوير قواعد للتعامل مع صيغ المبالغة** وأسماء الفاعل والمفعول.
3. **تحسين التعرف على المشتقات** من الجذور.
4. **معالجة الكلمات غير القياسية** بشكل خاص.
"""

        report_content += """
## 4. نظام التقييم والتحقق

### 4.1 مكونات النظام

تم تطوير نظام متكامل للتقييم والتحقق يشمل:

1. **أداة تدقيق المعجم:** للتحقق من صحة وجودة الكلمات المضافة.
2. **نظام تقييم الخوارزميات:** لقياس دقة خوارزميات استخراج الجذور وتحليل الصرف.
3. **أداة مقارنة الأداء:** لمقارنة أداء الخوارزميات قبل وبعد التحسين.
4. **نظام توليد التقارير:** لإنشاء تقارير تفصيلية عن نتائج التقييم.

### 4.2 نتائج التقييم
"""

        # إضافة رسم دقة الخوارزميات إذا كان متوفراً
        if visualizations and "algorithm_accuracy" in visualizations:
            rel_path = os.path.relpath(
                visualizations["algorithm_accuracy"], os.path.dirname(self.output_path)
            )
            report_content += f"\n![دقة الخوارزميات]({rel_path})\n\n"

        # إضافة معلومات من نتائج التقييم إذا كانت متوفرة
        if self.evaluation_results and "algorithm_performance" in self.evaluation_results:
            performance = self.evaluation_results["algorithm_performance"]

            root_accuracy = performance.get("root_extraction", {}).get("accuracy", 0) * 100
            morph_accuracy = performance.get("morphology_analysis", {}).get("accuracy", 0) * 100

            report_content += f"""
#### نتائج اختبارات الخوارزميات:

- **دقة خوارزمية استخراج الجذور:** {root_accuracy:.2f}%
- **دقة خوارزمية تحليل الصرف:** {morph_accuracy:.2f}%

#### توزيع الأخطاء:

"""

            # إضافة أمثلة على الأخطاء
            if "errors" in performance.get("root_extraction", {}):
                report_content += "##### أمثلة على أخطاء استخراج الجذور:\n\n"
                report_content += "| الكلمة | الجذر المتوقع | الجذر المستخرج |\n"
                report_content += "| ------ | ------------- | -------------- |\n"

                for error in performance["root_extraction"]["errors"][:5]:  # أخذ أول 5 أمثلة فقط
                    report_content += f"| {error.get('word', '')} | {error.get('expected', '')} | {error.get('extracted', '')} |\n"

                report_content += "\n"

        report_content += """
## 5. التحديات والدروس المستفادة

### 5.1 التحديات الرئيسية

1. **تعقيد اللغة العربية:** التعامل مع خصائص اللغة العربية المعقدة، مثل الإعلال والإبدال والتشكيل.
2. **تنوع الأوزان والصيغ:** صعوبة التعرف على جميع الأوزان والصيغ الصرفية.
3. **الكلمات غير القياسية:** تحديات في التعامل مع الكلمات ذات القواعد الخاصة.
4. **اكتمال البيانات:** ضمان اكتمال وصحة البيانات المدخلة للمعجم.
5. **أتمتة عملية التوسيع:** تطوير عمليات آلية لتوسيع المعجم مع الحفاظ على الجودة.

### 5.2 الدروس المستفادة

1. **أهمية التدقيق المستمر:** ضرورة التحقق المستمر من جودة البيانات المضافة.
2. **قيمة التحليل التفصيلي:** تحليل أنماط الأخطاء ساعد في تحديد مجالات التحسين.
3. **فعالية النهج الهجين:** الجمع بين الخوارزميات وقواعد البيانات الخاصة أثبت فعاليته.
4. **أهمية التوثيق:** توثيق القرارات والإجراءات ساعد في تتبع التقدم وتحسين العملية.
5. **قيمة الأدوات المساعدة:** تطوير أدوات مساعدة وفر الوقت وحسّن الجودة.

## 6. الخطوات المستقبلية

### 6.1 توصيات للمرحلة القادمة

1. **زيادة حجم المعجم:** استهداف الوصول إلى 5000 كلمة في المعجم.
2. **تحسين تغطية المعاني:** زيادة نسبة الكلمات ذات المعاني المكتملة.
3. **تطوير واجهة استخدام:** إنشاء واجهة سهلة الاستخدام للتفاعل مع المعجم.
4. **دمج تقنيات الذكاء الاصطناعي:** استخدام تقنيات التعلم الآلي لتحسين استخراج الجذور وتحليل الصرف.
5. **توسيع نطاق الاختبارات:** زيادة تغطية الاختبارات وتحسين دقة التقييم.

### 6.2 خطة التنفيذ المقترحة

1. **الربع الأول:** تحسين واجهة المستخدم وتطوير أدوات جديدة للتفاعل مع المعجم.
2. **الربع الثاني:** استكمال توسيع المعجم والتركيز على زيادة تغطية المعاني.
3. **الربع الثالث:** دمج تقنيات الذكاء الاصطناعي وتطوير نماذج تعلم آلي متخصصة.
4. **الربع الرابع:** تقييم شامل وإطلاق نسخة متكاملة من المعجم.

## 7. الخاتمة

حققت المرحلة الثالثة من المشروع أهدافها الرئيسية في توسيع المعجم وتحسين الخوارزميات، مع تطوير نظام متكامل للتقييم والتحقق. التحديات التي واجهتها فرق العمل أدت إلى دروس قيمة ستساهم في تحسين المراحل المستقبلية.

التركيز المستمر على جودة البيانات والتحسين المستمر للخوارزميات سيضمن نجاح المشروع وتحقيق هدفه النهائي في توفير معجم قرآني شامل ودقيق.

---

**إعداد فريق تطوير المعجم القرآني**  
**تاريخ الإصدار:** {datetime.now().strftime('%Y-%m-%d')}
"""

        # حفظ التقرير
        with open(self.output_path, "w", encoding="utf-8") as f:
            f.write(report_content)

        logger.info(f"تم توليد التقرير النهائي بنجاح: {self.output_path}")


def main():
    """النقطة الرئيسية لتنفيذ برنامج توليد تقرير المرحلة الثالثة"""
    parser = argparse.ArgumentParser(description="أداة توليد التقرير النهائي للمرحلة الثالثة")
    parser.add_argument("--lexicon", required=True, help="مسار ملف المعجم الموسع")
    parser.add_argument("--original", required=True, help="مسار ملف المعجم الأصلي")
    parser.add_argument("--evaluation", help="مسار نتائج التقييم (اختياري)")
    parser.add_argument("--algorithm", help="مسار نتائج تحسين الخوارزميات (اختياري)")
    parser.add_argument("--audit", help="مسار تقرير تدقيق المعجم (اختياري)")
    parser.add_argument(
        "--output", default="reports/stage3_final_report.md", help="مسار ملف التقرير النهائي"
    )
    parser.add_argument("--images", default="reports/images", help="دليل حفظ الرسوم التوضيحية")

    args = parser.parse_args()

    try:
        # إنشاء مولد التقرير
        report_generator = Stage3ReportGenerator(
            lexicon_path=args.lexicon,
            original_lexicon_path=args.original,
            evaluation_results_path=args.evaluation,
            algorithm_results_path=args.algorithm,
            audit_report_path=args.audit,
            output_path=args.output,
        )

        # توليد الرسوم التوضيحية
        visualizations = report_generator.generate_visualizations(args.images)

        # توليد التقرير
        report_generator.generate_report(visualizations)

        return 0

    except Exception as e:
        logger.error(f"خطأ أثناء توليد تقرير المرحلة الثالثة: {str(e)}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
