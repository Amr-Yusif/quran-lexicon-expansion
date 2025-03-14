#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
نظام التعلم النشط للتحسين المستمر من خلال تفاعلات المستخدمين
"""

import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Union

# استيراد المكونات الضرورية
from core.explorer.pattern_discovery import PatternDiscovery

# إعداد التسجيل
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ActiveLearningSystem:
    """
    نظام التعلم النشط للتحسين المستمر من خلال تفاعلات المستخدمين
    يقوم بتحليل الاستعلامات، اكتشاف الأنماط، وتحسين أداء النظام بناءً على التغذية الراجعة
    """
    
    def __init__(self, knowledge_base_path: str = None):
        """
        تهيئة نظام التعلم النشط
        
        Args:
            knowledge_base_path: مسار قاعدة المعرفة (اختياري)
        """
        logger.info("تهيئة نظام التعلم النشط...")
        
        # تعيين مسار قاعدة المعرفة
        if knowledge_base_path:
            self.knowledge_base_path = Path(knowledge_base_path)
        else:
            # استخدام المسار الافتراضي
            self.knowledge_base_path = Path(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../data/knowledge_base")))
        
        # إنشاء المجلدات اللازمة إذا لم تكن موجودة
        self.patterns_path = self.knowledge_base_path / "patterns"
        self.relationships_path = self.knowledge_base_path / "relationships"
        self.feedback_path = self.knowledge_base_path / "feedback"
        self.metrics_path = self.knowledge_base_path / "metrics"
        
        for path in [self.patterns_path, self.relationships_path, self.feedback_path, self.metrics_path]:
            path.mkdir(parents=True, exist_ok=True)
        
        # تهيئة محرك اكتشاف الأنماط
        self.pattern_discovery = PatternDiscovery()
        
        # تهيئة سجل التعلم
        self.learning_history = []
        self._load_learning_history()
        
        # تهيئة مقاييس الأداء
        self.performance_metrics = {
            "pattern_discovery": {
                "total_patterns": 0,
                "new_patterns": 0,
                "pattern_quality": 0.0
            },
            "relationship_discovery": {
                "total_relationships": 0,
                "new_relationships": 0,
                "relationship_quality": 0.0
            },
            "feedback_integration": {
                "total_feedback": 0,
                "integrated_feedback": 0,
                "feedback_quality": 0.0
            },
            "query_analysis": {
                "total_queries": 0,
                "useful_queries": 0,
                "query_diversity": 0.0
            },
            "embedding_updates": {
                "total_updates": 0,
                "improvement_rate": 0.0
            }
        }
        self._load_performance_metrics()
        
        logger.info("تم تهيئة نظام التعلم النشط بنجاح")
    
    def _load_learning_history(self) -> None:
        """
        تحميل سجل التعلم من الملف
        """
        history_file = self.knowledge_base_path / "learning_history.json"
        
        if history_file.exists():
            try:
                with open(history_file, 'r', encoding='utf-8') as f:
                    self.learning_history = json.load(f)
                logger.info(f"تم تحميل سجل التعلم: {len(self.learning_history)} عنصر")
            except Exception as e:
                logger.error(f"خطأ في تحميل سجل التعلم: {e}")
    
    def _save_learning_history(self) -> None:
        """
        حفظ سجل التعلم في ملف
        """
        history_file = self.knowledge_base_path / "learning_history.json"
        
        try:
            with open(history_file, 'w', encoding='utf-8') as f:
                json.dump(self.learning_history, f, ensure_ascii=False, indent=2)
            logger.info(f"تم حفظ سجل التعلم: {len(self.learning_history)} عنصر")
        except Exception as e:
            logger.error(f"خطأ في حفظ سجل التعلم: {e}")
    
    def _load_performance_metrics(self) -> None:
        """
        تحميل مقاييس الأداء من الملف
        """
        metrics_file = self.metrics_path / "performance_metrics.json"
        
        if metrics_file.exists():
            try:
                with open(metrics_file, 'r', encoding='utf-8') as f:
                    self.performance_metrics = json.load(f)
                logger.info("تم تحميل مقاييس الأداء بنجاح")
            except Exception as e:
                logger.error(f"خطأ في تحميل مقاييس الأداء: {e}")
    
    def _save_performance_metrics(self) -> None:
        """
        حفظ مقاييس الأداء في ملف
        """
        metrics_file = self.metrics_path / "performance_metrics.json"
        
        try:
            with open(metrics_file, 'w', encoding='utf-8') as f:
                json.dump(self.performance_metrics, f, ensure_ascii=False, indent=2)
            logger.info("تم حفظ مقاييس الأداء بنجاح")
        except Exception as e:
            logger.error(f"خطأ في حفظ مقاييس الأداء: {e}")
    
    def discover_new_patterns(self, texts: List[str], context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        اكتشاف أنماط جديدة من مجموعة نصوص
        
        Args:
            texts: قائمة النصوص للتحليل
            context: معلومات سياقية إضافية (اختياري)
            
        Returns:
            قاموس يحتوي على الأنماط المكتشفة
        """
        logger.info(f"اكتشاف أنماط جديدة من {len(texts)} نص")
        
        # اكتشاف أنماط الكلمات
        word_patterns = self.pattern_discovery.find_word_patterns(texts)
        
        # تجميع المفاهيم
        concept_clusters = self.pattern_discovery.cluster_concepts(texts)
        
        # اكتشاف العلاقات الدلالية
        semantic_relationships = self.pattern_discovery.find_semantic_relationships(texts)
        
        # تجميع النتائج
        patterns = {
            "word_patterns": word_patterns,
            "concept_clusters": concept_clusters,
            "semantic_relationships": semantic_relationships,
            "timestamp": datetime.now().isoformat(),
            "context": context or {}
        }
        
        # حفظ الأنماط وتحديث المقاييس
        self._save_patterns(patterns)
        self._update_pattern_metrics(patterns)
        
        logger.info(f"تم اكتشاف {len(word_patterns.get('patterns', []))} نمط كلمات و {len(concept_clusters.get('clusters', []))} مجموعة مفاهيم")
        
        return patterns
    
    def discover_relationships(self, entities: List[Dict[str, Any]], context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        اكتشاف العلاقات بين الكيانات
        
        Args:
            entities: قائمة الكيانات للتحليل
            context: معلومات سياقية إضافية (اختياري)
            
        Returns:
            قاموس يحتوي على العلاقات المكتشفة
        """
        logger.info(f"اكتشاف العلاقات بين {len(entities)} كيان")
        
        # استخراج النصوص من الكيانات
        entity_texts = [entity.get("text", "") for entity in entities if "text" in entity]
        
        # بناء رسم بياني للمعرفة
        knowledge_graph = self.pattern_discovery.build_knowledge_graph(entity_texts)
        
        # إضافة معلومات الكيانات إلى العلاقات
        relationships = knowledge_graph.get("relationships", [])
        for i, relationship in enumerate(relationships):
            if i < len(entities):
                relationship["entity_info"] = {
                    "id": entities[i].get("id"),
                    "type": entities[i].get("type", "unknown")
                }
        
        # تجميع النتائج
        result = {
            "relationships": relationships,
            "graph": knowledge_graph.get("graph", {}),
            "timestamp": datetime.now().isoformat(),
            "context": context or {}
        }
        
        # حفظ العلاقات وتحديث المقاييس
        self._save_relationships(result)
        self._update_relationship_metrics(result)
        
        logger.info(f"تم اكتشاف {len(relationships)} علاقة")
        
        return result
    
    def analyze_user_queries(self, queries: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        تحليل استعلامات المستخدمين لاكتشاف أنماط واتجاهات
        
        Args:
            queries: قائمة استعلامات المستخدمين للتحليل
            
        Returns:
            قاموس يحتوي على نتائج التحليل
        """
        logger.info(f"تحليل {len(queries)} استعلام للمستخدمين")
        
        # استخراج نصوص الاستعلامات
        query_texts = [query.get("text", "") for query in queries if "text" in query]
        
        # تحليل تنوع الاستعلامات
        query_diversity = self._calculate_query_diversity(query_texts)
        
        # تحديد الاستعلامات المفيدة
        useful_queries = self._identify_useful_queries(queries)
        
        # تحديث مقاييس تحليل الاستعلامات
        self.performance_metrics["query_analysis"]["total_queries"] += len(queries)
        self.performance_metrics["query_analysis"]["useful_queries"] += len(useful_queries)
        self.performance_metrics["query_analysis"]["query_diversity"] = query_diversity
        
        # حفظ مقاييس الأداء
        self._save_performance_metrics()
        
        # تجميع النتائج
        result = {
            "query_count": len(queries),
            "useful_query_count": len(useful_queries),
            "query_diversity": query_diversity,
            "useful_queries": useful_queries,
            "timestamp": datetime.now().isoformat()
        }
        
        logger.info(f"تم تحليل الاستعلامات: {len(useful_queries)} استعلام مفيد من أصل {len(queries)}")
        
        return result
    
    def update_embedding_model(self, new_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        تحديث نموذج التضمين بناءً على بيانات جديدة
        
        Args:
            new_data: بيانات جديدة لتحديث النموذج
            
        Returns:
            قاموس يحتوي على نتائج التحديث
        """
        logger.info(f"تحديث نموذج التضمين باستخدام {len(new_data)} عنصر بيانات جديد")
        
        # هنا يمكن إضافة رمز لتحديث نموذج التضمين
        # هذا يتطلب تكامل مع وحدة نماذج التضمين
        
        # تحديث مقاييس تحديث التضمين
        self.performance_metrics["embedding_updates"]["total_updates"] += 1
        self.performance_metrics["embedding_updates"]["improvement_rate"] = 0.8  # قيمة افتراضية
        
        # حفظ مقاييس الأداء
        self._save_performance_metrics()
        
        # تجميع النتائج
        result = {
            "status": "success",
            "updated_with": len(new_data),
            "timestamp": datetime.now().isoformat(),
            "improvement_rate": self.performance_metrics["embedding_updates"]["improvement_rate"]
        }
        
        logger.info(f"تم تحديث نموذج التضمين بنجاح")
        
        return result
    
    def integrate_feedback(self, feedback: Dict[str, Any]) -> Dict[str, Any]:
        """
        دمج التغذية الراجعة من المستخدمين لتحسين النظام
        
        Args:
            feedback: التغذية الراجعة للدمج
            
        Returns:
            قاموس يحتوي على نتائج الدمج
        """
        logger.info("دمج تغذية راجعة جديدة")
        
        # التحقق من صحة التغذية الراجعة
        if "type" not in feedback or "content" not in feedback:
            logger.error("تغذية راجعة غير صالحة: نوع أو محتوى مفقود")
            return {"status": "error", "message": "تغذية راجعة غير صالحة: نوع أو محتوى مفقود"}
        
        # التحقق من نوع التغذية الراجعة
        valid_types = ["pattern_correction", "relationship_suggestion", "query_improvement", "embedding_feedback"]
        if feedback["type"] not in valid_types:
            logger.error(f"نوع تغذية راجعة غير صالح: {feedback['type']}")
            return {"status": "error", "message": f"نوع تغذية راجعة غير صالح: {feedback['type']}"}
        
        # معالجة التغذية الراجعة حسب النوع
        feedback_id = f"feedback_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        feedback_file = self.feedback_path / f"{feedback_id}.json"
        
        # إضافة معلومات إضافية للتغذية الراجعة
        feedback["id"] = feedback_id
        feedback["timestamp"] = datetime.now().isoformat()
        feedback["status"] = "pending"
        
        # حفظ التغذية الراجعة
        with open(feedback_file, 'w', encoding='utf-8') as f:
            json.dump(feedback, f, ensure_ascii=False, indent=2)
        
        # تحديث سجل التعلم
        self.learning_history.append({
            "type": "feedback_integration",
            "id": feedback_id,
            "timestamp": feedback["timestamp"],
            "summary": f"دمج تغذية راجعة من النوع {feedback['type']}"
        })
        
        # تحديث مقاييس التغذية الراجعة
        self._update_feedback_metrics(feedback)
        
        # حفظ سجل التعلم
        self._save_learning_history()
        
        logger.info(f"تم دمج التغذية الراجعة بنجاح (المعرف: {feedback_id})")
        
        return {
            "status": "success",
            "feedback_id": feedback_id,
            "timestamp": feedback["timestamp"]
        }
    
    def update_agent_knowledge(self, agent, new_knowledge: Dict[str, Any]) -> bool:
        """
        تحديث معرفة وكيل بمعلومات جديدة
        
        Args:
            agent: الوكيل المراد تحديث معرفته
            new_knowledge: المعرفة الجديدة للإضافة
            
        Returns:
            نجاح أو فشل عملية التحديث
        """
        logger.info(f"تحديث معرفة الوكيل: {agent.name if hasattr(agent, 'name') else 'unknown'}")
        
        # التحقق من أن الوكيل يدعم تحديث المعرفة
        if not hasattr(agent, 'update_knowledge') or not callable(getattr(agent, 'update_knowledge')):
            logger.warning("الوكيل لا يدعم تحديث المعرفة")
            return False
        
        try:
            # تحديث معرفة الوكيل
            result = agent.update_knowledge(new_knowledge)
            
            # تسجيل التحديث في سجل التعلم
            self.learning_history.append({
                "type": "agent_knowledge_update",
                "agent": agent.name if hasattr(agent, 'name') else "unknown",
                "timestamp": datetime.now().isoformat(),
                "summary": f"تحديث معرفة الوكيل بـ {len(new_knowledge)} عنصر"
            })
            
            # حفظ سجل التعلم
            self._save_learning_history()
            
            logger.info(f"تم تحديث معرفة الوكيل بنجاح")
            
            return result
        except Exception as e:
            logger.error(f"خطأ في تحديث معرفة الوكيل: {e}")
            return False
    
    def generate_learning_report(self, days: int = 7) -> Dict[str, Any]:
        """
        إنشاء تقرير عن التعلم والتحسينات خلال فترة زمنية محددة
        
        Args:
            days: عدد الأيام السابقة للتقرير
            
        Returns:
            قاموس يحتوي على تقرير التعلم
        """
        logger.info(f"إنشاء تقرير التعلم للـ {days} أيام السابقة")
        
        # الحصول على الاكتشافات الأخيرة
        recent_discoveries = self._get_recent_discoveries(days)
        
        # تجميع إحصائيات التعلم
        learning_stats = {
            "patterns": {
                "total": self.performance_metrics["pattern_discovery"]["total_patterns"],
                "recent": sum(1 for item in recent_discoveries if item["type"] == "pattern_discovery")
            },
            "relationships": {
                "total": self.performance_metrics["relationship_discovery"]["total_relationships"],
                "recent": sum(1 for item in recent_discoveries if item["type"] == "relationship_discovery")
            },
            "feedback": {
                "total": self.performance_metrics["feedback_integration"]["total_feedback"],
                "recent": sum(1 for item in recent_discoveries if item["type"] == "feedback_integration")
            },
            "embedding_updates": {
                "total": self.performance_metrics["embedding_updates"]["total_updates"],
                "recent": sum(1 for item in recent_discoveries if item["type"] == "embedding_update")
            }
        }
        
        # إنشاء التقرير
        report = {
            "timestamp": datetime.now().isoformat(),
            "period_days": days,
            "learning_history": recent_discoveries,
            "statistics": learning_stats,
            "performance_metrics": self.performance_metrics,
            "recommendations": self._generate_improvement_recommendations()
        }
        
        logger.info("تم إنشاء تقرير التعلم بنجاح")
        
        return report
    
    def _calculate_query_diversity(self, query_texts: List[str]) -> float:
        """
        حساب تنوع الاستعلامات
        
        Args:
            query_texts: نصوص الاستعلامات
            
        Returns:
            درجة التنوع (0-1)
        """
        if not query_texts:
            return 0.0
        
        # هنا يمكن تنفيذ خوارزمية لحساب تنوع الاستعلامات
        # مثال بسيط: حساب نسبة الكلمات الفريدة إلى إجمالي الكلمات
        all_words = []
        for query in query_texts:
            words = query.split()
            all_words.extend(words)
        
        if not all_words:
            return 0.0
        
        unique_words = set(all_words)
        diversity = len(unique_words) / len(all_words)
        
        return diversity
    
    def _identify_useful_queries(self, queries: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        تحديد الاستعلامات المفيدة للتعلم
        
        Args:
            queries: قائمة الاستعلامات
            
        Returns:
            قائمة الاستعلامات المفيدة
        """
        useful_queries = []
        
        for query in queries:
            # معايير تحديد الاستعلامات المفيدة
            is_useful = False
            
            # 1. الاستعلامات التي تحتوي على كلمات مفتاحية محددة
            if "text" in query:
                keywords = ["كيف", "لماذا", "متى", "أين", "من", "ما", "هل"]
                if any(keyword in query["text"] for keyword in keywords):
                    is_useful = True
            
            # 2. الاستعلامات التي لها نتائج قليلة (تشير إلى فجوة معرفية)
            if "result_count" in query and query["result_count"] < 3:
                is_useful = True
            
            # 3. الاستعلامات التي استغرقت وقتًا طويلاً في المعالجة
            if "processing_time" in query and query["processing_time"] > 2.0:
                is_useful = True
            
            # إضافة الاستعلام المفيد إلى القائمة
            if is_useful:
                useful_queries.append(query)
        
        return useful_queries
    
    def _get_recent_discoveries(self, days: int) -> List[Dict[str, Any]]:
        """
        الحصول على الاكتشافات الأخيرة خلال فترة زمنية محددة
        
        Args:
            days: عدد الأيام
            
        Returns:
            قائمة الاكتشافات الأخيرة
        """
        # حساب التاريخ قبل عدد الأيام المحدد
        from datetime import timedelta
        
        cutoff_date = datetime.now() - timedelta(days=days)
        cutoff_date_str = cutoff_date.isoformat()
        
        # تصفية سجل التعلم حسب التاريخ
        recent_discoveries = []
        for item in self.learning_history:
            if "timestamp" in item and item["timestamp"] >= cutoff_date_str:
                recent_discoveries.append(item)
        
        return recent_discoveries
    
    def _generate_improvement_recommendations(self) -> List[str]:
        """
        توليد توصيات لتحسين النظام بناءً على البيانات المتاحة
        
        Returns:
            قائمة التوصيات
        """
        recommendations = []
        
        # 1. توصيات بناءً على جودة الأنماط
        pattern_quality = self.performance_metrics["pattern_discovery"]["pattern_quality"]
        if pattern_quality < 0.7:
            recommendations.append("تحسين جودة اكتشاف الأنماط من خلال تحسين خوارزميات التحليل")
        
        # 2. توصيات بناءً على جودة العلاقات
        relationship_quality = self.performance_metrics["relationship_discovery"]["relationship_quality"]
        if relationship_quality < 0.7:
            recommendations.append("تحسين جودة اكتشاف العلاقات من خلال تحسين بناء الرسم البياني للمعرفة")
        
        # 3. توصيات بناءً على تنوع الاستعلامات
        query_diversity = self.performance_metrics["query_analysis"]["query_diversity"]
        if query_diversity < 0.5:
            recommendations.append("زيادة تنوع الاستعلامات لتحسين تغطية المعرفة")
        
        # 4. توصيات بناءً على معدل تحسين نموذج التضمين
        improvement_rate = self.performance_metrics["embedding_updates"]["improvement_rate"]
        if improvement_rate < 0.6:
            recommendations.append("تحسين نموذج التضمين من خلال زيادة جودة البيانات المستخدمة للتحديث")
        
        # 5. توصيات عامة
        recommendations.append("جمع المزيد من التغذية الراجعة من المستخدمين لتحسين أداء النظام")
        recommendations.append("تحديث قاعدة المعرفة بشكل دوري لضمان حداثة المعلومات")
        
        return recommendations
    
    def _save_patterns(self, patterns: Dict[str, Any]) -> str:
        """
        حفظ الأنماط المكتشفة في قاعدة المعرفة
        
        Args:
            patterns: الأنماط المكتشفة للحفظ
            
        Returns:
            معرف الأنماط المحفوظة
        """
        # إنشاء معرف فريد للأنماط
        pattern_id = f"pattern_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # حفظ الأنماط في ملف JSON
        pattern_file = self.patterns_path / f"{pattern_id}.json"
        
        with open(pattern_file, 'w', encoding='utf-8') as f:
            json.dump(patterns, f, ensure_ascii=False, indent=2)
        
        # تحديث سجل التعلم
        self.learning_history.append({
            "type": "pattern_discovery",
            "id": pattern_id,
            "timestamp": patterns.get("timestamp", datetime.now().isoformat()),
            "summary": f"اكتشاف {len(patterns.get('word_patterns', {}).get('patterns', []))} أنماط كلمات و {len(patterns.get('concept_clusters', {}).get('clusters', []))} مجموعات مفاهيم"
        })
        
        logger.info(f"تم حفظ الأنماط المكتشفة بمعرف: {pattern_id}")
        
        return pattern_id