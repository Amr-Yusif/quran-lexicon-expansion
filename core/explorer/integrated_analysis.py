#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
نظام التحليل المتكامل للنصوص القرآنية والإسلامية
يجمع بين البحث الدلالي والتحليل اللغوي واكتشاف الأنماط
"""

import logging
import json
import os
import re
from pathlib import Path
from typing import List, Dict, Any, Union, Tuple
import pandas as pd
import matplotlib.pyplot as plt
from tqdm import tqdm

# استيراد المكونات الرئيسية للنظام
from semantic_search import EnhancedSemanticSearch
from linguistic_analysis import IslamicTextAnalyzer
from pattern_discovery import PatternDiscovery

# إعداد التسجيل
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class IntegratedQuranAnalysis:
    """نظام متكامل لتحليل النصوص القرآنية والإسلامية"""
    
    def __init__(self, embedding_model="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"):
        """
        تهيئة نظام التحليل المتكامل
        
        Args:
            embedding_model: نموذج التضمين المستخدم للتحليل الدلالي
        """
        logger.info("تهيئة نظام التحليل المتكامل للنصوص القرآنية والإسلامية...")
        
        # تهيئة المكونات الأساسية
        self.search_engine = EnhancedSemanticSearch(model_name=embedding_model)
        self.text_analyzer = IslamicTextAnalyzer()
        self.pattern_discoverer = PatternDiscovery(model_name=embedding_model)
        
        # إنشاء مجلدات الإخراج
        self.output_dir = Path("analysis_results")
        self.output_dir.mkdir(exist_ok=True)
        
        # إنشاء قاموس للمعلومات المكتشفة
        self.discoveries = {
            "linguistic_patterns": [],
            "semantic_relationships": [],
            "numerical_patterns": [],
            "thematic_clusters": []
        }
        
        logger.info("تم تهيئة نظام التحليل المتكامل بنجاح")
    
    def load_text_from_file(self, file_path: str) -> str:
        """
        تحميل نص من ملف
        
        Args:
            file_path: مسار الملف
            
        Returns:
            النص المحمل من الملف
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            logger.error(f"الملف غير موجود: {file_path}")
            return ""
        
        logger.info(f"تحميل النص من الملف: {file_path}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except Exception as e:
            logger.error(f"خطأ في قراءة الملف: {e}")
            return ""
    
    def process_text(self, text: str, document_info: Dict = None) -> Dict:
        """
        معالجة نص وإجراء تحليل شامل له
        
        Args:
            text: النص المراد تحليله
            document_info: معلومات إضافية عن المستند (اختياري)
            
        Returns:
            نتائج التحليل
        """
        if not text:
            logger.warning("النص فارغ، لا يمكن إجراء التحليل")
            return {}
        
        logger.info("بدء تحليل النص...")
        results = {}
        
        # إضافة معلومات المستند إذا كانت متوفرة
        if document_info:
            results["document_info"] = document_info
        
        # استخراج الجمل من النص
        sentences = re.split(r'[.،؛!؟\n]', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        # 1. التحليل اللغوي
        logger.info("إجراء التحليل اللغوي...")
        results["linguistic_analysis"] = {
            "morphology": self.text_analyzer.analyze_morphology(text),
            "syntax": self.text_analyzer.analyze_syntax(text),
            "rhetoric": self.text_analyzer.analyze_rhetoric(text)
        }
        
        # 2. تحليل المعاني والمفاهيم
        logger.info("إجراء التحليل الدلالي...")
        # نخزن النص للبحث عنه لاحقاً
        if document_info:
            doc_id = self.search_engine.index_document({
                "text": text,
                **document_info
            })
            results["document_id"] = doc_id
        
        # 3. اكتشاف الأنماط
        logger.info("البحث عن الأنماط في النص...")
        results["patterns"] = {
            "word_patterns": self.pattern_discoverer.find_word_patterns([text]),
            "sequence_patterns": self.pattern_discoverer.find_sequence_patterns([sentences])
        }
        
        # 4. استخراج المفاهيم والموضوعات
        logger.info("تحليل الموضوعات والمفاهيم...")
        if len(sentences) > 3:  # نحتاج لعدد كافٍ من الجمل للتجميع
            results["thematic_analysis"] = self.pattern_discoverer.cluster_similar_texts(sentences)
        
        # 5. تحليل خاص بالنصوص القرآنية (إذا كان النص قرآنياً)
        if document_info and document_info.get("type") == "quran":
            logger.info("إجراء تحليل خاص بالنص القرآني...")
            results["quran_specific"] = self._analyze_quranic_text(text)
        
        logger.info("اكتمال تحليل النص بنجاح")
        return results
    
    def _analyze_quranic_text(self, text: str) -> Dict:
        """
        تحليل خاص بالنصوص القرآنية
        
        Args:
            text: النص القرآني
            
        Returns:
            نتائج التحليل الخاص بالقرآن
        """
        # تحليل التكرار العددي
        numerical_analysis = self._analyze_numerical_patterns(text)
        
        # تحليل البلاغة القرآنية بشكل موسّع
        rhetorical_analysis = self.text_analyzer.analyze_quranic_rhetoric(text) if hasattr(self.text_analyzer, 'analyze_quranic_rhetoric') else {}
        
        return {
            "numerical_analysis": numerical_analysis,
            "rhetorical_analysis": rhetorical_analysis
        }
    
    def _analyze_numerical_patterns(self, text: str) -> Dict:
        """
        تحليل الأنماط العددية في النص
        
        Args:
            text: النص المراد تحليله
            
        Returns:
            الأنماط العددية المكتشفة
        """
        patterns = {}
        
        # 1. حساب تكرار الحروف
        letter_counts = {}
        for letter in text:
            if letter.strip() and letter not in ".,;:\"'[]{}()!؟،؛/\\ \n\t":
                letter_counts[letter] = letter_counts.get(letter, 0) + 1
        
        patterns["letter_counts"] = letter_counts
        
        # 2. حساب تكرار الكلمات المهمة
        words = re.findall(r'\b\w+\b', text)
        word_counts = {}
        for word in words:
            if len(word) > 2:  # استبعاد الكلمات القصيرة جداً
                word_counts[word] = word_counts.get(word, 0) + 1
        
        patterns["word_counts"] = {k: v for k, v in sorted(word_counts.items(), key=lambda item: item[1], reverse=True)[:20]}
        
        # 3. البحث عن أنماط عددية متقدمة (يمكن تطويرها لاحقاً)
        # مثال: البحث عن الكلمات التي تتكرر بنفس العدد
        same_frequency_words = {}
        for freq, words_group in pd.Series(word_counts).groupby(lambda x: word_counts[x]).items():
            if len(words_group) > 1 and freq > 1:  # كلمات متعددة بنفس التكرار
                same_frequency_words[freq] = words_group.index.tolist()
        
        patterns["same_frequency_words"] = same_frequency_words
        
        return patterns
    
    def search_for_concept(self, concept: str, limit: int = 10) -> List[Dict]:
        """
        البحث عن مفهوم في النصوص المفهرسة
        
        Args:
            concept: المفهوم المراد البحث عنه
            limit: عدد النتائج المطلوبة
            
        Returns:
            قائمة بالنصوص ذات الصلة بالمفهوم
        """
        logger.info(f"البحث عن مفهوم: {concept}")
        return self.search_engine.conceptual_search(concept, limit=limit)
    
    def discover_relationships(self, concepts: List[str]) -> Dict:
        """
        اكتشاف العلاقات بين المفاهيم المختلفة
        
        Args:
            concepts: قائمة بالمفاهيم المراد تحليل العلاقات بينها
            
        Returns:
            العلاقات المكتشفة بين المفاهيم
        """
        logger.info(f"تحليل العلاقات بين {len(concepts)} مفهوم")
        
        # البحث عن كل مفهوم
        concept_results = {}
        for concept in concepts:
            results = self.search_engine.conceptual_search(concept, limit=5)
            concept_results[concept] = results
        
        # بناء الكيانات والعلاقات
        entities = []
        relationships = []
        
        # إضافة المفاهيم الرئيسية كعقد
        for i, concept in enumerate(concepts):
            entities.append({
                "id": f"concept_{i}",
                "type": "concept",
                "name": concept,
                "attributes": {}
            })
        
        # إيجاد العلاقات بين المفاهيم
        for i, concept1 in enumerate(concepts):
            for j, concept2 in enumerate(concepts):
                if i < j:  # لتجنب التكرار
                    # حساب مدى الترابط بين المفهومين
                    similarity = self.search_engine.calculate_similarity(concept1, concept2)
                    
                    if similarity > 0.4:  # عتبة التشابه
                        relationships.append({
                            "source": f"concept_{i}",
                            "target": f"concept_{j}",
                            "type": "related",
                            "weight": float(similarity),
                            "attributes": {"similarity": float(similarity)}
                        })
        
        # بناء رسم بياني للمعرفة
        graph = self.pattern_discoverer.build_knowledge_graph(entities, relationships)
        
        # تصور العلاقات بين المفاهيم
        self.pattern_discoverer.visualize_knowledge_graph("concept_relationships.png")
        
        # إضافة الاكتشاف إلى قائمة الاكتشافات
        discovery = {
            "type": "semantic_relationship",
            "concepts": concepts,
            "relationship_count": len(relationships),
            "graph_visualization": "concept_relationships.png"
        }
        self.discoveries["semantic_relationships"].append(discovery)
        
        return {
            "concepts": concepts,
            "entities": entities,
            "relationships": relationships,
            "visualization": "concept_relationships.png"
        }
    
    def analyze_surah(self, surah_text: str, surah_info: Dict) -> Dict:
        """
        تحليل شامل لسورة قرآنية
        
        Args:
            surah_text: نص السورة
            surah_info: معلومات السورة
            
        Returns:
            نتائج التحليل الشامل للسورة
        """
        logger.info(f"تحليل سورة: {surah_info.get('name', 'غير معروف')}")
        
        # إضافة معلومات نوع المستند
        surah_info["type"] = "quran"
        
        # إجراء التحليل الشامل
        results = self.process_text(surah_text, surah_info)
        
        # حفظ نتائج التحليل
        output_file = self.output_dir / f"surah_{surah_info.get('number', 'unknown')}_analysis.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        logger.info(f"تم حفظ نتائج تحليل السورة في: {output_file}")
        return results
    
    def batch_analyze_texts(self, texts: List[Dict[str, Union[str, Dict]]]) -> List[Dict]:
        """
        تحليل مجموعة من النصوص
        
        Args:
            texts: قائمة من النصوص مع معلوماتها
            
        Returns:
            نتائج التحليل لجميع النصوص
        """
        logger.info(f"تحليل دفعة من {len(texts)} نص")
        
        results = []
        for text_item in tqdm(texts, desc="معالجة النصوص"):
            text = text_item.get("text", "")
            info = text_item.get("info", {})
            
            if text:
                result = self.process_text(text, info)
                results.append(result)
            else:
                logger.warning("تم تخطي نص فارغ")
        
        return results
    
    def find_correlations(self, analysis_results: List[Dict]) -> Dict:
        """
        البحث عن الارتباطات بين نتائج التحليل المختلفة
        
        Args:
            analysis_results: قائمة بنتائج التحليل
            
        Returns:
            الارتباطات المكتشفة
        """
        logger.info("البحث عن الارتباطات في نتائج التحليل...")
        
        # تحضير البيانات للتحليل
        data = []
        for result in analysis_results:
            # استخراج سمات مختلفة من نتائج التحليل
            item = {}
            
            # معلومات المستند
            if "document_info" in result:
                item.update(result["document_info"])
            
            # مقاييس التحليل اللغوي
            if "linguistic_analysis" in result:
                ling = result["linguistic_analysis"]
                if "morphology" in ling and ling["morphology"]:
                    item["noun_count"] = sum(1 for m in ling["morphology"] if m.get("pos") == "noun")
                    item["verb_count"] = sum(1 for m in ling["morphology"] if m.get("pos") == "verb")
                
                if "rhetoric" in ling:
                    for pattern, count in ling["rhetoric"].get("pattern_counts", {}).items():
                        item[f"rhetoric_{pattern}"] = count
            
            # مقاييس الأنماط المكتشفة
            if "patterns" in result and "word_patterns" in result["patterns"]:
                word_patterns = result["patterns"]["word_patterns"].get("word_patterns", [])
                item["significant_patterns"] = len(word_patterns)
            
            # إضافة إلى البيانات إذا كانت غير فارغة
            if len(item) > 3:  # نحتاج على الأقل لبعض السمات للتحليل
                data.append(item)
        
        if not data:
            logger.warning("لا توجد بيانات كافية للتحليل")
            return {}
        
        # استخراج السمات المشتركة للتحليل
        features = list(set().union(*[set(d.keys()) for d in data]))
        features = [f for f in features if all(isinstance(d.get(f, 0), (int, float)) for d in data)]
        
        # اكتشاف الارتباطات
        correlations = self.pattern_discoverer.discover_correlations(data, features)
        
        # إضافة الاكتشاف إلى قائمة الاكتشافات
        if correlations.get("strong_correlations"):
            discovery = {
                "type": "statistical_correlation",
                "correlations": correlations.get("strong_correlations"),
                "data_points": len(data)
            }
            self.discoveries["numerical_patterns"].append(discovery)
        
        return correlations
    
    def report_discoveries(self) -> Dict:
        """
        تقرير بالاكتشافات المهمة من تحليل النصوص
        
        Returns:
            الاكتشافات المهمة
        """
        logger.info("إعداد تقرير بالاكتشافات المهمة...")
        
        # ترتيب الاكتشافات حسب النوع
        report = {
            "summary": {
                "total_discoveries": sum(len(v) for v in self.discoveries.values()),
                "discovery_types": {k: len(v) for k, v in self.discoveries.items()}
            },
            "detailed_discoveries": self.discoveries
        }
        
        # حفظ التقرير
        output_file = self.output_dir / "discoveries_report.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        logger.info(f"تم حفظ تقرير الاكتشافات في: {output_file}")
        return report


# مثال للاستخدام
if __name__ == "__main__":
    # إنشاء نظام التحليل المتكامل
    analyzer = IntegratedQuranAnalysis()
    
    # تحليل سورة الفاتحة كمثال
    fatiha_text = """بسم الله الرحمن الرحيم
الحمد لله رب العالمين
الرحمن الرحيم
مالك يوم الدين
إياك نعبد وإياك نستعين
اهدنا الصراط المستقيم
صراط الذين أنعمت عليهم غير المغضوب عليهم ولا الضالين"""

    fatiha_info = {
        "name": "الفاتحة",
        "number": 1,
        "verses": 7,
        "type": "مكية"
    }
    
    # تحليل السورة
    results = analyzer.analyze_surah(fatiha_text, fatiha_info)
    
    # البحث عن مفاهيم مرتبطة
    concepts = ["الهداية", "العبادة", "الرحمة"]
    relationships = analyzer.discover_relationships(concepts)
    
    # طباعة تقرير الاكتشافات
    print(analyzer.report_discoveries())
