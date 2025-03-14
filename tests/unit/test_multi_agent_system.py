#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
اختبارات وحدة لنظام الوكلاء المتعددين
"""

import pytest
import os
import sys
from unittest.mock import MagicMock, patch
from typing import Dict, List, Any, Optional

# إضافة المجلد الرئيسي للمشروع إلى مسار Python
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# استيراد الوحدة المراد اختبارها
from core.ai.multi_agent_system import MultiAgentSystem, Agent, AgentCoordinator, IntegrationAgent


class TestMultiAgentSystem:
    """اختبارات لنظام الوكلاء المتعددين"""

    @pytest.fixture
    def multi_agent_system(self, mock_agents):
        """إعداد نظام الوكلاء المتعددين للاختبارات باستخدام الوكلاء الوهميين من fixture"""
        # إنشاء نظام الوكلاء المتعددين
        system = MultiAgentSystem()
        
        # تسجيل الوكلاء من fixture
        for agent_name, agent in mock_agents.items():
            system.register_agent(agent)
        
        return system

    def test_initialization(self):
        """اختبار تهيئة نظام الوكلاء المتعددين"""
        system = MultiAgentSystem()
        assert system is not None
        assert hasattr(system, 'agents')
        assert hasattr(system, 'coordinator')
        assert isinstance(system.agents, dict)
        assert isinstance(system.coordinator, AgentCoordinator)

    def test_register_agent(self, multi_agent_system):
        """اختبار تسجيل وكيل في النظام"""
        # إنشاء وكيل جديد
        new_agent = MagicMock()
        new_agent.name = "new_agent"
        
        # تسجيل الوكيل
        multi_agent_system.register_agent(new_agent)
        
        # التحقق من تسجيل الوكيل
        assert "new_agent" in multi_agent_system.agents
        assert multi_agent_system.agents["new_agent"] == new_agent

    def test_remove_agent(self, multi_agent_system):
        """اختبار إزالة وكيل من النظام"""
        # إزالة وكيل موجود
        multi_agent_system.remove_agent("linguistic_agent")
        
        # التحقق من إزالة الوكيل
        assert "linguistic_agent" not in multi_agent_system.agents

    def test_get_agent(self, multi_agent_system):
        """اختبار الحصول على وكيل من النظام"""
        # الحصول على وكيل موجود
        agent = multi_agent_system.get_agent("pattern_agent")
        
        # التحقق من الوكيل
        assert agent is not None
        assert agent.name == "pattern_agent"
        
        # محاولة الحصول على وكيل غير موجود
        with pytest.raises(KeyError):
            multi_agent_system.get_agent("non_existent_agent")

    def test_process_query(self, multi_agent_system):
        """اختبار معالجة استعلام باستخدام نظام الوكلاء المتعددين"""
        # تجهيز منسق الوكلاء الوهمي
        multi_agent_system.coordinator.coordinate_agents = MagicMock()
        multi_agent_system.coordinator.coordinate_agents.return_value = {
            "linguistic_analysis": {"analysis": "تحليل لغوي للنص"},
            "patterns": {"patterns": ["نمط1", "نمط2"]},
            "reasoning": {"conclusions": ["استنتاج1", "استنتاج2"]},
            "search_results": {"results": ["نتيجة1", "نتيجة2"]}
        }
        
        # معالجة استعلام
        query = "ما هي المعجزات العلمية في القرآن؟"
        result = multi_agent_system.process_query(query)
        
        # التحقق من النتائج
        assert result is not None
        assert "linguistic_analysis" in result
        assert "patterns" in result
        assert "reasoning" in result
        assert "search_results" in result
        
        # التحقق من استدعاء منسق الوكلاء
        multi_agent_system.coordinator.coordinate_agents.assert_called_once()

    def test_agent_class(self):
        """اختبار فئة الوكيل الأساسية"""
        # إنشاء وكيل
        agent = Agent("test_agent")
        
        # التحقق من خصائص الوكيل
        assert agent.name == "test_agent"
        assert hasattr(agent, 'process')
        
        # اختبار طريقة المعالجة الافتراضية
        with pytest.raises(NotImplementedError):
            agent.process("test query")

    @pytest.mark.parametrize(
        "execution_strategy,context_behavior",
        [
            # استراتيجية التنفيذ المتوازي
            ("parallel", "isolated"),  # كل وكيل يحصل على نسخة من السياق
            # استراتيجية التنفيذ المتسلسل
            ("sequential", "shared")   # الوكلاء يشاركون نفس السياق ويمكنهم رؤية نتائج بعضهم
        ]
    )
    def test_agent_coordinator(self, coordinator_factory, execution_strategy, context_behavior):
        """اختبار منسق الوكلاء مع استراتيجيات تنفيذ مختلفة"""
        # إنشاء منسق الوكلاء باستخدام مصنع المنسقين
        coordinator = coordinator_factory(execution_strategy=execution_strategy)
        
        # التحقق من خصائص المنسق
        assert hasattr(coordinator, 'coordinate_agents')
        assert hasattr(coordinator, 'synthesize_results')
        assert hasattr(coordinator, 'set_agent_weights')
        assert hasattr(coordinator, 'set_agent_trust_scores')
        assert coordinator.execution_strategy == execution_strategy
        
        # إنشاء وكلاء وهميين
        agents = {
            "agent1": MagicMock(),
            "agent2": MagicMock()
        }
        agents["agent1"].process.return_value = {"result": "نتيجة1"}
        agents["agent2"].process.return_value = {"result": "نتيجة2"}
        
        # إنشاء سياق اختبار
        test_context = {"initial_data": "بيانات أولية"}
        
        # اختبار تنسيق الوكلاء
        query = "استعلام اختبار"
        result = coordinator.coordinate_agents(agents, query, test_context)
        
        # التحقق من النتائج
        assert result is not None
        assert "agent1" in result
        assert "agent2" in result
        assert "synthesized" in result
        assert result["agent1"] == {"result": "نتيجة1"}
        assert result["agent2"] == {"result": "نتيجة2"}
        
        # التحقق من استدعاء الوكلاء بالطريقة المناسبة حسب استراتيجية التنفيذ
        if execution_strategy == "parallel":
            # في التنفيذ المتوازي، يجب أن يتم استدعاء كل وكيل بنسخة من السياق
            agents["agent1"].process.assert_called_once()
            agents["agent2"].process.assert_called_once()
        elif execution_strategy == "sequential":
            # في التنفيذ المتسلسل، يجب أن يتم استدعاء الوكلاء بنفس السياق
            # ويمكن للوكيل الثاني رؤية نتائج الوكيل الأول
            agents["agent1"].process.assert_called_once()
            agents["agent2"].process.assert_called_once()
    
    @pytest.mark.parametrize(
        "strategy,weights,trust_scores,conflicting_data,expected_value",
        [
            # استراتيجية الترجيح
            (
                "weighted", 
                {"agent1": 0.7, "agent2": 0.3}, 
                None, 
                {"key": {"agent1": "value1", "agent2": "value2"}},
                "value1"  # الوكيل 1 له وزن أعلى
            ),
            # استراتيجية الأغلبية
            (
                "majority", 
                None, 
                None, 
                {"key": {"agent1": "value1", "agent2": "value1", "agent3": "value2"}},
                "value1"  # القيمة 1 لها أغلبية
            ),
            # استراتيجية الثقة
            (
                "trust_based", 
                None, 
                {"agent1": 0.3, "agent2": 0.8}, 
                {"key": {"agent1": "value1", "agent2": "value2"}},
                "value2"  # الوكيل 2 له درجة ثقة أعلى
            ),
        ]
    )
    def test_conflict_resolution_strategies(self, coordinator_factory, strategy, weights, trust_scores, conflicting_data, expected_value):
        """اختبار استراتيجيات حل التعارضات باستخدام parametrization"""
        # إنشاء منسق الوكلاء باستخدام مصنع المنسقين
        coordinator = coordinator_factory(conflict_resolution_strategy=strategy)
        
        # تعيين أوزان الوكلاء إذا كانت موجودة
        if weights:
            coordinator.set_agent_weights(weights)
        
        # تعيين درجات الثقة في الوكلاء إذا كانت موجودة
        if trust_scores:
            coordinator.set_agent_trust_scores(trust_scores)
        
        # اختبار استراتيجية حل التعارضات المناسبة
        if strategy == "weighted":
            result = coordinator._resolve_conflicts_weighted(conflicting_data)
        elif strategy == "majority":
            result = coordinator._resolve_conflicts_majority(conflicting_data)
        elif strategy == "trust_based":
            result = coordinator._resolve_conflicts_trust_based(conflicting_data)
        
        # التحقق من النتيجة المتوقعة
        assert result["key"] == expected_value
    
    def test_integration_agent(self):
        """اختبار وكيل التكامل"""
        # استيراد وكيل التكامل
        from core.ai.multi_agent_system import IntegrationAgent
        
        # إنشاء وكيل التكامل
        integration_agent = IntegrationAgent()
        
        # إنشاء سياق يحتوي على نتائج الوكلاء المختلفة
        context = {
            "linguistic_agent": {
                "rhetorical_analysis": {
                    "figures_of_speech": ["استعارة", "تشبيه"],
                    "stylistic_features": ["تكرار", "جناس"]
                }
            },
            "pattern_agent": {
                "semantic_patterns": {
                    "themes": ["الإيمان", "العدل"],
                    "motifs": ["النور", "الماء"]
                }
            },
            "reasoning_agent": {
                "logical_inferences": ["استنتاج1", "استنتاج2"],
                "conclusions": ["خلاصة1", "خلاصة2"],
                "evidence": ["دليل1", "دليل2"],
                "confidence_scores": {"دليل1": 0.8, "دليل2": 0.6}
            },
            "search_agent": {
                "relevant_verses": ["آية1", "آية2"],
                "relevant_hadiths": ["حديث1", "حديث2"],
                "relevant_tafsir": ["تفسير1", "تفسير2"],
                "relevance_scores": {"آية1": 0.9, "آية2": 0.7, "حديث1": 0.8, "حديث2": 0.6}
            }
        }
        
        # معالجة الاستعلام
        query = "ما هي المعجزات العلمية في القرآن؟"
        result = integration_agent.process(query, context)
        
        # التحقق من النتائج
        assert result is not None
        assert "summary" in result
        assert "key_insights" in result
        assert "supporting_evidence" in result
        assert "related_concepts" in result
        assert "recommendations" in result
        assert "confidence_level" in result
        assert "metadata" in result
        
        # التحقق من وجود رؤى رئيسية
        assert len(result["key_insights"]) > 0
        
        # التحقق من وجود أدلة داعمة
        assert len(result["supporting_evidence"]) > 0
        
        # التحقق من مستوى الثقة
        assert 0.0 <= result["confidence_level"] <= 1.0