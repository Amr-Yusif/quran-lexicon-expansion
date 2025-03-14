#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
محرك استدلال للنصوص القرآنية والإسلامية
يستخدم نظرية المخططات والتفكير الجانبي لاكتشاف روابط جديدة واستنتاجات
"""

import logging
import re
import os
from typing import List, Dict, Any, Optional, Tuple, Set, Union
from pathlib import Path
import numpy as np
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
from tqdm import tqdm
import json
from collections import defaultdict, Counter
from sentence_transformers import SentenceTransformer, util

# التحقق من وجود المكتبات وتثبيتها تلقائياً إذا كانت غير موجودة
try:
    import community as community_louvain
except ImportError:
    import subprocess
    import sys
    subprocess.check_call([sys.executable, "-m", "pip", "install", "python-louvain"])
    import community as community_louvain

# إعداد التسجيل
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ReasoningEngine:
    """محرك استدلال لربط المفاهيم واكتشاف استنتاجات جديدة"""
    
    def __init__(self, embedding_model: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"):
        """
        تهيئة محرك الاستدلال
        
        Args:
            embedding_model: نموذج التضمين المستخدم للتحليل الدلالي
        """
        logger.info("تهيئة محرك الاستدلال...")
        
        # تحميل نموذج التضمين
        self.model = SentenceTransformer(embedding_model)
        
        # إنشاء الرسم البياني للمعرفة
        self.knowledge_graph = nx.Graph()
        
        # تخزين المفاهيم والعلاقات والاستنتاجات
        self.concepts = {}  # المفاهيم الأساسية
        self.relations = []  # العلاقات بين المفاهيم
        self.inferences = []  # الاستنتاجات المكتشفة
        
        # إعدادات محرك الاستدلال
        self.config = {
            "similarity_threshold": 0.6,  # عتبة التشابه للاعتبار مفهومين مرتبطين
            "inference_confidence": 0.7,  # عتبة الثقة للاستنتاجات
            "community_resolution": 1.0,  # دقة اكتشاف المجتمعات في الرسم البياني
            "lateral_thinking_depth": 2  # عمق التفكير الجانبي
        }
        
        # إنشاء مجلد للمخرجات
        self.output_dir = Path("reasoning_results")
        self.output_dir.mkdir(exist_ok=True)
        
        logger.info("تم تهيئة محرك الاستدلال بنجاح")
    
    def add_concept(self, concept_id: str, concept_text: str, concept_type: str = "generic", attributes: Dict = None) -> None:
        """
        إضافة مفهوم جديد إلى قاعدة المعرفة
        
        Args:
            concept_id: معرف المفهوم
            concept_text: النص الوصفي للمفهوم
            concept_type: نوع المفهوم (generic, quranic, tafsir, linguistic, scientific)
            attributes: سمات إضافية للمفهوم
        """
        if concept_id in self.concepts:
            logger.warning(f"المفهوم {concept_id} موجود بالفعل، سيتم تحديثه")
        
        # إنشاء سمات افتراضية إذا كانت غير موجودة
        if attributes is None:
            attributes = {}
        
        # إضافة المفهوم إلى القاموس
        self.concepts[concept_id] = {
            "id": concept_id,
            "text": concept_text,
            "type": concept_type,
            "attributes": attributes,
            "embedding": self.model.encode(concept_text)
        }
        
        # إضافة المفهوم إلى الرسم البياني
        self.knowledge_graph.add_node(
            concept_id, 
            text=concept_text, 
            type=concept_type, 
            **attributes
        )
        
        logger.info(f"تمت إضافة المفهوم: {concept_id} ({concept_type})")
    
    def add_relation(self, source_id: str, target_id: str, relation_type: str, weight: float = 1.0, attributes: Dict = None) -> None:
        """
        إضافة علاقة بين مفهومين
        
        Args:
            source_id: معرف المفهوم المصدر
            target_id: معرف المفهوم الهدف
            relation_type: نوع العلاقة
            weight: وزن العلاقة
            attributes: سمات إضافية للعلاقة
        """
        # التحقق من وجود المفاهيم
        if source_id not in self.concepts:
            logger.warning(f"المفهوم المصدر {source_id} غير موجود")
            return
        
        if target_id not in self.concepts:
            logger.warning(f"المفهوم الهدف {target_id} غير موجود")
            return
        
        # إنشاء سمات افتراضية إذا كانت غير موجودة
        if attributes is None:
            attributes = {}
        
        # إنشاء العلاقة
        relation = {
            "source": source_id,
            "target": target_id,
            "type": relation_type,
            "weight": weight,
            "attributes": attributes
        }
        
        # إضافة العلاقة إلى القائمة
        self.relations.append(relation)
        
        # إضافة الحافة إلى الرسم البياني
        self.knowledge_graph.add_edge(
            source_id, 
            target_id, 
            type=relation_type, 
            weight=weight, 
            **attributes
        )
        
        logger.info(f"تمت إضافة العلاقة: {source_id} -{relation_type}-> {target_id}")
    
    def discover_relations(self, threshold: float = None) -> List[Dict]:
        """
        اكتشاف العلاقات بين المفاهيم تلقائياً
        
        Args:
            threshold: عتبة التشابه (تجاوز الإعداد الافتراضي)
            
        Returns:
            قائمة بالعلاقات المكتشفة
        """
        if threshold is None:
            threshold = self.config["similarity_threshold"]
        
        logger.info(f"اكتشاف العلاقات بين المفاهيم (عتبة التشابه: {threshold})...")
        
        # جمع المفاهيم والتضمينات
        concept_ids = list(self.concepts.keys())
        embeddings = [self.concepts[cid]["embedding"] for cid in concept_ids]
        
        # حساب مصفوفة التشابه
        similarity_matrix = util.pytorch_cos_sim(embeddings, embeddings).numpy()
        
        # اكتشاف العلاقات
        discovered_relations = []
        
        for i in range(len(concept_ids)):
            for j in range(i+1, len(concept_ids)):  # تجنب التكرار والمقارنة الذاتية
                similarity = similarity_matrix[i][j]
                
                if similarity >= threshold:
                    source_id = concept_ids[i]
                    target_id = concept_ids[j]
                    
                    # إنشاء نوع العلاقة بناءً على نوع المفاهيم
                    source_type = self.concepts[source_id]["type"]
                    target_type = self.concepts[target_id]["type"]
                    
                    if source_type == target_type:
                        relation_type = "semantically_related"
                    else:
                        relation_type = f"links_{source_type}_to_{target_type}"
                    
                    # إضافة العلاقة
                    relation = {
                        "source": source_id,
                        "target": target_id,
                        "type": relation_type,
                        "weight": float(similarity),
                        "attributes": {"discovered": True, "similarity": float(similarity)}
                    }
                    
                    discovered_relations.append(relation)
                    
                    # إضافة العلاقة إلى الرسم البياني إذا لم تكن موجودة بالفعل
                    if not self.knowledge_graph.has_edge(source_id, target_id):
                        self.add_relation(
                            source_id, 
                            target_id, 
                            relation_type, 
                            weight=float(similarity),
                            attributes={"discovered": True, "similarity": float(similarity)}
                        )
        
        logger.info(f"تم اكتشاف {len(discovered_relations)} علاقة بين المفاهيم")
        return discovered_relations
    
    def infer_new_knowledge(self) -> List[Dict]:
        """
        استنتاج معرفة جديدة بناءً على العلاقات الموجودة في الرسم البياني
        
        Returns:
            قائمة بالاستنتاجات الجديدة
        """
        logger.info("استنتاج معرفة جديدة من الرسم البياني...")
        
        # قائمة الاستنتاجات الجديدة
        new_inferences = []
        
        # 1. استنتاج العلاقات الانتقالية (a->b, b->c لذلك a->c)
        transitive_relations = self._infer_transitive_relations()
        new_inferences.extend(transitive_relations)
        
        # 2. استنتاج العلاقات المشتركة (a->c, b->c لذلك a قد يرتبط بـ b)
        common_target_relations = self._infer_common_target_relations()
        new_inferences.extend(common_target_relations)
        
        # 3. استنتاج مفاهيم تنتمي لنفس المجموعة
        community_inferences = self._infer_community_relations()
        new_inferences.extend(community_inferences)
        
        # إضافة الاستنتاجات إلى القائمة
        self.inferences.extend(new_inferences)
        
        logger.info(f"تم استنتاج {len(new_inferences)} معلومة جديدة")
        return new_inferences
    
    def _infer_transitive_relations(self) -> List[Dict]:
        """
        استنتاج العلاقات الانتقالية: إذا كان a مرتبط بـ b، و b مرتبط بـ c، إذن a قد يكون مرتبط بـ c
        
        Returns:
            قائمة بالعلاقات الانتقالية المستنتجة
        """
        transitive_relations = []
        confidence_threshold = self.config["inference_confidence"]
        
        # للأداء الأمثل، نستخدم القائمة المخزنة للعلاقات بدلاً من مسح الرسم البياني
        relation_dict = defaultdict(list)
        for relation in self.relations:
            source = relation["source"]
            target = relation["target"]
            weight = relation["weight"]
            relation_dict[source].append((target, weight))
        
        # البحث عن المسارات ذات الخطوتين
        for node_a in relation_dict:
            for node_b, weight_ab in relation_dict[node_a]:
                if node_b in relation_dict:
                    for node_c, weight_bc in relation_dict[node_b]:
                        # تجنب العلاقات مع النفس والعلاقات الموجودة بالفعل
                        if node_a != node_c and not self.knowledge_graph.has_edge(node_a, node_c):
                            # حساب وزن العلاقة الانتقالية
                            transitive_weight = weight_ab * weight_bc
                            
                            if transitive_weight >= confidence_threshold:
                                inference = {
                                    "type": "transitive_relation",
                                    "source": node_a,
                                    "target": node_c,
                                    "intermediate": node_b,
                                    "confidence": transitive_weight,
                                    "explanation": f"استنتاج انتقالي: {node_a} مرتبط بـ {node_b} و {node_b} مرتبط بـ {node_c}، لذلك {node_a} قد يكون مرتبط بـ {node_c}"
                                }
                                
                                transitive_relations.append(inference)
                                
                                # إضافة العلاقة المستنتجة إلى الرسم البياني
                                self.add_relation(
                                    node_a, 
                                    node_c, 
                                    "inferred_relation", 
                                    weight=transitive_weight,
                                    attributes={"inferred": True, "inference_type": "transitive", "intermediate": node_b}
                                )
        
        return transitive_relations
    
    def _infer_common_target_relations(self) -> List[Dict]:
        """
        استنتاج العلاقات المشتركة: إذا كان a و b يرتبطان بنفس c، فقد يكون a و b مرتبطين
        
        Returns:
            قائمة بالعلاقات المشتركة المستنتجة
        """
        common_target_relations = []
        confidence_threshold = self.config["inference_confidence"]
        
        # إنشاء قاموس العلاقات العكسية
        reverse_relation_dict = defaultdict(list)
        for relation in self.relations:
            source = relation["source"]
            target = relation["target"]
            weight = relation["weight"]
            reverse_relation_dict[target].append((source, weight))
        
        # البحث عن العلاقات المشتركة
        for node_c in reverse_relation_dict:
            sources = reverse_relation_dict[node_c]
            
            for i in range(len(sources)):
                node_a, weight_ac = sources[i]
                
                for j in range(i+1, len(sources)):
                    node_b, weight_bc = sources[j]
                    
                    # تجنب العلاقات الموجودة بالفعل
                    if not self.knowledge_graph.has_edge(node_a, node_b):
                        # حساب وزن العلاقة المشتركة
                        common_weight = (weight_ac + weight_bc) / 2
                        
                        if common_weight >= confidence_threshold:
                            inference = {
                                "type": "common_target_relation",
                                "source": node_a,
                                "target": node_b,
                                "common_node": node_c,
                                "confidence": common_weight,
                                "explanation": f"استنتاج علاقة مشتركة: {node_a} و {node_b} كلاهما مرتبط بـ {node_c}، لذلك قد يكون {node_a} و {node_b} مرتبطين"
                            }
                            
                            common_target_relations.append(inference)
                            
                            # إضافة العلاقة المستنتجة إلى الرسم البياني
                            self.add_relation(
                                node_a, 
                                node_b, 
                                "inferred_relation", 
                                weight=common_weight,
                                attributes={"inferred": True, "inference_type": "common_target", "common_node": node_c}
                            )
        
        return common_target_relations
    
    def _infer_community_relations(self) -> List[Dict]:
        """
        استنتاج العلاقات داخل المجتمعات في الرسم البياني
        
        Returns:
            قائمة بالعلاقات المجتمعية المستنتجة
        """
        community_relations = []
        
        # التحقق من وجود عدد كافٍ من العقد
        if self.knowledge_graph.number_of_nodes() < 3:
            return []
        
        # اكتشاف المجتمعات باستخدام خوارزمية Louvain
        communities = community_louvain.best_partition(
            self.knowledge_graph, 
            resolution=self.config["community_resolution"]
        )
        
        # تنظيم العقد حسب المجتمعات
        community_nodes = defaultdict(list)
        for node, community_id in communities.items():
            community_nodes[community_id].append(node)
        
        # استنتاج العلاقات داخل المجتمعات
        for community_id, nodes in community_nodes.items():
            if len(nodes) >= 3:  # نحتاج على الأقل 3 عقد لاستنتاج علاقات مجتمعية ذات معنى
                for i in range(len(nodes)):
                    for j in range(i+1, len(nodes)):
                        node_a = nodes[i]
                        node_b = nodes[j]
                        
                        # تجنب العلاقات الموجودة بالفعل
                        if not self.knowledge_graph.has_edge(node_a, node_b):
                            inference = {
                                "type": "community_relation",
                                "source": node_a,
                                "target": node_b,
                                "community_id": community_id,
                                "confidence": 0.7,  # قيمة افتراضية للثقة
                                "explanation": f"استنتاج علاقة مجتمعية: {node_a} و {node_b} ينتميان إلى نفس المجموعة الدلالية {community_id}"
                            }
                            
                            community_relations.append(inference)
                            
                            # إضافة العلاقة المستنتجة إلى الرسم البياني
                            self.add_relation(
                                node_a, 
                                node_b, 
                                "community_relation", 
                                weight=0.7,
                                attributes={"inferred": True, "inference_type": "community", "community_id": community_id}
                            )
        
        return community_relations
