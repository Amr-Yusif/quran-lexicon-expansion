#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
الواجهة الأساسية الموحدة للوكلاء
توفر طبقة تجريد متسقة لجميع أنواع الوكلاء في النظام
"""

import logging
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Union

# إعداد التسجيل
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class BaseAgent(ABC):
    """
    الفئة الأساسية لجميع الوكلاء في النظام
    توفر واجهة موحدة ومتسقة لجميع الوكلاء المتخصصين
    
    الخصائص الرئيسية:
    - توحيد طرق الإدخال والإخراج
    - دعم التكوين والإعدادات
    - الخصائص الوصفية الموحدة
    - آلية تنشيط وإلغاء تنشيط الوكلاء
    """
    
    def __init__(
        self,
        name: str,
        agent_type: str,
        description: str,
        version: str,
        capabilities: List[str],
        config: Optional[Dict[str, Any]] = None
    ):
        """
        تهيئة الوكيل الأساسي
        
        Args:
            name: اسم الوكيل
            agent_type: نوع الوكيل (مثل: تحليل_لغوي، اكتشاف_أنماط، استدلال)
            description: وصف موجز للوكيل
            version: إصدار الوكيل
            capabilities: قائمة بقدرات الوكيل
            config: تكوين إضافي للوكيل (اختياري)
        """
        self.name = name
        self.agent_type = agent_type
        self.description = description
        self.version = version
        self.capabilities = capabilities
        self.config = config or {}
        self.is_active = True
        
        # تسجيل إنشاء الوكيل
        logger.info(f"تم إنشاء وكيل {name} من نوع {agent_type} (إصدار {version})")
    
    @abstractmethod
    def process(self, query: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        معالجة الاستعلام باستخدام قدرات الوكيل
        
        Args:
            query: الاستعلام المراد معالجته
            context: سياق إضافي للمعالجة (اختياري)
            
        Returns:
            نتائج المعالجة بتنسيق موحد
        """
        pass
    
    def activate(self) -> None:
        """تنشيط الوكيل"""
        self.is_active = True
        logger.info(f"تم تنشيط الوكيل: {self.name}")
    
    def deactivate(self) -> None:
        """إلغاء تنشيط الوكيل"""
        self.is_active = False
        logger.info(f"تم إلغاء تنشيط الوكيل: {self.name}")
    
    def get_metadata(self) -> Dict[str, Any]:
        """
        الحصول على البيانات الوصفية للوكيل
        
        Returns:
            البيانات الوصفية للوكيل
        """
        return {
            "name": self.name,
            "type": self.agent_type,
            "description": self.description,
            "version": self.version,
            "is_active": self.is_active
        }
    
    def get_capabilities(self) -> List[str]:
        """
        الحصول على قدرات الوكيل
        
        Returns:
            قائمة بقدرات الوكيل
        """
        return self.capabilities
    
    def update_config(self, config_update: Dict[str, Any]) -> None:
        """
        تحديث تكوين الوكيل
        
        Args:
            config_update: التحديثات المراد تطبيقها على التكوين
        """
        self.config.update(config_update)
        logger.info(f"تم تحديث تكوين الوكيل {self.name}")
    
    def __str__(self) -> str:
        """تمثيل الوكيل كسلسلة نصية"""
        return f"{self.name} ({self.agent_type} agent, v{self.version})"
    
    def __repr__(self) -> str:
        """تمثيل الوكيل للمطورين"""
        return f"BaseAgent(name='{self.name}', type='{self.agent_type}', version='{self.version}')"
