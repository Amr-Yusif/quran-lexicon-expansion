#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
واجهة توسيع المعجم القرآني.

هذه الأداة توفر واجهة متكاملة لتوسيع المعجم القرآني من خلال:
- توليد اقتراحات للكلمات الجديدة (الجذور، الأنواع، الأوزان)
- مراجعة الاقتراحات وتصفيتها
- إضافة الكلمات المعتمدة إلى المعجم
- تصدير واستيراد البيانات من/إلى ملفات CSV
- معالجة الكلمات في دفعات مع دعم المعالجة المتوازية
- توليد تقارير عن عملية التوسيع

يمكن استخدام هذه الأداة من سطر الأوامر أو استيرادها كوحدة في سكربتات أخرى.
"""

import os
import sys
import json
import re
import csv
import datetime
import time
import threading
import concurrent.futures
from pathlib import Path
import argparse
from typing import Dict, List, Any, Optional, Tuple, Set, Iterator, Generator
import tqdm
import logging
import random

# إعداد التسجيل
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("lexicon_expansion")

# إضافة مسار المشروع الجذر إلى PYTHONPATH
current_path = Path(os.path.dirname(os.path.abspath(__file__)))
root_path = current_path.parent
sys.path.append(str(root_path))

# استيراد المكونات الأساسية من المشروع
from core.lexicon.quranic_lexicon import QuranicLexicon
from core.lexicon.hybrid_processor import HybridProcessor
from core.nlp.root_extraction import ArabicRootExtractor
from core.nlp.morphology import ArabicMorphologyAnalyzer
from core.nlp.diacritics import DiacriticsProcessor


class LexiconExpansionInterface:
    """واجهة لتوسيع المعجم القرآني بطريقة منظمة وموثوقة."""

    def __init__(self, lexicon_path: str, output_path: Optional[str] = None):
        """
        تهيئة واجهة توسيع المعجم.

        المعلمات:
            lexicon_path: مسار ملف المعجم الأصلي
            output_path: مسار ملف المعجم الموسع (اختياري، يستخدم نفس المسار الأصلي إذا لم يتم تحديده)
        """
        logger.info(f"تهيئة واجهة توسيع المعجم. المعجم الأصلي: {lexicon_path}")

        # مسارات الملفات
        self.lexicon_path = lexicon_path
        self.output_path = output_path if output_path else lexicon_path

        # تحميل المعجم
        self._load_lexicon()

        # إنشاء المعالجات
        self.hybrid_processor = HybridProcessor(lexicon_path=lexicon_path)
        self.root_extractor = ArabicRootExtractor()
        self.morphology_analyzer = ArabicMorphologyAnalyzer()
        self.diacritics_processor = DiacriticsProcessor()

        # الاقتراحات
        self.suggestions = []
        self.approved_suggestions = []
        self.rejected_suggestions = []

        # إحصائيات
        self.stats = {
            "initial_lexicon_size": len(self.lexicon.words),
            "words_processed": 0,
            "words_added": 0,
            "words_rejected": 0,
            "start_time": datetime.now().isoformat(),
            "last_update": datetime.now().isoformat(),
        }

        logger.info(
            f"تم تهيئة واجهة توسيع المعجم. حجم المعجم الأولي: {self.stats['initial_lexicon_size']} كلمة"
        )

    def _load_lexicon(self):
        """تحميل المعجم من الملف."""
        try:
            self.lexicon = QuranicLexicon(self.lexicon_path)
            logger.info(f"تم تحميل المعجم بنجاح. عدد الكلمات: {len(self.lexicon.words)}")
        except Exception as e:
            logger.error(f"فشل في تحميل المعجم: {str(e)}")
            raise ValueError(f"فشل في تحميل المعجم من المسار: {self.lexicon_path}")

    def analyze_word_patterns(self, words: List[str]) -> Dict[str, Dict[str, Any]]:
        """
        تحليل أنماط الكلمات وخصائصها.

        المعلمات:
            words: قائمة الكلمات للتحليل

        العوائد:
            قاموس يحتوي على أنماط الكلمات وخصائصها
        """
        logger.info(f"تحليل أنماط {len(words)} كلمة")
        patterns = {}

        for word in words:
            # تنظيف الكلمة
            clean_word = self.diacritics_processor.remove_diacritics(word).strip()

            # تجاهل الكلمات الموجودة بالفعل في المعجم
            if clean_word in self.lexicon.words:
                continue

            # استخراج الجذر باستخدام الخوارزميات المختلفة
            root_info = self.root_extractor.extract_root(clean_word)
            root = root_info.get("root", "")

            # تحليل صرفي
            morphology = self.morphology_analyzer.analyze_word(clean_word)
            word_type = morphology.get("type", "غير معروف")
            pattern = morphology.get("pattern", "غير معروف")

            # تخزين المعلومات حسب النمط
            if pattern not in patterns:
                patterns[pattern] = {
                    "count": 0,
                    "examples": [],
                    "roots": set(),
                    "word_types": set(),
                }

            patterns[pattern]["count"] += 1
            if len(patterns[pattern]["examples"]) < 5:  # نحتفظ بحد أقصى 5 أمثلة
                patterns[pattern]["examples"].append(clean_word)
            patterns[pattern]["roots"].add(root)
            patterns[pattern]["word_types"].add(word_type)

        # تحويل المجموعات إلى قوائم للتسهيل
        for pattern in patterns:
            patterns[pattern]["roots"] = list(patterns[pattern]["roots"])
            patterns[pattern]["word_types"] = list(patterns[pattern]["word_types"])

        logger.info(f"تم تحليل الكلمات وإيجاد {len(patterns)} نمط مختلف")
        return patterns

    def generate_suggestions(self, words_file: str) -> List[Dict[str, Any]]:
        """
        توليد اقتراحات للكلمات من ملف.

        المعلمات:
            words_file: مسار ملف يحتوي على الكلمات، كلمة واحدة في كل سطر

        العوائد:
            قائمة من الاقتراحات لكل كلمة، تتضمن معلومات مثل الجذر والنوع
        """
        logger.info(f"توليد اقتراحات للكلمات من الملف: {words_file}")

        try:
            # قراءة الكلمات من الملف
            with open(words_file, "r", encoding="utf-8") as f:
                word_list = [line.strip() for line in f if line.strip()]

            logger.info(f"تم قراءة {len(word_list)} كلمة من الملف")

            # تصفية الكلمات الموجودة بالفعل في المعجم
            new_words = []
            for word in word_list:
                clean_word = self.diacritics_processor.remove_diacritics(word).strip()
                if clean_word not in self.lexicon.words:
                    new_words.append(clean_word)

            logger.info(f"تبقى {len(new_words)} كلمة جديدة غير موجودة في المعجم")

            # توليد اقتراحات
            suggestions = []
            for word in tqdm.tqdm(new_words, desc="توليد اقتراحات"):
                # استخدام المعالج الهجين للحصول على معلومات الكلمة
                word_info = self.hybrid_processor.process_word(word)

                # استخدام الخوارزميات مباشرة للحصول على معلومات إضافية
                root_info = self.root_extractor.extract_root(word)
                morphology = self.morphology_analyzer.analyze_word(word)

                # تقييم مستوى الثقة في الاقتراح
                confidence = self._calculate_confidence(word_info, root_info, morphology)

                # إنشاء اقتراح
                suggestion = {
                    "word": word,
                    "root": word_info.get("root", root_info.get("root", "")),
                    "root_source": word_info.get("root_source", "خوارزمية"),
                    "type": word_info.get("type", morphology.get("type", "غير معروف")),
                    "pattern": morphology.get("pattern", "غير معروف"),
                    "meaning": "",  # يجب ملؤه يدويًا أو من مصدر آخر
                    "confidence": confidence,
                    "verified": False,
                    "algorithm_results": {
                        "root_extraction": root_info,
                        "morphology": morphology,
                    },
                }

                suggestions.append(suggestion)

            # حفظ الاقتراحات
            self.suggestions = suggestions

            logger.info(f"تم توليد {len(suggestions)} اقتراح")
            self.stats["words_processed"] += len(new_words)
            self.stats["last_update"] = datetime.now().isoformat()

            return suggestions

        except FileNotFoundError:
            logger.error(f"لم يتم العثور على ملف الكلمات: {words_file}")
            return []
        except Exception as e:
            logger.error(f"خطأ أثناء توليد الاقتراحات: {str(e)}")
            return []

    def _calculate_confidence(
        self, word_info: Dict[str, Any], root_info: Dict[str, Any], morphology: Dict[str, Any]
    ) -> float:
        """
        حساب مستوى الثقة في الاقتراح.

        المعلمات:
            word_info: معلومات الكلمة من المعالج الهجين
            root_info: معلومات الجذر من مستخرج الجذور
            morphology: معلومات التحليل الصرفي

        العوائد:
            قيمة بين 0 و 1 تمثل مستوى الثقة
        """
        confidence = 0.0

        # مصدر الجذر
        if word_info.get("root_source") == "lexicon":
            confidence += 0.4  # ثقة عالية إذا كان الجذر من المعجم
        elif word_info.get("root_source") == "algorithm":
            confidence += 0.2  # ثقة متوسطة إذا كان الجذر من الخوارزمية

        # مستوى الثقة في استخراج الجذر
        if root_info.get("confidence", 0) > 0.7:
            confidence += 0.3
        elif root_info.get("confidence", 0) > 0.5:
            confidence += 0.2
        else:
            confidence += 0.1

        # دقة التحليل الصرفي
        if morphology.get("pattern") != "غير معروف":
            confidence += 0.2
        if morphology.get("type") != "غير معروف":
            confidence += 0.1

        # تطبيع النتيجة للتأكد من أنها بين 0 و 1
        return min(1.0, confidence)

    def export_suggestions_to_csv(self, output_file: str) -> None:
        """
        تصدير الاقتراحات إلى ملف CSV للمراجعة اليدوية.

        المعلمات:
            output_file: مسار ملف CSV للتصدير
        """
        logger.info(f"تصدير الاقتراحات إلى ملف CSV: {output_file}")

        try:
            # التأكد من وجود اقتراحات للتصدير
            if not self.suggestions:
                logger.warning("لا توجد اقتراحات للتصدير")
                return

            # إنشاء دليل الإخراج إذا لم يكن موجودًا
            output_dir = os.path.dirname(output_file)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir)

            # تصدير البيانات إلى CSV
            with open(output_file, "w", encoding="utf-8", newline="") as csvfile:
                fieldnames = [
                    "word",
                    "root",
                    "type",
                    "pattern",
                    "meaning",
                    "confidence",
                    "verified",
                    "notes",
                ]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

                writer.writeheader()
                for suggestion in self.suggestions:
                    # تحضير البيانات للتصدير
                    row = {
                        "word": suggestion["word"],
                        "root": suggestion["root"],
                        "type": suggestion["type"],
                        "pattern": suggestion["pattern"],
                        "meaning": suggestion.get("meaning", ""),
                        "confidence": f"{suggestion['confidence']:.2f}",
                        "verified": "نعم" if suggestion.get("verified", False) else "لا",
                        "notes": suggestion.get("notes", ""),
                    }
                    writer.writerow(row)

            logger.info(f"تم تصدير {len(self.suggestions)} اقتراح بنجاح إلى {output_file}")

        except Exception as e:
            logger.error(f"خطأ أثناء تصدير الاقتراحات: {str(e)}")

    def import_verified_suggestions(self, csv_file: str) -> None:
        """
        استيراد الاقتراحات المراجعة من ملف CSV.

        المعلمات:
            csv_file: مسار ملف CSV المحتوي على الاقتراحات المراجعة
        """
        logger.info(f"استيراد الاقتراحات المراجعة من ملف CSV: {csv_file}")

        try:
            if not os.path.exists(csv_file):
                logger.error(f"لم يتم العثور على ملف CSV: {csv_file}")
                return

            # استيراد البيانات من CSV
            imported_suggestions = []
            with open(csv_file, "r", encoding="utf-8") as csvfile:
                reader = csv.DictReader(csvfile)

                for row in reader:
                    # تفسير البيانات من الملف
                    verified = row.get("verified", "لا") in ["نعم", "True", "true", "1"]

                    # تخطي الاقتراحات غير المراجعة
                    if not verified:
                        continue

                    # إنشاء اقتراح من البيانات المستوردة
                    suggestion = {
                        "word": row["word"],
                        "root": row["root"],
                        "type": row["type"],
                        "pattern": row["pattern"],
                        "meaning": row.get("meaning", ""),
                        "confidence": float(row.get("confidence", "0.0")),
                        "verified": True,
                        "notes": row.get("notes", ""),
                    }

                    # إضافة إلى قائمة الاقتراحات المستوردة
                    imported_suggestions.append(suggestion)

            # تحديث قائمة الاقتراحات المعتمدة
            self.approved_suggestions.extend(imported_suggestions)

            logger.info(f"تم استيراد {len(imported_suggestions)} اقتراح مراجع بنجاح")

        except Exception as e:
            logger.error(f"خطأ أثناء استيراد الاقتراحات: {str(e)}")

    def review_suggestions(self) -> None:
        """
        واجهة تفاعلية لمراجعة الاقتراحات.
        """
        logger.info("بدء واجهة المراجعة التفاعلية")

        if not self.suggestions:
            logger.warning("لا توجد اقتراحات للمراجعة")
            return

        print("\n=== مراجعة الاقتراحات ===\n")

        for i, suggestion in enumerate(self.suggestions):
            print(f"\n[{i + 1}/{len(self.suggestions)}] مراجعة اقتراح:")
            print(f"الكلمة: {suggestion['word']}")
            print(
                f"الجذر المقترح: {suggestion['root']} (المصدر: {suggestion.get('root_source', 'غير معروف')})"
            )
            print(f"النوع: {suggestion['type']}")
            print(f"الوزن: {suggestion['pattern']}")
            print(f"مستوى الثقة: {suggestion['confidence']:.2f}")

            # عرض نتائج الخوارزميات إذا كانت متوفرة
            if "algorithm_results" in suggestion:
                print("\nنتائج الخوارزميات:")
                root_info = suggestion["algorithm_results"].get("root_extraction", {})
                print(
                    f"  استخراج الجذر: {root_info.get('root', 'غير معروف')} (ثقة: {root_info.get('confidence', 0):.2f})"
                )

                morphology = suggestion["algorithm_results"].get("morphology", {})
                print(
                    f"  تحليل صرفي: النوع: {morphology.get('type', 'غير معروف')}, النمط: {morphology.get('pattern', 'غير معروف')}"
                )

            # اختيارات المستخدم
            print("\nالإجراءات المتاحة:")
            print("1. قبول الاقتراح كما هو")
            print("2. تعديل الاقتراح")
            print("3. رفض الاقتراح")
            print("4. تخطي هذا الاقتراح")
            print("5. الخروج من المراجعة")

            choice = input("\nاختر إجراءً (1-5): ").strip()

            if choice == "1":
                # قبول الاقتراح
                suggestion["verified"] = True
                self.approved_suggestions.append(suggestion)
                print("تم قبول الاقتراح.")

            elif choice == "2":
                # تعديل الاقتراح
                print("\n--- تعديل الاقتراح ---")

                root = input(f"الجذر ({suggestion['root']}): ").strip()
                if root:
                    suggestion["root"] = root

                word_type = input(f"النوع ({suggestion['type']}): ").strip()
                if word_type:
                    suggestion["type"] = word_type

                pattern = input(f"الوزن ({suggestion['pattern']}): ").strip()
                if pattern:
                    suggestion["pattern"] = pattern

                meaning = input(f"المعنى ({suggestion.get('meaning', '')}): ").strip()
                if meaning:
                    suggestion["meaning"] = meaning

                notes = input("ملاحظات إضافية: ").strip()
                if notes:
                    suggestion["notes"] = notes

                suggestion["verified"] = True
                self.approved_suggestions.append(suggestion)
                print("تم تعديل وقبول الاقتراح.")

            elif choice == "3":
                # رفض الاقتراح
                self.rejected_suggestions.append(suggestion)
                print("تم رفض الاقتراح.")

            elif choice == "4":
                # تخطي الاقتراح
                print("تم تخطي الاقتراح.")

            elif choice == "5":
                # الخروج من المراجعة
                print("تم الخروج من المراجعة.")
                break

            else:
                print("اختيار غير صالح. تم تخطي الاقتراح.")

        # تحديث الإحصائيات
        self.stats["words_added"] = len(self.approved_suggestions)
        self.stats["words_rejected"] = len(self.rejected_suggestions)
        self.stats["last_update"] = datetime.now().isoformat()

        print(f"\n=== انتهت المراجعة ===")
        print(f"تمت مراجعة {i + 1} اقتراح")
        print(
            f"تم قبول: {len(self.approved_suggestions)} / تم رفض: {len(self.rejected_suggestions)}"
        )

        # سؤال المستخدم عما إذا كان يرغب في إضافة الاقتراحات المعتمدة إلى المعجم
        if self.approved_suggestions:
            choice = input(
                "\nهل ترغب في إضافة الاقتراحات المعتمدة إلى المعجم الآن؟ (نعم/لا): "
            ).strip()
            if choice.lower() in ["نعم", "y", "yes"]:
                self.add_to_lexicon()

    def add_to_lexicon(self) -> bool:
        """
        إضافة الاقتراحات المعتمدة إلى المعجم.

        العوائد:
            True إذا تمت الإضافة بنجاح، False خلاف ذلك
        """
        logger.info("إضافة الاقتراحات المعتمدة إلى المعجم")

        if not self.approved_suggestions:
            logger.warning("لا توجد اقتراحات معتمدة للإضافة إلى المعجم")
            return False

        try:
            # إضافة كل اقتراح معتمد إلى المعجم
            added_count = 0
            for suggestion in self.approved_suggestions:
                # التحقق من أن الكلمة غير موجودة بالفعل
                word = suggestion["word"]
                if word in self.lexicon.words:
                    logger.warning(f"الكلمة '{word}' موجودة بالفعل في المعجم. تم تخطيها.")
                    continue

                # إضافة الكلمة إلى المعجم
                properties = {
                    "root": suggestion["root"],
                    "type": suggestion["type"],
                    "pattern": suggestion["pattern"],
                }

                if suggestion.get("meaning"):
                    properties["meaning"] = suggestion["meaning"]

                if suggestion.get("notes"):
                    properties["notes"] = suggestion["notes"]

                # إضافة الكلمة إلى المعجم
                self.lexicon.add_word(word, properties)
                added_count += 1

            # تحديث الإحصائيات
            if added_count > 0:
                logger.info(f"تمت إضافة {added_count} كلمة إلى المعجم")

                # حفظ المعجم
                save_success = self.save_lexicon()
                if save_success:
                    # مسح قوائم الاقتراحات بعد الإضافة
                    self.approved_suggestions = []

                    # تحديث المعالج الهجين بالمعجم الجديد
                    self.hybrid_processor = HybridProcessor(lexicon_path=self.output_path)

                    return True
                else:
                    logger.error("فشل في حفظ المعجم بعد إضافة الكلمات")
                    return False
            else:
                logger.warning("لم تتم إضافة أي كلمات إلى المعجم")
                return False

        except Exception as e:
            logger.error(f"خطأ أثناء إضافة الاقتراحات إلى المعجم: {str(e)}")
            return False

    def save_lexicon(self, auto_save_path: Optional[str] = None) -> bool:
        """
        حفظ المعجم إلى ملف.

        المعلمات:
            auto_save_path: مسار ملف بديل للحفظ (اختياري)

        العوائد:
            True إذا تم الحفظ بنجاح، False خلاف ذلك
        """
        save_path = auto_save_path if auto_save_path else self.output_path
        logger.info(f"حفظ المعجم إلى الملف: {save_path}")

        try:
            # التأكد من وجود الدليل
            os.makedirs(os.path.dirname(os.path.abspath(save_path)), exist_ok=True)

            # حفظ المعجم
            self.lexicon.save_to_file(save_path)

            logger.info(f"تم حفظ المعجم بنجاح. عدد الكلمات: {len(self.lexicon.words)}")
            return True

        except Exception as e:
            logger.error(f"خطأ أثناء حفظ المعجم: {str(e)}")
            return False

    def bulk_expand_lexicon(
        self, words_file: str, auto_approve_threshold: float = 0.9
    ) -> Tuple[int, int]:
        """
        توسيع المعجم بشكل آلي باستخدام قائمة كلمات من ملف.

        المعلمات:
            words_file: مسار ملف الكلمات
            auto_approve_threshold: عتبة الثقة للقبول التلقائي

        العوائد:
            زوج من (عدد الكلمات المضافة تلقائيًا، عدد الكلمات التي تحتاج إلى مراجعة)
        """
        logger.info(f"بدء التوسيع التلقائي للمعجم باستخدام الملف: {words_file}")
        logger.info(f"عتبة القبول التلقائي: {auto_approve_threshold}")

        try:
            # توليد اقتراحات للكلمات
            self.generate_suggestions(words_file)

            if not self.suggestions:
                logger.warning("لم يتم توليد أي اقتراحات")
                return (0, 0)

            # فرز الاقتراحات حسب مستوى الثقة
            auto_approved = []
            need_review = []

            for suggestion in self.suggestions:
                if suggestion["confidence"] >= auto_approve_threshold:
                    suggestion["verified"] = True
                    auto_approved.append(suggestion)
                else:
                    need_review.append(suggestion)

            # تحديث قوائم الاقتراحات
            self.approved_suggestions = auto_approved
            self.suggestions = need_review

            logger.info(f"تم اعتماد {len(auto_approved)} اقتراح تلقائيًا")
            logger.info(f"يتطلب {len(need_review)} اقتراح مراجعة يدوية")

            # إضافة الاقتراحات المعتمدة تلقائيًا إلى المعجم
            if auto_approved:
                logger.info("إضافة الاقتراحات المعتمدة تلقائيًا إلى المعجم")
                self.add_to_lexicon()

            # تصدير الاقتراحات التي تحتاج مراجعة إلى ملف CSV
            if need_review:
                review_file = f"review_{os.path.basename(words_file).split('.')[0]}.csv"
                review_path = os.path.join(os.path.dirname(self.output_path), review_file)
                logger.info(f"تصدير الاقتراحات التي تحتاج مراجعة إلى: {review_path}")
                self.suggestions = need_review  # تأكيد استخدام الاقتراحات التي تحتاج مراجعة
                self.export_suggestions_to_csv(review_path)

            return (len(auto_approved), len(need_review))

        except Exception as e:
            logger.error(f"خطأ أثناء التوسيع التلقائي للمعجم: {str(e)}")
            return (0, 0)

    def add_word_interactively(self) -> None:
        """
        إضافة كلمة جديدة إلى المعجم بطريقة تفاعلية.
        """
        print("\n=== إضافة كلمة جديدة إلى المعجم ===\n")

        # الحصول على الكلمة من المستخدم
        word = input("أدخل الكلمة: ").strip()
        if not word:
            print("لم يتم إدخال كلمة.")
            return

        # التحقق من أن الكلمة غير موجودة بالفعل
        clean_word = self.diacritics_processor.remove_diacritics(word).strip()
        if clean_word in self.lexicon.words:
            print(f"الكلمة '{clean_word}' موجودة بالفعل في المعجم.")
            return

        # استخدام الخوارزميات لاقتراح معلومات الكلمة
        word_info = self.hybrid_processor.process_word(clean_word)
        root_info = self.root_extractor.extract_root(clean_word)
        morphology = self.morphology_analyzer.analyze_word(clean_word)

        # عرض المعلومات المقترحة للمستخدم
        print("\nالمعلومات المقترحة للكلمة:")
        suggested_root = word_info.get("root", root_info.get("root", ""))
        print(f"الجذر المقترح: {suggested_root}")
        suggested_type = word_info.get("type", morphology.get("type", "غير معروف"))
        print(f"نوع الكلمة المقترح: {suggested_type}")
        suggested_pattern = morphology.get("pattern", "غير معروف")
        print(f"وزن الكلمة المقترح: {suggested_pattern}")

        # السماح للمستخدم بتأكيد أو تعديل المعلومات
        print("\nيمكنك قبول المعلومات المقترحة أو تعديلها:")

        root = input(f"الجذر ({suggested_root}): ").strip() or suggested_root
        word_type = input(f"النوع ({suggested_type}): ").strip() or suggested_type
        pattern = input(f"الوزن ({suggested_pattern}): ").strip() or suggested_pattern
        meaning = input("المعنى: ").strip()
        notes = input("ملاحظات إضافية: ").strip()

        # إنشاء كائن الكلمة
        properties = {
            "root": root,
            "type": word_type,
            "pattern": pattern,
        }

        if meaning:
            properties["meaning"] = meaning

        if notes:
            properties["notes"] = notes

        # إضافة الكلمة إلى المعجم
        self.lexicon.add_word(clean_word, properties)

        # حفظ المعجم
        if self.save_lexicon():
            print(f"تمت إضافة الكلمة '{clean_word}' إلى المعجم بنجاح.")

            # تحديث المعالج الهجين بالمعجم الجديد
            self.hybrid_processor = HybridProcessor(lexicon_path=self.output_path)
        else:
            print("فشل في حفظ المعجم بعد إضافة الكلمة.")

    def get_related_words(self, root: str) -> List[Dict[str, Any]]:
        """
        الحصول على الكلمات المرتبطة بجذر معين من المعجم.

        المعلمات:
            root: الجذر المطلوب

        العوائد:
            قائمة بالكلمات المرتبطة بالجذر المحدد
        """
        related_words = []

        for word, properties in self.lexicon.words.items():
            if properties.get("root") == root:
                word_info = {
                    "word": word,
                    "type": properties.get("type", "غير معروف"),
                    "pattern": properties.get("pattern", "غير معروف"),
                    "meaning": properties.get("meaning", ""),
                }
                related_words.append(word_info)

        return related_words

    def show_stats(self) -> Dict[str, Any]:
        """
        عرض إحصائيات المعجم والتوسيع.

        العوائد:
            قاموس يحتوي على الإحصائيات
        """
        # تحديث الإحصائيات
        current_lexicon_size = len(self.lexicon.words)
        growth = current_lexicon_size - self.stats["initial_lexicon_size"]

        stats = {
            "lexicon": {
                "initial_size": self.stats["initial_lexicon_size"],
                "current_size": current_lexicon_size,
                "growth": growth,
                "growth_percentage": (growth / self.stats["initial_lexicon_size"]) * 100
                if self.stats["initial_lexicon_size"] > 0
                else 0,
            },
            "expansion": {
                "processed": self.stats["words_processed"],
                "added": self.stats["words_added"],
                "rejected": self.stats["words_rejected"],
                "pending_review": len(self.suggestions),
                "start_time": self.stats["start_time"],
                "last_update": self.stats["last_update"],
            },
        }

        # عرض الإحصائيات
        print("\n=== إحصائيات المعجم ===")
        print(f"الحجم الأولي: {stats['lexicon']['initial_size']} كلمة")
        print(f"الحجم الحالي: {stats['lexicon']['current_size']} كلمة")
        print(
            f"النمو: {stats['lexicon']['growth']} كلمة ({stats['lexicon']['growth_percentage']:.2f}%)"
        )

        print("\n=== إحصائيات التوسيع ===")
        print(f"الكلمات المعالجة: {stats['expansion']['processed']}")
        print(f"الكلمات المضافة: {stats['expansion']['added']}")
        print(f"الكلمات المرفوضة: {stats['expansion']['rejected']}")
        print(f"الكلمات بانتظار المراجعة: {stats['expansion']['pending_review']}")

        return stats

    def process_words_in_batches(
        self,
        words_file: str,
        batch_size: int = 100,
        auto_approve_threshold: float = 0.9,
        use_parallel: bool = True,
    ) -> Dict[str, Any]:
        """
        معالجة الكلمات في دفعات مع دعم المعالجة المتوازية.

        المعلمات:
            words_file: مسار ملف الكلمات
            batch_size: حجم الدفعة
            auto_approve_threshold: عتبة الثقة للقبول التلقائي
            use_parallel: استخدام المعالجة المتوازية

        العوائد:
            إحصائيات المعالجة
        """
        logger.info(f"معالجة الكلمات في دفعات من حجم {batch_size} من الملف: {words_file}")
        logger.info(f"استخدام المعالجة المتوازية: {use_parallel}")

        try:
            # قراءة الكلمات من الملف
            with open(words_file, "r", encoding="utf-8") as f:
                word_list = [line.strip() for line in f if line.strip()]

            # إزالة الكلمات المكررة
            word_list = list(set(word_list))

            # تصفية الكلمات الموجودة بالفعل في المعجم
            new_words = []
            for word in word_list:
                clean_word = self.diacritics_processor.remove_diacritics(word).strip()
                if clean_word not in self.lexicon.words:
                    new_words.append(clean_word)

            logger.info(f"تم العثور على {len(new_words)} كلمة جديدة من أصل {len(word_list)}")

            # تقسيم الكلمات إلى دفعات
            batches = []
            for i in range(0, len(new_words), batch_size):
                batches.append(new_words[i : i + batch_size])

            logger.info(f"تم تقسيم الكلمات إلى {len(batches)} دفعة")

            # معالجة الدفعات
            auto_approved = []
            need_review = []

            for i, batch in enumerate(batches):
                logger.info(f"معالجة الدفعة {i + 1}/{len(batches)}")

                # معالجة الدفعة
                if use_parallel:
                    batch_suggestions = self._process_batch_parallel(batch)
                else:
                    batch_suggestions = self._process_batch_sequential(batch)

                # تصنيف الاقتراحات
                for suggestion in batch_suggestions:
                    if suggestion["confidence"] >= auto_approve_threshold:
                        suggestion["verified"] = True
                        auto_approved.append(suggestion)
                    else:
                        need_review.append(suggestion)

            # تحديث الإحصائيات
            self.stats["words_processed"] += len(new_words)

            # إضافة الاقتراحات المعتمدة تلقائيًا إلى المعجم
            self.approved_suggestions = auto_approved
            if auto_approved:
                logger.info(f"إضافة {len(auto_approved)} اقتراح معتمد تلقائيًا إلى المعجم")
                self.add_to_lexicon()

            # تحديث قائمة الاقتراحات التي تحتاج مراجعة
            self.suggestions = need_review

            # تصدير الاقتراحات التي تحتاج مراجعة إلى ملف CSV
            if need_review:
                review_file = f"review_{os.path.basename(words_file).split('.')[0]}.csv"
                review_path = os.path.join(os.path.dirname(self.output_path), review_file)
                logger.info(f"تصدير {len(need_review)} اقتراح للمراجعة إلى: {review_path}")
                self.export_suggestions_to_csv(review_path)

            # إعداد الإحصائيات النهائية
            result_stats = {
                "total_words": len(word_list),
                "new_words": len(new_words),
                "auto_approved": len(auto_approved),
                "need_review": len(need_review),
                "review_file": review_path if need_review else None,
            }

            logger.info(f"اكتملت معالجة الكلمات. الإحصائيات: {result_stats}")
            return result_stats

        except Exception as e:
            logger.error(f"خطأ أثناء معالجة الكلمات في دفعات: {str(e)}")
            return {
                "error": str(e),
                "total_words": 0,
                "new_words": 0,
                "auto_approved": 0,
                "need_review": 0,
            }

    def _process_batch_parallel(self, batch_words: List[str]) -> List[Dict[str, Any]]:
        """
        معالجة دفعة من الكلمات بشكل متوازي.

        المعلمات:
            batch_words: قائمة الكلمات للمعالجة

        العوائد:
            قائمة من الاقتراحات
        """
        suggestions = []
        max_workers = min(os.cpu_count() or 4, 8)  # استخدام عدد معقول من العمال

        logger.info(f"معالجة {len(batch_words)} كلمة بشكل متوازي باستخدام {max_workers} عمال")

        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_word = {
                executor.submit(self._process_single_word, word): word for word in batch_words
            }

            for future in tqdm.tqdm(
                concurrent.futures.as_completed(future_to_word),
                total=len(batch_words),
                desc="معالجة الكلمات",
            ):
                word = future_to_word[future]
                try:
                    suggestion = future.result()
                    if suggestion:
                        suggestions.append(suggestion)
                except Exception as e:
                    logger.error(f"خطأ في معالجة الكلمة '{word}': {str(e)}")

        return suggestions

    def _process_batch_sequential(self, batch_words: List[str]) -> List[Dict[str, Any]]:
        """
        معالجة دفعة من الكلمات بشكل متسلسل.

        المعلمات:
            batch_words: قائمة الكلمات للمعالجة

        العوائد:
            قائمة من الاقتراحات
        """
        suggestions = []

        logger.info(f"معالجة {len(batch_words)} كلمة بشكل متسلسل")

        for word in tqdm.tqdm(batch_words, desc="معالجة الكلمات"):
            suggestion = self._process_single_word(word)
            if suggestion:
                suggestions.append(suggestion)

        return suggestions

    def _process_single_word(self, word: str) -> Optional[Dict[str, Any]]:
        """
        معالجة كلمة واحدة وتوليد اقتراح.

        المعلمات:
            word: الكلمة للمعالجة

        العوائد:
            اقتراح للكلمة، أو None إذا فشلت المعالجة
        """
        try:
            # استخدام المعالج الهجين للحصول على معلومات الكلمة
            word_info = self.hybrid_processor.process_word(word)

            # استخدام الخوارزميات مباشرة للحصول على معلومات إضافية
            root_info = self.root_extractor.extract_root(word)
            morphology = self.morphology_analyzer.analyze_word(word)

            # تقييم مستوى الثقة في الاقتراح
            confidence = self._calculate_confidence(word_info, root_info, morphology)

            # إنشاء اقتراح
            suggestion = {
                "word": word,
                "root": word_info.get("root", root_info.get("root", "")),
                "root_source": word_info.get("root_source", "خوارزمية"),
                "type": word_info.get("type", morphology.get("type", "غير معروف")),
                "pattern": morphology.get("pattern", "غير معروف"),
                "meaning": "",  # يجب ملؤه يدويًا أو من مصدر آخر
                "confidence": confidence,
                "verified": False,
                "algorithm_results": {
                    "root_extraction": root_info,
                    "morphology": morphology,
                },
            }

            return suggestion

        except Exception as e:
            logger.error(f"خطأ في معالجة الكلمة '{word}': {str(e)}")
            return None

    def generate_report(self, output_file: str) -> None:
        """
        توليد تقرير مفصل عن عملية توسيع المعجم.

        المعلمات:
            output_file: مسار ملف التقرير
        """
        logger.info(f"توليد تقرير توسيع المعجم: {output_file}")

        try:
            # الحصول على إحصائيات
            stats = self.show_stats()

            # إنشاء محتوى التقرير
            report = "# تقرير توسيع المعجم القرآني\n\n"
            report += f"**تاريخ التقرير:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"

            # معلومات المعجم
            report += "## معلومات المعجم\n\n"
            report += f"- **المعجم الأصلي:** {self.lexicon_path}\n"
            report += f"- **المعجم الموسع:** {self.output_path}\n"
            report += f"- **الحجم الأولي:** {stats['lexicon']['initial_size']} كلمة\n"
            report += f"- **الحجم الحالي:** {stats['lexicon']['current_size']} كلمة\n"
            report += f"- **النمو:** {stats['lexicon']['growth']} كلمة ({stats['lexicon']['growth_percentage']:.2f}%)\n\n"

            # إحصائيات التوسيع
            report += "## إحصائيات التوسيع\n\n"
            report += f"- **تاريخ البدء:** {stats['expansion']['start_time']}\n"
            report += f"- **آخر تحديث:** {stats['expansion']['last_update']}\n"
            report += f"- **الكلمات المعالجة:** {stats['expansion']['processed']}\n"
            report += f"- **الكلمات المضافة:** {stats['expansion']['added']}\n"
            report += f"- **الكلمات المرفوضة:** {stats['expansion']['rejected']}\n"
            report += f"- **الكلمات بانتظار المراجعة:** {stats['expansion']['pending_review']}\n\n"

            # أمثلة للكلمات المضافة
            report += "## أمثلة للكلمات المضافة\n\n"
            report += "| الكلمة | الجذر | النوع | الوزن | المعنى |\n"
            report += "| ------ | ---- | ---- | ---- | ------ |\n"

            # جمع بعض الأمثلة (حتى 10)
            examples = []
            for word, properties in self.lexicon.words.items():
                if len(examples) >= 10:
                    break

                # التحقق من أن الكلمة أضيفت خلال هذه العملية
                if (
                    word in self.lexicon.words
                    and word
                    not in list(self.lexicon.words.keys())[: self.stats["initial_lexicon_size"]]
                ):
                    examples.append(
                        {
                            "word": word,
                            "root": properties.get("root", ""),
                            "type": properties.get("type", ""),
                            "pattern": properties.get("pattern", ""),
                            "meaning": properties.get("meaning", ""),
                        }
                    )

            # إضافة الأمثلة إلى التقرير
            for example in examples:
                report += f"| {example['word']} | {example['root']} | {example['type']} | {example['pattern']} | {example['meaning']} |\n"

            # حفظ التقرير إلى ملف
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(report)

            logger.info(f"تم توليد التقرير بنجاح: {output_file}")

        except Exception as e:
            logger.error(f"خطأ أثناء توليد التقرير: {str(e)}")


def main():
    """النقطة الرئيسية لتنفيذ البرنامج."""
    parser = argparse.ArgumentParser(description="واجهة توسيع المعجم القرآني")

    # المعلمات الأساسية
    parser.add_argument("--lexicon", required=True, help="مسار ملف المعجم الأصلي")
    parser.add_argument("--output", help="مسار ملف المعجم الموسع (اختياري)")

    # خيارات التوسيع
    parser.add_argument("--words", help="مسار ملف الكلمات للمعالجة")
    parser.add_argument(
        "--threshold", type=float, default=0.85, help="عتبة الثقة للقبول التلقائي (الافتراضي: 0.85)"
    )

    # خيارات التشغيل
    parser.add_argument("--interactive", action="store_true", help="تفعيل الوضع التفاعلي")
    parser.add_argument("--review", help="مسار ملف CSV للاقتراحات المراجعة")
    parser.add_argument("--export", help="تصدير الاقتراحات إلى ملف CSV")
    parser.add_argument("--report", help="توليد تقرير وحفظه إلى ملف")
    parser.add_argument(
        "--batch-size", type=int, default=100, help="حجم الدفعة للمعالجة (الافتراضي: 100)"
    )
    parser.add_argument("--no-parallel", action="store_true", help="تعطيل المعالجة المتوازية")

    args = parser.parse_args()

    try:
        # إنشاء واجهة التوسيع
        interface = LexiconExpansionInterface(args.lexicon, args.output)

        # التحقق من نوع العملية المطلوبة
        if args.words:
            # معالجة الكلمات في دفعات
            logger.info(f"معالجة الكلمات من الملف: {args.words}")
            result = interface.process_words_in_batches(
                args.words,
                batch_size=args.batch_size,
                auto_approve_threshold=args.threshold,
                use_parallel=not args.no_parallel,
            )
            logger.info(f"نتائج المعالجة: {result}")

        elif args.review:
            # استيراد الاقتراحات المراجعة
            logger.info(f"استيراد الاقتراحات المراجعة من: {args.review}")
            interface.import_verified_suggestions(args.review)

            # إضافة الاقتراحات المعتمدة إلى المعجم
            logger.info("إضافة الاقتراحات المعتمدة إلى المعجم")
            interface.add_to_lexicon()

        elif args.export:
            # توليد وتصدير الاقتراحات
            if not interface.suggestions:
                logger.warning("لا توجد اقتراحات للتصدير")
            else:
                logger.info(f"تصدير الاقتراحات إلى: {args.export}")
                interface.export_suggestions_to_csv(args.export)

        elif args.interactive:
            # الوضع التفاعلي
            logger.info("بدء الوضع التفاعلي")

            while True:
                print("\n=== واجهة توسيع المعجم التفاعلية ===")
                print("1. إضافة كلمة جديدة")
                print("2. توليد اقتراحات من ملف")
                print("3. مراجعة الاقتراحات")
                print("4. إضافة الاقتراحات المعتمدة إلى المعجم")
                print("5. تصدير الاقتراحات إلى ملف CSV")
                print("6. استيراد اقتراحات مراجعة من ملف CSV")
                print("7. عرض إحصائيات المعجم")
                print("8. حفظ المعجم")
                print("9. الخروج")

                choice = input("\nاختر إجراءً (1-9): ").strip()

                if choice == "1":
                    interface.add_word_interactively()
                elif choice == "2":
                    words_file = input("أدخل مسار ملف الكلمات: ").strip()
                    if os.path.isfile(words_file):
                        interface.generate_suggestions(words_file)
                    else:
                        print(f"خطأ: الملف '{words_file}' غير موجود")
                elif choice == "3":
                    interface.review_suggestions()
                elif choice == "4":
                    interface.add_to_lexicon()
                elif choice == "5":
                    export_file = input("أدخل مسار ملف التصدير: ").strip()
                    interface.export_suggestions_to_csv(export_file)
                elif choice == "6":
                    import_file = input("أدخل مسار ملف الاقتراحات المراجعة: ").strip()
                    if os.path.isfile(import_file):
                        interface.import_verified_suggestions(import_file)
                    else:
                        print(f"خطأ: الملف '{import_file}' غير موجود")
                elif choice == "7":
                    interface.show_stats()
                elif choice == "8":
                    interface.save_lexicon()
                elif choice == "9":
                    print("الخروج من البرنامج...")
                    break
                else:
                    print("خيار غير صالح. الرجاء المحاولة مرة أخرى.")

        elif args.report:
            # توليد تقرير
            logger.info(f"توليد تقرير وحفظه إلى: {args.report}")
            interface.generate_report(args.report)

        else:
            # عرض الإحصائيات الافتراضية
            interface.show_stats()

    except Exception as e:
        logger.error(f"خطأ أثناء تنفيذ البرنامج: {str(e)}")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
