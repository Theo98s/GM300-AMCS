# -*- coding: utf-8 -*-
"""More AMCS health-check contract tests."""
from __future__ import annotations

import allure


@allure.feature("系统管理")
class TestHealthContractsMore:
    """Extra checks for health-check service composition."""

    @allure.title("健康检查服务名集合保持稳定")
    def test_health_check_service_name_set_is_stable(self, system_api):
        """Verify the current environment exposes the expected six health-check service names."""
        body = system_api.get_health().json()
        names = {item["name"] for item in body["data"]}
        assert names == {
            "移动巡检设备",
            "cameras",
            "局级主站",
            "段级主站",
            "流媒体服务",
            "device",
        }

    @allure.title("健康检查不同服务的 deviceList 可空模式保持稳定")
    def test_health_check_device_list_nullability_pattern_is_stable(self, system_api):
        """Verify list-backed and null-backed services keep their current deviceList nullability pattern."""
        body = system_api.get_health().json()["data"]
        service_map = {item["name"]: item["deviceList"] for item in body}

        assert isinstance(service_map["移动巡检设备"], list)
        assert isinstance(service_map["cameras"], list)
        assert isinstance(service_map["device"], list)
        assert service_map["局级主站"] is None
        assert service_map["段级主站"] is None
        assert service_map["流媒体服务"] is None

