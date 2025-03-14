#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
وحدة تحميل الوكلاء من ملفات التكوين

توفر آليات لاكتشاف وتحميل وتكوين الوكلاء تلقائياً من ملفات YAML
"""

import logging
import os
import importlib
import importlib.util
import inspect
import yaml
import glob
from typing import Dict, List, Any, Optional, Union, Type
from pathlib import Path

from core.ai.multi_agent_system import Agent, MultiAgentSystem

# إعداد التسجيل
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class AgentLoader:
    """
    فئة تحميل الوكلاء وتهيئتها من ملفات YAML
    """

    def __init__(self, config_path: str = "config/agents.yaml"):
        """
        تهيئة محمل الوكلاء

        Args:
            config_path: مسار ملف تكوين الوكلاء الرئيسي
        """
        self.config_path = config_path
        self.config = self._load_config(config_path)
        self.agent_classes = {}
        logger.info(f"تم تهيئة محمل الوكلاء من المسار: {config_path}")

    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """
        تحميل ملف التكوين الرئيسي

        Args:
            config_path: مسار ملف التكوين

        Returns:
            بيانات التكوين
        """
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                config = yaml.safe_load(f)
            logger.info(f"تم تحميل ملف التكوين: {config_path}")
            return config
        except Exception as e:
            logger.error(f"خطأ في تحميل ملف التكوين: {str(e)}")
            return {"general": {}, "agents": []}

    def discover_agent_classes(self) -> Dict[str, Type[Agent]]:
        """
        اكتشاف فئات الوكلاء المتاحة في المسارات المحددة

        Returns:
            قاموس بفئات الوكلاء المكتشفة
        """
        agent_classes = {}

        # مسارات البحث عن الوكلاء
        scan_dirs = self.config.get("general", {}).get("scan_directories", ["core/ai"])

        for scan_dir in scan_dirs:
            logger.info(f"جاري البحث عن الوكلاء في: {scan_dir}")

            # التأكد من وجود المسار
            if not os.path.exists(scan_dir):
                logger.warning(f"المسار غير موجود: {scan_dir}")
                continue

            # البحث عن ملفات Python
            py_files = glob.glob(f"{scan_dir}/**/*.py", recursive=True)

            for py_file in py_files:
                try:
                    # تحويل مسار الملف إلى اسم الوحدة
                    module_path = py_file.replace("/", ".").replace("\\", ".").replace(".py", "")

                    # تحميل الوحدة
                    spec = importlib.util.spec_from_file_location(module_path, py_file)
                    if spec is None or spec.loader is None:
                        continue

                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)

                    # البحث عن فئات الوكلاء في الوحدة
                    for name, obj in inspect.getmembers(module):
                        if (
                            inspect.isclass(obj)
                            and issubclass(obj, Agent)
                            and obj != Agent
                            and name.endswith("Agent")
                        ):
                            agent_classes[name] = obj
                            logger.info(f"تم اكتشاف فئة وكيل: {name}")

                except Exception as e:
                    logger.error(f"خطأ في تحميل الوحدة {py_file}: {str(e)}")

        self.agent_classes = agent_classes
        return agent_classes

    def load_agent_config(self, agent_name: str, agent_file: str) -> Dict[str, Any]:
        """
        تحميل تكوين وكيل معين من ملف

        Args:
            agent_name: اسم الوكيل
            agent_file: مسار ملف تكوين الوكيل

        Returns:
            بيانات تكوين الوكيل
        """
        config_dir = self.config.get("general", {}).get("config_dir", "config/agents")
        file_path = Path(config_dir) / agent_file

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                agent_config = yaml.safe_load(f)
            logger.info(f"تم تحميل تكوين الوكيل {agent_name} من: {file_path}")
            return agent_config
        except Exception as e:
            logger.error(f"خطأ في تحميل تكوين الوكيل {agent_name}: {str(e)}")
            return {}

    def create_agent(
        self, agent_type: str, agent_name: str, agent_config: Dict[str, Any] = None
    ) -> Optional[Agent]:
        """
        إنشاء وكيل بناءً على نوعه وتكوينه

        Args:
            agent_type: نوع الوكيل
            agent_name: اسم الوكيل
            agent_config: تكوين الوكيل

        Returns:
            وكيل مهيأ، أو None في حالة الفشل
        """
        if agent_type not in self.agent_classes:
            logger.error(f"نوع الوكيل غير معروف: {agent_type}")
            return None

        agent_class = self.agent_classes[agent_type]
        agent_config = agent_config or {}
        parameters = agent_config.get("parameters", {})

        try:
            # إنشاء وكيل بناءً على نوعه واسمه
            if parameters:
                agent = agent_class(name=agent_name, **parameters)
            else:
                agent = agent_class(name=agent_name)

            logger.info(f"تم إنشاء وكيل من النوع {agent_type} باسم {agent_name}")
            return agent

        except Exception as e:
            logger.error(f"خطأ في إنشاء الوكيل {agent_name} من النوع {agent_type}: {str(e)}")
            return None

    def register_agents(self, system: MultiAgentSystem) -> int:
        """
        تسجيل جميع الوكلاء في نظام الوكلاء المتعددين

        Args:
            system: نظام الوكلاء المتعددين

        Returns:
            عدد الوكلاء التي تم تسجيلها بنجاح
        """
        # اكتشاف فئات الوكلاء المتاحة
        if not self.agent_classes:
            self.discover_agent_classes()

        # التأكد من وجود تكوين للوكلاء
        agents_config = self.config.get("agents", {})
        if not agents_config:
            logger.warning("لا يوجد تكوين للوكلاء في ملف التكوين")
            return 0

        # تسجيل الوكلاء
        registered_count = 0
        for agent_name, agent_config in agents_config.items():
            agent_type = agent_config.get("type")
            agent_enabled = agent_config.get(
                "enabled", self.config.get("general", {}).get("default_enabled", True)
            )

            if not agent_type:
                logger.warning(f"تكوين الوكيل غير صالح: {agent_config}")
                continue

            if not agent_enabled:
                logger.info(f"الوكيل معطل: {agent_name}")
                continue

            # تحميل ملف تكوين الوكيل إذا كان موجوداً
            detailed_config = None
            if "config_file" in agent_config:
                detailed_config = self.load_agent_config(agent_name, agent_config["config_file"])

            # إنشاء الوكيل
            agent = self.create_agent(agent_type, agent_name, detailed_config)
            if agent:
                system.register_agent(agent)
                registered_count += 1

        logger.info(f"تم تسجيل {registered_count} وكيل بنجاح")
        return registered_count


def auto_register_agents(system: MultiAgentSystem, config_path: str = "config/agents.yaml") -> int:
    """
    تسجيل الوكلاء تلقائياً في نظام الوكلاء المتعددين

    Args:
        system: نظام الوكلاء المتعددين
        config_path: مسار ملف تكوين الوكلاء الرئيسي

    Returns:
        عدد الوكلاء التي تم تسجيلها بنجاح
    """
    loader = AgentLoader(config_path)
    return loader.register_agents(system)
