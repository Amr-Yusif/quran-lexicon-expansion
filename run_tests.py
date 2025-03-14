#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
تشغيل اختبارات المشروع
"""

import pytest
import sys

if __name__ == "__main__":
    # تشغيل الاختبارات مع إظهار تفاصيل تقدم الاختبارات
    exit_code = pytest.main(["-v", "tests/test_ai/test_base_agent.py"])
    sys.exit(exit_code)
