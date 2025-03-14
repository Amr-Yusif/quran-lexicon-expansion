#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
اختبارات وحدة لنظام التعلم النشط
"""

import pytest
import os
import sys
import json
from unittest.mock import MagicMock, patch
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

# إضافة المجلد الرئيسي للمشروع إلى مسار Python
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# استيراد الوحدة المراد اختبارها
from core.ai.active_learning_system import ActiveLearningSystem
from core.explorer.pattern_discovery import PatternDiscovery
from core.ai.multi_agent_system import Agent


class TestActiveLearningSystem:
    """اختبارات لنظام التعلم النشط"""

    @pytest.fixture
    def temp_knowledge_base(self, tmp_path):
        """إنشاء قاعدة معرفة مؤقتة للاختبارات"""
        knowledge_base_path = tmp_path / "knowledge_base"
        knowledge_base_path.mkdir()
        return str(knowledge_base_path)

    @pytest.fixture
    def active_learning_system(self, temp_knowledge_base):
        """إنشاء نظام التعلم النشط للاختبارات"""
        return ActiveLearningSystem(knowledge_base_path=temp_knowledge_base)

    @pytest.fixture
    def mock_pattern_discovery(self):
        """إنشاء محاكاة لمحرك اكتشاف الأنماط"""
        mock = MagicMock(spec=PatternDiscovery)
        
        # تعريف سلوك الدوال المحاكاة
        mock.find_word_patterns.return_value = {
            "patterns": [
                {"word": "قرآن", "count": 5, "related_words": {"كريم": 3, "آية": 2}},
                {"word": "إسلام", "count": 4, "related_words": {"دين": 3}}
            ]
        }
        
        mock.cluster_concepts.return_value = {
            "clusters": [
                {"name": "العقيدة", "concepts": ["توحيد", "إيمان", "عبادة"]},
                {"name": "الأخلاق", "concepts": ["صدق", "أمانة", "إحسان"]}
            ]
        }
        
        mock.find_semantic_relationships.return_value = {
            "relationships": [
                {"source": "قرآن", "target": "هداية", "type": "provides", "strength": 0.9},
                {"source": "صلاة", "target": "خشوع", "type": "requires", "strength": 0.8}
            ]
        }
        
        mock.build_knowledge_graph.return_value = {
            "relationships": [
                {"source": "قرآن", "target": "هداية", "type": "provides"},
                {"source": "صلاة", "target": "خشوع", "type": "requires"}
            ],
            "graph": {"nodes": 4, "edges": 2}
        }
        
        return mock

    def test_initialization(self, active_learning_system, temp_knowledge_base):
        """اختبار تهيئة نظام التعلم النشط"""
        assert active_learning_system is not None
        assert active_learning_system.knowledge_base_path == Path(temp_knowledge_base)
        assert active_learning_system.patterns_path.exists()
        assert active_learning_system.relationships_path.exists()
        assert active_learning_system.feedback_path.exists()
        assert isinstance(active_learning_system.pattern_discovery, PatternDiscovery)
        assert active_learning_system.learning_history == []
        assert "pattern_discovery" in active_learning_system.performance_metrics
        assert "relationship_discovery" in active_learning_system.performance_metrics
        assert "feedback_integration" in active_learning_system.performance_metrics

    def test_discover_new_patterns(self, active_learning_system, monkeypatch, mock_pattern_discovery):
        """اختبار اكتشاف أنماط جديدة"""
        # استبدال محرك اكتشاف الأنماط بالمحاكاة
        monkeypatch.setattr(active_learning_system, "pattern_discovery", mock_pattern_discovery)
        
        # تعطيل دالة الحفظ للاختبار
        monkeypatch.setattr(active_learning_system, "_save_patterns", lambda x: None)
        monkeypatch.setattr(active_learning_system, "_update_pattern_metrics", lambda x: None)
        
        # اختبار اكتشاف الأنماط
        texts = ["القرآن الكريم هو كتاب الله", "الإسلام دين الحق"]
        result = active_learning_system.discover_new_patterns(texts)
        
        # التحقق من النتائج
        assert "word_patterns" in result
        assert "concept_clusters" in result
        assert "semantic_relationships" in result
        assert "timestamp" in result
        assert "context" in result
        
        # التحقق من استدعاء الدوال المتوقعة
        mock_pattern_discovery.find_word_patterns.assert_called_once_with(texts)
        mock_pattern_discovery.cluster_concepts.assert_called_once_with(texts)
        mock_pattern_discovery.find_semantic_relationships.assert_called_once_with(texts)

    def test_discover_relationships(self, active_learning_system, monkeypatch, mock_pattern_discovery):
        """اختبار اكتشاف العلاقات"""
        # استبدال محرك اكتشاف الأنماط بالمحاكاة
        monkeypatch.setattr(active_learning_system, "pattern_discovery", mock_pattern_discovery)
        
        # تعطيل دالة الحفظ للاختبار
        monkeypatch.setattr(active_learning_system, "_save_relationships", lambda x: None)
        monkeypatch.setattr(active_learning_system, "_update_relationship_metrics", lambda x: None)
        
        # اختبار اكتشاف العلاقات
        entities = [
            {"id": 1, "text": "القرآن هو كلام الله المنزل على محمد"},
            {"id": 2, "text": "الصلاة عمود الدين وأول ما يحاسب عليه العبد"}
        ]
        result = active_learning_system.discover_relationships(entities)
        
        # التحقق من النتائج
        assert "relationships" in result
        assert "graph" in result
        assert "timestamp" in result
        assert "context" in result
        
        # التحقق من استدعاء الدوال المتوقعة
        entity_texts = [entity["text"] for entity in entities]
        mock_pattern_discovery.build_knowledge_graph.assert_called_once_with(entity_texts)
        
        # التحقق من إضافة معلومات الكيانات
        for i, relationship in enumerate(result["relationships"]):
            if i < len(entities):
                assert "entity_info" in relationship

    def test_integrate_feedback_invalid(self, active_learning_system):
        """اختبار دمج تغذية راجعة غير صالحة"""
        # تغذية راجعة بدون حقول مطلوبة
        invalid_feedback = {"summary": "تغذية راجعة غير مكتملة"}
        result = active_learning_system.integrate_feedback(invalid_feedback)
        
        assert result["status"] == "error"
        assert "message" in result
        
        # تغذية راجعة بنوع غير صالح
        invalid_type_feedback = {"type": "invalid_type", "content": {}}
        result = active_learning_system.integrate_feedback(invalid_type_feedback)
        
        assert result["status"] == "error"
        assert "message" in result

    def test_update_agent_knowledge(self, active_learning_system):
        """اختبار تحديث معرفة وكيل"""
        # إنشاء وكيل وهمي
        mock_agent = MagicMock(spec=Agent)
        mock_agent.name = "test_agent"
        mock_agent.update_knowledge = MagicMock(return_value=True)
        
        # اختبار تحديث المعرفة
        new_knowledge = {"patterns": ["نمط جديد"], "concepts": ["مفهوم جديد"]}
        result = active_learning_system.update_agent_knowledge(mock_agent, new_knowledge)
        
        assert result is True
        mock_agent.update_knowledge.assert_called_once_with(new_knowledge)
        
        # اختبار وكيل لا يدعم تحديث المعرفة
        mock_agent_without_update = MagicMock(spec=Agent)
        mock_agent_without_update.name = "agent_without_update"
        # لا نضيف دالة update_knowledge
        
        result = active_learning_system.update_agent_knowledge(mock_agent_without_update, new_knowledge)
        assert result is False

    def test_generate_learning_report(self, active_learning_system, monkeypatch):
        """اختبار إنشاء تقرير التعلم"""
        # تعطيل دالة الحصول على الاكتشافات الأخيرة للاختبار
        monkeypatch.setattr(active_learning_system, "_get_recent_discoveries", lambda x: [])
        
        # إضافة بعض العناصر إلى سجل التعلم
        active_learning_system.learning_history = [
            {"type": "pattern", "id": "pattern_1", "timestamp": datetime.now().isoformat()},
            {"type": "relationship", "id": "relationship_1", "timestamp": datetime.now().isoformat()}
        ]
        
        # اختبار إنشاء التقرير
        report = active_learning_system.generate_learning_report()
        
        assert "timestamp" in report
        assert "learning_history" in report
        assert "performance_metrics" in report
        assert "statistics" in report
        assert "recent_discoveries" in report
        assert len(report["learning_history"]) == 2

    def test_validate_feedback(self, active_learning_system):
        """اختبار التحقق من صحة التغذية الراجعة"""
        # تغذية راجعة صالحة
        valid_feedback = {
            "type": "pattern_correction",
            "content": {"pattern_id": "pattern_1", "correction": "تصحيح النمط"}
        }
        assert active_learning_system._validate_feedback(valid_feedback) is True
        
        # تغذية راجعة بدون حقل مطلوب
        missing_field_feedback = {"type": "pattern_correction"}
        assert active_learning_system._validate_feedback(missing_field_feedback) is False
        
        # تغذية راجعة بنوع غير صالح
        invalid_type_feedback = {"type": "invalid_type", "content": {}}
        assert active_learning_system._validate_feedback(invalid_type_feedback) is False


if __name__ == "__main__":
    pytest.main(['-xvs', __file__])