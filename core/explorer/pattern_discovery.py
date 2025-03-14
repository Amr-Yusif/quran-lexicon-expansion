#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
نظام اكتشاف الأنماط والعلاقات في النصوص الإسلامية
يستخدم أساليب التعلم الآلي والتحليل الشبكي لكشف العلاقات غير الظاهرة
"""

import numpy as np
import pandas as pd
import logging
import json
from typing import List, Dict, Any, Tuple
from collections import Counter, defaultdict
import re
from pathlib import Path

# استيراد المكتبات المطلوبة (بالتنزيل التلقائي إذا لم تكن موجودة)
try:
    from sklearn.cluster import DBSCAN
    from sklearn.feature_extraction.text import TfidfVectorizer
    import networkx as nx
    import matplotlib.pyplot as plt
    from sentence_transformers import SentenceTransformer
except ImportError:
    print("تثبيت المكتبات المطلوبة لاكتشاف الأنماط...")
    import os
    os.system("pip install scikit-learn networkx matplotlib sentence-transformers")
    from sklearn.cluster import DBSCAN
    from sklearn.feature_extraction.text import TfidfVectorizer
    import networkx as nx
    import matplotlib.pyplot as plt
    from sentence_transformers import SentenceTransformer

# إعداد التسجيل
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class PatternDiscovery:
    def __init__(self, model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"):
        """
        تهيئة محرك اكتشاف الأنماط باستخدام نموذج تضمين متعدد اللغات
        
        Args:
            model_name: اسم نموذج التضمين المستخدم
        """
        logger.info(f"تهيئة نظام اكتشاف الأنماط باستخدام النموذج: {model_name}")
        self.model = SentenceTransformer(model_name)
        self.graph = nx.Graph()
        self.output_dir = Path("results")
        self.output_dir.mkdir(exist_ok=True)
    
    def find_word_patterns(self, texts: List[str]) -> Dict:
        """
        اكتشاف الأنماط المتكررة للكلمات في مجموعة نصوص
        
        Args:
            texts: قائمة من النصوص للتحليل
            
        Returns:
            قاموس يحتوي على الأنماط المكتشفة
        """
        logger.info("البحث عن أنماط الكلمات في النصوص...")
        # استخراج الكلمات من النصوص
        all_words = []
        for text in texts:
            words = re.findall(r'\b\w+\b', text)
            all_words.extend(words)
        
        # حساب تكرار الكلمات
        word_counts = Counter(all_words)
        
        # حساب الترابط بين الكلمات
        word_co_occurrence = defaultdict(Counter)
        
        for text in texts:
            words = re.findall(r'\b\w+\b', text)
            unique_words = set(words)
            
            for word1 in unique_words:
                for word2 in unique_words:
                    if word1 != word2:
                        word_co_occurrence[word1][word2] += 1
        
        # استخراج الأنماط المهمة
        significant_patterns = []
        
        for word, count in word_counts.items():
            if count >= 3:  # كلمات تكررت على الأقل 3 مرات
                related_words = word_co_occurrence[word]
                
                strong_relations = {
                    related: count for related, count in related_words.items()
                    if count >= 2  # علاقات تكررت على الأقل مرتين
                }
                
                if strong_relations:
                    significant_patterns.append({
                        'word': word,
                        'count': count,
                        'related_words': strong_relations
                    })
        
        logger.info(f"تم العثور على {len(significant_patterns)} نمط مهم للكلمات")
        return {
            'word_patterns': significant_patterns
        }
    
    def cluster_similar_texts(self, texts: List[str]) -> Dict:
        """
        تجميع النصوص المتشابهة معًا لاكتشاف الأنماط الموضوعية
        
        Args:
            texts: قائمة من النصوص للتحليل
            
        Returns:
            قاموس يحتوي على المجموعات المكتشفة
        """
        logger.info("تجميع النصوص المتشابهة...")
        # تحويل النصوص إلى تضمينات
        embeddings = self.model.encode(texts)
        
        # تطبيق خوارزمية DBSCAN للتجميع
        clustering = DBSCAN(eps=0.3, min_samples=2).fit(embeddings)
        
        # تحليل النتائج
        labels = clustering.labels_
        n_clusters = len(set(labels)) - (1 if -1 in labels else 0)
        
        # تنظيم النصوص حسب المجموعات
        clusters = defaultdict(list)
        
        for i, label in enumerate(labels):
            if label != -1:  # استبعاد الضوضاء
                clusters[label].append({
                    'text': texts[i],
                    'id': i
                })
        
        # استخراج المواضيع الرئيسية لكل مجموعة
        cluster_topics = {}
        
        for cluster_id, cluster_texts in clusters.items():
            # استخراج النصوص فقط من المجموعة
            texts_only = [item['text'] for item in cluster_texts]
            
            # استخدام TF-IDF لاستخراج الكلمات المميزة
            vectorizer = TfidfVectorizer(max_features=10)
            tfidf_matrix = vectorizer.fit_transform(texts_only)
            
            # استخراج الكلمات المميزة
            feature_names = vectorizer.get_feature_names_out()
            tfidf_scores = tfidf_matrix.sum(axis=0).A1
            
            # ترتيب الكلمات حسب الأهمية
            important_words = [(feature_names[i], tfidf_scores[i]) for i in range(len(feature_names))]
            important_words.sort(key=lambda x: x[1], reverse=True)
            
            cluster_topics[cluster_id] = {
                'texts': cluster_texts,
                'size': len(cluster_texts),
                'key_terms': important_words[:5]  # أهم 5 كلمات
            }
        
        logger.info(f"تم اكتشاف {n_clusters} مجموعة من النصوص المتشابهة")
        return {
            'num_clusters': n_clusters,
            'clusters': cluster_topics,
            'noise_count': list(labels).count(-1)
        }
    
    def build_knowledge_graph(self, entities: List[Dict], relationships: List[Dict]) -> nx.Graph:
        """
        بناء رسم بياني للمعرفة من الكيانات والعلاقات المستخرجة
        
        Args:
            entities: قائمة من الكيانات
            relationships: قائمة من العلاقات
            
        Returns:
            رسم بياني للمعرفة
        """
        logger.info("بناء رسم بياني للمعرفة...")
        # إنشاء رسم بياني جديد
        self.graph = nx.Graph()
        
        # إضافة الكيانات كعقد في الرسم البياني
        for entity in entities:
            self.graph.add_node(
                entity['id'],
                type=entity['type'],
                name=entity['name'],
                attributes=entity.get('attributes', {})
            )
        
        # إضافة العلاقات كروابط في الرسم البياني
        for relation in relationships:
            self.graph.add_edge(
                relation['source'],
                relation['target'],
                type=relation['type'],
                weight=relation.get('weight', 1.0),
                attributes=relation.get('attributes', {})
            )
        
        logger.info(f"تم بناء رسم بياني للمعرفة يحتوي على {len(self.graph.nodes)} كيان و {len(self.graph.edges)} علاقة")
        return self.graph
    
    def discover_correlations(self, data: List[Dict], features: List[str]) -> Dict:
        """
        اكتشاف الارتباطات بين الخصائص المختلفة في البيانات
        
        Args:
            data: قائمة من البيانات
            features: قائمة من الخصائص للتحليل
            
        Returns:
            قاموس يحتوي على الارتباطات المكتشفة
        """
        logger.info("اكتشاف الارتباطات بين الخصائص...")
        # تحويل البيانات إلى DataFrame
        df = pd.DataFrame(data)
        
        # حساب مصفوفة الارتباط للخصائص المحددة
        correlation_matrix = df[features].corr()
        
        # استخراج الارتباطات القوية
        strong_correlations = []
        
        for i in range(len(features)):
            for j in range(i+1, len(features)):
                feature1 = features[i]
                feature2 = features[j]
                corr_value = correlation_matrix.iloc[i, j]
                
                # اعتبار الارتباطات ذات القيمة المطلقة أكبر من 0.5 قوية
                if abs(corr_value) > 0.5:
                    strong_correlations.append({
                        'feature1': feature1,
                        'feature2': feature2,
                        'correlation': corr_value
                    })
        
        logger.info(f"تم اكتشاف {len(strong_correlations)} ارتباط قوي بين الخصائص")
        return {
            'strong_correlations': strong_correlations,
            'full_matrix': correlation_matrix.to_dict()
        }
    
    def find_sequence_patterns(self, sequences: List[List[str]]) -> Dict:
        """
        اكتشاف الأنماط المتسلسلة في البيانات
        
        Args:
            sequences: قائمة من تسلسلات العناصر
            
        Returns:
            قاموس يحتوي على الأنماط المتسلسلة المكتشفة
        """
        logger.info("البحث عن أنماط متسلسلة...")
        # بناء قاموس للترتيب المتسلسل
        sequence_dict = defaultdict(list)
        
        for sequence in sequences:
            for i in range(len(sequence) - 1):
                current = sequence[i]
                next_item = sequence[i + 1]
                sequence_dict[current].append(next_item)
        
        # حساب أكثر العناصر التالية شيوعًا لكل عنصر
        common_next_items = {}
        
        for item, next_items in sequence_dict.items():
            counter = Counter(next_items)
            common_next_items[item] = counter.most_common(3)  # أكثر 3 عناصر شيوعًا
        
        # استخراج الأنماط المتسلسلة الشائعة
        common_patterns = []
        
        for item, next_items in common_next_items.items():
            if next_items:
                for next_item, count in next_items:
                    if count >= 2:  # التسلسل يجب أن يظهر على الأقل مرتين
                        common_patterns.append({
                            'sequence': [item, next_item],
                            'count': count
                        })
        
        logger.info(f"تم اكتشاف {len(common_patterns)} نمط متسلسل شائع")
        return {
            'common_next_items': common_next_items,
            'common_patterns': common_patterns
        }
    
    def visualize_knowledge_graph(self, output_file: str = "knowledge_graph.png"):
        """
        تصور الرسم البياني للمعرفة
        
        Args:
            output_file: اسم ملف الإخراج
        """
        if not self.graph.nodes():
            logger.warning("الرسم البياني فارغ. قم ببناء الرسم البياني أولاً باستخدام build_knowledge_graph.")
            return
        
        logger.info(f"تصور الرسم البياني للمعرفة وحفظه في {output_file}...")
        plt.figure(figsize=(12, 10))
        
        # استخراج أنواع العقد المختلفة
        node_types = set(nx.get_node_attributes(self.graph, 'type').values())
        node_colors = {}
        
        # تعيين لون مختلف لكل نوع
        for i, node_type in enumerate(node_types):
            node_colors[node_type] = plt.cm.tab10(i)
        
        # إعداد ألوان العقد
        colors = [node_colors[self.graph.nodes[n]['type']] for n in self.graph.nodes()]
        
        # رسم الرسم البياني
        pos = nx.spring_layout(self.graph)
        nx.draw_networkx_nodes(self.graph, pos, node_color=colors, node_size=300, alpha=0.8)
        nx.draw_networkx_edges(self.graph, pos, width=1.0, alpha=0.5)
        
        # إضافة تسميات للعقد
        labels = {n: self.graph.nodes[n]['name'] for n in self.graph.nodes()}
        nx.draw_networkx_labels(self.graph, pos, labels, font_size=8, font_family="sans-serif")
        
        # إضافة مفتاح للرسم
        legend_handles = []
        for node_type, color in node_colors.items():
            legend_handles.append(plt.Line2D([0], [0], marker='o', color='w', markerfacecolor=color, markersize=10, label=node_type))
        
        plt.legend(handles=legend_handles, loc='upper right')
        plt.axis('off')
        plt.tight_layout()
        
        # حفظ الرسم
        output_path = self.output_dir / output_file
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info(f"تم حفظ الرسم البياني للمعرفة في {output_path}")
