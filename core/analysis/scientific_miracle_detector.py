"""
كشف المعجزات العلمية - تحليل النصوص الإسلامية لاكتشاف الإعجاز العلمي
"""

import re
from typing import List, Dict, Any, Optional, Tuple
import numpy as np
from pathlib import Path
import json
import os

# استيراد المكونات الضرورية من المشروع
from local_mem0_agent.core.utils.arabic_text_utils import ArabicTextProcessor
from local_mem0_agent.core.embeddings.embedding_models import ArabicEmbeddingModel
from local_mem0_agent.core.utils.config import get_config


class ScientificMiracleDetector:
    """
    كاشف المعجزات العلمية - يستخدم تقنيات معالجة اللغة الطبيعية وتعلم الآلة
    للكشف عن المعجزات العلمية في القرآن الكريم والكتب الإسلامية
    """

    # فئات المعجزات العلمية
    MIRACLE_CATEGORIES = {
        "astronomy": ["سماء", "نجم", "كوكب", "شمس", "قمر", "مجرة", "فضاء", "كون", "فلك"],
        "earth": ["أرض", "جبال", "بحر", "نهر", "محيط", "زلزال", "بركان", "صخور"],
        "biology": ["إنسان", "حيوان", "نبات", "خلية", "جنين", "نطفة", "علقة", "مضغة"],
        "physics": ["ضوء", "ظلمة", "موجة", "حرارة", "برودة", "جاذبية", "توازن", "حركة"],
        "chemistry": ["ماء", "هواء", "نار", "تراب", "حديد", "معدن", "تفاعل", "تركيب"],
        "medicine": ["شفاء", "مرض", "علاج", "قلب", "دماغ", "عصب", "دم", "عظم"],
        "mathematics": ["عدد", "حساب", "ميزان", "قياس", "نسبة", "تناسب", "إحصاء"],
    }

    def __init__(
        self,
        data_dir: Optional[str] = None,
        model_name: str = "paraphrase-multilingual-mpnet-base-v2",
    ):
        """
        تهيئة كاشف المعجزات العلمية

        Args:
            data_dir: مسار مجلد البيانات (اختياري)
            model_name: اسم نموذج التضمين
        """
        # تهيئة مدير التكوين
        self.config = get_config()

        # تعيين مسار البيانات
        if data_dir is None:
            self.data_dir = self.config.get_data_path("scientific_miracles")
        else:
            self.data_dir = Path(data_dir)
            self.data_dir.mkdir(parents=True, exist_ok=True)

        # تهيئة معالج النصوص العربية
        self.text_processor = ArabicTextProcessor

        # تهيئة نموذج التضمين
        self.embedding_model = ArabicEmbeddingModel(model_name)

        # تهيئة قاعدة المعرفة للمعجزات العلمية
        self.knowledge_base_file = self.data_dir / "scientific_miracles_kb.json"
        self.knowledge_base = self._load_knowledge_base()

        # تهيئة قاموس المصطلحات العلمية
        self.scientific_terms_file = self.data_dir / "scientific_terms.json"
        self.scientific_terms = self._load_scientific_terms()

        # تهيئة قاموس الاكتشافات العلمية
        self.discoveries_file = self.data_dir / "scientific_discoveries.json"
        self.discoveries = self._load_discoveries()

    def _load_knowledge_base(self) -> List[Dict[str, Any]]:
        """
        تحميل قاعدة معرفة المعجزات العلمية

        Returns:
            قائمة من المعجزات العلمية المخزنة
        """
        if self.knowledge_base_file.exists():
            try:
                with open(self.knowledge_base_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                print(f"خطأ في تحميل قاعدة المعرفة: {str(e)}")

        # إنشاء قاعدة معرفة فارغة إذا لم تكن موجودة
        return []

    def _save_knowledge_base(self) -> None:
        """حفظ قاعدة معرفة المعجزات العلمية"""
        try:
            with open(self.knowledge_base_file, "w", encoding="utf-8") as f:
                json.dump(self.knowledge_base, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"خطأ في حفظ قاعدة المعرفة: {str(e)}")

    def _load_scientific_terms(self) -> Dict[str, List[str]]:
        """
        تحميل قاموس المصطلحات العلمية

        Returns:
            قاموس من المصطلحات العلمية مقسمة حسب المجال
        """
        if self.scientific_terms_file.exists():
            try:
                with open(self.scientific_terms_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                print(f"خطأ في تحميل قاموس المصطلحات العلمية: {str(e)}")

        # إنشاء قاموس افتراضي إذا لم يكن موجودًا
        return self.MIRACLE_CATEGORIES

    def _load_discoveries(self) -> List[Dict[str, Any]]:
        """
        تحميل قاموس الاكتشافات العلمية

        Returns:
            قائمة من الاكتشافات العلمية الحديثة
        """
        if self.discoveries_file.exists():
            try:
                with open(self.discoveries_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                print(f"خطأ في تحميل قاموس الاكتشافات العلمية: {str(e)}")

        # إنشاء قاموس فارغ إذا لم يكن موجودًا
        return []

    def detect_scientific_content(self, text: str) -> Dict[str, Any]:
        """
        الكشف عن المحتوى العلمي في النص

        Args:
            text: النص المراد تحليله

        Returns:
            معلومات عن المحتوى العلمي المكتشف
        """
        # تنظيف النص
        clean_text = self.text_processor.normalize_arabic_text(text)

        # استخراج الآيات القرآنية
        verses = self.text_processor.extract_quran_verses(text)
        verse_references = self.text_processor.extract_verse_references(text)

        # الكشف عن الكلمات العلمية
        has_scientific_content, keywords = self.text_processor.detect_scientific_content(clean_text)

        # تحديد فئات العلوم
        categories = self._identify_scientific_categories(keywords)

        # تخمين المجال العلمي الرئيسي
        primary_category = self._get_primary_category(categories)

        # البحث عن مطابقات مع الاكتشافات العلمية المعروفة
        matched_discoveries = self._match_with_discoveries(clean_text)

        # البحث عن مطابقات مع المعجزات العلمية المعروفة
        similarity_matches = self._find_similar_miracles(clean_text)

        # إعداد نتيجة الكشف
        result = {
            "has_scientific_content": has_scientific_content,
            "scientific_keywords": keywords,
            "categories": categories,
            "primary_category": primary_category,
            "quran_verses": verses,
            "verse_references": verse_references,
            "matched_discoveries": matched_discoveries,
            "similar_miracles": similarity_matches[:5] if similarity_matches else [],
        }

        return result

    def _identify_scientific_categories(self, keywords: List[str]) -> Dict[str, int]:
        """
        تحديد فئات العلوم بناءً على الكلمات المفتاحية

        Args:
            keywords: قائمة الكلمات المفتاحية العلمية

        Returns:
            قاموس بفئات العلوم وعدد المطابقات
        """
        categories = {}

        for category, terms in self.scientific_terms.items():
            count = 0
            for keyword in keywords:
                if keyword in terms:
                    count += 1

            if count > 0:
                categories[category] = count

        return categories

    def _get_primary_category(self, categories: Dict[str, int]) -> Optional[str]:
        """
        تحديد الفئة العلمية الرئيسية

        Args:
            categories: قاموس بفئات العلوم وعدد المطابقات

        Returns:
            اسم الفئة الرئيسية أو None
        """
        if not categories:
            return None

        # اختيار الفئة ذات أكبر عدد مطابقات
        return max(categories.items(), key=lambda x: x[1])[0]

    def _match_with_discoveries(self, text: str) -> List[Dict[str, Any]]:
        """
        مطابقة النص مع الاكتشافات العلمية المعروفة

        Args:
            text: النص المراد مطابقته

        Returns:
            قائمة بالاكتشافات العلمية المطابقة
        """
        matches = []

        if not self.discoveries:
            return matches

        # تضمين النص
        text_embedding = self.embedding_model.embed_text(text)

        # حساب التشابه مع كل اكتشاف
        for discovery in self.discoveries:
            discovery_embedding = np.array(discovery.get("embedding", []))

            # تخطي الاكتشافات بدون تضمين
            if len(discovery_embedding) == 0:
                continue

            # حساب تشابه جيب التمام
            similarity = np.dot(text_embedding[0], discovery_embedding) / (
                np.linalg.norm(text_embedding[0]) * np.linalg.norm(discovery_embedding)
            )

            # إضافة المطابقات ذات التشابه العالي
            if similarity > 0.75:
                discovery_match = {
                    "id": discovery.get("id"),
                    "title": discovery.get("title"),
                    "description": discovery.get("description"),
                    "year": discovery.get("year"),
                    "category": discovery.get("category"),
                    "similarity": float(similarity),
                }
                matches.append(discovery_match)

        # ترتيب المطابقات حسب التشابه
        matches.sort(key=lambda x: x["similarity"], reverse=True)

        return matches[:5]  # إرجاع أفضل 5 مطابقات

    def _find_similar_miracles(self, text: str) -> List[Dict[str, Any]]:
        """
        البحث عن معجزات علمية مشابهة في قاعدة المعرفة

        Args:
            text: النص المراد البحث عنه

        Returns:
            قائمة بالمعجزات العلمية المشابهة
        """
        matches = []

        if not self.knowledge_base:
            return matches

        # تضمين النص
        text_embedding = self.embedding_model.embed_text(text)

        # حساب التشابه مع كل معجزة
        for miracle in self.knowledge_base:
            miracle_embedding = np.array(miracle.get("embedding", []))

            # تخطي المعجزات بدون تضمين
            if len(miracle_embedding) == 0:
                continue

            # حساب تشابه جيب التمام
            similarity = np.dot(text_embedding[0], miracle_embedding) / (
                np.linalg.norm(text_embedding[0]) * np.linalg.norm(miracle_embedding)
            )

            # إضافة المطابقات ذات التشابه العالي
            if similarity > 0.7:
                miracle_match = {
                    "id": miracle.get("id"),
                    "title": miracle.get("title"),
                    "description": miracle.get("description"),
                    "evidence": miracle.get("evidence"),
                    "category": miracle.get("category"),
                    "similarity": float(similarity),
                }
                matches.append(miracle_match)

        # ترتيب المطابقات حسب التشابه
        matches.sort(key=lambda x: x["similarity"], reverse=True)

        return matches

    def add_scientific_miracle(
        self,
        title: str,
        description: str,
        evidence: str,
        verses: List[Dict[str, Any]],
        category: str = None,
    ) -> Dict[str, Any]:
        """
        إضافة معجزة علمية جديدة إلى قاعدة المعرفة

        Args:
            title: عنوان المعجزة
            description: وصف المعجزة
            evidence: الدليل العلمي
            verses: الآيات القرآنية المرتبطة
            category: فئة المعجزة (اختياري)

        Returns:
            معلومات المعجزة العلمية المضافة
        """
        # تركيب النص الكامل للتضمين
        full_text = f"{title}. {description}. {evidence}"

        # كشف الفئة إذا لم يتم تحديدها
        if not category:
            _, keywords = self.text_processor.detect_scientific_content(full_text)
            categories = self._identify_scientific_categories(keywords)
            category = self._get_primary_category(categories) or "other"

        # إنشاء معرف فريد للمعجزة
        import uuid

        miracle_id = str(uuid.uuid4())

        # تضمين النص
        embedding = self.embedding_model.embed_text(full_text)[0].tolist()

        # إنشاء كائن المعجزة
        miracle = {
            "id": miracle_id,
            "title": title,
            "description": description,
            "evidence": evidence,
            "verses": verses,
            "category": category,
            "embedding": embedding,
            "created_at": self._get_timestamp(),
        }

        # إضافة المعجزة إلى قاعدة المعرفة
        self.knowledge_base.append(miracle)

        # حفظ قاعدة المعرفة
        self._save_knowledge_base()

        return miracle

    def add_scientific_discovery(
        self, title: str, description: str, year: int, source: str, category: str = None
    ) -> Dict[str, Any]:
        """
        إضافة اكتشاف علمي جديد إلى قاعدة البيانات

        Args:
            title: عنوان الاكتشاف
            description: وصف الاكتشاف
            year: سنة الاكتشاف
            source: مصدر المعلومات
            category: فئة الاكتشاف (اختياري)

        Returns:
            معلومات الاكتشاف العلمي المضاف
        """
        # تركيب النص الكامل للتضمين
        full_text = f"{title}. {description}. اكتشف في عام {year}."

        # كشف الفئة إذا لم يتم تحديدها
        if not category:
            _, keywords = self.text_processor.detect_scientific_content(full_text)
            categories = self._identify_scientific_categories(keywords)
            category = self._get_primary_category(categories) or "other"

        # إنشاء معرف فريد للاكتشاف
        import uuid

        discovery_id = str(uuid.uuid4())

        # تضمين النص
        embedding = self.embedding_model.embed_text(full_text)[0].tolist()

        # إنشاء كائن الاكتشاف
        discovery = {
            "id": discovery_id,
            "title": title,
            "description": description,
            "year": year,
            "source": source,
            "category": category,
            "embedding": embedding,
            "created_at": self._get_timestamp(),
        }

        # إضافة الاكتشاف إلى قاعدة البيانات
        self.discoveries.append(discovery)

        # حفظ قاعدة البيانات
        self._save_discoveries()

        return discovery

    def _save_discoveries(self) -> None:
        """حفظ قاعدة بيانات الاكتشافات العلمية"""
        try:
            with open(self.discoveries_file, "w", encoding="utf-8") as f:
                json.dump(self.discoveries, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"خطأ في حفظ قاعدة بيانات الاكتشافات: {str(e)}")

    def search_miracles(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        البحث في قاعدة معرفة المعجزات العلمية

        Args:
            query: استعلام البحث
            limit: الحد الأقصى لعدد النتائج

        Returns:
            قائمة بالمعجزات المطابقة
        """
        # تنظيف الاستعلام
        clean_query = self.text_processor.normalize_arabic_text(query)

        # تضمين الاستعلام
        query_embedding = self.embedding_model.embed_text(clean_query)

        # حساب التشابه مع كل معجزة
        results = []
        for miracle in self.knowledge_base:
            miracle_embedding = np.array(miracle.get("embedding", []))

            # تخطي المعجزات بدون تضمين
            if len(miracle_embedding) == 0:
                continue

            # حساب تشابه جيب التمام
            similarity = np.dot(query_embedding[0], miracle_embedding) / (
                np.linalg.norm(query_embedding[0]) * np.linalg.norm(miracle_embedding)
            )

            # إضافة المعجزة إلى النتائج
            result = {
                "id": miracle.get("id"),
                "title": miracle.get("title"),
                "description": miracle.get("description"),
                "evidence": miracle.get("evidence"),
                "category": miracle.get("category"),
                "similarity": float(similarity),
            }
            results.append(result)

        # ترتيب النتائج حسب التشابه
        results.sort(key=lambda x: x["similarity"], reverse=True)

        return results[:limit]

    def get_miracle_by_id(self, miracle_id: str) -> Optional[Dict[str, Any]]:
        """
        الحصول على معجزة علمية من قاعدة المعرفة بواسطة المعرف

        Args:
            miracle_id: معرف المعجزة

        Returns:
            معلومات المعجزة العلمية أو None
        """
        for miracle in self.knowledge_base:
            if miracle.get("id") == miracle_id:
                return miracle

        return None

    def _get_timestamp(self) -> str:
        """
        الحصول على الطابع الزمني الحالي

        Returns:
            الطابع الزمني بتنسيق ISO
        """
        from datetime import datetime

        return datetime.now().isoformat()

    def analyze_text_for_miracles(self, text: str) -> Dict[str, Any]:
        """
        تحليل النص للكشف عن المعجزات العلمية المحتملة

        Args:
            text: النص المراد تحليله

        Returns:
            نتائج التحليل
        """
        # تقسيم النص إلى فقرات
        paragraphs = [p.strip() for p in text.split("\n") if p.strip()]

        # تحليل كل فقرة
        miracle_candidates = []
        scientific_paragraphs = []

        for paragraph in paragraphs:
            # الكشف عن المحتوى العلمي
            result = self.detect_scientific_content(paragraph)

            # حفظ الفقرات ذات المحتوى العلمي
            if result["has_scientific_content"]:
                scientific_paragraphs.append({"text": paragraph, "detection_result": result})

                # إذا كانت تحتوي على آيات قرآنية، أضفها كمرشح محتمل
                if result["quran_verses"] or result["verse_references"]:
                    miracle_candidates.append(
                        {
                            "text": paragraph,
                            "detection_result": result,
                            "score": len(result["scientific_keywords"])
                            + len(result["quran_verses"]) * 2,
                        }
                    )

        # ترتيب المرشحين حسب الأهمية
        miracle_candidates.sort(key=lambda x: x["score"], reverse=True)

        return {
            "scientific_paragraphs": scientific_paragraphs,
            "miracle_candidates": miracle_candidates,
            "total_candidates": len(miracle_candidates),
            "total_scientific_paragraphs": len(scientific_paragraphs),
        }
