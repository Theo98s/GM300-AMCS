# -*- coding: utf-8 -*-
"""AMCS 健康检查分组拓扑补充契约测试。"""
from __future__ import annotations

import re

import allure


@allure.feature("系统管理")
class TestHealthTopologyContractsExtra:
    """补充校验健康检查分组类型、主机信息和设备行默认值。"""

    @staticmethod
    def _health_map(system_api) -> dict:
        """按名称索引健康检查分组，便于分别断言不同服务类型。"""
        rows = system_api.get_health().json()["data"]
        return {row["name"]: row for row in rows}

    @allure.title("健康检查主机型服务保持非空 IP 和类型字段")
    def test_health_host_services_keep_ip_and_type_fields(self, system_api):
        """校验主机型服务仍使用非空 IP 和明确类型字段。"""
        health_map = self._health_map(system_api)

        for service_name in ("局级主站", "段级主站", "流媒体服务"):
            row = health_map[service_name]
            assert row["deviceList"] is None
            assert isinstance(row["type"], str) and row["type"]
            assert re.fullmatch(r"\d+\.\d+\.\d+\.\d+", row["ip"])
            assert isinstance(row["serviceUp"], bool)

    @allure.title("健康检查列表型服务保持空主机信息字段")
    def test_health_list_services_keep_null_host_fields(self, system_api):
        """校验列表型服务仍把 IP 和类型放空，并通过 deviceList 承载明细。"""
        health_map = self._health_map(system_api)

        for service_name in ("移动巡检设备", "cameras", "device"):
            row = health_map[service_name]
            assert row["type"] is None
            assert row["ip"] is None
            assert isinstance(row["deviceList"], list)
            assert isinstance(row["serviceUp"], bool)

    @allure.title("健康检查 device 分组前几条记录保持网关类默认空业务字段")
    def test_health_device_group_rows_keep_null_business_fields(self, system_api):
        """校验 device 分组前几条记录仍保持空业务编码字段和合法 IP 格式。"""
        device_rows = self._health_map(system_api)["device"]["deviceList"]
        assert len(device_rows) > 0

        for row in device_rows[:4]:
            assert isinstance(row["name"], str) and row["name"]
            assert re.fullmatch(r"\d+\.\d+\.\d+\.\d+", row["ip"])
            assert row["customCode"] is None
            assert row["areaCode"] is None
            assert row["areaName"] is None
            assert row["nvr"] is None
