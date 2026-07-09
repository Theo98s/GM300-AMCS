# -*- coding: utf-8 -*-
"""Additional AMCS health-check ordering contract tests."""
from __future__ import annotations

import allure


@allure.feature("系统管理")
class TestHealthOrderContracts:
    """Extra checks for health-check service order."""

    @allure.title("健康检查服务顺序保持稳定")
    def test_health_check_service_order_is_stable(self, system_api):
        """Verify the current health-check service order stays stable for dashboard rendering."""
        body = system_api.get_health().json()["data"]
        names = [item["name"] for item in body]
        assert names == [
            "移动巡检设备",
            "cameras",
            "局级主站",
            "段级主站",
            "流媒体服务",
            "device",
        ]

