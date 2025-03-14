import pytest
import streamlit as st
from unittest.mock import MagicMock, patch
from ui.components.dashboard.main_dashboard import MainDashboard
from ui.components.dashboard.agent_dashboard import AgentDashboard
from core.agent_controller import AgentController
from core.resource_manager import ResourceManager


@pytest.fixture
def mock_resource_manager():
    manager = MagicMock(spec=ResourceManager)
    manager.get_current_metrics.return_value = {
        "cpu_usage": 45,
        "cpu_change": 5,
        "memory_usage": 2.5,
        "memory_change": 0.3,
        "active_tasks": 3,
        "tasks_change": 1,
        "timestamps": [1, 2, 3],
        "response_times": [100, 95, 105],
    }
    return manager


@pytest.fixture
def mock_agent_controller():
    controller = MagicMock(spec=AgentController)
    controller.get_agent.return_value = MagicMock()
    return controller


class TestMainDashboard:
    def test_initialization(self, mock_resource_manager, mock_agent_controller):
        """اختبار تهيئة الداشبورد الرئيسي"""
        dashboard = MainDashboard()
        assert isinstance(dashboard.resource_manager, ResourceManager)
        assert isinstance(dashboard.agent_controller, AgentController)

    @patch("streamlit.sidebar")
    def test_render_system_controls(self, mock_sidebar, mock_resource_manager):
        """اختبار عرض عناصر التحكم في النظام"""
        dashboard = MainDashboard()
        dashboard.resource_manager = mock_resource_manager

        # محاكاة التفاعل مع واجهة streamlit
        with patch("streamlit.toggle") as mock_toggle:
            with patch("streamlit.slider") as mock_slider:
                with patch("streamlit.button") as mock_button:
                    mock_toggle.return_value = True
                    mock_slider.side_effect = [4, 50]  # قيم للذاكرة والمعالج
                    mock_button.return_value = True

                    dashboard.render_system_controls()

                    # التحقق من استدعاء الدوال المتوقعة
                    mock_toggle.assert_called_once()
                    assert mock_slider.call_count == 2
                    mock_button.assert_called_once()
                    mock_resource_manager.update_limits.assert_called_once_with(4, 50)

    def test_render_performance_metrics(self, mock_resource_manager):
        """اختبار عرض مؤشرات الأداء"""
        dashboard = MainDashboard()
        dashboard.resource_manager = mock_resource_manager

        with patch("streamlit.columns") as mock_columns:
            with patch("streamlit.metric") as mock_metric:
                dashboard.render_performance_metrics()

                # التحقق من عرض المقاييس الثلاثة
                assert mock_metric.call_count == 3

                # التحقق من البيانات المعروضة
                metrics = mock_resource_manager.get_current_metrics()
                expected_calls = [
                    (("استخدام المعالج", f"{metrics['cpu_usage']}%", f"{metrics['cpu_change']}%"),),
                    (
                        (
                            "استخدام الذاكرة",
                            f"{metrics['memory_usage']}GB",
                            f"{metrics['memory_change']}GB",
                        ),
                    ),
                    (("عدد العمليات", metrics["active_tasks"], metrics["tasks_change"]),),
                ]

                mock_metric.assert_has_calls(expected_calls)


class TestAgentDashboard:
    def test_initialization(self, mock_agent_controller):
        """اختبار تهيئة داشبورد الوكيل"""
        dashboard = AgentDashboard("tafseer")
        assert dashboard.agent_type == "tafseer"
        assert isinstance(dashboard.agent, MagicMock)

    def test_render_agent_status(self, mock_agent_controller):
        """اختبار عرض حالة الوكيل"""
        dashboard = AgentDashboard("tafseer")
        dashboard.agent.get_status.return_value = {"state": "active"}

        with patch("streamlit.info") as mock_info:
            dashboard.render()
            mock_info.assert_called_once_with("الحالة: active")

    def test_update_agent_settings(self, mock_agent_controller):
        """اختبار تحديث إعدادات الوكيل"""
        dashboard = AgentDashboard("tafseer")
        test_settings = {"learning_rate": 0.01, "max_tokens": 100, "use_cache": True}
        dashboard.agent.get_settings.return_value = test_settings

        with patch("streamlit.number_input") as mock_number:
            with patch("streamlit.checkbox") as mock_checkbox:
                with patch("streamlit.button") as mock_button:
                    mock_number.side_effect = [0.01, 100]
                    mock_checkbox.return_value = True
                    mock_button.return_value = True

                    dashboard.render()

                    dashboard.agent.update_settings.assert_called_once_with(
                        {"learning_rate": 0.01, "max_tokens": 100, "use_cache": True}
                    )


if __name__ == "__main__":
    pytest.main([__file__])
