import psutil
from typing import Dict, Any
import time


class ResourceManager:
    """إدارة موارد النظام"""

    def __init__(self):
        self.max_memory = 4  # GB
        self.max_cpu = 50  # %
        self._last_metrics = None
        self._last_update = 0
        self._update_interval = 5  # ثواني

    def update_limits(self, max_memory: int, max_cpu: int):
        """تحديث حدود استخدام الموارد

        Args:
            max_memory: الحد الأقصى للذاكرة بالجيجابايت
            max_cpu: الحد الأقصى للمعالج بالنسبة المئوية
        """
        self.max_memory = max_memory
        self.max_cpu = max_cpu

    def get_current_metrics(self) -> Dict[str, Any]:
        """الحصول على مقاييس الموارد الحالية

        Returns:
            قاموس يحتوي على مقاييس الموارد
        """
        current_time = time.time()

        # تحديث المقاييس كل 5 ثواني فقط
        if self._last_metrics is None or current_time - self._last_update >= self._update_interval:
            cpu_usage = psutil.cpu_percent()
            memory = psutil.virtual_memory()

            # حساب التغيير عن القياس السابق
            if self._last_metrics is not None:
                cpu_change = cpu_usage - self._last_metrics["cpu_usage"]
                memory_change = (memory.used / (1024**3)) - self._last_metrics["memory_usage"]
                tasks_change = len(psutil.Process().children()) - self._last_metrics["active_tasks"]
            else:
                cpu_change = 0
                memory_change = 0
                tasks_change = 0

            self._last_metrics = {
                "cpu_usage": cpu_usage,
                "cpu_change": cpu_change,
                "memory_usage": memory.used / (1024**3),  # تحويل إلى GB
                "memory_change": memory_change,
                "active_tasks": len(psutil.Process().children()),
                "tasks_change": tasks_change,
                "timestamps": list(range(10)),  # للعرض التجريبي
                "response_times": [100 - i * 2 for i in range(10)],  # للعرض التجريبي
            }
            self._last_update = current_time

        return self._last_metrics
