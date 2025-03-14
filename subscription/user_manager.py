"""
إدارة المستخدمين ومتابعة الاشتراكات
"""
import os
import json
import uuid
import hashlib
import datetime
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, asdict
from pathlib import Path

from .plans import PlanType, SubscriptionPlan, get_plan

@dataclass
class UserUsage:
    """تتبع استخدام المستخدم للميزات"""
    daily_queries: int = 0
    quran_searches: int = 0
    tafseer_access: int = 0
    hadith_access: int = 0
    fiqh_access: int = 0
    seera_access: int = 0
    pdf_uploads: int = 0
    llm_access: int = 0
    last_reset: str = ""  # تاريخ آخر إعادة تعيين
    
    def reset_daily_usage(self):
        """إعادة تعيين حدود الاستخدام اليومية"""
        self.daily_queries = 0
        self.last_reset = datetime.datetime.now().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """تحويل بيانات الاستخدام إلى قاموس"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UserUsage':
        """إنشاء كائن استخدام من قاموس"""
        return cls(**data)

@dataclass
class Subscription:
    """اشتراك المستخدم"""
    plan_type: PlanType
    start_date: str
    expiry_date: str
    auto_renew: bool = False
    payment_method: Optional[str] = None
    
    def is_active(self) -> bool:
        """التحقق مما إذا كان الاشتراك نشطًا"""
        now = datetime.datetime.now()
        expiry = datetime.datetime.fromisoformat(self.expiry_date)
        return now < expiry
    
    def to_dict(self) -> Dict[str, Any]:
        """تحويل الاشتراك إلى قاموس"""
        return {
            "plan_type": self.plan_type.value,
            "start_date": self.start_date,
            "expiry_date": self.expiry_date,
            "auto_renew": self.auto_renew,
            "payment_method": self.payment_method
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Subscription':
        """إنشاء اشتراك من قاموس"""
        return cls(
            plan_type=PlanType(data["plan_type"]),
            start_date=data["start_date"],
            expiry_date=data["expiry_date"],
            auto_renew=data.get("auto_renew", False),
            payment_method=data.get("payment_method")
        )

@dataclass
class User:
    """معلومات المستخدم"""
    id: str
    username: str
    email: str
    password_hash: str
    name: Optional[str] = None
    created_at: str = ""
    last_login: Optional[str] = None
    subscription: Optional[Subscription] = None
    usage: Optional[UserUsage] = None
    saved_searches: List[Dict[str, Any]] = None
    settings: Dict[str, Any] = None
    
    def __post_init__(self):
        """تهيئة بعد الإنشاء"""
        if self.created_at == "":
            self.created_at = datetime.datetime.now().isoformat()
        if self.usage is None:
            self.usage = UserUsage(last_reset=datetime.datetime.now().isoformat())
        if self.saved_searches is None:
            self.saved_searches = []
        if self.settings is None:
            self.settings = {"theme": "light", "language": "ar"}
    
    def set_password(self, password: str):
        """تعيين كلمة المرور"""
        self.password_hash = self._hash_password(password)
    
    def verify_password(self, password: str) -> bool:
        """التحقق من كلمة المرور"""
        return self.password_hash == self._hash_password(password)
    
    def get_active_plan(self) -> SubscriptionPlan:
        """الحصول على خطة الاشتراك النشطة"""
        if self.subscription and self.subscription.is_active():
            return get_plan(self.subscription.plan_type)
        return get_plan(PlanType.FREE)
    
    def subscribe(self, plan_type: PlanType, months: int = 1, auto_renew: bool = False, payment_method: str = None):
        """الاشتراك في خطة"""
        now = datetime.datetime.now()
        expiry = now + datetime.timedelta(days=30 * months)
        
        self.subscription = Subscription(
            plan_type=plan_type,
            start_date=now.isoformat(),
            expiry_date=expiry.isoformat(),
            auto_renew=auto_renew,
            payment_method=payment_method
        )
    
    def can_use_feature(self, feature_name: str) -> bool:
        """التحقق مما إذا كان المستخدم يمكنه استخدام ميزة"""
        plan = self.get_active_plan()
        feature = plan.get_feature(feature_name)
        
        if not feature or not feature.enabled:
            return False
        
        # التحقق من حدود الاستخدام، إذا كانت محددة
        if feature.limit is not None:
            # التأكد من تحديث حدود الاستخدام اليومية
            self._check_daily_reset()
            
            # التحقق من الحد المناسب
            if feature_name == "daily_queries":
                return self.usage.daily_queries < feature.limit
            elif feature_name == "quran_search":
                return self.usage.quran_searches < feature.limit
            elif feature_name == "tafseer_access":
                return self.usage.tafseer_access < feature.limit
            elif feature_name == "hadith_access":
                return self.usage.hadith_access < feature.limit
            elif feature_name == "fiqh_access":
                return self.usage.fiqh_access < feature.limit
            elif feature_name == "seera_access":
                return self.usage.seera_access < feature.limit
            elif feature_name == "pdf_upload":
                return self.usage.pdf_uploads < feature.limit
            elif feature_name == "llm_access":
                return self.usage.llm_access < feature.limit
            elif feature_name == "saved_searches":
                return len(self.saved_searches) < feature.limit
        
        return True
    
    def track_feature_usage(self, feature_name: str):
        """تتبع استخدام ميزة"""
        self._check_daily_reset()
        
        if feature_name == "daily_queries":
            self.usage.daily_queries += 1
        elif feature_name == "quran_search":
            self.usage.quran_searches += 1
        elif feature_name == "tafseer_access":
            self.usage.tafseer_access += 1
        elif feature_name == "hadith_access":
            self.usage.hadith_access += 1
        elif feature_name == "fiqh_access":
            self.usage.fiqh_access += 1
        elif feature_name == "seera_access":
            self.usage.seera_access += 1
        elif feature_name == "pdf_upload":
            self.usage.pdf_uploads += 1
        elif feature_name == "llm_access":
            self.usage.llm_access += 1
    
    def add_saved_search(self, query: str, results: List[Dict[str, Any]], category: str = "quran"):
        """إضافة بحث محفوظ"""
        # التحقق من إمكانية حفظ البحث
        if not self.can_use_feature("saved_searches"):
            raise ValueError("تجاوزت الحد المسموح لعمليات البحث المحفوظة")
        
        search = {
            "id": str(uuid.uuid4()),
            "query": query,
            "results": results[:10],  # تخزين أول 10 نتائج فقط لتوفير المساحة
            "category": category,
            "timestamp": datetime.datetime.now().isoformat()
        }
        
        self.saved_searches.append(search)
    
    def get_saved_searches(self, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """الحصول على البحوث المحفوظة"""
        if category:
            return [s for s in self.saved_searches if s.get("category") == category]
        return self.saved_searches
    
    def delete_saved_search(self, search_id: str) -> bool:
        """حذف بحث محفوظ"""
        original_len = len(self.saved_searches)
        self.saved_searches = [s for s in self.saved_searches if s.get("id") != search_id]
        return len(self.saved_searches) < original_len
    
    def to_dict(self) -> Dict[str, Any]:
        """تحويل المستخدم إلى قاموس"""
        user_dict = {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "password_hash": self.password_hash,
            "name": self.name,
            "created_at": self.created_at,
            "last_login": self.last_login,
            "saved_searches": self.saved_searches,
            "settings": self.settings
        }
        
        if self.subscription:
            user_dict["subscription"] = self.subscription.to_dict()
        
        if self.usage:
            user_dict["usage"] = self.usage.to_dict()
        
        return user_dict
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'User':
        """إنشاء مستخدم من قاموس"""
        subscription = None
        if "subscription" in data:
            subscription = Subscription.from_dict(data["subscription"])
        
        usage = None
        if "usage" in data:
            usage = UserUsage.from_dict(data["usage"])
        
        return cls(
            id=data["id"],
            username=data["username"],
            email=data["email"],
            password_hash=data["password_hash"],
            name=data.get("name"),
            created_at=data.get("created_at", ""),
            last_login=data.get("last_login"),
            subscription=subscription,
            usage=usage,
            saved_searches=data.get("saved_searches", []),
            settings=data.get("settings", {"theme": "light", "language": "ar"})
        )
    
    def _hash_password(self, password: str) -> str:
        """حساب تجزئة كلمة المرور"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def _check_daily_reset(self):
        """التحقق من ضرورة إعادة تعيين حدود الاستخدام اليومية"""
        if not self.usage.last_reset:
            self.usage.reset_daily_usage()
            return
        
        last_reset = datetime.datetime.fromisoformat(self.usage.last_reset)
        now = datetime.datetime.now()
        
        # إعادة تعيين إذا كان اليوم الحالي مختلفًا عن يوم آخر إعادة تعيين
        if last_reset.date() < now.date():
            self.usage.reset_daily_usage()

class UserManager:
    """إدارة المستخدمين"""
    
    def __init__(self, data_dir: str = None):
        """
        تهيئة مدير المستخدمين

        Args:
            data_dir: مسار مجلد البيانات
        """
        if data_dir is None:
            # استخدام المجلد الافتراضي إذا لم يتم تحديد مجلد
            self.data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
        else:
            self.data_dir = data_dir
        
        # التأكد من وجود مجلد البيانات
        self.users_dir = os.path.join(self.data_dir, "users")
        os.makedirs(self.users_dir, exist_ok=True)
        
        # مسار ملف بيانات المستخدمين
        self.users_file = os.path.join(self.users_dir, "users.json")
        
        # قائمة المستخدمين الحالية
        self.users = self._load_users()
        
        # إنشاء ملف المستخدمين إذا لم يكن موجودًا
        if not os.path.exists(self.users_file):
            self._save_users()
    
    def create_user(self, username: str, email: str, password: str, name: Optional[str] = None) -> User:
        """
        إنشاء مستخدم جديد

        Args:
            username: اسم المستخدم
            email: البريد الإلكتروني
            password: كلمة المرور
            name: الاسم الكامل (اختياري)

        Returns:
            كائن المستخدم الجديد
        """
        # التحقق من عدم وجود مستخدم بنفس اسم المستخدم أو البريد الإلكتروني
        if self.get_user_by_username(username):
            raise ValueError(f"اسم المستخدم '{username}' موجود بالفعل")
        
        if self.get_user_by_email(email):
            raise ValueError(f"البريد الإلكتروني '{email}' موجود بالفعل")
        
        # إنشاء معرف فريد للمستخدم
        user_id = str(uuid.uuid4())
        
        # إنشاء كائن المستخدم
        user = User(
            id=user_id,
            username=username,
            email=email,
            password_hash="",
            name=name
        )
        
        # تعيين كلمة المرور
        user.set_password(password)
        
        # حفظ المستخدم
        self.users.append(user)
        self._save_users()
        
        return user
    
    def authenticate(self, username_or_email: str, password: str) -> Optional[User]:
        """
        مصادقة المستخدم

        Args:
            username_or_email: اسم المستخدم أو البريد الإلكتروني
            password: كلمة المرور

        Returns:
            كائن المستخدم إذا نجحت المصادقة، وإلا None
        """
        # البحث عن المستخدم بواسطة اسم المستخدم أو البريد الإلكتروني
        user = self.get_user_by_username(username_or_email)
        if not user:
            user = self.get_user_by_email(username_or_email)
        
        # التحقق من المستخدم وكلمة المرور
        if user and user.verify_password(password):
            # تحديث وقت آخر تسجيل دخول
            user.last_login = datetime.datetime.now().isoformat()
            self._save_users()
            return user
        
        return None
    
    def get_user(self, user_id: str) -> Optional[User]:
        """
        الحصول على مستخدم بواسطة المعرف

        Args:
            user_id: معرف المستخدم

        Returns:
            كائن المستخدم أو None إذا لم يتم العثور عليه
        """
        for user in self.users:
            if user.id == user_id:
                return user
        return None
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        """
        الحصول على مستخدم بواسطة اسم المستخدم

        Args:
            username: اسم المستخدم

        Returns:
            كائن المستخدم أو None إذا لم يتم العثور عليه
        """
        for user in self.users:
            if user.username.lower() == username.lower():
                return user
        return None
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """
        الحصول على مستخدم بواسطة البريد الإلكتروني

        Args:
            email: البريد الإلكتروني

        Returns:
            كائن المستخدم أو None إذا لم يتم العثور عليه
        """
        for user in self.users:
            if user.email.lower() == email.lower():
                return user
        return None
    
    def update_user(self, user: User) -> bool:
        """
        تحديث معلومات المستخدم

        Args:
            user: كائن المستخدم المحدث

        Returns:
            نجاح العملية
        """
        for i, existing_user in enumerate(self.users):
            if existing_user.id == user.id:
                self.users[i] = user
                self._save_users()
                return True
        return False
    
    def delete_user(self, user_id: str) -> bool:
        """
        حذف مستخدم

        Args:
            user_id: معرف المستخدم

        Returns:
            نجاح العملية
        """
        original_len = len(self.users)
        self.users = [user for user in self.users if user.id != user_id]
        
        if len(self.users) < original_len:
            self._save_users()
            return True
        
        return False
    
    def get_all_users(self) -> List[User]:
        """
        الحصول على قائمة جميع المستخدمين

        Returns:
            قائمة كائنات المستخدمين
        """
        return self.users
    
    def subscribe_user(self, user_id: str, plan_type: PlanType, months: int = 1, auto_renew: bool = False, payment_method: str = None) -> bool:
        """
        اشتراك مستخدم في خطة

        Args:
            user_id: معرف المستخدم
            plan_type: نوع الخطة
            months: عدد أشهر الاشتراك
            auto_renew: تجديد تلقائي
            payment_method: طريقة الدفع

        Returns:
            نجاح العملية
        """
        user = self.get_user(user_id)
        if not user:
            return False
        
        user.subscribe(plan_type, months, auto_renew, payment_method)
        self._save_users()
        return True
    
    def _load_users(self) -> List[User]:
        """
        تحميل قائمة المستخدمين من ملف

        Returns:
            قائمة كائنات المستخدمين
        """
        try:
            if not os.path.exists(self.users_file):
                return []
            
            with open(self.users_file, 'r', encoding='utf-8') as f:
                users_data = json.load(f)
            
            return [User.from_dict(user_data) for user_data in users_data]
        
        except Exception as e:
            print(f"خطأ في تحميل المستخدمين: {str(e)}")
            return []
    
    def _save_users(self) -> bool:
        """
        حفظ قائمة المستخدمين إلى ملف

        Returns:
            نجاح العملية
        """
        try:
            users_data = [user.to_dict() for user in self.users]
            
            with open(self.users_file, 'w', encoding='utf-8') as f:
                json.dump(users_data, f, ensure_ascii=False, indent=4)
            
            return True
        
        except Exception as e:
            print(f"خطأ في حفظ المستخدمين: {str(e)}")
            return False
