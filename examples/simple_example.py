#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
مثال بسيط لاستخدام نظام الوكلاء المتعددين

يوضح هذا المثال كيفية استخدام نظام الوكلاء المتعددين بطريقة بسيطة
"""

import os
import sys
import logging

# إضافة المسار الرئيسي للمشروع
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.ai.multi_agent_system import MultiAgentSystem, Agent

# إعداد التسجيل
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


# إنشاء وكيل بسيط للاختبار
class SimpleTestAgent(Agent):
    """وكيل بسيط للاختبار"""

    def process(self, query, context=None):
        """معالجة الاستعلام"""
        return {"agent": self.name, "result": f"معالجة الاستعلام: {query}", "confidence": 0.9}


def example_manual_registration():
    """مثال للتسجيل اليدوي للوكلاء"""
    logger.info("مثال التسجيل اليدوي للوكلاء")

    # إنشاء نظام الوكلاء المتعددين
    system = MultiAgentSystem()

    # إنشاء وكلاء للاختبار
    agent1 = SimpleTestAgent(name="test_agent_1")
    agent2 = SimpleTestAgent(name="test_agent_2")

    # تسجيل الوكلاء في النظام
    system.register_agent(agent1)
    system.register_agent(agent2)

    # طباعة قائمة الوكلاء المسجلين
    logger.info(f"عدد الوكلاء المسجلين: {len(system.agents)}")
    logger.info(f"الوكلاء المسجلين: {list(system.agents.keys())}")

    # معالجة استعلام باستخدام الوكلاء المسجلين
    query = "ما هي الآيات التي تتحدث عن خلق الإنسان؟"
    logger.info(f"معالجة الاستعلام: {query}")

    results = system.process_query(query)

    # طباعة النتائج
    for agent_name, result in results.items():
        logger.info(f"نتيجة الوكيل {agent_name}: {result}")

    return system


def example_auto_registration():
    """مثال للتسجيل التلقائي للوكلاء"""
    logger.info("مثال التسجيل التلقائي للوكلاء")

    # إنشاء نظام الوكلاء المتعددين مع تفعيل التسجيل التلقائي
    system = MultiAgentSystem(auto_register=True)

    # طباعة قائمة الوكلاء المسجلين
    logger.info(f"عدد الوكلاء المسجلين: {len(system.agents)}")
    logger.info(f"الوكلاء المسجلين: {list(system.agents.keys())}")

    # معالجة استعلام باستخدام الوكلاء المسجلين
    if system.agents:
        query = "ما هي الآيات التي تتحدث عن خلق السماوات والأرض؟"
        logger.info(f"معالجة الاستعلام: {query}")

        results = system.process_query(query)

        # طباعة النتائج
        for agent_name, result in results.items():
            logger.info(f"نتيجة الوكيل {agent_name}: {result}")
    else:
        logger.warning("لم يتم تسجيل أي وكلاء تلقائياً. تأكد من وجود ملف التكوين config/agents.yaml")

    return system


if __name__ == "__main__":
    logger.info("بدء تشغيل المثال البسيط لنظام الوكلاء المتعددين")

    # تنفيذ مثال التسجيل اليدوي
    system1 = example_manual_registration()

    print("\n" + "-" * 80 + "\n")

    # تنفيذ مثال التسجيل التلقائي
    system2 = example_auto_registration()

    logger.info("انتهى المثال البسيط لنظام الوكلاء المتعددين")
