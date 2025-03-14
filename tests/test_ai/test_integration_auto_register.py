#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
اختبارات تكامل نظام الوكلاء المتعددين مع آلية التحميل التلقائي
"""

import os
import pytest
import tempfile
import yaml
import shutil
from unittest import mock

from core.ai.multi_agent_system import Agent, MultiAgentSystem


# إنشاء فئات وكلاء اختبارية
class TestIntegrationAgent(Agent):
    """وكيل اختباري للتكامل"""

    def __init__(self, name, weight=0.5, capabilities=None):
        super().__init__(name)
        self.weight = weight
        self.capabilities = capabilities or []

    def process(self, query, context=None):
        return {
            "agent": self.name,
            "result": f"معالجة: {query}",
            "weight": self.weight,
            "capabilities": self.capabilities,
        }


# تجهيز مسارات الملفات ومجلدات الاختبار
@pytest.fixture
def setup_test_environment():
    """تجهيز بيئة الاختبار ومسارات الملفات"""
    orig_dir = os.getcwd()
    with tempfile.TemporaryDirectory() as temp_dir:
        # إنشاء هيكل المجلدات
        os.makedirs(os.path.join(temp_dir, "core/ai"), exist_ok=True)
        os.makedirs(os.path.join(temp_dir, "config/agents"), exist_ok=True)

        # إنشاء ملف الوكيل للاختبار
        with open(os.path.join(temp_dir, "core/ai/test_agent.py"), "w", encoding="utf-8") as f:
            f.write("""
from core.ai.multi_agent_system import Agent

class SimpleAgent(Agent):
    def process(self, query, context=None):
        return {"result": "simple agent result"}

class ComplexAgent(Agent):
    def __init__(self, name, param1=None, param2=None):
        super().__init__(name)
        self.param1 = param1
        self.param2 = param2
    
    def process(self, query, context=None):
        return {
            "result": "complex agent result",
            "param1": self.param1,
            "param2": self.param2
        }
""")

        # إنشاء ملفات التكوين
        agents_config = {
            "general": {
                "auto_register": True,
                "config_dir": os.path.join(temp_dir, "config/agents"),
                "default_enabled": True,
                "scan_directories": [os.path.join(temp_dir, "core/ai")],
            },
            "agents": [
                {"name": "simple_agent", "type": "SimpleAgent", "enabled": True},
                {
                    "name": "complex_agent",
                    "type": "ComplexAgent",
                    "enabled": True,
                    "file": "complex_agent.yaml",
                },
            ],
        }

        complex_agent_config = {
            "name": "complex_agent",
            "type": "ComplexAgent",
            "description": "وكيل متقدم للاختبار",
            "enabled": True,
            "parameters": {"param1": "قيمة1", "param2": "قيمة2"},
        }

        # كتابة ملفات التكوين
        with open(os.path.join(temp_dir, "config/agents.yaml"), "w", encoding="utf-8") as f:
            yaml.dump(agents_config, f, allow_unicode=True)

        with open(
            os.path.join(temp_dir, "config/agents/complex_agent.yaml"), "w", encoding="utf-8"
        ) as f:
            yaml.dump(complex_agent_config, f, allow_unicode=True)

        # نسخ الملفات المطلوبة للاختبار
        try:
            os.chdir(temp_dir)

            # إنشاء ملف multi_agent_system.py أساسي للاختبار
            with open(
                os.path.join(temp_dir, "core/ai/multi_agent_system.py"), "w", encoding="utf-8"
            ) as f:
                f.write("""
import logging
import time
from typing import Dict, Any, List

# إعداد التسجيل
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Agent:
    def __init__(self, name):
        self.name = name
    
    def process(self, query, context=None):
        raise NotImplementedError("يجب تنفيذ طريقة process في الفئة المشتقة")

class AgentCoordinator:
    def __init__(self, execution_strategy="parallel", conflict_resolution_strategy="weighted"):
        self.execution_strategy = execution_strategy
        self.conflict_resolution_strategy = conflict_resolution_strategy
    
    def coordinate_agents(self, agents, query, context=None):
        results = {}
        for name, agent in agents.items():
            try:
                results[name] = agent.process(query, context)
            except Exception as e:
                logger.error(f"خطأ في معالجة الوكيل {name}: {str(e)}")
        return results

class MultiAgentSystem:
    def __init__(self, execution_strategy="parallel", conflict_resolution_strategy="weighted", 
                 auto_register=False, config_path='config/agents.yaml'):
        self.agents = {}
        self.coordinator = AgentCoordinator(
            execution_strategy=execution_strategy,
            conflict_resolution_strategy=conflict_resolution_strategy
        )
        self.results_history = []
        
        # التسجيل التلقائي للوكلاء إذا كان مفعلاً
        if auto_register:
            try:
                from core.ai.agent_loader import auto_register_agents
                registered_count = auto_register_agents(self, config_path)
                logger.info(f"تم التسجيل التلقائي لـ {registered_count} وكيل من التكوين")
            except ImportError:
                logger.warning("تعذر استيراد وحدة تحميل الوكلاء. التسجيل التلقائي غير متاح.")
            except Exception as e:
                logger.error(f"خطأ أثناء التسجيل التلقائي للوكلاء: {str(e)}")
    
    def register_agent(self, agent):
        if not hasattr(agent, 'name') or not agent.name:
            raise ValueError("يجب أن يكون للوكيل اسم صالح")
        
        self.agents[agent.name] = agent
        logger.info(f"تم تسجيل الوكيل: {agent.name}")
    
    def remove_agent(self, agent_name):
        if agent_name in self.agents:
            del self.agents[agent_name]
            logger.info(f"تم إزالة الوكيل: {agent_name}")
        else:
            logger.warning(f"الوكيل غير موجود: {agent_name}")
    
    def get_agent(self, agent_name):
        if agent_name not in self.agents:
            raise KeyError(f"الوكيل غير موجود: {agent_name}")
        
        return self.agents[agent_name]
    
    def process_query(self, query, context=None):
        if not self.agents:
            logger.warning("لا توجد وكلاء مسجلين في النظام")
            return {}
        
        logger.info(f"معالجة استعلام: {query[:50]}...")
        
        # تنسيق الوكلاء لمعالجة الاستعلام
        results = self.coordinator.coordinate_agents(self.agents, query, context)
        
        # حفظ النتائج في السجل
        self.results_history.append({
            "query": query,
            "results": results,
            "timestamp": time.time()
        })
        
        return results
    
    def register_agents_from_config(self, config_path='config/agents.yaml'):
        try:
            from core.ai.agent_loader import auto_register_agents
            return auto_register_agents(self, config_path)
        except ImportError:
            logger.warning("تعذر استيراد وحدة تحميل الوكلاء")
            return 0
        except Exception as e:
            logger.error(f"خطأ أثناء تسجيل الوكلاء من التكوين: {str(e)}")
            return 0
""")

            # إنشاء ملف agent_loader.py للاختبار
            with open(
                os.path.join(temp_dir, "core/ai/agent_loader.py"), "w", encoding="utf-8"
            ) as f:
                f.write("""
import logging
import os
import importlib
import inspect
import yaml
import glob
from typing import Dict, List, Any, Optional, Union, Type
from pathlib import Path

from core.ai.multi_agent_system import Agent, MultiAgentSystem

# إعداد التسجيل
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AgentLoader:
    def __init__(self, config_path='config/agents.yaml'):
        self.config_path = config_path
        self.config = self._load_config(config_path)
        self.agent_classes = {}
    
    def _load_config(self, config_path):
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            return config
        except Exception as e:
            logger.error(f"خطأ في تحميل ملف التكوين: {str(e)}")
            return {"general": {}, "agents": []}
    
    def discover_agent_classes(self):
        agent_classes = {}
        
        # مسارات البحث عن الوكلاء
        scan_dirs = self.config.get('general', {}).get('scan_directories', ['core/ai'])
        
        for scan_dir in scan_dirs:
            if not os.path.exists(scan_dir):
                continue
            
            # البحث عن ملفات Python
            py_files = glob.glob(f"{scan_dir}/**/*.py", recursive=True)
            
            for py_file in py_files:
                try:
                    # تحميل الوحدة
                    module_name = os.path.basename(py_file).replace('.py', '')
                    spec = importlib.util.spec_from_file_location(module_name, py_file)
                    if spec is None or spec.loader is None:
                        continue
                    
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    
                    # البحث عن فئات الوكلاء في الوحدة
                    for name, obj in inspect.getmembers(module):
                        if (inspect.isclass(obj) and 
                            issubclass(obj, Agent) and 
                            obj != Agent and 
                            name.endswith('Agent')):
                            agent_classes[name] = obj
                
                except Exception as e:
                    logger.error(f"خطأ في تحميل الوحدة {py_file}: {str(e)}")
        
        self.agent_classes = agent_classes
        return agent_classes
    
    def load_agent_config(self, agent_name, agent_file):
        config_dir = self.config.get('general', {}).get('config_dir', 'config/agents')
        file_path = os.path.join(config_dir, agent_file)
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                agent_config = yaml.safe_load(f)
            return agent_config
        except Exception as e:
            logger.error(f"خطأ في تحميل تكوين الوكيل {agent_name}: {str(e)}")
            return {}
    
    def create_agent(self, agent_type, agent_name, agent_config=None):
        if agent_type not in self.agent_classes:
            logger.error(f"نوع الوكيل غير معروف: {agent_type}")
            return None
        
        agent_class = self.agent_classes[agent_type]
        agent_config = agent_config or {}
        parameters = agent_config.get('parameters', {})
        
        try:
            # إنشاء وكيل بناءً على نوعه واسمه
            if parameters:
                agent = agent_class(name=agent_name, **parameters)
            else:
                agent = agent_class(name=agent_name)
            
            return agent
        
        except Exception as e:
            logger.error(f"خطأ في إنشاء الوكيل {agent_name} من النوع {agent_type}: {str(e)}")
            return None
    
    def register_agents(self, system):
        # اكتشاف فئات الوكلاء المتاحة
        if not self.agent_classes:
            self.discover_agent_classes()
        
        # التأكد من وجود تكوين للوكلاء
        agents_config = self.config.get('agents', [])
        if not agents_config:
            return 0
        
        # تسجيل الوكلاء
        registered_count = 0
        for agent_config in agents_config:
            agent_name = agent_config.get('name')
            agent_type = agent_config.get('type')
            agent_enabled = agent_config.get('enabled', self.config.get('general', {}).get('default_enabled', True))
            
            if not agent_name or not agent_type:
                continue
            
            if not agent_enabled:
                continue
            
            # تحميل ملف تكوين الوكيل إذا كان موجوداً
            detailed_config = None
            if 'file' in agent_config:
                detailed_config = self.load_agent_config(agent_name, agent_config['file'])
            
            # إنشاء الوكيل
            agent = self.create_agent(agent_type, agent_name, detailed_config)
            if agent:
                system.register_agent(agent)
                registered_count += 1
        
        return registered_count

def auto_register_agents(system, config_path='config/agents.yaml'):
    loader = AgentLoader(config_path)
    return loader.register_agents(system)
""")

            yield temp_dir
        finally:
            os.chdir(orig_dir)


# اختبارات التكامل
class TestAutoRegisterIntegration:
    """اختبارات تكامل التسجيل التلقائي للوكلاء"""

    def test_auto_register_on_init(self, setup_test_environment):
        """اختبار التسجيل التلقائي عند تهيئة النظام"""
        # إنشاء النظام مع تفعيل التسجيل التلقائي
        system = MultiAgentSystem(auto_register=True)

        # التحقق من تسجيل الوكلاء
        assert len(system.agents) == 2
        assert "simple_agent" in system.agents
        assert "complex_agent" in system.agents

        # التحقق من خصائص الوكيل المعقد
        complex_agent = system.agents["complex_agent"]
        assert complex_agent.param1 == "قيمة1"
        assert complex_agent.param2 == "قيمة2"

        # معالجة استعلام للتأكد من عمل الوكلاء
        results = system.process_query("استعلام اختباري")
        assert "simple_agent" in results
        assert "complex_agent" in results
        assert results["complex_agent"]["param1"] == "قيمة1"
        assert results["complex_agent"]["param2"] == "قيمة2"

    def test_register_from_config(self, setup_test_environment):
        """اختبار تسجيل الوكلاء من ملف تكوين بعد التهيئة"""
        # إنشاء النظام بدون تسجيل تلقائي
        system = MultiAgentSystem(auto_register=False)

        # التأكد من عدم وجود وكلاء مسجلين
        assert len(system.agents) == 0

        # تسجيل الوكلاء من ملف التكوين
        registered = system.register_agents_from_config()

        # التحقق من تسجيل الوكلاء
        assert registered == 2
        assert len(system.agents) == 2
        assert "simple_agent" in system.agents
        assert "complex_agent" in system.agents

    def test_missing_config_file(self, setup_test_environment):
        """اختبار السلوك عند عدم وجود ملف التكوين"""
        # حذف ملف التكوين
        os.remove("config/agents.yaml")

        # إنشاء النظام مع تفعيل التسجيل التلقائي
        system = MultiAgentSystem(auto_register=True)

        # التأكد من عدم وجود وكلاء مسجلين
        assert len(system.agents) == 0

        # استدعاء التسجيل من تكوين غير موجود
        registered = system.register_agents_from_config("config/nonexistent.yaml")
        assert registered == 0

    def test_integration_with_manual_registration(self, setup_test_environment):
        """اختبار تكامل التسجيل التلقائي مع التسجيل اليدوي"""
        # إنشاء النظام مع تفعيل التسجيل التلقائي
        system = MultiAgentSystem(auto_register=True)

        # التأكد من تسجيل الوكلاء تلقائياً
        assert len(system.agents) == 2

        # تسجيل وكيل إضافي يدوياً
        integration_agent = TestIntegrationAgent(
            name="manual_agent", weight=0.8, capabilities=["test", "integration"]
        )
        system.register_agent(integration_agent)

        # التأكد من إضافة الوكيل اليدوي
        assert len(system.agents) == 3
        assert "manual_agent" in system.agents

        # معالجة استعلام للتأكد من عمل جميع الوكلاء
        results = system.process_query("استعلام اختباري")
        assert "simple_agent" in results
        assert "complex_agent" in results
        assert "manual_agent" in results
        assert results["manual_agent"]["weight"] == 0.8
        assert results["manual_agent"]["capabilities"] == ["test", "integration"]


if __name__ == "__main__":
    pytest.main(["-v", "test_integration_auto_register.py"])
