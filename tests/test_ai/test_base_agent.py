#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
اختبارات الواجهة الأساسية الموحدة للوكلاء (BaseAgent)
"""

import pytest
from typing import Dict, List, Any, Optional, Tuple
import json
import os
import sys

# إضافة المسار الرئيسي للمشروع إلى مسار البحث للاختبارات
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from core.ai.base_agent import BaseAgent

class TestBaseAgent:
    """اختبارات للواجهة الأساسية الموحدة للوكلاء"""
    
    def test_base_agent_initialization(self):
        """اختبار تهيئة الوكيل الأساسي مع المعلمات المطلوبة"""
        # تنفيذ فئة وكيل وهمية للاختبار تستند إلى الواجهة الأساسية
        class MockAgent(BaseAgent):
            def process(self, query, context=None):
                return {"result": "mock"}
            
            def get_metadata(self):
                return {"name": self.name, "type": self.agent_type}
            
            def get_capabilities(self):
                return self.capabilities
        
        # إنشاء وكيل وهمي
        agent = MockAgent(
            name="test_agent",
            agent_type="mock",
            description="وكيل اختبار",
            version="1.0.0",
            capabilities=["test"]
        )
        
        # التحقق من تهيئة الخصائص الأساسية
        assert agent.name == "test_agent"
        assert agent.agent_type == "mock"
        assert agent.description == "وكيل اختبار"
        assert agent.version == "1.0.0"
        assert agent.capabilities == ["test"]
        assert agent.is_active is True
    
    def test_optional_parameters(self):
        """اختبار المعلمات الاختيارية في تهيئة الوكيل الأساسي"""
        # تنفيذ فئة وكيل وهمية للاختبار
        class MockAgent(BaseAgent):
            def process(self, query, context=None):
                return {"result": "mock"}
            
            def get_metadata(self):
                return {"name": self.name, "type": self.agent_type}
            
            def get_capabilities(self):
                return self.capabilities
        
        # إنشاء وكيل وهمي بمعلمات إضافية
        config = {
            "api_key": "test_key",
            "max_tokens": 100,
            "temperature": 0.7
        }
        
        agent = MockAgent(
            name="test_agent",
            agent_type="mock",
            description="وكيل اختبار",
            version="1.0.0",
            capabilities=["test"],
            config=config
        )
        
        # التحقق من تهيئة المعلمات الاختيارية
        assert agent.config == config
        assert agent.config["api_key"] == "test_key"
        assert agent.config["max_tokens"] == 100
        assert agent.config["temperature"] == 0.7
    
    def test_abstract_methods(self):
        """اختبار أن الطرق المجردة يجب تنفيذها في الفئات الفرعية"""
        with pytest.raises(TypeError):
            # محاولة إنشاء كائن مباشرة من BaseAgent يجب أن تفشل
            agent = BaseAgent(
                name="test_agent",
                agent_type="abstract",
                description="وكيل مجرد",
                version="1.0.0",
                capabilities=["none"]
            )
    
    def test_process_method_required(self):
        """اختبار أن طريقة process يجب تنفيذها في الفئات الفرعية"""
        # تنفيذ فئة وهمية بدون تنفيذ طريقة process
        class IncompleteAgent(BaseAgent):
            def get_metadata(self):
                return {"name": self.name, "type": self.agent_type}
            
            def get_capabilities(self):
                return self.capabilities
        
        with pytest.raises(TypeError):
            # محاولة إنشاء وكيل بدون تنفيذ process يجب أن تفشل
            agent = IncompleteAgent(
                name="incomplete",
                agent_type="incomplete",
                description="وكيل غير مكتمل",
                version="1.0.0",
                capabilities=["none"]
            )
    
    def test_standard_input_output_interface(self):
        """اختبار واجهة الإدخال/الإخراج الموحدة"""
        class StandardAgent(BaseAgent):
            def process(self, query, context=None):
                # التحقق من أن الإدخال يتبع المعيار المتوقع
                assert isinstance(query, str)
                assert context is None or isinstance(context, dict)
                
                # إرجاع مخرجات موحدة
                return {
                    "result": f"Processed: {query}",
                    "metadata": {
                        "agent": self.name,
                        "type": self.agent_type,
                        "version": self.version
                    }
                }
            
            def get_metadata(self):
                return {"name": self.name, "type": self.agent_type}
            
            def get_capabilities(self):
                return self.capabilities
        
        # إنشاء وكيل قياسي
        agent = StandardAgent(
            name="standard_agent",
            agent_type="standard",
            description="وكيل قياسي",
            version="1.0.0",
            capabilities=["standard_processing"]
        )
        
        # اختبار استدعاء process مع المدخلات القياسية
        query = "اختبار المدخلات"
        context = {"key": "value"}
        
        result = agent.process(query, context)
        
        # التحقق من هيكل المخرجات
        assert isinstance(result, dict)
        assert "result" in result
        assert "metadata" in result
        assert result["metadata"]["agent"] == "standard_agent"
        assert result["metadata"]["type"] == "standard"
    
    def test_activating_deactivating_agent(self):
        """اختبار تنشيط وإلغاء تنشيط الوكيل"""
        class MockAgent(BaseAgent):
            def process(self, query, context=None):
                if not self.is_active:
                    return {"error": "Agent is not active"}
                return {"result": "Processed"}
            
            def get_metadata(self):
                return {"name": self.name, "type": self.agent_type}
            
            def get_capabilities(self):
                return self.capabilities
        
        # إنشاء وكيل
        agent = MockAgent(
            name="test_agent",
            agent_type="mock",
            description="وكيل اختبار",
            version="1.0.0",
            capabilities=["test"]
        )
        
        # التحقق من أن الوكيل نشط افتراضياً
        assert agent.is_active is True
        
        # اختبار المعالجة عندما يكون الوكيل نشطاً
        result = agent.process("test")
        assert result == {"result": "Processed"}
        
        # إلغاء تنشيط الوكيل
        agent.deactivate()
        assert agent.is_active is False
        
        # اختبار المعالجة عندما يكون الوكيل غير نشط
        result = agent.process("test")
        assert result == {"error": "Agent is not active"}
        
        # إعادة تنشيط الوكيل
        agent.activate()
        assert agent.is_active is True
        
        # اختبار المعالجة بعد إعادة التنشيط
        result = agent.process("test")
        assert result == {"result": "Processed"}
