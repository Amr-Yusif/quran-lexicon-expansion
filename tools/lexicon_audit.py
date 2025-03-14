#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
أداة تدقيق المعجم
===============

أداة لتدقيق المعجم والتحقق من صحة الكلمات المضافة وجودتها.
تتيح الأداة مراجعة الكلمات المضافة وتصحيح أي أخطاء والتأكد من صحة
الجذور والأنواع والأوزان والمعاني.
"""

import os
import sys
import json
import csv
import time
import argparse
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Tuple, Set, Optional

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
        logging.FileHandler(os.path.join(root_path, "logs", "lexicon_audit.log")),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger("lexicon_audit")


class LexiconAuditor:
    """فئة تدقيق المعجم والتحقق من صحة الكلمات وجودتها."""

    def __init__(self, lexicon_path: str, original_lexicon_path: Optional[str] = None):
        """
        تهيئة مدقق المعجم.

        المعلمات:
            lexicon_path: مسار ملف المعجم الموسع
            original_lexicon_path: مسار ملف المعجم الأصلي (اختياري)
        """
        self.lexicon_path = lexicon_path
        self.original_lexicon_path = original_lexicon_path

        # تحميل المعجم
        self.lexicon = QuranicLexicon(lexicon_path)
        logger.info(f"تم تحميل المعجم الموسع: {lexicon_path} ({len(self.lexicon.words)} كلمة)")

        # تحميل المعجم الأصلي إذا تم توفيره
        self.original_lexicon = None
        if original_lexicon_path:
            self.original_lexicon = QuranicLexicon(original_lexicon_path)
            logger.info(
                f"تم تحميل المعجم الأصلي: {original_lexicon_path} ({len(self.original_lexicon.words)} كلمة)"
            )

        # تهيئة المعالجات
        self.root_extractor = ArabicRootExtractor()
        self.morphology_analyzer = ArabicMorphologyAnalyzer()
        self.diacritics_processor = DiacriticsProcessor()

        # إحصائيات التدقيق
        self.audit_stats = {
            "total_words": len(self.lexicon.words),
            "new_words": 0,
            "verified_words": 0,
            "corrected_words": 0,
            "removed_words": 0,
            "start_time": datetime.now().isoformat(),
        }

        # تحديد الكلمات الجديدة المضافة
        self.new_words = set()
        if self.original_lexicon:
            self.new_words = set(self.lexicon.words.keys()) - set(
                self.original_lexicon.words.keys()
            )
            self.audit_stats["new_words"] = len(self.new_words)
            logger.info(f"تم العثور على {len(self.new_words)} كلمة جديدة مضافة")

    def verify_word_properties(self, word: str) -> Dict[str, Any]:
        """
        التحقق من خصائص كلمة وإعطاء توصيات للتصحيح.

        المعلمات:
            word: الكلمة المراد تدقيقها

        العوائد:
            قاموس يحتوي على نتائج التدقيق والتوصيات
        """
        if word not in self.lexicon.words:
            return {"error": "الكلمة غير موجودة في المعجم"}

        word_properties = self.lexicon.words[word]

        # استخراج خصائص الكلمة من الخوارزميات مباشرة للمقارنة
        root_info = self.root_extractor.extract_root(word)
        morphology_info = self.morphology_analyzer.analyze_word(word)

        # نتائج التدقيق
        verification = {
            "word": word,
            "current": word_properties,
            "algorithm_suggestions": {
                "root": root_info.get("root", ""),
                "type": morphology_info.get("type", ""),
                "pattern": morphology_info.get("pattern", ""),
            },
            "issues": [],
            "needs_correction": False,
        }

        # التحقق من الجذر
        if "root" in word_properties:
            if (
                word_properties["root"] != root_info.get("root", "")
                and root_info.get("confidence", 0) > 0.8
            ):
                verification["issues"].append(
                    {
                        "type": "root",
                        "message": f"الجذر قد يكون غير صحيح. جذر المعجم: {word_properties['root']} - جذر الخوارزمية: {root_info.get('root', '')}",
                        "severity": "متوسط",
                    }
                )
                verification["needs_correction"] = True
        else:
            verification["issues"].append(
                {"type": "root", "message": "الكلمة تفتقر إلى الجذر", "severity": "عالي"}
            )
            verification["needs_correction"] = True

        # التحقق من نوع الكلمة
        if "type" in word_properties:
            if (
                word_properties["type"] != morphology_info.get("type", "")
                and morphology_info.get("type", "") != "غير معروف"
            ):
                verification["issues"].append(
                    {
                        "type": "type",
                        "message": f"نوع الكلمة قد يكون غير صحيح. نوع المعجم: {word_properties['type']} - نوع الخوارزمية: {morphology_info.get('type', '')}",
                        "severity": "منخفض",
                    }
                )
        else:
            verification["issues"].append(
                {"type": "type", "message": "الكلمة تفتقر إلى النوع", "severity": "متوسط"}
            )
            verification["needs_correction"] = True

        # التحقق من وزن الكلمة
        if "pattern" in word_properties:
            if (
                word_properties["pattern"] != morphology_info.get("pattern", "")
                and morphology_info.get("pattern", "") != "غير معروف"
            ):
                verification["issues"].append(
                    {
                        "type": "pattern",
                        "message": f"وزن الكلمة قد يكون غير صحيح. وزن المعجم: {word_properties['pattern']} - وزن الخوارزمية: {morphology_info.get('pattern', '')}",
                        "severity": "منخفض",
                    }
                )
        else:
            verification["issues"].append(
                {"type": "pattern", "message": "الكلمة تفتقر إلى الوزن", "severity": "منخفض"}
            )

        # التحقق من المعنى
        if "meaning" not in word_properties or not word_properties["meaning"]:
            verification["issues"].append(
                {"type": "meaning", "message": "الكلمة تفتقر إلى المعنى", "severity": "متوسط"}
            )

        return verification

    def audit_new_words(self) -> List[Dict[str, Any]]:
        """
        تدقيق جميع الكلمات الجديدة المضافة.

        العوائد:
            قائمة بنتائج التدقيق لكل كلمة
        """
        if not self.new_words:
            logger.warning("لا توجد كلمات جديدة للتدقيق")
            return []

        logger.info(f"بدء تدقيق {len(self.new_words)} كلمة جديدة")
        audit_results = []

        for word in self.new_words:
            verification = self.verify_word_properties(word)
            audit_results.append(verification)

        # تصنيف النتائج
        issues_count = sum(1 for result in audit_results if result.get("needs_correction", False))
        self.audit_stats["words_with_issues"] = issues_count

        logger.info(
            f"اكتمل تدقيق الكلمات الجديدة. تم العثور على {issues_count} كلمة تحتاج إلى تصحيح"
        )
        return audit_results

    def interactive_audit(self) -> Dict[str, Any]:
        """
        تدقيق المعجم بشكل تفاعلي. يعرض التوصيات ويسمح للمستخدم بتصحيح الكلمات.

        العوائد:
            إحصائيات عملية التدقيق
        """
        logger.info("بدء التدقيق التفاعلي للمعجم")

        # الحصول على نتائج التدقيق
        audit_results = self.audit_new_words()

        if not audit_results:
            print("لا توجد كلمات للتدقيق")
            return self.audit_stats

        print(f"\n=== تدقيق المعجم - {len(audit_results)} كلمة ===\n")

        corrections_made = 0
        words_verified = 0
        words_removed = 0

        # فرز النتائج حسب الحاجة للتصحيح
        needs_correction = [r for r in audit_results if r.get("needs_correction", False)]
        no_issues = [r for r in audit_results if not r.get("needs_correction", False)]

        print(f"كلمات تحتاج إلى تصحيح: {len(needs_correction)}")
        print(f"كلمات بدون مشاكل: {len(no_issues)}")

        # معالجة الكلمات التي تحتاج إلى تصحيح أولاً
        for result in needs_correction:
            word = result["word"]
            current = result["current"]
            suggestions = result["algorithm_suggestions"]
            issues = result["issues"]

            print("\n" + "=" * 40)
            print(f"الكلمة: {word}")
            print("الخصائص الحالية:")
            for key, value in current.items():
                print(f"  - {key}: {value}")

            print("\nالمشاكل المكتشفة:")
            for issue in issues:
                print(f"  - {issue['message']} (خطورة: {issue['severity']})")

            print("\nاقتراحات الخوارزمية:")
            for key, value in suggestions.items():
                if value:
                    print(f"  - {key}: {value}")

            # خيارات المستخدم
            print("\nالخيارات:")
            print("1. تصحيح الكلمة")
            print("2. تأكيد الكلمة كما هي")
            print("3. حذف الكلمة من المعجم")
            print("4. تخطي")

            choice = input("\nاختر إجراءً (1-4): ").strip()

            if choice == "1":
                # تصحيح الكلمة
                print("\nتصحيح الكلمة. اترك الحقل فارغًا للإبقاء على القيمة الحالية.")

                root = input(
                    f"الجذر ({current.get('root', suggestions.get('root', ''))}): "
                ).strip()
                if root:
                    current["root"] = root
                elif "root" not in current and suggestions.get("root"):
                    current["root"] = suggestions.get("root")

                word_type = input(
                    f"النوع ({current.get('type', suggestions.get('type', ''))}): "
                ).strip()
                if word_type:
                    current["type"] = word_type
                elif "type" not in current and suggestions.get("type"):
                    current["type"] = suggestions.get("type")

                pattern = input(
                    f"الوزن ({current.get('pattern', suggestions.get('pattern', ''))}): "
                ).strip()
                if pattern:
                    current["pattern"] = pattern
                elif "pattern" not in current and suggestions.get("pattern"):
                    current["pattern"] = suggestions.get("pattern")

                meaning = input(f"المعنى ({current.get('meaning', '')}): ").strip()
                if meaning:
                    current["meaning"] = meaning

                # تحديث الكلمة في المعجم
                self.lexicon.words[word] = current
                corrections_made += 1
                print("تم تصحيح الكلمة.")

            elif choice == "2":
                # تأكيد الكلمة كما هي
                words_verified += 1
                print("تم تأكيد الكلمة.")

            elif choice == "3":
                # حذف الكلمة من المعجم
                if word in self.lexicon.words:
                    del self.lexicon.words[word]
                    words_removed += 1
                    print("تم حذف الكلمة من المعجم.")

            elif choice == "4":
                print("تم تخطي الكلمة.")

            else:
                print("خيار غير صالح. تم تخطي الكلمة.")

        # تحديث المعجم بعد التغييرات
        if corrections_made > 0 or words_removed > 0:
            self.lexicon.save_to_file(self.lexicon_path)
            print(f"\nتم حفظ التغييرات إلى: {self.lexicon_path}")

        # تحديث الإحصائيات
        self.audit_stats.update(
            {
                "verified_words": words_verified,
                "corrected_words": corrections_made,
                "removed_words": words_removed,
                "end_time": datetime.now().isoformat(),
            }
        )

        # عرض ملخص
        print("\n=== ملخص عملية التدقيق ===")
        print(f"إجمالي الكلمات المدققة: {len(audit_results)}")
        print(f"الكلمات المصححة: {corrections_made}")
        print(f"الكلمات المؤكدة: {words_verified}")
        print(f"الكلمات المحذوفة: {words_removed}")

        return self.audit_stats

    def export_audit_report(self, output_path: str) -> None:
        """
        تصدير تقرير التدقيق إلى ملف.

        المعلمات:
            output_path: مسار ملف التقرير
        """
        logger.info(f"تصدير تقرير التدقيق إلى: {output_path}")

        # تدقيق الكلمات الجديدة
        audit_results = self.audit_new_words()

        # إنشاء التقرير
        report_content = "# تقرير تدقيق المعجم\n\n"
        report_content += f"**تاريخ التقرير:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        report_content += f"**المعجم:** {self.lexicon_path}\n\n"

        # إحصائيات عامة
        report_content += "## إحصائيات التدقيق\n\n"
        report_content += f"- **إجمالي الكلمات في المعجم:** {self.audit_stats['total_words']}\n"
        report_content += f"- **الكلمات الجديدة المضافة:** {self.audit_stats['new_words']}\n"

        issues_count = sum(1 for result in audit_results if result.get("needs_correction", False))
        report_content += f"- **الكلمات التي تحتاج إلى تصحيح:** {issues_count}\n"

        # تصنيف المشاكل
        issues_by_type = {"root": 0, "type": 0, "pattern": 0, "meaning": 0}

        for result in audit_results:
            for issue in result.get("issues", []):
                issue_type = issue.get("type")
                if issue_type in issues_by_type:
                    issues_by_type[issue_type] += 1

        report_content += "\n### توزيع المشاكل حسب النوع\n\n"
        for issue_type, count in issues_by_type.items():
            report_content += f"- **{issue_type}:** {count}\n"

        # قائمة الكلمات التي تحتاج إلى تصحيح
        needs_correction = [r for r in audit_results if r.get("needs_correction", False)]

        if needs_correction:
            report_content += "\n## الكلمات التي تحتاج إلى تصحيح\n\n"
            report_content += "| الكلمة | المشاكل | اقتراحات |\n"
            report_content += "| ------ | ------- | -------- |\n"

            for result in needs_correction:
                word = result["word"]
                issues_str = "<br>".join([issue["message"] for issue in result["issues"]])

                suggestions = result["algorithm_suggestions"]
                suggestions_str = "<br>".join([f"{k}: {v}" for k, v in suggestions.items() if v])

                report_content += f"| {word} | {issues_str} | {suggestions_str} |\n"

        # حفظ التقرير
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(report_content)

        logger.info(f"تم تصدير تقرير التدقيق بنجاح إلى: {output_path}")

    def export_to_csv(self, output_path: str) -> None:
        """
        تصدير نتائج التدقيق إلى ملف CSV.

        المعلمات:
            output_path: مسار ملف CSV
        """
        logger.info(f"تصدير نتائج التدقيق إلى CSV: {output_path}")

        # تدقيق الكلمات الجديدة
        audit_results = self.audit_new_words()

        if not audit_results:
            logger.warning("لا توجد نتائج تدقيق لتصديرها")
            return

        # إعداد بيانات CSV
        csv_data = []

        for result in audit_results:
            word = result["word"]
            current = result["current"]
            suggestions = result["algorithm_suggestions"]

            # تجميع المشاكل
            issues_text = "; ".join([issue["message"] for issue in result.get("issues", [])])

            row = {
                "word": word,
                "current_root": current.get("root", ""),
                "current_type": current.get("type", ""),
                "current_pattern": current.get("pattern", ""),
                "current_meaning": current.get("meaning", ""),
                "suggested_root": suggestions.get("root", ""),
                "suggested_type": suggestions.get("type", ""),
                "suggested_pattern": suggestions.get("pattern", ""),
                "issues": issues_text,
                "needs_correction": "نعم" if result.get("needs_correction", False) else "لا",
            }

            csv_data.append(row)

        # إنشاء دليل الإخراج إذا لم يكن موجوداً
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

        # كتابة ملف CSV
        with open(output_path, "w", encoding="utf-8", newline="") as csvfile:
            fieldnames = [
                "word",
                "current_root",
                "current_type",
                "current_pattern",
                "current_meaning",
                "suggested_root",
                "suggested_type",
                "suggested_pattern",
                "issues",
                "needs_correction",
            ]

            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            for row in csv_data:
                writer.writerow(row)

        logger.info(f"تم تصدير {len(csv_data)} صف من بيانات التدقيق إلى: {output_path}")


def main():
    """النقطة الرئيسية لتنفيذ برنامج تدقيق المعجم"""
    parser = argparse.ArgumentParser(description="أداة تدقيق المعجم")
    parser.add_argument("--lexicon", required=True, help="مسار ملف المعجم المراد تدقيقه")
    parser.add_argument("--original", help="مسار ملف المعجم الأصلي (اختياري)")
    parser.add_argument("--interactive", action="store_true", help="تنفيذ تدقيق تفاعلي")
    parser.add_argument("--report", help="مسار ملف تقرير التدقيق (Markdown)")
    parser.add_argument("--csv", help="مسار ملف نتائج التدقيق (CSV)")

    args = parser.parse_args()

    try:
        # إنشاء مدقق المعجم
        auditor = LexiconAuditor(lexicon_path=args.lexicon, original_lexicon_path=args.original)

        # التدقيق التفاعلي
        if args.interactive:
            auditor.interactive_audit()

        # تصدير تقرير التدقيق
        if args.report:
            auditor.export_audit_report(args.report)

        # تصدير نتائج التدقيق إلى CSV
        if args.csv:
            auditor.export_to_csv(args.csv)

        # إذا لم يتم تحديد أي خيار، عرض المساعدة
        if not (args.interactive or args.report or args.csv):
            parser.print_help()
            return 1

        return 0

    except Exception as e:
        logger.error(f"خطأ أثناء تنفيذ تدقيق المعجم: {str(e)}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
