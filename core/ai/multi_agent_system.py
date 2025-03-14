#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
نظام الوكلاء المتعددين للتحليل المتكامل للنصوص الإسلامية
يوفر إطارًا لتنسيق عمل وكلاء متخصصين في مختلف جوانب التحليل
"""

import logging
from typing import Dict, List, Any, Optional, Union, Callable
import time
import json
from pathlib import Path

# إعداد التسجيل
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class Agent:
    """
    فئة أساسية للوكلاء المتخصصين
    يجب أن يرث منها كل وكيل متخصص ويعيد تعريف طريقة المعالجة
    """

    def __init__(self, name: str):
        """
        تهيئة الوكيل

        Args:
            name: اسم الوكيل
        """
        self.name = name
        logger.info(f"تم إنشاء الوكيل: {name}")

    def process(self, query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        معالجة استعلام

        Args:
            query: الاستعلام المراد معالجته
            context: سياق إضافي للمعالجة (اختياري)

        Returns:
            نتائج المعالجة
        """
        raise NotImplementedError("يجب تنفيذ هذه الطريقة في الفئات الفرعية")


class AgentCoordinator:
    """
    منسق الوكلاء المتعددين
    مسؤول عن تنسيق عمل الوكلاء وتجميع نتائجهم
    """

    def __init__(
        self, execution_strategy: str = "parallel", conflict_resolution_strategy: str = "weighted"
    ):
        """
        تهيئة منسق الوكلاء

        Args:
            execution_strategy: استراتيجية تنفيذ الوكلاء (متوازي أو متسلسل)
            conflict_resolution_strategy: استراتيجية حل التعارضات (weighted, majority, trust_based)
        """
        self.execution_strategy = execution_strategy
        self.conflict_resolution_strategy = conflict_resolution_strategy
        self.agent_weights = {}  # أوزان الوكلاء لاستراتيجية الترجيح
        self.agent_trust_scores = {}  # درجات الثقة في الوكلاء لاستراتيجية الثقة
        logger.info(
            f"تم إنشاء منسق الوكلاء باستراتيجية تنفيذ: {execution_strategy} واستراتيجية حل تعارضات: {conflict_resolution_strategy}"
        )

    def set_agent_weights(self, weights: Dict[str, float]) -> None:
        """
        تعيين أوزان الوكلاء لاستراتيجية الترجيح

        Args:
            weights: قاموس يحتوي على أوزان الوكلاء (اسم الوكيل: الوزن)
        """
        self.agent_weights = weights
        logger.info(f"تم تعيين أوزان الوكلاء: {weights}")

    def set_agent_trust_scores(self, trust_scores: Dict[str, float]) -> None:
        """
        تعيين درجات الثقة في الوكلاء لاستراتيجية الثقة

        Args:
            trust_scores: قاموس يحتوي على درجات الثقة في الوكلاء (اسم الوكيل: درجة الثقة)
        """
        self.agent_trust_scores = trust_scores
        logger.info(f"تم تعيين درجات الثقة في الوكلاء: {trust_scores}")

    def update_agent_trust_score(
        self, agent_name: str, performance_score: float, learning_rate: float = 0.1
    ) -> None:
        """
        تحديث درجة الثقة في وكيل بناءً على أدائه

        Args:
            agent_name: اسم الوكيل
            performance_score: درجة أداء الوكيل (0.0 إلى 1.0)
            learning_rate: معدل التعلم لتحديث درجة الثقة
        """
        current_score = self.agent_trust_scores.get(agent_name, 0.5)  # القيمة الافتراضية هي 0.5
        new_score = current_score * (1 - learning_rate) + performance_score * learning_rate
        self.agent_trust_scores[agent_name] = new_score
        logger.info(
            f"تم تحديث درجة الثقة في الوكيل {agent_name} من {current_score:.2f} إلى {new_score:.2f}"
        )

    def coordinate_agents(
        self, agents: Dict[str, Agent], query: str, context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        تنسيق عمل الوكلاء ومعالجة الاستعلام

        Args:
            agents: قاموس الوكلاء المتاحين
            query: الاستعلام المراد معالجته
            context: سياق إضافي للمعالجة (اختياري)

        Returns:
            نتائج معالجة جميع الوكلاء
        """
        if not agents:
            logger.warning("لا توجد وكلاء متاحين للتنسيق")
            return {}

        results = {}
        context = context or {}

        logger.info(f"بدء تنسيق {len(agents)} وكلاء لمعالجة الاستعلام: {query[:50]}...")

        # استراتيجية التنفيذ المتسلسل
        if self.execution_strategy == "sequential":
            for agent_name, agent in agents.items():
                try:
                    start_time = time.time()
                    agent_result = agent.process(query, context)
                    elapsed_time = time.time() - start_time

                    results[agent_name] = agent_result
                    logger.info(f"اكتمل وكيل {agent_name} في {elapsed_time:.2f} ثانية")

                    # تحديث السياق بنتائج هذا الوكيل للوكلاء اللاحقين
                    context[agent_name] = agent_result

                except Exception as e:
                    logger.error(f"خطأ في وكيل {agent_name}: {str(e)}")
                    results[agent_name] = {"error": str(e)}

        # استراتيجية التنفيذ المتوازي (تنفيذ بسيط بدون تعدد مسارات حقيقي)
        else:  # parallel
            for agent_name, agent in agents.items():
                try:
                    start_time = time.time()
                    agent_result = agent.process(query, context.copy())  # نسخة من السياق لكل وكيل
                    elapsed_time = time.time() - start_time

                    results[agent_name] = agent_result
                    logger.info(f"اكتمل وكيل {agent_name} في {elapsed_time:.2f} ثانية")

                except Exception as e:
                    logger.error(f"خطأ في وكيل {agent_name}: {str(e)}")
                    results[agent_name] = {"error": str(e)}

        logger.info(f"اكتمل تنسيق الوكلاء، تم جمع {len(results)} نتائج")

        # تطبيق استراتيجية حل التعارضات إذا كان هناك أكثر من وكيل
        if len(results) > 1:
            synthesized_results = self.synthesize_results(results, query)
            results["synthesized"] = synthesized_results
            logger.info("تم توليف النتائج من جميع الوكلاء")

        return results

    def synthesize_results(
        self, agent_results: Dict[str, Dict[str, Any]], query: str = ""
    ) -> Dict[str, Any]:
        """
        توليف النتائج من مختلف الوكلاء وحل التعارضات

        Args:
            agent_results: نتائج الوكلاء المختلفة
            query: الاستعلام الأصلي (اختياري)

        Returns:
            النتائج المولفة
        """
        logger.info("بدء توليف النتائج من الوكلاء المختلفة")

        # تجميع النتائج المشتركة والمتعارضة
        common_findings = {}  # النتائج المشتركة بين الوكلاء
        conflicting_findings = {}  # النتائج المتعارضة

        # استخراج المفاتيح المشتركة بين جميع نتائج الوكلاء
        all_keys = set()
        for agent_name, results in agent_results.items():
            if isinstance(results, dict):
                all_keys.update(results.keys())

        # تصنيف النتائج إلى مشتركة ومتعارضة
        for key in all_keys:
            key_values = {}
            for agent_name, results in agent_results.items():
                if isinstance(results, dict) and key in results:
                    key_values[agent_name] = results[key]

            # إذا كانت جميع القيم متطابقة، فهي نتيجة مشتركة
            if len(set(str(v) for v in key_values.values())) == 1 and key_values:
                common_findings[key] = next(iter(key_values.values()))
            # وإلا، فهي نتيجة متعارضة
            elif key_values:
                conflicting_findings[key] = key_values

        logger.info(
            f"تم العثور على {len(common_findings)} نتائج مشتركة و {len(conflicting_findings)} نتائج متعارضة"
        )

        # حل التعارضات باستخدام الاستراتيجية المحددة
        resolved_conflicts = {}

        if self.conflict_resolution_strategy == "weighted":
            resolved_conflicts = self._resolve_conflicts_weighted(conflicting_findings)
        elif self.conflict_resolution_strategy == "majority":
            resolved_conflicts = self._resolve_conflicts_majority(conflicting_findings)
        elif self.conflict_resolution_strategy == "trust_based":
            resolved_conflicts = self._resolve_conflicts_trust_based(conflicting_findings)
        else:  # استراتيجية افتراضية
            resolved_conflicts = self._resolve_conflicts_weighted(conflicting_findings)

        # دمج النتائج المشتركة والمحلولة
        synthesized_results = {**common_findings, **resolved_conflicts}

        # إضافة بيانات وصفية
        synthesized_results["metadata"] = {
            "synthesis_time": time.time(),
            "num_agents": len(agent_results),
            "common_findings": len(common_findings),
            "resolved_conflicts": len(resolved_conflicts),
            "resolution_strategy": self.conflict_resolution_strategy,
            "query": query[:100] if query else "",
        }

        logger.info(f"اكتمل توليف النتائج، تم دمج {len(synthesized_results) - 1} نتيجة")
        return synthesized_results

    def _resolve_conflicts_weighted(
        self, conflicting_findings: Dict[str, Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        حل التعارضات باستخدام استراتيجية الترجيح

        Args:
            conflicting_findings: النتائج المتعارضة

        Returns:
            النتائج المحلولة
        """
        resolved = {}

        for key, values in conflicting_findings.items():
            # إذا لم تكن هناك أوزان محددة، استخدم أوزان متساوية
            if not self.agent_weights:
                default_weight = 1.0 / len(values)
                weights = {agent: default_weight for agent in values.keys()}
            else:
                # استخدم الأوزان المحددة، مع قيمة افتراضية للوكلاء غير المحددة
                weights = {agent: self.agent_weights.get(agent, 0.1) for agent in values.keys()}

            # حساب الوزن الإجمالي لكل قيمة
            value_weights = {}
            for agent, value in values.items():
                str_value = str(value)
                if str_value not in value_weights:
                    value_weights[str_value] = 0.0
                value_weights[str_value] += weights[agent]

            # اختيار القيمة ذات الوزن الأعلى
            if value_weights:
                best_value_str = max(value_weights.items(), key=lambda x: x[1])[0]
                # تحويل القيمة المختارة إلى نوعها الأصلي إذا أمكن
                for agent, value in values.items():
                    if str(value) == best_value_str:
                        resolved[key] = value
                        break

        return resolved

    def _resolve_conflicts_majority(
        self, conflicting_findings: Dict[str, Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        حل التعارضات باستخدام استراتيجية الأغلبية

        Args:
            conflicting_findings: النتائج المتعارضة

        Returns:
            النتائج المحلولة
        """
        resolved = {}

        for key, values in conflicting_findings.items():
            # عد تكرار كل قيمة
            value_counts = {}
            for value in values.values():
                str_value = str(value)
                if str_value not in value_counts:
                    value_counts[str_value] = 0
                value_counts[str_value] += 1

            # اختيار القيمة الأكثر تكراراً
            if value_counts:
                best_value_str = max(value_counts.items(), key=lambda x: x[1])[0]
                # تحويل القيمة المختارة إلى نوعها الأصلي إذا أمكن
                for value in values.values():
                    if str(value) == best_value_str:
                        resolved[key] = value
                        break

        return resolved

    def _resolve_conflicts_trust_based(
        self, conflicting_findings: Dict[str, Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        حل التعارضات باستخدام استراتيجية الثقة

        Args:
            conflicting_findings: النتائج المتعارضة

        Returns:
            النتائج المحلولة
        """
        resolved = {}

        for key, values in conflicting_findings.items():
            # إذا لم تكن هناك درجات ثقة محددة، استخدم درجات متساوية
            if not self.agent_trust_scores:
                default_trust = 0.5
                trust_scores = {agent: default_trust for agent in values.keys()}
            else:
                # استخدم درجات الثقة المحددة، مع قيمة افتراضية للوكلاء غير المحددة
                trust_scores = {
                    agent: self.agent_trust_scores.get(agent, 0.1) for agent in values.keys()
                }

            # حساب درجة الثقة الإجمالية لكل قيمة
            value_trust = {}
            for agent, value in values.items():
                str_value = str(value)
                if str_value not in value_trust:
                    value_trust[str_value] = 0.0
                value_trust[str_value] += trust_scores[agent]

            # اختيار القيمة ذات درجة الثقة الأعلى
            if value_trust:
                best_value_str = max(value_trust.items(), key=lambda x: x[1])[0]
                # تحويل القيمة المختارة إلى نوعها الأصلي إذا أمكن
                for agent, value in values.items():
                    if str(value) == best_value_str:
                        resolved[key] = value
                        break

        return resolved


class MultiAgentSystem:
    """
    نظام الوكلاء المتعددين
    يدير مجموعة من الوكلاء المتخصصين ويوفر واجهة موحدة للتفاعل معهم
    """

    def __init__(
        self,
        execution_strategy: str = "parallel",
        conflict_resolution_strategy: str = "weighted",
        auto_register: bool = False,
        config_path: str = "config/agents.yaml",
    ):
        """
        تهيئة نظام الوكلاء المتعددين

        Args:
            execution_strategy: استراتيجية تنفيذ الوكلاء (متوازي أو متسلسل)
            conflict_resolution_strategy: استراتيجية حل التعارضات (weighted, majority, trust_based)
            auto_register: تفعيل التسجيل التلقائي للوكلاء
            config_path: مسار ملف تكوين الوكلاء
        """
        self.agents = {}
        self.coordinator = AgentCoordinator(
            execution_strategy=execution_strategy,
            conflict_resolution_strategy=conflict_resolution_strategy,
        )
        self.results_history = []
        logger.info(
            f"تم إنشاء نظام الوكلاء المتعددين باستراتيجية تنفيذ: {execution_strategy} واستراتيجية حل تعارضات: {conflict_resolution_strategy}"
        )

        # التسجيل التلقائي للوكلاء إذا كان مفعلاً
        if auto_register:
            try:
                # استيراد آلية التسجيل التلقائي
                from core.ai.agent_loader import auto_register_agents

                registered_count = auto_register_agents(self, config_path)
                logger.info(f"تم التسجيل التلقائي لـ {registered_count} وكيل من التكوين")
            except ImportError:
                logger.warning("تعذر استيراد وحدة تحميل الوكلاء. التسجيل التلقائي غير متاح.")
            except Exception as e:
                logger.error(f"خطأ أثناء التسجيل التلقائي للوكلاء: {str(e)}")

    def register_agent(self, agent: Agent) -> None:
        """
        تسجيل وكيل في النظام

        Args:
            agent: الوكيل المراد تسجيله
        """
        if not hasattr(agent, "name") or not agent.name:
            raise ValueError("يجب أن يكون للوكيل اسم صالح")

        self.agents[agent.name] = agent
        logger.info(f"تم تسجيل الوكيل: {agent.name}")

    def remove_agent(self, agent_name: str) -> None:
        """
        إزالة وكيل من النظام

        Args:
            agent_name: اسم الوكيل المراد إزالته
        """
        if agent_name in self.agents:
            del self.agents[agent_name]
            logger.info(f"تم إزالة الوكيل: {agent_name}")
        else:
            logger.warning(f"الوكيل غير موجود: {agent_name}")

    def get_agent(self, agent_name: str) -> Agent:
        """
        الحصول على وكيل من النظام

        Args:
            agent_name: اسم الوكيل المطلوب

        Returns:
            الوكيل المطلوب

        Raises:
            KeyError: إذا كان الوكيل غير موجود
        """
        if agent_name not in self.agents:
            raise KeyError(f"الوكيل غير موجود: {agent_name}")

        return self.agents[agent_name]

    def process_query(self, query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        معالجة استعلام باستخدام جميع الوكلاء المسجلين

        Args:
            query: الاستعلام المراد معالجته
            context: سياق إضافي للمعالجة (اختياري)

        Returns:
            نتائج معالجة جميع الوكلاء
        """
        if not self.agents:
            logger.warning("لا توجد وكلاء مسجلين في النظام")
            return {}

        logger.info(f"معالجة استعلام: {query[:50]}...")

        # تنسيق الوكلاء لمعالجة الاستعلام
        results = self.coordinator.coordinate_agents(self.agents, query, context)

        # حفظ النتائج في السجل
        self.results_history.append({"query": query, "results": results, "timestamp": time.time()})

        return results

    def save_results(self, file_path: str) -> bool:
        """
        حفظ نتائج المعالجة في ملف

        Args:
            file_path: مسار الملف

        Returns:
            نجاح العملية
        """
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(self.results_history, f, ensure_ascii=False, indent=2)
            logger.info(f"تم حفظ نتائج المعالجة في: {file_path}")
            return True
        except Exception as e:
            logger.error(f"خطأ في حفظ النتائج: {str(e)}")
            return False

    def load_results(self, file_path: str) -> bool:
        """
        تحميل نتائج المعالجة من ملف

        Args:
            file_path: مسار الملف

        Returns:
            نجاح العملية
        """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                self.results_history = json.load(f)
            logger.info(f"تم تحميل نتائج المعالجة من: {file_path}")
            return True
        except Exception as e:
            logger.error(f"خطأ في تحميل النتائج: {str(e)}")
            return False

    def register_agents_from_config(self, config_path: str = "config/agents.yaml") -> int:
        """
        تسجيل الوكلاء من ملف تكوين

        Args:
            config_path: مسار ملف تكوين الوكلاء

        Returns:
            عدد الوكلاء التي تم تسجيلها بنجاح
        """
        try:
            from core.ai.agent_loader import auto_register_agents

            return auto_register_agents(self, config_path)
        except ImportError:
            logger.warning("تعذر استيراد وحدة تحميل الوكلاء")
            return 0
        except Exception as e:
            logger.error(f"خطأ أثناء تسجيل الوكلاء من التكوين: {str(e)}")
            return 0


# فئات الوكلاء المتخصصين


class LinguisticAgent(Agent):
    """
    وكيل التحليل اللغوي
    متخصص في تحليل النصوص من الناحية اللغوية والبلاغية
    """

    def __init__(self, name: str = "linguistic_agent"):
        """
        تهيئة وكيل التحليل اللغوي

        Args:
            name: اسم الوكيل
        """
        super().__init__(name)

    def process(self, query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        تحليل النص من الناحية اللغوية

        Args:
            query: النص المراد تحليله
            context: سياق إضافي للتحليل (اختياري)

        Returns:
            نتائج التحليل اللغوي
        """
        logger.info(f"وكيل التحليل اللغوي يعالج: {query[:50]}...")

        # هنا يتم استدعاء محلل النصوص الإسلامية
        # في التنفيذ الفعلي، سيتم استخدام محلل النصوص الحقيقي
        # لأغراض هذا المثال، نعيد نتائج بسيطة

        results = {
            "morphological_analysis": {
                "tokens": [],  # تحليل صرفي للكلمات
                "pos_tags": [],  # أقسام الكلام
            },
            "syntactic_analysis": {
                "sentence_structure": [],  # تركيب الجمل
                "dependencies": [],  # العلاقات النحوية
            },
            "rhetorical_analysis": {
                "figures_of_speech": [],  # الصور البلاغية
                "stylistic_features": [],  # السمات الأسلوبية
            },
        }

        return results


class PatternDiscoveryAgent(Agent):
    """
    وكيل اكتشاف الأنماط
    متخصص في اكتشاف الأنماط والعلاقات في النصوص
    """

    def __init__(self, name: str = "pattern_agent"):
        """
        تهيئة وكيل اكتشاف الأنماط

        Args:
            name: اسم الوكيل
        """
        super().__init__(name)

    def process(self, query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        اكتشاف الأنماط في النص

        Args:
            query: النص المراد تحليله
            context: سياق إضافي للتحليل (اختياري)

        Returns:
            الأنماط المكتشفة
        """
        logger.info(f"وكيل اكتشاف الأنماط يعالج: {query[:50]}...")

        # هنا يتم استدعاء مكتشف الأنماط
        # في التنفيذ الفعلي، سيتم استخدام مكتشف الأنماط الحقيقي
        # لأغراض هذا المثال، نعيد نتائج بسيطة

        results = {
            "linguistic_patterns": {
                "repetitions": [],  # التكرارات
                "parallelisms": [],  # التوازيات
            },
            "semantic_patterns": {
                "themes": [],  # المواضيع المتكررة
                "motifs": [],  # العناصر المتكررة
            },
            "structural_patterns": {
                "verse_structures": [],  # هياكل الآيات
                "chapter_structures": [],  # هياكل السور
            },
            "numerical_patterns": {
                "word_counts": {},  # عدد الكلمات
                "letter_counts": {},  # عدد الحروف
            },
        }

        return results


class ReasoningAgent(Agent):
    """
    وكيل الاستدلال
    متخصص في الاستدلال المنطقي واستخلاص النتائج
    """

    def __init__(self, name: str = "reasoning_agent"):
        """
        تهيئة وكيل الاستدلال

        Args:
            name: اسم الوكيل
        """
        super().__init__(name)

    def process(self, query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        الاستدلال المنطقي على النص

        Args:
            query: النص المراد تحليله
            context: سياق إضافي للتحليل (اختياري)

        Returns:
            نتائج الاستدلال
        """
        logger.info(f"وكيل الاستدلال يعالج: {query[:50]}...")

        # استخدام نتائج التحليل اللغوي واكتشاف الأنماط إذا كانت متاحة في السياق
        linguistic_results = {}
        pattern_results = {}

        if context:
            if "linguistic_agent" in context:
                linguistic_results = context["linguistic_agent"]
            if "pattern_agent" in context:
                pattern_results = context["pattern_agent"]

        # هنا يتم استدعاء محرك الاستدلال
        # في التنفيذ الفعلي، سيتم استخدام محرك الاستدلال الحقيقي
        # لأغراض هذا المثال، نعيد نتائج بسيطة

        results = {
            "logical_inferences": [],  # الاستنتاجات المنطقية
            "hypotheses": [],  # الفرضيات
            "conclusions": [],  # الاستنتاجات
            "evidence": [],  # الأدلة
            "confidence_scores": {},  # درجات الثقة
        }

        return results


class SearchAgent(Agent):
    """
    وكيل البحث
    متخصص في البحث الدلالي واسترجاع المعلومات
    """

    def __init__(self, name: str = "search_agent"):
        """
        تهيئة وكيل البحث

        Args:
            name: اسم الوكيل
        """
        super().__init__(name)

    def process(self, query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        البحث الدلالي في النصوص

        Args:
            query: الاستعلام المراد البحث عنه
            context: سياق إضافي للبحث (اختياري)

        Returns:
            نتائج البحث
        """
        logger.info(f"وكيل البحث يعالج: {query[:50]}...")

        # هنا يتم استدعاء محرك البحث الدلالي
        # في التنفيذ الفعلي، سيتم استخدام محرك البحث الحقيقي
        # لأغراض هذا المثال، نعيد نتائج بسيطة

        results = {
            "relevant_verses": [],  # الآيات ذات الصلة
            "relevant_hadiths": [],  # الأحاديث ذات الصلة
            "relevant_tafsir": [],  # التفاسير ذات الصلة
            "relevance_scores": {},  # درجات الصلة
            "search_metadata": {  # بيانات وصفية للبحث
                "query_time": time.time(),
                "total_results": 0,
            },
        }

        return results


class IntegrationAgent(Agent):
    """
    وكيل التكامل
    متخصص في دمج نتائج الوكلاء المختلفة وتقديم تحليل متكامل
    """

    def __init__(self, name: str = "integration_agent"):
        """
        تهيئة وكيل التكامل

        Args:
            name: اسم الوكيل
        """
        super().__init__(name)

    def process(self, query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        دمج نتائج الوكلاء المختلفة

        Args:
            query: الاستعلام الأصلي
            context: سياق يحتوي على نتائج الوكلاء الأخرى

        Returns:
            تحليل متكامل
        """
        logger.info(f"وكيل التكامل يعالج: {query[:50]}...")

        if not context:
            logger.warning("لا يوجد سياق لدمج النتائج")
            return {"error": "لا يوجد سياق لدمج النتائج"}

        # استخراج نتائج الوكلاء المختلفة من السياق
        linguistic_results = context.get("linguistic_agent", {})
        pattern_results = context.get("pattern_agent", {})
        reasoning_results = context.get("reasoning_agent", {})
        search_results = context.get("search_agent", {})

        # دمج النتائج وتقديم تحليل متكامل
        integrated_analysis = {
            "summary": self._generate_summary(
                query, linguistic_results, pattern_results, reasoning_results, search_results
            ),
            "key_insights": self._extract_key_insights(
                linguistic_results, pattern_results, reasoning_results, search_results
            ),
            "supporting_evidence": self._gather_supporting_evidence(
                linguistic_results, pattern_results, reasoning_results, search_results
            ),
            "related_concepts": self._identify_related_concepts(
                linguistic_results, pattern_results, reasoning_results, search_results
            ),
            "recommendations": self._generate_recommendations(
                query, linguistic_results, pattern_results, reasoning_results, search_results
            ),
            "confidence_level": self._calculate_confidence_level(
                linguistic_results, pattern_results, reasoning_results, search_results
            ),
            "metadata": {  # بيانات وصفية
                "integration_time": time.time(),
                "agents_involved": list(context.keys()),
                "integration_version": "1.0",
                "query_length": len(query),
            },
        }

        logger.info(
            f"تم إنتاج تحليل متكامل مع {len(integrated_analysis['key_insights'])} رؤى رئيسية"
        )
        return integrated_analysis

    def _generate_summary(
        self,
        query: str,
        linguistic_results: Dict,
        pattern_results: Dict,
        reasoning_results: Dict,
        search_results: Dict,
    ) -> str:
        """
        توليد ملخص للتحليل المتكامل

        Args:
            query: الاستعلام الأصلي
            linguistic_results: نتائج التحليل اللغوي
            pattern_results: نتائج اكتشاف الأنماط
            reasoning_results: نتائج الاستدلال
            search_results: نتائج البحث

        Returns:
            ملخص التحليل
        """
        # استخراج المعلومات الرئيسية من نتائج الوكلاء المختلفة
        summary_components = []

        # إضافة معلومات من نتائج التحليل اللغوي
        if linguistic_results:
            rhetorical_features = linguistic_results.get("rhetorical_analysis", {}).get(
                "figures_of_speech", []
            )
            if rhetorical_features:
                summary_components.append(f"تم تحديد {len(rhetorical_features)} صور بلاغية في النص")

        # إضافة معلومات من نتائج اكتشاف الأنماط
        if pattern_results:
            themes = pattern_results.get("semantic_patterns", {}).get("themes", [])
            if themes:
                summary_components.append(f"تم اكتشاف {len(themes)} مواضيع رئيسية")

        # إضافة معلومات من نتائج الاستدلال
        if reasoning_results:
            conclusions = reasoning_results.get("conclusions", [])
            if conclusions:
                summary_components.append(f"تم التوصل إلى {len(conclusions)} استنتاجات")

        # إضافة معلومات من نتائج البحث
        if search_results:
            relevant_verses = search_results.get("relevant_verses", [])
            relevant_hadiths = search_results.get("relevant_hadiths", [])
            if relevant_verses or relevant_hadiths:
                summary_components.append(
                    f"تم العثور على {len(relevant_verses)} آية و {len(relevant_hadiths)} حديث ذات صلة"
                )

        # دمج المكونات في ملخص واحد
        if summary_components:
            summary = "تحليل متكامل: " + ". ".join(summary_components) + "."
        else:
            summary = "تم إجراء تحليل متكامل للنص المدخل، ولكن لم يتم العثور على معلومات كافية لتقديم ملخص تفصيلي."

        return summary

    def _extract_key_insights(
        self,
        linguistic_results: Dict,
        pattern_results: Dict,
        reasoning_results: Dict,
        search_results: Dict,
    ) -> List[str]:
        """
        استخراج الرؤى الرئيسية من نتائج الوكلاء المختلفة

        Args:
            linguistic_results: نتائج التحليل اللغوي
            pattern_results: نتائج اكتشاف الأنماط
            reasoning_results: نتائج الاستدلال
            search_results: نتائج البحث

        Returns:
            قائمة بالرؤى الرئيسية
        """
        key_insights = []

        # استخراج رؤى من نتائج التحليل اللغوي
        if linguistic_results:
            rhetorical_features = linguistic_results.get("rhetorical_analysis", {}).get(
                "stylistic_features", []
            )
            for feature in rhetorical_features:
                key_insights.append(f"تحليل لغوي: {feature}")

        # استخراج رؤى من نتائج اكتشاف الأنماط
        if pattern_results:
            themes = pattern_results.get("semantic_patterns", {}).get("themes", [])
            for theme in themes:
                key_insights.append(f"نمط دلالي: {theme}")

        # استخراج رؤى من نتائج الاستدلال
        if reasoning_results:
            inferences = reasoning_results.get("logical_inferences", [])
            for inference in inferences:
                key_insights.append(f"استدلال منطقي: {inference}")

            conclusions = reasoning_results.get("conclusions", [])
            for conclusion in conclusions:
                key_insights.append(f"استنتاج: {conclusion}")

        # إذا لم يتم العثور على رؤى كافية، أضف رسالة افتراضية
        if not key_insights:
            key_insights.append("لم يتم العثور على رؤى رئيسية كافية في النص المدخل")

        return key_insights

    def _gather_supporting_evidence(
        self,
        linguistic_results: Dict,
        pattern_results: Dict,
        reasoning_results: Dict,
        search_results: Dict,
    ) -> List[Dict]:
        """
        جمع الأدلة الداعمة من نتائج الوكلاء المختلفة

        Args:
            linguistic_results: نتائج التحليل اللغوي
            pattern_results: نتائج اكتشاف الأنماط
            reasoning_results: نتائج الاستدلال
            search_results: نتائج البحث

        Returns:
            قائمة بالأدلة الداعمة
        """
        supporting_evidence = []

        # جمع الأدلة من نتائج البحث
        if search_results:
            relevant_verses = search_results.get("relevant_verses", [])
            for verse in relevant_verses:
                supporting_evidence.append(
                    {
                        "type": "verse",
                        "content": verse,
                        "source": "القرآن الكريم",
                        "relevance": search_results.get("relevance_scores", {}).get(verse, 0.0),
                    }
                )

            relevant_hadiths = search_results.get("relevant_hadiths", [])
            for hadith in relevant_hadiths:
                supporting_evidence.append(
                    {
                        "type": "hadith",
                        "content": hadith,
                        "source": "الحديث الشريف",
                        "relevance": search_results.get("relevance_scores", {}).get(hadith, 0.0),
                    }
                )

            relevant_tafsir = search_results.get("relevant_tafsir", [])
            for tafsir in relevant_tafsir:
                supporting_evidence.append(
                    {
                        "type": "tafsir",
                        "content": tafsir,
                        "source": "التفسير",
                        "relevance": search_results.get("relevance_scores", {}).get(tafsir, 0.0),
                    }
                )

        # جمع الأدلة من نتائج الاستدلال
        if reasoning_results:
            evidence_list = reasoning_results.get("evidence", [])
            for evidence in evidence_list:
                supporting_evidence.append(
                    {
                        "type": "reasoning",
                        "content": evidence,
                        "source": "الاستدلال المنطقي",
                        "confidence": reasoning_results.get("confidence_scores", {}).get(
                            evidence, 0.0
                        ),
                    }
                )

        return supporting_evidence

    def _identify_related_concepts(
        self,
        linguistic_results: Dict,
        pattern_results: Dict,
        reasoning_results: Dict,
        search_results: Dict,
    ) -> List[str]:
        """
        تحديد المفاهيم ذات الصلة من نتائج الوكلاء المختلفة

        Args:
            linguistic_results: نتائج التحليل اللغوي
            pattern_results: نتائج اكتشاف الأنماط
            reasoning_results: نتائج الاستدلال
            search_results: نتائج البحث

        Returns:
            قائمة بالمفاهيم ذات الصلة
        """
        related_concepts = set()  # استخدام مجموعة لتجنب التكرار

        # استخراج المفاهيم من نتائج اكتشاف الأنماط
        if pattern_results:
            themes = pattern_results.get("semantic_patterns", {}).get("themes", [])
            for theme in themes:
                related_concepts.add(theme)

            motifs = pattern_results.get("semantic_patterns", {}).get("motifs", [])
            for motif in motifs:
                related_concepts.add(motif)

        # استخراج المفاهيم من نتائج الاستدلال
        if reasoning_results:
            hypotheses = reasoning_results.get("hypotheses", [])
            for hypothesis in hypotheses:
                related_concepts.add(hypothesis)

        return list(related_concepts)

    def _generate_recommendations(
        self,
        query: str,
        linguistic_results: Dict,
        pattern_results: Dict,
        reasoning_results: Dict,
        search_results: Dict,
    ) -> List[str]:
        """
        توليد توصيات بناءً على نتائج الوكلاء المختلفة

        Args:
            query: الاستعلام الأصلي
            linguistic_results: نتائج التحليل اللغوي
            pattern_results: نتائج اكتشاف الأنماط
            reasoning_results: نتائج الاستدلال
            search_results: نتائج البحث

        Returns:
            قائمة بالتوصيات
        """
        recommendations = []

        # توليد توصيات بناءً على نتائج الاستدلال
        if reasoning_results:
            conclusions = reasoning_results.get("conclusions", [])
            for conclusion in conclusions:
                recommendations.append(f"استنادًا إلى الاستنتاجات: {conclusion}")

        # توليد توصيات بناءً على نتائج البحث
        if search_results:
            relevant_tafsir = search_results.get("relevant_tafsir", [])
            if relevant_tafsir:
                recommendations.append("مراجعة التفاسير ذات الصلة للحصول على فهم أعمق")

        # توليد توصيات بناءً على نتائج التحليل اللغوي
        if linguistic_results:
            rhetorical_features = linguistic_results.get("rhetorical_analysis", {}).get(
                "figures_of_speech", []
            )
            if rhetorical_features:
                recommendations.append(
                    "دراسة الصور البلاغية المستخدمة في النص لفهم أبعاده الجمالية"
                )

        # إذا لم يتم توليد توصيات كافية، أضف توصيات افتراضية
        if len(recommendations) < 2:
            recommendations.append("البحث عن مصادر إضافية لتعميق الفهم")
            recommendations.append("مقارنة النتائج مع تفسيرات العلماء المعتمدين")

        return recommendations

    def _calculate_confidence_level(
        self,
        linguistic_results: Dict,
        pattern_results: Dict,
        reasoning_results: Dict,
        search_results: Dict,
    ) -> float:
        """
        حساب مستوى الثقة في التحليل المتكامل

        Args:
            linguistic_results: نتائج التحليل اللغوي
            pattern_results: نتائج اكتشاف الأنماط
            reasoning_results: نتائج الاستدلال
            search_results: نتائج البحث

        Returns:
            مستوى الثقة (0.0 إلى 1.0)
        """
        # تعيين أوزان لمختلف أنواع النتائج
        weights = {"linguistic": 0.2, "pattern": 0.2, "reasoning": 0.3, "search": 0.3}

        confidence_scores = []

        # حساب درجة الثقة من نتائج التحليل اللغوي
        if linguistic_results:
            linguistic_confidence = 0.5  # قيمة افتراضية
            # يمكن تحسين هذا باستخدام معلومات أكثر تفصيلاً من نتائج التحليل اللغوي
            confidence_scores.append(("linguistic", linguistic_confidence))

        # حساب درجة الثقة من نتائج اكتشاف الأنماط
        if pattern_results:
            pattern_confidence = 0.5  # قيمة افتراضية
            # يمكن تحسين هذا باستخدام معلومات أكثر تفصيلاً من نتائج اكتشاف الأنماط
            confidence_scores.append(("pattern", pattern_confidence))

        # حساب درجة الثقة من نتائج الاستدلال
        if reasoning_results:
            reasoning_confidence = 0.0
            confidence_values = reasoning_results.get("confidence_scores", {}).values()
            if confidence_values:
                reasoning_confidence = sum(confidence_values) / len(confidence_values)
            confidence_scores.append(("reasoning", reasoning_confidence))

        # حساب درجة الثقة من نتائج البحث
        if search_results:
            search_confidence = 0.0
            relevance_values = search_results.get("relevance_scores", {}).values()
            if relevance_values:
                search_confidence = sum(relevance_values) / len(relevance_values)
            confidence_scores.append(("search", search_confidence))

        # حساب المتوسط المرجح لدرجات الثقة
        if not confidence_scores:
            return 0.0

        weighted_sum = 0.0
        total_weight = 0.0

        for source, score in confidence_scores:
            weight = weights.get(source, 0.0)
            weighted_sum += score * weight
            total_weight += weight

        if total_weight == 0.0:
            return 0.0

        return weighted_sum / total_weight
