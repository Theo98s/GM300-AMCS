# -*- coding: utf-8 -*-
"""AMCS 健康检查状态补充契约测试。"""
from __future__ import annotations

import allure


@allure.feature("系统管理")
class TestHealthRuntimeStatusContractsMore:
    """补充校验健康检查各服务当前运行状态模式。"""

    @staticmethod
    def _health_map(system_api) -> dict:
        """按名称索引健康检查服务，便于逐项断言。"""
        rows = system_api.get_health().json()["data"]
        return {row["name"]: row for row in rows}

    @allure.title("健康检查各服务保持当前 serviceUp 分布模式")
    def test_health_check_keeps_current_service_up_pattern(self, system_api):
        """校验当前环境各服务仍保持稳定的 serviceUp 分布模式。"""
        health_map = self._health_map(system_api)

        assert health_map["移动巡检设备"]["serviceUp"] is True
        assert health_map["cameras"]["serviceUp"] is False
        assert health_map["局级主站"]["serviceUp"] is True
        assert health_map["段级主站"]["serviceUp"] is True
        assert health_map["流媒体服务"]["serviceUp"] is True
        assert health_map["device"]["serviceUp"] is False

    @allure.title("健康检查顶层服务保持空 signalTypeCode 模式")
    def test_health_check_top_level_services_keep_null_signal_type_code(self, system_api):
        """校验健康检查顶层服务仍统一保持空 signalTypeCode。"""
        health_map = self._health_map(system_api)

        for row in health_map.values():
            assert row["signalTypeCode"] is None
