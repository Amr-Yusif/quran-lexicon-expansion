#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
اختبارات منسق الوكلاء (AgentCoordinator)
"""

import pytest
from unittest.mock import MagicMock, patch
import sys
import os

# إضافة المسار الرئيسي للمشروع إلى مسار البحث للاختبارات
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from core.ai.multi_agent_system import AgentCoordinator, Agent
from core.ai.base_agent import BaseAgent


class TestAgentCoordinator:
    """اختبارات لمنسق الوكلاء"""

    def setup_method(self):
        """إعداد لكل اختبار"""
        self.coordinator = AgentCoordinator(
            execution_strategy="parallel", conflict_resolution_strategy="weighted"
        )

        # إنشاء وكلاء وهمية
        self.mock_agent1 = MagicMock(spec=Agent)
        self.mock_agent2 = MagicMock(spec=Agent)

        # تكوين سلوك الوكلاء الوهمية
        self.mock_agent1.process.return_value = {"result": "result1", "confidence": 0.8}
        self.mock_agent2.process.return_value = {"result": "result2", "confidence": 0.5}
        self.mock_agent1.name = "agent1"
        self.mock_agent2.name = "agent2"

        self.agents = {"agent1": self.mock_agent1, "agent2": self.mock_agent2}

    def test_initialization(self):
        """اختبار تهيئة منسق الوكلاء"""
        assert self.coordinator.execution_strategy == "parallel"
        assert self.coordinator.conflict_resolution_strategy == "weighted"

    def test_coordinate_agents_parallel(self):
        """اختبار تنسيق الوكلاء بالتنفيذ المتوازي"""
        results = self.coordinator.coordinate_agents(
            self.agents, "test query", {"context_key": "value"}
        )

        # التحقق من استدعاء process لكل وكيل
        self.mock_agent1.process.assert_called_once_with("test query", {"context_key": "value"})
        self.mock_agent2.process.assert_called_once_with("test query", {"context_key": "value"})

        # التحقق من النتائج
        assert "agent1" in results
        assert "agent2" in results
        assert "synthesized" in results

    def test_synthesize_results_weighted(self):
        """اختبار توليف النتائج باستراتيجية الترجيح"""
        agent_results = {
            "agent1": {"result": "value1", "confidence": 0.8},
            "agent2": {"result": "value2", "confidence": 0.5},
        }

        self.coordinator.set_agent_weights({"agent1": 0.6, "agent2": 0.4})
        result = self.coordinator.synthesize_results(agent_results, "test query")

        # يجب أن تكون النتيجة المرجحة من الوكيل ذي الثقة الأعلى
        assert "metadata" in result
        assert result["metadata"]["query"] == "test query"
        # نتأكد من وجود نتيجة مرجحة
        assert "result" in result

    def test_set_agent_weights(self):
        """اختبار تعيين أوزان الوكلاء"""
        weights = {"agent1": 0.7, "agent2": 0.3}
        self.coordinator.set_agent_weights(weights)

        # التحقق من تعيين الأوزان
        assert self.coordinator.agent_weights == weights

    def test_set_agent_trust_scores(self):
        """اختبار تعيين درجات الثقة في الوكلاء"""
        trust_scores = {"agent1": 0.8, "agent2": 0.6}
        self.coordinator.set_agent_trust_scores(trust_scores)

        # التحقق من تعيين درجات الثقة
        assert self.coordinator.agent_trust_scores == trust_scores

    def test_update_agent_trust_score(self):
        """اختبار تحديث درجة الثقة في وكيل"""
        # تعيين درجات الثقة الأولية
        self.coordinator.set_agent_trust_scores({"agent1": 0.5})

        # تحديث درجة الثقة في الوكيل
        self.coordinator.update_agent_trust_score("agent1", 0.9, 0.1)

        # التحقق من تحديث درجة الثقة
        assert self.coordinator.agent_trust_scores["agent1"] > 0.5

    def test_conflict_resolution_weighted(self):
        """اختبار حل التعارضات باستراتيجية الترجيح"""
        # تكوين منسق وكلاء باستراتيجية الترجيح
        coordinator = AgentCoordinator(
            execution_strategy="parallel", conflict_resolution_strategy="weighted"
        )

        # تعيين أوزان الوكلاء
        coordinator.set_agent_weights({"agent1": 0.7, "agent2": 0.3})

        # إنشاء نتائج متعارضة
        conflicting_results = {
            "finding1": {
                "agent1": {"result": "A", "confidence": 0.8},
                "agent2": {"result": "B", "confidence": 0.7},
            }
        }

        # حل التعارضات
        result = coordinator._resolve_conflicts_weighted(conflicting_results)

        # التحقق من النتيجة (في البنية الفعلية، النتيجة هي كائن)
        assert result["finding1"]["result"] == "A"

    def test_conflict_resolution_majority(self):
        """اختبار حل التعارضات باستراتيجية الأغلبية"""
        # تكوين منسق وكلاء باستراتيجية الأغلبية
        coordinator = AgentCoordinator(
            execution_strategy="parallel", conflict_resolution_strategy="majority"
        )

        # إنشاء نتائج متعارضة
        conflicting_results = {
            "finding1": {
                "agent1": {"result": "A"},
                "agent2": {"result": "A"},
                "agent3": {"result": "B"},
            }
        }

        # حل التعارضات
        result = coordinator._resolve_conflicts_majority(conflicting_results)

        # التحقق من النتيجة (في البنية الفعلية، النتيجة هي كائن)
        assert result["finding1"]["result"] == "A"

    def test_conflict_resolution_trust_based(self):
        """اختبار حل التعارضات باستراتيجية الثقة"""
        # تكوين منسق وكلاء باستراتيجية الثقة
        coordinator = AgentCoordinator(
            execution_strategy="parallel", conflict_resolution_strategy="trust-based"
        )

        # تعيين درجات الثقة في الوكلاء
        coordinator.set_agent_trust_scores({"agent1": 0.8, "agent2": 0.6})

        # إنشاء نتائج متعارضة
        conflicting_results = {
            "finding1": {
                "agent1": {"result": "A", "confidence": 0.7},
                "agent2": {"result": "B", "confidence": 0.9},
            }
        }

        # حل التعارضات
        result = coordinator._resolve_conflicts_trust_based(conflicting_results)

        # التحقق من النتيجة (في البنية الفعلية، النتيجة هي كائن)
        assert result["finding1"]["result"] == "A"
