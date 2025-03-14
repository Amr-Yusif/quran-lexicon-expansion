"""
تعريف خطط الاشتراك للمرشد القرآني الذكي
"""
from enum import Enum
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta

class PlanType(Enum):
    """أنواع خطط الاشتراك المتاحة"""
    FREE = "free"
    BASIC = "basic"
    ADVANCED = "advanced"
    SCHOLAR = "scholar"

@dataclass
class Feature:
    """ميزة في خطة اشتراك"""
    name: str
    description: str
    enabled: bool
    limit: Optional[int] = None  # حد للاستخدام، None يعني غير محدود

@dataclass
class SubscriptionPlan:
    """
    تعريف خطة اشتراك
    """
    type: PlanType
    name: str
    description: str
    price_usd: float
    features: List[Feature]
    billing_cycle: str = "monthly"  # monthly, yearly
    
    def get_feature(self, feature_name: str) -> Optional[Feature]:
        """الحصول على ميزة معينة في الخطة"""
        for feature in self.features:
            if feature.name == feature_name:
                return feature
        return None
    
    def is_feature_enabled(self, feature_name: str) -> bool:
        """التحقق مما إذا كانت ميزة معينة مفعلة في الخطة"""
        feature = self.get_feature(feature_name)
        return feature.enabled if feature else False
    
    def get_feature_limit(self, feature_name: str) -> Optional[int]:
        """الحصول على حد استخدام ميزة معينة"""
        feature = self.get_feature(feature_name)
        return feature.limit if feature else None
    
    def to_dict(self) -> Dict:
        """تحويل الخطة إلى قاموس"""
        return {
            "type": self.type.value,
            "name": self.name,
            "description": self.description,
            "price_usd": self.price_usd,
            "features": [
                {
                    "name": f.name,
                    "description": f.description,
                    "enabled": f.enabled,
                    "limit": f.limit
                } for f in self.features
            ],
            "billing_cycle": self.billing_cycle
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'SubscriptionPlan':
        """إنشاء خطة من قاموس"""
        features = [
            Feature(
                name=f["name"],
                description=f["description"],
                enabled=f["enabled"],
                limit=f.get("limit")
            ) for f in data.get("features", [])
        ]
        
        return cls(
            type=PlanType(data["type"]),
            name=data["name"],
            description=data["description"],
            price_usd=data["price_usd"],
            features=features,
            billing_cycle=data.get("billing_cycle", "monthly")
        )

# تعريف الميزات المتاحة في النظام
QURAN_SEARCH = "quran_search"
TAFSEER_ACCESS = "tafseer_access"
HADITH_ACCESS = "hadith_access"
FIQH_ACCESS = "fiqh_access"
SEERA_ACCESS = "seera_access"
PDF_UPLOAD = "pdf_upload"
DAILY_QUERIES = "daily_queries"
SAVED_SEARCHES = "saved_searches"
LLM_ACCESS = "llm_access"
SELF_LEARNING = "self_learning"
EARLY_ACCESS = "early_access"

# تعريف خطط الاشتراك المتاحة
FREE_PLAN = SubscriptionPlan(
    type=PlanType.FREE,
    name="الخطة المجانية",
    description="وصول محدود للبحث في القرآن والتفسير",
    price_usd=0,
    features=[
        Feature(name=QURAN_SEARCH, description="البحث في القرآن الكريم", enabled=True, limit=10),
        Feature(name=TAFSEER_ACCESS, description="الوصول إلى التفاسير", enabled=True, limit=5),
        Feature(name=HADITH_ACCESS, description="الوصول إلى الأحاديث", enabled=False),
        Feature(name=FIQH_ACCESS, description="الوصول إلى الفقه", enabled=False),
        Feature(name=SEERA_ACCESS, description="الوصول إلى السيرة", enabled=False),
        Feature(name=PDF_UPLOAD, description="تحميل ملفات PDF", enabled=False),
        Feature(name=DAILY_QUERIES, description="عدد الاستعلامات اليومية", enabled=True, limit=10),
        Feature(name=SAVED_SEARCHES, description="حفظ البحوث", enabled=False),
        Feature(name=LLM_ACCESS, description="الوصول إلى النماذج اللغوية", enabled=True, limit=5),
        Feature(name=SELF_LEARNING, description="ميزات التعلم الذاتي", enabled=False),
        Feature(name=EARLY_ACCESS, description="الوصول المبكر للميزات الجديدة", enabled=False)
    ]
)

BASIC_PLAN = SubscriptionPlan(
    type=PlanType.BASIC,
    name="الخطة الأساسية",
    description="وصول غير محدود للقرآن والتفسير والحديث والسيرة",
    price_usd=5,
    features=[
        Feature(name=QURAN_SEARCH, description="البحث في القرآن الكريم", enabled=True),
        Feature(name=TAFSEER_ACCESS, description="الوصول إلى التفاسير", enabled=True),
        Feature(name=HADITH_ACCESS, description="الوصول إلى الأحاديث", enabled=True),
        Feature(name=FIQH_ACCESS, description="الوصول إلى الفقه", enabled=False),
        Feature(name=SEERA_ACCESS, description="الوصول إلى السيرة", enabled=True),
        Feature(name=PDF_UPLOAD, description="تحميل ملفات PDF", enabled=False),
        Feature(name=DAILY_QUERIES, description="عدد الاستعلامات اليومية", enabled=True, limit=50),
        Feature(name=SAVED_SEARCHES, description="حفظ البحوث", enabled=True, limit=20),
        Feature(name=LLM_ACCESS, description="الوصول إلى النماذج اللغوية", enabled=True, limit=30),
        Feature(name=SELF_LEARNING, description="ميزات التعلم الذاتي", enabled=False),
        Feature(name=EARLY_ACCESS, description="الوصول المبكر للميزات الجديدة", enabled=False)
    ]
)

ADVANCED_PLAN = SubscriptionPlan(
    type=PlanType.ADVANCED,
    name="الخطة المتقدمة",
    description="وصول كامل لجميع المصادر الإسلامية وتحليل الكتب",
    price_usd=10,
    features=[
        Feature(name=QURAN_SEARCH, description="البحث في القرآن الكريم", enabled=True),
        Feature(name=TAFSEER_ACCESS, description="الوصول إلى التفاسير", enabled=True),
        Feature(name=HADITH_ACCESS, description="الوصول إلى الأحاديث", enabled=True),
        Feature(name=FIQH_ACCESS, description="الوصول إلى الفقه", enabled=True),
        Feature(name=SEERA_ACCESS, description="الوصول إلى السيرة", enabled=True),
        Feature(name=PDF_UPLOAD, description="تحميل ملفات PDF", enabled=True, limit=5),
        Feature(name=DAILY_QUERIES, description="عدد الاستعلامات اليومية", enabled=True, limit=100),
        Feature(name=SAVED_SEARCHES, description="حفظ البحوث", enabled=True, limit=50),
        Feature(name=LLM_ACCESS, description="الوصول إلى النماذج اللغوية", enabled=True, limit=100),
        Feature(name=SELF_LEARNING, description="ميزات التعلم الذاتي", enabled=False),
        Feature(name=EARLY_ACCESS, description="الوصول المبكر للميزات الجديدة", enabled=False)
    ]
)

SCHOLAR_PLAN = SubscriptionPlan(
    type=PlanType.SCHOLAR,
    name="خطة العالِم",
    description="وصول غير محدود لجميع المصادر والميزات المتقدمة",
    price_usd=20,
    features=[
        Feature(name=QURAN_SEARCH, description="البحث في القرآن الكريم", enabled=True),
        Feature(name=TAFSEER_ACCESS, description="الوصول إلى التفاسير", enabled=True),
        Feature(name=HADITH_ACCESS, description="الوصول إلى الأحاديث", enabled=True),
        Feature(name=FIQH_ACCESS, description="الوصول إلى الفقه", enabled=True),
        Feature(name=SEERA_ACCESS, description="الوصول إلى السيرة", enabled=True),
        Feature(name=PDF_UPLOAD, description="تحميل ملفات PDF", enabled=True),
        Feature(name=DAILY_QUERIES, description="عدد الاستعلامات اليومية", enabled=True),
        Feature(name=SAVED_SEARCHES, description="حفظ البحوث", enabled=True),
        Feature(name=LLM_ACCESS, description="الوصول إلى النماذج اللغوية", enabled=True),
        Feature(name=SELF_LEARNING, description="ميزات التعلم الذاتي", enabled=True),
        Feature(name=EARLY_ACCESS, description="الوصول المبكر للميزات الجديدة", enabled=True)
    ]
)

# قاموس لجميع خطط الاشتراك
SUBSCRIPTION_PLANS = {
    PlanType.FREE: FREE_PLAN,
    PlanType.BASIC: BASIC_PLAN,
    PlanType.ADVANCED: ADVANCED_PLAN,
    PlanType.SCHOLAR: SCHOLAR_PLAN
}

def get_plan(plan_type: PlanType) -> SubscriptionPlan:
    """الحصول على خطة اشتراك من النوع المحدد"""
    return SUBSCRIPTION_PLANS.get(plan_type, FREE_PLAN)

def get_all_plans() -> List[SubscriptionPlan]:
    """الحصول على جميع خطط الاشتراك المتاحة"""
    return list(SUBSCRIPTION_PLANS.values())
