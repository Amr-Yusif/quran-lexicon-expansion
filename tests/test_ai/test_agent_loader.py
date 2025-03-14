#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
اختبارات وحدة تحميل الوكلاء من ملفات YAML
"""

import os
import sys
import pytest
import tempfile
import yaml
from unittest import mock

# إضافة المسار الرئيسي للمشروع
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from core.ai.multi_agent_system import Agent, MultiAgentSystem


# إنشاء فئات وكلاء اختبارية
class MockAgentA(Agent):
    def process(self, query, context=None):
        return {"result": "A"}


class MockAgentB(Agent):
    def process(self, query, context=None):
        return {"result": "B"}


class MockAgentC(Agent):
    def __init__(self, name, param1=None, param2=None):
        super().__init__(name)
        self.param1 = param1
        self.param2 = param2

    def process(self, query, context=None):
        return {"result": "C", "params": {"param1": self.param1, "param2": self.param2}}


# تجهيز ملفات YAML للاختبار
@pytest.fixture
def yaml_config_dir():
    """إنشاء دليل مؤقت لملفات التكوين"""
    with tempfile.TemporaryDirectory() as temp_dir:
        # إنشاء ملفات التكوين
        agents_dir = os.path.join(temp_dir, "agents")
        os.makedirs(agents_dir, exist_ok=True)

        # ملف التكوين الرئيسي
        main_config = {
            "general": {
                "auto_register": True,
                "config_dir": os.path.join(temp_dir, "agents"),
                "default_enabled": True,
                "scan_directories": [os.path.dirname(__file__)],
            },
            "agents": [
                {"name": "agent_a", "type": "MockAgentA", "enabled": True},
                {"name": "agent_b", "type": "MockAgentB", "enabled": True},
                {"name": "agent_c", "type": "MockAgentC", "enabled": True, "file": "agent_c.yaml"},
                {"name": "agent_d", "type": "NonExistentAgent", "enabled": False},
            ],
        }

        # تكوين الوكيل C
        agent_c_config = {
            "name": "agent_c",
            "type": "MockAgentC",
            "description": "وكيل اختباري C",
            "enabled": True,
            "parameters": {"param1": "value1", "param2": "value2"},
        }

        # كتابة ملفات التكوين
        main_config_path = os.path.join(temp_dir, "agents.yaml")
        with open(main_config_path, "w", encoding="utf-8") as f:
            yaml.dump(main_config, f, allow_unicode=True)

        agent_c_path = os.path.join(agents_dir, "agent_c.yaml")
        with open(agent_c_path, "w", encoding="utf-8") as f:
            yaml.dump(agent_c_config, f, allow_unicode=True)

        yield temp_dir


class TestAgentLoader:
    """اختبارات محمل الوكلاء"""

    def test_yaml_config_loading(self, yaml_config_dir):
        """اختبار تحميل ملفات التكوين YAML"""
        # التحقق من وجود ملفات التكوين
        main_config_path = os.path.join(yaml_config_dir, "agents.yaml")
        agent_c_config_path = os.path.join(yaml_config_dir, "agents", "agent_c.yaml")

        assert os.path.exists(main_config_path)
        assert os.path.exists(agent_c_config_path)

        # تحميل ملفات التكوين
        with open(main_config_path, "r", encoding="utf-8") as f:
            main_config = yaml.safe_load(f)

        with open(agent_c_config_path, "r", encoding="utf-8") as f:
            agent_c_config = yaml.safe_load(f)

        # التحقق من محتوى ملفات التكوين
        assert "general" in main_config
        assert "agents" in main_config
        assert len(main_config["agents"]) == 4

        assert agent_c_config["name"] == "agent_c"
        assert agent_c_config["type"] == "MockAgentC"
        assert agent_c_config["parameters"]["param1"] == "value1"
        assert agent_c_config["parameters"]["param2"] == "value2"

    def test_agent_creation(self):
        """اختبار إنشاء الوكلاء"""
        # إنشاء وكلاء مباشرة
        agent_a = MockAgentA(name="agent_a")
        agent_b = MockAgentB(name="agent_b")
        agent_c = MockAgentC(name="agent_c", param1="value1", param2="value2")

        # التحقق من خصائص الوكلاء
        assert agent_a.name == "agent_a"
        assert agent_b.name == "agent_b"
        assert agent_c.name == "agent_c"
        assert agent_c.param1 == "value1"
        assert agent_c.param2 == "value2"

        # التحقق من نتائج المعالجة
        result_a = agent_a.process("test query")
        result_b = agent_b.process("test query")
        result_c = agent_c.process("test query")

        assert result_a["result"] == "A"
        assert result_b["result"] == "B"
        assert result_c["result"] == "C"
        assert result_c["params"]["param1"] == "value1"
        assert result_c["params"]["param2"] == "value2"

    def test_agent_registration(self):
        """اختبار تسجيل الوكلاء في النظام"""
        # إنشاء نظام وكلاء متعددين
        system = MultiAgentSystem()

        # إنشاء وكلاء
        agent_a = MockAgentA(name="agent_a")
        agent_b = MockAgentB(name="agent_b")
        agent_c = MockAgentC(name="agent_c", param1="value1", param2="value2")

        # تسجيل الوكلاء في النظام
        system.register_agent(agent_a)
        system.register_agent(agent_b)
        system.register_agent(agent_c)

        # التحقق من تسجيل الوكلاء
        assert len(system.agents) == 3
        assert "agent_a" in system.agents
        assert "agent_b" in system.agents
        assert "agent_c" in system.agents

        # التحقق من نوع الوكلاء المسجلين
        assert isinstance(system.agents["agent_a"], MockAgentA)
        assert isinstance(system.agents["agent_b"], MockAgentB)
        assert isinstance(system.agents["agent_c"], MockAgentC)

        # التحقق من خصائص الوكلاء المسجلين
        assert system.agents["agent_c"].param1 == "value1"
        assert system.agents["agent_c"].param2 == "value2"

        # اختبار إزالة وكيل
        system.remove_agent("agent_b")
        assert len(system.agents) == 2
        assert "agent_b" not in system.agents

        # اختبار الحصول على وكيل
        agent = system.get_agent("agent_c")
        assert agent.name == "agent_c"
        assert agent.param1 == "value1"

        # اختبار معالجة استعلام
        results = system.process_query("test query")
        assert "agent_a" in results
        assert "agent_c" in results
        assert "agent_b" not in results
        assert results["agent_a"]["result"] == "A"
        assert results["agent_c"]["result"] == "C"
