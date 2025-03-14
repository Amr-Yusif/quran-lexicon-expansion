"""
إدارة التكوين والإعدادات للمشروع
"""
import os
from pathlib import Path
from typing import Dict, Any, Optional
import json
import logging
from dotenv import load_dotenv

# تحميل متغيرات البيئة من ملف .env
load_dotenv()

class ConfigManager:
    """
    مدير التكوين المركزي للمشروع.
    يقوم بقراءة الإعدادات من متغيرات البيئة وملفات التكوين.
    """
    
    def __init__(self):
        """تهيئة مدير التكوين"""
        # المسار الأساسي للمشروع
        self.base_path = Path(__file__).parent.parent.parent.parent
        
        # قراءة الإعدادات من متغيرات البيئة
        self.config = {
            # بيانات اعتماد Qdrant
            "qdrant": {
                "api_key": os.getenv("QDRANT_API_KEY"),
                "url": os.getenv("QDRANT_URL")
            },
            # بيانات اعتماد Mem0
            "mem0": {
                "api_key": os.getenv("MEM0_API_KEY")
            },
            # إعدادات Ollama
            "ollama": {
                "host": os.getenv("OLLAMA_HOST", "http://localhost:11434"),
                "default_model": os.getenv("OLLAMA_DEFAULT_MODEL", "mistral")
            },
            # مسارات الملفات
            "paths": {
                "data_dir": os.getenv("DATA_DIR", str(self.base_path / "data")),
                "models_dir": os.getenv("MODELS_DIR", str(self.base_path / "models")),
                "quran_data": str(self.base_path / "data" / "quran"),
                "tafseer_data": str(self.base_path / "data" / "tafseer"),
                "scientific_miracles_data": str(self.base_path / "data" / "scientific_miracles"),
                "books_data": str(self.base_path / "data" / "books")
            },
            # إعدادات أخرى
            "debug": os.getenv("DEBUG", "False").lower() in ("true", "1", "t"),
            "log_level": os.getenv("LOG_LEVEL", "INFO"),
            "secret_key": os.getenv("SECRET_KEY", "default_secret_key_for_development_only")
        }
        
        # إنشاء المسارات إذا لم تكن موجودة
        self._create_directories()
        
        # إعداد التسجيل
        self._setup_logging()
    
    def _create_directories(self):
        """إنشاء مسارات الملفات إذا لم تكن موجودة"""
        paths = self.config["paths"]
        
        # التأكد من وجود المسارات الأساسية
        for path_name, path in paths.items():
            Path(path).mkdir(parents=True, exist_ok=True)
    
    def _setup_logging(self):
        """إعداد نظام التسجيل"""
        log_level = getattr(logging, self.config["log_level"].upper(), logging.INFO)
        
        # تكوين التسجيل الأساسي
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler(Path(self.config["paths"]["data_dir"]) / "app.log", encoding="utf-8")
            ]
        )
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        الحصول على قيمة من التكوين

        Args:
            key: مفتاح التكوين، يمكن استخدام النقطة للوصول إلى قيم مدمجة
            default: القيمة الافتراضية إذا لم يتم العثور على المفتاح

        Returns:
            قيمة المفتاح في التكوين أو القيمة الافتراضية
        """
        # دعم الوصول المتداخل باستخدام النقطة (مثل "qdrant.api_key")
        parts = key.split(".")
        value = self.config
        
        for part in parts:
            if isinstance(value, dict) and part in value:
                value = value[part]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any) -> None:
        """
        تعيين قيمة في التكوين

        Args:
            key: مفتاح التكوين، يمكن استخدام النقطة للوصول إلى قيم مدمجة
            value: القيمة الجديدة
        """
        parts = key.split(".")
        target = self.config
        
        for i, part in enumerate(parts[:-1]):
            if part not in target:
                target[part] = {}
            target = target[part]
        
        target[parts[-1]] = value
    
    def load_custom_config(self, file_path: str) -> None:
        """
        تحميل تكوين مخصص من ملف JSON

        Args:
            file_path: مسار ملف التكوين
        """
        file_path = Path(file_path)
        if file_path.exists():
            with open(file_path, 'r', encoding='utf-8') as f:
                custom_config = json.load(f)
                self._merge_configs(self.config, custom_config)
    
    def _merge_configs(self, target: Dict[str, Any], source: Dict[str, Any]) -> None:
        """
        دمج تكوينين معًا بشكل تكراري

        Args:
            target: التكوين الهدف
            source: التكوين المصدر
        """
        for key, value in source.items():
            if isinstance(value, dict) and key in target and isinstance(target[key], dict):
                self._merge_configs(target[key], value)
            else:
                target[key] = value
    
    def save_custom_config(self, file_path: str) -> None:
        """
        حفظ التكوين الحالي في ملف JSON

        Args:
            file_path: مسار ملف التكوين
        """
        with open(file_path, 'w', encoding='utf-8') as f:
            # تحويل المسارات إلى نصوص
            config_copy = self._prepare_config_for_serialization(self.config)
            json.dump(config_copy, f, ensure_ascii=False, indent=2)
    
    def _prepare_config_for_serialization(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        تحضير التكوين للتسلسل (تحويل المسارات إلى نصوص)

        Args:
            config: التكوين المراد تحضيره

        Returns:
            نسخة معدلة من التكوين جاهزة للتسلسل
        """
        result = {}
        for key, value in config.items():
            if isinstance(value, dict):
                result[key] = self._prepare_config_for_serialization(value)
            elif isinstance(value, Path):
                result[key] = str(value)
            else:
                result[key] = value
        return result
    
    def get_qdrant_credentials(self) -> Dict[str, str]:
        """
        الحصول على بيانات اعتماد Qdrant

        Returns:
            قاموس يحتوي على مفتاح API وعنوان URL لـ Qdrant
        """
        return {
            "api_key": self.get("qdrant.api_key", ""),
            "url": self.get("qdrant.url", "")
        }
    
    def get_mem0_credentials(self) -> Dict[str, str]:
        """
        الحصول على بيانات اعتماد Mem0

        Returns:
            قاموس يحتوي على مفتاح API لـ Mem0
        """
        return {
            "api_key": self.get("mem0.api_key", "")
        }
    
    def get_data_path(self, data_type: str) -> Path:
        """
        الحصول على مسار لنوع معين من البيانات

        Args:
            data_type: نوع البيانات (quran, tafseer, scientific_miracles, books)

        Returns:
            مسار المجلد للبيانات المطلوبة
        """
        key = f"paths.{data_type}_data"
        path_str = self.get(key)
        
        if path_str:
            path = Path(path_str)
            path.mkdir(parents=True, exist_ok=True)
            return path
        
        # مسار افتراضي
        default_path = Path(self.get("paths.data_dir")) / data_type
        default_path.mkdir(parents=True, exist_ok=True)
        return default_path


# إنشاء نسخة عامة من مدير التكوين
config_manager = ConfigManager()

def get_config() -> ConfigManager:
    """
    الحصول على نسخة من مدير التكوين

    Returns:
        مدير التكوين
    """
    return config_manager
