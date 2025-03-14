#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
اختبارات وكيل المعجزات العلمية (ScientificMiraclesAgent)
"""

import pytest
from unittest.mock import MagicMock, patch
import sys
import os

# إضافة المسار الرئيسي للمشروع إلى مسار البحث للاختبارات
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from core.ai.scientific_miracles_agent import ScientificMiraclesAgent


class TestScientificMiraclesAgent:
    """اختبارات لوكيل المعجزات العلمية"""

    def setup_method(self):
        """إعداد لكل اختبار"""
        self.agent = ScientificMiraclesAgent(name="test_scientific_agent")

    def test_initialization(self):
        """اختبار تهيئة الوكيل"""
        assert self.agent.name == "test_scientific_agent"
        assert len(self.agent.scientific_domains) > 0
        assert len(self.agent.domain_keywords) > 0

        # التحقق من وجود مجالات علمية مختلفة
        assert "astronomy" in self.agent.scientific_domains
        assert "biology" in self.agent.scientific_domains
        assert "embryology" in self.agent.scientific_domains

        # التحقق من وجود كلمات مفتاحية لكل مجال
        for domain in self.agent.scientific_domains:
            assert domain in self.agent.domain_keywords
            assert len(self.agent.domain_keywords[domain]) > 0

    def test_identify_relevant_domains(self):
        """اختبار تحديد المجالات العلمية ذات الصلة"""
        # استعلام يحتوي على كلمات مفتاحية من مجال الفلك
        query1 = "الآيات التي تتحدث عن السماء والنجوم"
        domains1 = self.agent._identify_relevant_domains(query1)
        assert "astronomy" in domains1

        # استعلام يحتوي على كلمات مفتاحية من مجال علم الأجنة
        query2 = "مراحل تكوين الجنين في القرآن"
        domains2 = self.agent._identify_relevant_domains(query2)
        assert "embryology" in domains2

        # استعلام لا يحتوي على كلمات مفتاحية محددة
        query3 = "آيات من سورة البقرة"
        domains3 = self.agent._identify_relevant_domains(query3)
        # يجب أن تكون جميع المجالات
        assert set(domains3) == set(self.agent.scientific_domains)

    def test_identify_scientific_verses(self):
        """اختبار تحديد الآيات ذات المحتوى العلمي"""
        # الحصول على الكلمات المفتاحية الفعلية من الوكيل
        keywords = []
        for domain in ["astronomy", "geology"]:
            keywords.extend(self.agent.domain_keywords[domain])

        # إنشاء قائمة من الآيات الافتراضية باستخدام الكلمات المفتاحية الفعلية
        verses = [
            {"id": "2:164", "text": f"إن في خلق {keywords[0]} والأرض واختلاف الليل والنهار..."},
            {
                "id": "21:30",
                "text": f"أولم ير الذين كفروا أن {keywords[0]} {keywords[5]} كانتا رتقاً ففتقناهما...",
            },
            {"id": "36:38", "text": f"و{keywords[2]} تجري لمستقر لها ذلك تقدير العزيز العليم"},
            {"id": "2:22", "text": "آية لا تحتوي على محتوى علمي واضح"},
        ]

        # تحديد المجالات
        domains = ["astronomy", "geology"]

        # تحديد الآيات العلمية
        scientific_verses = self.agent._identify_scientific_verses(verses, domains)

        # التحقق من النتائج
        assert len(scientific_verses) > 0

        # التحقق من وجود الكلمات المفتاحية
        for verse in scientific_verses:
            assert "domain_keywords" in verse
            assert len(verse["domain_keywords"]) > 0

        # التحقق من أن الآية الرابعة غير موجودة
        verse_ids = [v["id"] for v in scientific_verses]
        assert "2:22" not in verse_ids

    def test_analyze_scientific_content(self):
        """اختبار تحليل المحتوى العلمي"""
        # استخدام كلمات مفتاحية حقيقية من الوكيل
        astronomy_keyword = self.agent.domain_keywords["astronomy"][0]  # السماء
        geology_keyword = self.agent.domain_keywords["geology"][0]  # الأرض

        # إنشاء قائمة من الآيات العلمية
        scientific_verses = [
            {
                "id": "21:30",
                "text": f"أولم ير الذين كفروا أن {astronomy_keyword} و{geology_keyword} كانتا رتقاً ففتقناهما...",
                "domain_keywords": [astronomy_keyword, geology_keyword],
            },
            {
                "id": "36:38",
                "text": f"والشمس تجري لمستقر لها ذلك تقدير العزيز العليم",
                "domain_keywords": [self.agent.domain_keywords["astronomy"][2]],  # الشمس
            },
        ]

        # تحديد المجالات
        domains = ["astronomy", "geology"]

        # تحليل المحتوى العلمي
        analysis = self.agent._analyze_scientific_content(scientific_verses, domains)

        # التحقق من النتائج
        assert len(analysis) > 0

        # التحقق من وجود مجال الفلك
        assert "astronomy" in analysis or "geology" in analysis

        # التحقق من محتوى التحليل للمجال الأول الموجود
        domain = next(iter(analysis.keys()))
        domain_analysis = analysis[domain]
        assert "verses_count" in domain_analysis
        assert "key_concepts" in domain_analysis
        assert "scientific_principles" in domain_analysis
        assert len(domain_analysis["key_concepts"]) > 0
        assert len(domain_analysis["scientific_principles"]) > 0

    def test_correlate_with_modern_science(self):
        """اختبار ربط الآيات بالاكتشافات العلمية الحديثة"""
        # استخدام كلمات مفتاحية حقيقية من الوكيل
        astronomy_keyword = self.agent.domain_keywords["astronomy"][0]  # السماء
        geology_keyword = self.agent.domain_keywords["geology"][0]  # الأرض

        # إنشاء قائمة من الآيات العلمية
        scientific_verses = [
            {
                "id": "21:30",
                "text": f"أولم ير الذين كفروا أن {astronomy_keyword} و{geology_keyword} كانتا رتقاً ففتقناهما...",
                "domain_keywords": [astronomy_keyword, geology_keyword],
            }
        ]

        # تحديد المجالات
        domains = ["astronomy"]

        # ربط الآيات بالاكتشافات العلمية
        correlations = self.agent._correlate_with_modern_science(scientific_verses, domains)

        # التحقق من النتائج
        assert len(correlations) > 0
        assert "astronomy" in correlations

        # التحقق من محتوى الربط
        astronomy_correlations = correlations["astronomy"]
        assert len(astronomy_correlations) > 0
        assert "discovery" in astronomy_correlations[0]
        assert "year" in astronomy_correlations[0]
        assert "scientist" in astronomy_correlations[0]

    def test_evaluate_compatibility(self):
        """اختبار تقييم التوافق بين الآيات والاكتشافات العلمية"""
        # إنشاء نتائج تحليل علمي افتراضية
        scientific_analysis = {
            "astronomy": {
                "verses_count": 3,
                "verses": [],
                "key_concepts": ["توسع الكون", "حركة الأجرام السماوية"],
                "scientific_principles": ["توسع الكون المستمر"],
            },
            "geology": {
                "verses_count": 1,
                "verses": [],
                "key_concepts": ["تكوين الجبال"],
                "scientific_principles": ["وظيفة الجبال كأوتاد"],
            },
        }

        # تقييم التوافق
        compatibility = self.agent._evaluate_compatibility(scientific_analysis)

        # التحقق من النتائج
        assert len(compatibility) > 0
        assert "astronomy" in compatibility
        assert "geology" in compatibility
        assert "overall" in compatibility

        # التحقق من درجات التوافق
        assert 0 <= compatibility["astronomy"] <= 1
        assert 0 <= compatibility["geology"] <= 1
        assert 0 <= compatibility["overall"] <= 1

        # التحقق من أن درجة التوافق لمجال الفلك أعلى من مجال الجيولوجيا (بسبب عدد الآيات الأكبر)
        assert compatibility["astronomy"] > compatibility["geology"]

    def test_process_query(self):
        """اختبار معالجة استعلام كامل"""
        # إنشاء استعلام
        query = "الآيات التي تتحدث عن السماء والنجوم والكون"

        # استخدام كلمات مفتاحية حقيقية من الوكيل
        astronomy_keyword = self.agent.domain_keywords["astronomy"][0]  # السماء
        star_keyword = next(
            (kw for kw in self.agent.domain_keywords["astronomy"] if "نجم" in kw or "نجوم" in kw),
            "نجوم",
        )
        universe_keyword = next(
            (kw for kw in self.agent.domain_keywords["astronomy"] if "كون" in kw), "كون"
        )

        # إنشاء سياق مع آيات افتراضية تحتوي على الكلمات المفتاحية
        context = {
            "verses": [
                {
                    "id": "21:30",
                    "text": f"أولم ير الذين كفروا أن {astronomy_keyword} والأرض كانتا رتقاً ففتقناهما...",
                },
                {
                    "id": "41:11",
                    "text": f"ثم استوى إلى {astronomy_keyword} وهي دخان فقال لها وللأرض ائتيا طوعاً أو كرهاً...",
                },
                {"id": "51:47", "text": f"و{astronomy_keyword} بنيناها بأيد وإنا لموسعون"},
                {"id": "86:3", "text": f"وال{star_keyword} الثاقب"},
                {"id": "55:7", "text": f"وال{astronomy_keyword} رفعها ووضع الميزان"},
            ]
        }

        # معالجة الاستعلام
        result = self.agent.process(query, context)

        # التحقق من النتائج
        assert "relevant_domains" in result
        assert "astronomy" in result["relevant_domains"]

        assert "scientific_verses" in result
        assert len(result["scientific_verses"]) > 0

        assert "scientific_analysis" in result
        assert "astronomy" in result["scientific_analysis"]

        assert "scientific_correlations" in result
        assert "astronomy" in result["scientific_correlations"]

        assert "compatibility_score" in result
        assert "overall" in result["compatibility_score"]

        assert "confidence" in result
        assert 0 <= result["confidence"] <= 1

        assert "metadata" in result
        assert result["metadata"]["agent"] == "test_scientific_agent"

    def test_empty_context(self):
        """اختبار معالجة استعلام بدون سياق"""
        # إنشاء استعلام
        query = "الآيات التي تتحدث عن السماء والنجوم"

        # معالجة الاستعلام بدون سياق
        result = self.agent.process(query)

        # التحقق من النتائج
        assert "relevant_domains" in result
        assert "astronomy" in result["relevant_domains"]

        assert "scientific_verses" in result
        assert len(result["scientific_verses"]) == 0  # لا توجد آيات للتحليل

        assert "scientific_analysis" in result
        assert "scientific_correlations" in result
        assert "compatibility_score" in result
        assert "confidence" in result
        assert "metadata" in result
