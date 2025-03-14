"""
معالجة اللغة العربية الطبيعية

حزمة توفر أدوات متقدمة لمعالجة اللغة العربية مع التركيز على:
- معالجة جذور الكلمات
- التعامل مع التشكيل
- تحليل الأوزان الصرفية
- استخراج العلاقات اللغوية
"""

from core.nlp.root_extraction import ArabicRootExtractor
from core.nlp.morphology import ArabicMorphologyAnalyzer
from core.nlp.diacritics import DiacriticsProcessor

__all__ = [
    "ArabicRootExtractor",
    "ArabicMorphologyAnalyzer",
    "DiacriticsProcessor",
]
