#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
نظام الاستكشاف المنظم للنصوص القرآنية والإسلامية
يوفر آليات منهجية لاستكشاف المفاهيم والعلاقات وتوليد الفرضيات
"""

import logging
import numpy as np
from typing import List, Dict, Any, Tuple, Optional, Set
from pathlib import Path
import json
import re

# إعداد التسجيل
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SystematicExplorer:
    """
    نظام الاستكشاف المنظم للنصوص القرآنية والإسلامية
    يتضمن ثلاثة مكونات رئيسية:
    1. استكشاف المفاهيم
    2. توليد الفرضيات
    3. التحقق من الفرضيات
    """
    
    def __init__(self):
        """
        تهيئة نظام الاستكشاف المنظم
        """
        logger.info("تهيئة نظام الاستكشاف المنظم...")
        
        # قواعد المعرفة والمفاهيم
        self.concepts = {}
        self.hypotheses = []
        self.evidence = {}
        self.concept_relations = []
        
        # إعدادات متقدمة
        self.config = {
            "min_evidence_threshold": 3,  # الحد الأدنى للأدلة المطلوبة لتأكيد فرضية
            "confidence_threshold": 0.7,  # عتبة الثقة للفرضيات
            "max_exploration_depth": 5,  # أقصى عمق للاستكشاف
            "enable_active_learning": True  # تمكين التعلم النشط
        }
        
        logger.info("تم تهيئة نظام الاستكشاف المنظم بنجاح")
    
    def load_concepts(self, concepts_file: str) -> bool:
        """
        تحميل المفاهيم من ملف
        
        Args:
            concepts_file: مسار ملف المفاهيم
            
        Returns:
            نجاح العملية
        """
        try:
            with open(concepts_file, 'r', encoding='utf-8') as f:
                self.concepts = json.load(f)
            logger.info(f"تم تحميل {len(self.concepts)} مفهوم بنجاح")
            return True
        except Exception as e:
            logger.error(f"خطأ في تحميل المفاهيم: {str(e)}")
            return False
    
    def explore_concept(self, concept_name: str, max_depth: int = None) -> Dict[str, Any]:
        """
        استكشاف مفهوم معين والمفاهيم المرتبطة به
        
        Args:
            concept_name: اسم المفهوم
            max_depth: أقصى عمق للاستكشاف
            
        Returns:
            نتائج الاستكشاف
        """
        if max_depth is None:
            max_depth = self.config["max_exploration_depth"]
        
        logger.info(f"استكشاف المفهوم: {concept_name} (العمق: {max_depth})")
        
        # التحقق من وجود المفهوم
        if concept_name not in self.concepts:
            logger.warning(f"المفهوم غير موجود: {concept_name}")
            return {"error": f"المفهوم غير موجود: {concept_name}"}
        
        # استكشاف المفهوم والمفاهيم المرتبطة
        explored_concepts = {}
        visited = set()
        
        self._explore_concept_recursive(concept_name, explored_concepts, visited, 0, max_depth)
        
        # إضافة العلاقات بين المفاهيم
        concept_relations = []
        for relation in self.concept_relations:
            if relation["source"] in explored_concepts and relation["target"] in explored_concepts:
                concept_relations.append(relation)
        
        return {
            "main_concept": concept_name,
            "explored_concepts": explored_concepts,
            "concept_relations": concept_relations
        }
    
    def _explore_concept_recursive(self, concept_name: str, explored_concepts: Dict[str, Any], 
                                  visited: Set[str], current_depth: int, max_depth: int) -> None:
        """
        استكشاف مفهوم بشكل متكرر
        
        Args:
            concept_name: اسم المفهوم
            explored_concepts: المفاهيم المستكشفة
            visited: المفاهيم التي تمت زيارتها
            current_depth: العمق الحالي
            max_depth: أقصى عمق للاستكشاف
        """
        # التحقق من الشروط
        if current_depth > max_depth or concept_name in visited or concept_name not in self.concepts:
            return
        
        # إضافة المفهوم إلى المفاهيم المستكشفة والمزارة
        visited.add(concept_name)
        explored_concepts[concept_name] = self.concepts[concept_name]
        
        # استكشاف المفاهيم المرتبطة
        related_concepts = self.concepts[concept_name].get("related_concepts", [])
        for related_concept in related_concepts:
            # إضافة العلاقة
            relation = {
                "source": concept_name,
                "target": related_concept,
                "type": "related"
            }
            if relation not in self.concept_relations:
                self.concept_relations.append(relation)
            
            # استكشاف المفهوم المرتبط
            self._explore_concept_recursive(related_concept, explored_concepts, visited, 
                                          current_depth + 1, max_depth)
    
    def generate_hypothesis(self, concept_name: str, related_concept: str = None) -> Dict[str, Any]:
        """
        توليد فرضية حول مفهوم أو علاقة بين مفهومين
        
        Args:
            concept_name: اسم المفهوم الأول
            related_concept: اسم المفهوم الثاني (اختياري)
            
        Returns:
            الفرضية المولدة
        """
        logger.info(f"توليد فرضية حول المفهوم: {concept_name}")
        
        # التحقق من وجود المفهوم
        if concept_name not in self.concepts:
            logger.warning(f"المفهوم غير موجود: {concept_name}")
            return {"error": f"المفهوم غير موجود: {concept_name}"}
        
        # توليد فرضية حول مفهوم واحد أو علاقة بين مفهومين
        hypothesis = {
            "id": f"hyp_{len(self.hypotheses) + 1}",
            "timestamp": "2023-01-01T00:00:00Z",  # يجب تحديثه بالوقت الفعلي
            "concepts": [concept_name],
            "confidence": 0.5,  # قيمة أولية
            "evidence": [],
            "status": "pending"  # pending, confirmed, rejected
        }
        
        if related_concept:
            # التحقق من وجود المفهوم المرتبط
            if related_concept not in self.concepts:
                logger.warning(f"المفهوم المرتبط غير موجود: {related_concept}")
                return {"error": f"المفهوم المرتبط غير موجود: {related_concept}"}
            
            # إضافة المفهوم المرتبط
            hypothesis["concepts"].append(related_concept)
            
            # توليد فرضية حول العلاقة بين المفهومين
            hypothesis["description"] = f"هناك علاقة مهمة بين {concept_name} و {related_concept} في السياق القرآني"
            hypothesis["type"] = "relation"
        else:
            # توليد فرضية حول المفهوم
            concept_data = self.concepts[concept_name]
            hypothesis["description"] = f"مفهوم {concept_name} له أهمية خاصة في السياق القرآني"
            hypothesis["type"] = "concept"
        
        # إضافة الفرضية إلى قائمة الفرضيات
        self.hypotheses.append(hypothesis)
        
        return hypothesis
    
    def add_evidence(self, hypothesis_id: str, evidence: Dict[str, Any]) -> bool:
        """
        إضافة دليل لفرضية
        
        Args:
            hypothesis_id: معرف الفرضية
            evidence: الدليل
            
        Returns:
            نجاح العملية
        """
        # البحث عن الفرضية
        hypothesis = None
        for h in self.hypotheses:
            if h["id"] == hypothesis_id:
                hypothesis = h
                break
        
        if not hypothesis:
            logger.warning(f"الفرضية غير موجودة: {hypothesis_id}")
            return False
        
        # إضافة الدليل
        evidence_id = f"ev_{len(hypothesis['evidence']) + 1}"
        evidence["id"] = evidence_id
        hypothesis["evidence"].append(evidence_id)
        
        # تخزين الدليل
        self.evidence[evidence_id] = evidence
        
        # تحديث ثقة الفرضية
        self._update_hypothesis_confidence(hypothesis)
        
        return True
    
    def _update_hypothesis_confidence(self, hypothesis: Dict[str, Any]) -> None:
        """
        تحديث ثقة الفرضية بناءً على الأدلة
        
        Args:
            hypothesis: الفرضية
        """
        # حساب الثقة بناءً على عدد الأدلة وقوتها
        evidence_count = len(hypothesis["evidence"])
        evidence_strength = 0.0
        
        for evidence_id in hypothesis["evidence"]:
            if evidence_id in self.evidence:
                evidence_strength += self.evidence[evidence_id].get("strength", 0.5)
        
        # حساب متوسط قوة الأدلة
        avg_strength = evidence_strength / max(1, evidence_count)
        
        # تحديث الثقة
        base_confidence = min(0.9, evidence_count / self.config["min_evidence_threshold"])
        hypothesis["confidence"] = base_confidence * avg_strength
        
        # تحديث حالة الفرضية
        if hypothesis["confidence"] >= self.config["confidence_threshold"]:
            hypothesis["status"] = "confirmed"
        elif evidence_count > 0 and hypothesis["confidence"] < 0.3:
            hypothesis["status"] = "rejected"
        else:
            hypothesis["status"] = "pending"
    
    def get_hypothesis_status(self, hypothesis_id: str) -> Dict[str, Any]:
        """
        الحصول على حالة فرضية
        
        Args:
            hypothesis_id: معرف الفرضية
            
        Returns:
            حالة الفرضية
        """
        # البحث عن الفرضية
        for hypothesis in self.hypotheses:
            if hypothesis["id"] == hypothesis_id:
                # جمع الأدلة
                evidence_details = []
                for evidence_id in hypothesis["evidence"]:
                    if evidence_id in self.evidence:
                        evidence_details.append(self.evidence[evidence_id])
                
                return {
                    "hypothesis": hypothesis,
                    "evidence": evidence_details,
                    "missing_evidence_count": max(0, self.config["min_evidence_threshold"] - len(hypothesis["evidence"]))
                }
        
        return {"error": f"الفرضية غير موجودة: {hypothesis_id}"}
    
    def get_all_hypotheses(self, status: str = None) -> List[Dict[str, Any]]:
        """
        الحصول على جميع الفرضيات
        
        Args:
            status: حالة الفرضيات (اختياري)
            
        Returns:
            قائمة الفرضيات
        """
        if status:
            return [h for h in self.hypotheses if h["status"] == status]
        else:
            return self.hypotheses
    
    def suggest_exploration_paths(self, concept_name: str = None) -> List[Dict[str, Any]]:
        """
        اقتراح مسارات استكشاف جديدة
        
        Args:
            concept_name: اسم المفهوم (اختياري)
            
        Returns:
            قائمة مسارات الاستكشاف المقترحة
        """
        suggestions = []