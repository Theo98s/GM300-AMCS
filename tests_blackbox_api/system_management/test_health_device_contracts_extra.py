# -*- coding: utf-8 -*-
"""AMCS 健康检查明细补充契约测试。"""
from __future__ import annotations

import re

import allure


@allure.feature("System Management")
class TestHealthDeviceContractsExtra:
    """补充校验健康检查返回中嵌套设备行的契约。"""

    @staticmethod
    def _health_map(system_api) -> dict:
        """按名称索引健康检查条目，便于针对嵌套记录做断言。"""
        body = system_api.get_health().json()["data"]
        return {item["name"]: item for item in body}

    @allure.title("健康检查 cameras 列表保留稳定的嵌套设备行契约")
    def test_health_camera_device_rows_keep_expected_nested_contracts(self, system_api):
        """校验摄像机设备行保持稳定的标记、编码和 IP 字段契约。"""
        cameras = self._health_map(system_api)["cameras"]
        assert isinstance(cameras["deviceList"], list)
        assert len(cameras["deviceList"]) > 0

        for row in cameras["deviceList"][:5]:
            assert isinstance(row["name"], str) and row["name"]
            assert isinstance(row["serviceUp"], bool)
            assert row["value"] in {"1", "异常"}
            assert re.fullmatch(r"\d+", row["signalTypeCode"])
            assert row["ip"] is None or re.fullmatch(r"\d+\.\d+\.\d+\.\d+", row["ip"])
            assert row["customCode"] is None or isinstance(row["customCode"], str)

    @allure.title("健康检查 device 列表保留预期的 NVR 与通信设备契约")
    def test_health_device_group_keeps_expected_device_row_contracts(self, system_api):
        """校验 device 健康分组仍保留基于 IP 的 NVR 和通信设备记录。"""
        device_group = self._health_map(system_api)["device"]
        assert isinstance(device_group["deviceList"], list)
        assert len(device_group["deviceList"]) >= 4

        names = [row["name"] for row in device_group["deviceList"]]
        assert "NVR" in names
        assert "通信管理机" in names
        for row in device_group["deviceList"]:
            assert isinstance(row["serviceUp"], bool)
            assert row["value"] in {"1", "异常"}
            assert re.fullmatch(r"\d+\.\d+\.\d+\.\d+", row["ip"])
            assert row["signalTypeCode"] is None or re.fullmatch(r"\d+", row["signalTypeCode"])
