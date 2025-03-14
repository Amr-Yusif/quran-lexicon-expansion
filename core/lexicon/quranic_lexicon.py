"""
وحدة المعجم القرآني التي توفر واجهة للوصول إلى بيانات الكلمات القرآنية
والحصول على معلوماتها اللغوية المختلفة.
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Any, Set
import logging

# إعداد التسجيل
logger = logging.getLogger(__name__)


class QuranicLexicon:
    """
    فئة المعجم القرآني التي توفر واجهة للوصول إلى بيانات الكلمات
    واستخراج معلوماتها اللغوية مثل الجذر، النوع، الوزن، والمعنى.

    هذه الفئة تعتمد على قاعدة بيانات معجمية مدققة ومراجعة من متخصصين
    لضمان دقة عالية في معالجة النصوص القرآنية.
    """

    def __init__(self, data_path: Path = None):
        """
        تهيئة المعجم القرآني.

        المعاملات:
            data_path: مسار ملف قاعدة البيانات المعجمية.
                       إذا كان None، سيتم تهيئة معجم فارغ.
        """
        # قاموس يحتوي على كل الكلمات ومعلوماتها
        self.words: Dict[str, Dict[str, Any]] = {}

        # قاموس لتسريع البحث عن الكلمات بحسب الجذر
        self.root_to_words: Dict[str, Set[str]] = {}

        # تحميل البيانات إذا تم توفير مسار
        if data_path and os.path.exists(data_path):
            self._load_data(data_path)
        else:
            logger.info("تم إنشاء معجم فارغ. استخدم add_word لإضافة بيانات.")

    def _load_data(self, data_path: Path) -> None:
        """
        تحميل بيانات المعجم من ملف.

        المعاملات:
            data_path: مسار ملف البيانات (بصيغة JSON).
        """
        try:
            with open(data_path, "r", encoding="utf-8") as f:
                self.words = json.load(f)

            # بناء قاموس البحث عن الكلمات بحسب الجذر
            self._build_root_index()

            logger.info(f"تم تحميل {len(self.words)} كلمة من المعجم.")
        except Exception as e:
            logger.error(f"خطأ في تحميل بيانات المعجم: {str(e)}")
            # إعادة تعيين البيانات لتجنب الحالة غير المتسقة
            self.words = {}
            self.root_to_words = {}

    def _build_root_index(self) -> None:
        """بناء فهرس للبحث السريع عن الكلمات بحسب الجذر."""
        self.root_to_words = {}

        for word, info in self.words.items():
            root = info.get("root")
            if root:
                if root not in self.root_to_words:
                    self.root_to_words[root] = set()
                self.root_to_words[root].add(word)

    def get_root(self, word: str) -> Optional[str]:
        """
        استخراج جذر الكلمة من المعجم.

        المعاملات:
            word: الكلمة المراد استخراج جذرها.

        النتيجة:
            جذر الكلمة أو None إذا لم تكن الكلمة موجودة في المعجم.
        """
        if word in self.words:
            return self.words[word].get("root")
        return None

    def get_word_type(self, word: str) -> Optional[str]:
        """
        استخراج نوع الكلمة من المعجم (اسم، فعل، حرف).

        المعاملات:
            word: الكلمة المراد معرفة نوعها.

        النتيجة:
            نوع الكلمة أو None إذا لم تكن الكلمة موجودة في المعجم.
        """
        if word in self.words:
            return self.words[word].get("type")
        return None

    def get_pattern(self, word: str) -> Optional[str]:
        """
        استخراج الوزن الصرفي للكلمة من المعجم.

        المعاملات:
            word: الكلمة المراد معرفة وزنها.

        النتيجة:
            الوزن الصرفي للكلمة أو None إذا لم تكن الكلمة موجودة في المعجم.
        """
        if word in self.words:
            return self.words[word].get("pattern")
        return None

    def get_all_info(self, word: str) -> Optional[Dict[str, Any]]:
        """
        استخراج جميع معلومات الكلمة من المعجم.

        المعاملات:
            word: الكلمة المراد استخراج معلوماتها.

        النتيجة:
            قاموس يحتوي على جميع معلومات الكلمة أو None إذا لم تكن الكلمة موجودة.
        """
        return self.words.get(word)

    def add_word(self, word: str, info: Dict[str, Any]) -> None:
        """
        إضافة كلمة جديدة إلى المعجم مع معلوماتها.

        المعاملات:
            word: الكلمة المراد إضافتها.
            info: قاموس يحتوي على معلومات الكلمة (الجذر، النوع، الوزن، المعنى، المصدر).
        """
        # إضافة الكلمة إلى قاموس الكلمات
        self.words[word] = info

        # تحديث فهرس الجذور
        root = info.get("root")
        if root:
            if root not in self.root_to_words:
                self.root_to_words[root] = set()
            self.root_to_words[root].add(word)

        logger.info(f"تمت إضافة الكلمة '{word}' إلى المعجم.")

    def save(self, file_path: Path) -> bool:
        """
        حفظ بيانات المعجم إلى ملف.

        المعاملات:
            file_path: مسار الملف المراد الحفظ إليه.

        النتيجة:
            True إذا تم الحفظ بنجاح، False إذا حدث خطأ.
        """
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(self.words, f, ensure_ascii=False, indent=2)

            logger.info(f"تم حفظ المعجم ({len(self.words)} كلمة) إلى {file_path}")
            return True
        except Exception as e:
            logger.error(f"خطأ في حفظ بيانات المعجم: {str(e)}")
            return False

    def search_by_root(self, root: str) -> List[str]:
        """
        البحث عن الكلمات التي تنتمي إلى جذر معين.

        المعاملات:
            root: الجذر المراد البحث عنه.

        النتيجة:
            قائمة بالكلمات التي تنتمي إلى الجذر المحدد.
        """
        return list(self.root_to_words.get(root, set()))

    def verify_word_root(self, word: str, expected_root: str) -> bool:
        """
        التحقق من صحة الجذر المتوقع للكلمة.

        المعاملات:
            word: الكلمة المراد التحقق منها.
            expected_root: الجذر المتوقع للكلمة.

        النتيجة:
            True إذا كان الجذر المتوقع صحيحاً، False خلاف ذلك.
        """
        actual_root = self.get_root(word)
        if actual_root is None:
            return False
        return actual_root == expected_root

    def get_word_count(self) -> int:
        """
        الحصول على عدد الكلمات في المعجم.

        النتيجة:
            عدد الكلمات في المعجم.
        """
        return len(self.words)

    def get_root_count(self) -> int:
        """
        الحصول على عدد الجذور في المعجم.

        النتيجة:
            عدد الجذور الفريدة في المعجم.
        """
        return len(self.root_to_words)

    def get_statistics(self) -> Dict[str, Any]:
        """
        الحصول على إحصائيات عن المعجم.

        النتيجة:
            قاموس يحتوي على إحصائيات مختلفة عن المعجم.
        """
        # عدد الكلمات حسب النوع
        word_types = {}
        for word, info in self.words.items():
            word_type = info.get("type", "غير_معروف")
            word_types[word_type] = word_types.get(word_type, 0) + 1

        # متوسط عدد الكلمات لكل جذر
        avg_words_per_root = 0
        if self.root_to_words:
            avg_words_per_root = sum(len(words) for words in self.root_to_words.values()) / len(
                self.root_to_words
            )

        return {
            "total_words": len(self.words),
            "total_roots": len(self.root_to_words),
            "word_types": word_types,
            "avg_words_per_root": avg_words_per_root,
        }
