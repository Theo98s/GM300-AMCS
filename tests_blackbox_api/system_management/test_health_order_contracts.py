# -*- coding: utf-8 -*-
"""AMCS 健康检查顺序补充契约测试。"""
from __future__ import annotations

import allure


@allure.feature("系统管理")
class TestHealthOrderContracts:
    """补充校验健康检查服务顺序。"""

    @allure.title("健康检查服务顺序保持稳定")
    def test_health_check_service_order_is_stable(self, system_api):
        """校验当前健康检查服务顺序保持稳定，避免影响首页看板渲染。"""
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
