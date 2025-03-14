#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
مثال لاستخدام آلية التسجيل التلقائي للوكلاء

يوضح هذا المثال كيفية استخدام آلية التسجيل التلقائي للوكلاء من ملفات YAML
"""

import os
import sys
import logging

# إضافة المسار الرئيسي للمشروع
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.ai.multi_agent_system import MultiAgentSystem
from core.ai.agent_loader import AgentLoader, auto_register_agents

# إعداد التسجيل
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def example_auto_register():
    """
    مثال للتسجيل التلقائي للوكلاء عند إنشاء النظام
    """
    logger.info("مثال التسجيل التلقائي للوكلاء عند إنشاء النظام")

    # إنشاء نظام الوكلاء المتعددين مع تفعيل التسجيل التلقائي
    system = MultiAgentSystem(auto_register=True)

    # طباعة قائمة الوكلاء المسجلين
    logger.info(f"عدد الوكلاء المسجلين: {len(system.agents)}")
    logger.info(f"الوكلاء المسجلين: {list(system.agents.keys())}")

    # معالجة استعلام باستخدام الوكلاء المسجلين
    if system.agents:
        results = system.process_query("ما هي الآيات التي تتحدث عن خلق الإنسان؟")
        logger.info(f"نتائج المعالجة: {results}")


def example_register_from_config():
    """
    مثال لتسجيل الوكلاء من ملف تكوين
    """
    logger.info("مثال تسجيل الوكلاء من ملف تكوين")

    # إنشاء نظام الوكلاء المتعددين بدون تسجيل تلقائي
    system = MultiAgentSystem(auto_register=False)

    # التحقق من عدم وجود وكلاء مسجلين
    logger.info(f"عدد الوكلاء المسجلين قبل التسجيل: {len(system.agents)}")

    # تسجيل الوكلاء من ملف التكوين
    registered = system.register_agents_from_config()

    # طباعة قائمة الوكلاء المسجلين
    logger.info(f"عدد الوكلاء المسجلين بعد التسجيل: {len(system.agents)}")
    logger.info(f"الوكلاء المسجلين: {list(system.agents.keys())}")

    # معالجة استعلام باستخدام الوكلاء المسجلين
    if system.agents:
        results = system.process_query("ما هي الآيات التي تتحدث عن خلق السماوات والأرض؟")
        logger.info(f"نتائج المعالجة: {results}")


def example_custom_config():
    """
    مثال لاستخدام ملف تكوين مخصص
    """
    logger.info("مثال استخدام ملف تكوين مخصص")

    # مسار ملف التكوين المخصص
    custom_config_path = "config/custom_agents.yaml"

    # إنشاء نظام الوكلاء المتعددين مع ملف تكوين مخصص
    system = MultiAgentSystem(auto_register=True, config_path=custom_config_path)

    # طباعة قائمة الوكلاء المسجلين
    logger.info(f"عدد الوكلاء المسجلين: {len(system.agents)}")
    logger.info(f"الوكلاء المسجلين: {list(system.agents.keys())}")


def example_manual_agent_loader():
    """
    مثال لاستخدام محمل الوكلاء يدوياً
    """
    logger.info("مثال استخدام محمل الوكلاء يدوياً")

    # إنشاء محمل الوكلاء
    loader = AgentLoader("config/agents.yaml")

    # اكتشاف فئات الوكلاء المتاحة
    agent_classes = loader.discover_agent_classes()
    logger.info(f"فئات الوكلاء المكتشفة: {list(agent_classes.keys())}")

    # إنشاء نظام الوكلاء المتعددين
    system = MultiAgentSystem()

    # تسجيل الوكلاء في النظام
    registered = loader.register_agents(system)
    logger.info(f"تم تسجيل {registered} وكيل بنجاح")
    logger.info(f"الوكلاء المسجلين: {list(system.agents.keys())}")


if __name__ == "__main__":
    logger.info("بدء تشغيل أمثلة التسجيل التلقائي للوكلاء")

    # تنفيذ الأمثلة
    example_auto_register()
    print("\n" + "-" * 80 + "\n")

    example_register_from_config()
    print("\n" + "-" * 80 + "\n")

    example_manual_agent_loader()
    print("\n" + "-" * 80 + "\n")

    # تنفيذ مثال ملف التكوين المخصص إذا كان الملف موجوداً
    if os.path.exists("config/custom_agents.yaml"):
        example_custom_config()

    logger.info("انتهت أمثلة التسجيل التلقائي للوكلاء")
