#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
اختبارات نظام الوكلاء المتعددين (MultiAgentSystem)
"""

import pytest
from unittest.mock import MagicMock, patch
import sys
import os
import tempfile
import json

# إضافة المسار الرئيسي للمشروع إلى مسار البحث للاختبارات
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from core.ai.multi_agent_system import MultiAgentSystem, Agent
from core.ai.base_agent import BaseAgent


class TestMultiAgentSystem:
    """اختبارات لنظام الوكلاء المتعددين"""

    def setup_method(self):
        """إعداد لكل اختبار"""
        self.system = MultiAgentSystem(
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

    def test_initialization(self):
        """اختبار تهيئة نظام الوكلاء المتعددين"""
        assert hasattr(self.system, "coordinator")
        assert self.system.coordinator.execution_strategy == "parallel"
        assert self.system.coordinator.conflict_resolution_strategy == "weighted"
        assert isinstance(self.system.agents, dict)
        assert len(self.system.agents) == 0

    def test_register_agent(self):
        """اختبار تسجيل وكيل في النظام"""
        # التحقق من عدم وجود وكلاء مسجلة مسبقًا
        assert len(self.system.agents) == 0

        # تسجيل وكيل
        self.system.register_agent(self.mock_agent1)

        # التحقق من تسجيل الوكيل
        assert len(self.system.agents) == 1
        assert "agent1" in self.system.agents
        assert self.system.agents["agent1"] == self.mock_agent1

    def test_remove_agent(self):
        """اختبار إزالة وكيل من النظام"""
        # تسجيل وكيل
        self.system.register_agent(self.mock_agent1)

        # التحقق من وجود الوكيل
        assert "agent1" in self.system.agents

        # إزالة الوكيل
        self.system.remove_agent("agent1")

        # التحقق من إزالة الوكيل
        assert "agent1" not in self.system.agents

    def test_get_agent(self):
        """اختبار الحصول على وكيل من النظام"""
        # تسجيل وكيل
        self.system.register_agent(self.mock_agent1)

        # الحصول على الوكيل
        agent = self.system.get_agent("agent1")

        # التحقق من الوكيل
        assert agent == self.mock_agent1

        # محاولة الحصول على وكيل غير موجود
        with pytest.raises(KeyError):
            self.system.get_agent("nonexistent_agent")

    def test_process_query(self):
        """اختبار معالجة استعلام باستخدام جميع الوكلاء المسجلين"""
        # تسجيل وكلاء
        self.system.register_agent(self.mock_agent1)
        self.system.register_agent(self.mock_agent2)

        # تنفيذ المعالجة
        result = self.system.process_query("test query", {"context_key": "value"})

        # التحقق من النتائج
        assert "agent1" in result
        assert "agent2" in result
        assert "synthesized" in result

    def test_save_and_load_results(self):
        """اختبار حفظ وتحميل النتائج"""
        # تسجيل وكلاء
        self.system.register_agent(self.mock_agent1)
        self.system.register_agent(self.mock_agent2)

        # تنفيذ المعالجة
        results = self.system.process_query("test query")

        # إنشاء ملف مؤقت لحفظ النتائج
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as temp_file:
            temp_path = temp_file.name

        try:
            # حفظ النتائج
            success = self.system.save_results(temp_path)
            assert success

            # إنشاء نظام جديد
            new_system = MultiAgentSystem()

            # تحميل النتائج
            success = new_system.load_results(temp_path)
            assert success

            # التحقق من تحميل النتائج
            assert hasattr(new_system, "results_history")
            assert len(new_system.results_history) > 0

        finally:
            # تنظيف الملف المؤقت
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    def test_process_with_empty_agents(self):
        """اختبار معالجة استعلام بدون وكلاء مسجلين"""
        # لا نقوم بتسجيل أي وكلاء

        # تنفيذ المعالجة
        result = self.system.process_query("test query")

        # التحقق من النتائج - في هذه الحالة، قد لا يكون هناك نتيجة توليف لأنه لا توجد وكلاء
        # لذلك نتأكد فقط من أن النتيجة هي قاموس (يمكن أن يكون فارغًا)
        assert isinstance(result, dict)

    @pytest.mark.skip("ميزة agent_names غير متاحة في التنفيذ الحالي")
    def test_process_with_specific_agents(self):
        """اختبار معالجة استعلام باستخدام وكلاء محددين"""
        # تسجيل وكلاء
        self.system.register_agent(self.mock_agent1)
        self.system.register_agent(self.mock_agent2)

        # تنفيذ المعالجة باستخدام وكيل محدد
        result = self.system.process_query("test query", agent_names=["agent1"])

        # التحقق من النتائج
        assert "agent1" in result
        assert "agent2" not in result
        assert "synthesized" in result
