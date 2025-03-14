"""
وحدة معالجة هجينة تجمع بين المعجم القرآني والخوارزميات
لمعالجة النصوص العربية.
"""

from typing import Dict, Any, Optional, List, Tuple
from pathlib import Path
import logging

from core.lexicon.quranic_lexicon import QuranicLexicon

# استيراد الخوارزميات من الوحدات القائمة
from core.nlp.morphology import ArabicMorphologyAnalyzer
from core.nlp.root_extraction import ArabicRootExtractor
from core.nlp.diacritics import DiacriticsProcessor

# إعداد التسجيل
logger = logging.getLogger(__name__)


class HybridProcessor:
    """
    نظام معالجة هجين يجمع بين قاعدة البيانات المعجمية والخوارزميات
    لتحقيق أعلى دقة ممكنة في معالجة النصوص العربية.

    يعتمد النظام على المعجم كمصدر أساسي للمعلومات إذا كانت الكلمة
    موجودة فيه، وإلا يلجأ إلى الخوارزميات.
    """

    def __init__(
        self,
        lexicon_path: Path = None,
        use_algorithms: bool = True,
        morphology_analyzer: ArabicMorphologyAnalyzer = None,
        root_extractor: ArabicRootExtractor = None,
    ):
        """
        تهيئة نظام المعالجة الهجين.

        المعاملات:
            lexicon_path: مسار ملف المعجم القرآني.
            use_algorithms: ما إذا كان سيتم استخدام الخوارزميات كمصدر ثانوي.
            morphology_analyzer: محلل الصرف العربي (اختياري).
            root_extractor: مستخرج الجذور العربية (اختياري).
        """
        # تهيئة المعجم
        self.lexicon = QuranicLexicon(data_path=lexicon_path) if lexicon_path else QuranicLexicon()

        # تهيئة الخوارزميات
        self.use_algorithms = use_algorithms
        self.algorithms_initialized = False
        self.morphology_analyzer = None
        self.root_extractor = None

        if use_algorithms:
            try:
                # تهيئة الخوارزميات إذا لم يتم تمريرها
                if root_extractor is None:
                    self.root_extractor = ArabicRootExtractor()
                else:
                    self.root_extractor = root_extractor

                if morphology_analyzer is None:
                    diacritics_processor = DiacriticsProcessor()
                    self.morphology_analyzer = ArabicMorphologyAnalyzer(
                        diacritics_processor=diacritics_processor,
                        root_extractor=self.root_extractor,
                    )
                else:
                    self.morphology_analyzer = morphology_analyzer

                self.algorithms_initialized = True
                logger.info("تم تهيئة الخوارزميات بنجاح.")
            except Exception as e:
                logger.error(f"خطأ في تهيئة الخوارزميات: {str(e)}")
                logger.warning("لم يتم تهيئة الخوارزميات. سيتم استخدام المعجم فقط.")

    def extract_root(self, word: str) -> Tuple[str, float, str]:
        """
        استخراج جذر الكلمة باستخدام النظام الهجين.

        المعاملات:
            word: الكلمة المراد استخراج جذرها.

        النتيجة:
            ثلاثية (الجذر، درجة الثقة، المصدر)
        """
        # البحث في المعجم أولاً
        lexicon_root = self.lexicon.get_root(word)

        if lexicon_root:
            return (lexicon_root, 1.0, "lexicon")  # درجة ثقة 1.0 للمعجم

        # إذا لم نجد في المعجم ولدينا خوارزميات، نستخدمها
        if self.use_algorithms and self.algorithms_initialized:
            try:
                algorithm_root = self.root_extractor.extract_root(word, algorithm="hybrid")
                if algorithm_root:
                    return (algorithm_root, 0.8, "algorithm")  # درجة ثقة 0.8 للخوارزميات
            except Exception as e:
                logger.error(f"خطأ في استخراج جذر {word}: {str(e)}")

        return ("", 0.0, "unknown")

    def get_word_type(self, word: str) -> Tuple[str, float, str]:
        """
        تحديد نوع الكلمة باستخدام النظام الهجين.

        المعاملات:
            word: الكلمة المراد تحديد نوعها.

        النتيجة:
            ثلاثية (نوع الكلمة، درجة الثقة، المصدر)
        """
        # البحث في المعجم أولاً
        lexicon_type = self.lexicon.get_word_type(word)

        if lexicon_type:
            return (lexicon_type, 1.0, "lexicon")  # درجة ثقة 1.0 للمعجم

        # إذا لم نجد في المعجم ولدينا خوارزميات، نستخدمها
        if self.use_algorithms and self.algorithms_initialized:
            try:
                analysis = self.morphology_analyzer.analyze_word(word)
                if analysis and "نوع" in analysis:
                    word_type = self._map_arabic_type_to_english(analysis["نوع"])
                    return (word_type, 0.7, "algorithm")  # درجة ثقة 0.7 للخوارزميات
            except Exception as e:
                logger.error(f"خطأ في تحديد نوع الكلمة {word}: {str(e)}")

        return ("", 0.0, "unknown")

    def get_pattern(self, word: str) -> Tuple[str, float, str]:
        """
        استخراج الوزن الصرفي للكلمة باستخدام النظام الهجين.

        المعاملات:
            word: الكلمة المراد استخراج وزنها.

        النتيجة:
            ثلاثية (الوزن، درجة الثقة، المصدر)
        """
        # البحث في المعجم أولاً
        lexicon_pattern = self.lexicon.get_pattern(word)

        if lexicon_pattern:
            return (lexicon_pattern, 1.0, "lexicon")  # درجة ثقة 1.0 للمعجم

        # إذا لم نجد في المعجم ولدينا خوارزميات، نستخدمها
        if self.use_algorithms and self.algorithms_initialized:
            try:
                analysis = self.morphology_analyzer.analyze_word(word)
                if analysis and "وزن" in analysis:
                    return (analysis["وزن"], 0.6, "algorithm")  # درجة ثقة 0.6 للخوارزميات
            except Exception as e:
                logger.error(f"خطأ في استخراج وزن الكلمة {word}: {str(e)}")

        return ("", 0.0, "unknown")

    def process_word(self, word: str) -> Dict[str, Any]:
        """
        معالجة كلمة كاملة واستخراج جميع المعلومات المتاحة عنها.

        المعاملات:
            word: الكلمة المراد معالجتها.

        النتيجة:
            قاموس يحتوي على المعلومات المستخرجة مع درجات الثقة والمصادر.
        """
        result = {
            "word": word,
            "root": {"value": "", "confidence": 0.0, "source": ""},
            "type": {"value": "", "confidence": 0.0, "source": ""},
            "pattern": {"value": "", "confidence": 0.0, "source": ""},
        }

        # محاولة الحصول على جميع المعلومات من المعجم أولاً
        lexicon_info = self.lexicon.get_all_info(word)

        if lexicon_info:
            # إذا وجدنا المعلومات في المعجم، نستخدمها بالكامل
            result["root"]["value"] = lexicon_info.get("root", "")
            result["root"]["confidence"] = 1.0
            result["root"]["source"] = "lexicon"

            result["type"]["value"] = lexicon_info.get("type", "")
            result["type"]["confidence"] = 1.0
            result["type"]["source"] = "lexicon"

            result["pattern"]["value"] = lexicon_info.get("pattern", "")
            result["pattern"]["confidence"] = 1.0
            result["pattern"]["source"] = "lexicon"

            # إضافة معلومات إضافية إذا كانت متوفرة
            if "meaning" in lexicon_info:
                result["meaning"] = {"value": lexicon_info["meaning"], "source": "lexicon"}

            return result

        # إذا لم نجد في المعجم، نستخدم الخوارزميات للحصول على كل معلومة
        root_info = self.extract_root(word)
        result["root"]["value"] = root_info[0]
        result["root"]["confidence"] = root_info[1]
        result["root"]["source"] = root_info[2]

        type_info = self.get_word_type(word)
        result["type"]["value"] = type_info[0]
        result["type"]["confidence"] = type_info[1]
        result["type"]["source"] = type_info[2]

        pattern_info = self.get_pattern(word)
        result["pattern"]["value"] = pattern_info[0]
        result["pattern"]["confidence"] = pattern_info[1]
        result["pattern"]["source"] = pattern_info[2]

        # إذا كانت الخوارزميات مهيأة، نحاول الحصول على مزيد من المعلومات
        if self.use_algorithms and self.algorithms_initialized:
            try:
                analysis = self.morphology_analyzer.analyze_word(word)
                if analysis and "معلومات_إضافية" in analysis:
                    additional_info = {}
                    for key, value in analysis["معلومات_إضافية"].items():
                        additional_info[key] = {"value": value, "source": "algorithm"}

                    result["additional_info"] = additional_info
            except Exception as e:
                logger.error(f"خطأ في استخراج معلومات إضافية للكلمة {word}: {str(e)}")

        return result

    def verify_extraction(self, word: str, expected_root: str) -> Dict[str, Any]:
        """
        التحقق من صحة استخراج جذر لكلمة معينة.

        المعاملات:
            word: الكلمة المراد التحقق منها.
            expected_root: الجذر المتوقع للكلمة.

        النتيجة:
            قاموس يحتوي على نتيجة التحقق وتفاصيل المقارنة.
        """
        # الحصول على الجذر باستخدام النظام الهجين
        extracted_root, confidence, source = self.extract_root(word)

        # التحقق من الجذر المستخرج مع المتوقع
        is_correct = extracted_root == expected_root

        return {
            "word": word,
            "expected_root": expected_root,
            "extracted_root": extracted_root,
            "confidence": confidence,
            "source": source,
            "is_correct": is_correct,
        }

    def expand_lexicon(self, words: List[str]) -> Dict[str, Any]:
        """
        محاولة إثراء المعجم باستخدام الخوارزميات.

        هذه الوظيفة تستخدم الخوارزميات لمعالجة كلمات غير موجودة في المعجم
        وتقترح إضافتها إلى المعجم بعد التحقق البشري.

        المعاملات:
            words: قائمة الكلمات المراد معالجتها.

        النتيجة:
            قاموس يحتوي على اقتراحات الإضافة للمعجم.
        """
        if not self.use_algorithms or not self.algorithms_initialized:
            return {"error": "الخوارزميات غير مهيأة. لا يمكن إثراء المعجم."}

        suggestions = {}

        for word in words:
            # تخطي الكلمات الموجودة بالفعل في المعجم
            if self.lexicon.get_all_info(word):
                continue

            # معالجة الكلمة باستخدام الخوارزميات
            result = self.process_word(word)

            # إذا تمكنت الخوارزميات من استخراج معلومات بدرجة ثقة كافية
            if result["root"]["confidence"] >= 0.7 and result["type"]["confidence"] >= 0.6:
                # اقتراح إضافة الكلمة إلى المعجم
                suggestions[word] = {
                    "root": result["root"]["value"],
                    "type": result["type"]["value"],
                    "pattern": result["pattern"]["value"],
                    "confidence": min(
                        result["root"]["confidence"],
                        result["type"]["confidence"],
                        result["pattern"]["confidence"] or 1.0,
                    ),
                    "source": "algorithm",
                }

        return {
            "total_words": len(words),
            "suggestions_count": len(suggestions),
            "suggestions": suggestions,
        }

    def add_to_lexicon(self, word: str, info: Dict[str, Any], is_verified: bool = False) -> bool:
        """
        إضافة كلمة جديدة إلى المعجم مع معلوماتها.

        المعاملات:
            word: الكلمة المراد إضافتها.
            info: معلومات الكلمة (الجذر، النوع، الوزن، المعنى، المصدر).
            is_verified: ما إذا كانت المعلومات مدققة من قبل خبير بشري.

        النتيجة:
            True إذا تمت الإضافة بنجاح، False خلاف ذلك.
        """
        try:
            # إضافة معلومات إضافية
            info["verification_status"] = "verified" if is_verified else "algorithm_suggested"

            # إضافة الكلمة إلى المعجم
            self.lexicon.add_word(word, info)

            logger.info(f"تمت إضافة الكلمة '{word}' إلى المعجم بواسطة المعالج الهجين.")
            return True
        except Exception as e:
            logger.error(f"خطأ في إضافة الكلمة '{word}' إلى المعجم: {str(e)}")
            return False

    def save_lexicon(self, file_path: Path) -> bool:
        """
        حفظ المعجم القرآني بعد التعديل أو التوسيع.

        المعاملات:
            file_path: مسار الملف لحفظ المعجم.

        النتيجة:
            True إذا تم الحفظ بنجاح، False خلاف ذلك.
        """
        return self.lexicon.save(file_path)

    def _map_arabic_type_to_english(self, arabic_type: str) -> str:
        """
        تحويل نوع الكلمة من العربية إلى الإنجليزية.

        المعاملات:
            arabic_type: نوع الكلمة بالعربية ('اسم'، 'فعل'، 'حرف').

        النتيجة:
            نوع الكلمة بالإنجليزية ('noun', 'verb', 'particle').
        """
        type_mapping = {
            "اسم": "noun",
            "فعل": "verb",
            "حرف": "particle",
            "صفة": "adjective",
            "ضمير": "pronoun",
            "ظرف": "adverb",
            "جملة": "phrase",
        }

        return type_mapping.get(arabic_type, arabic_type)
