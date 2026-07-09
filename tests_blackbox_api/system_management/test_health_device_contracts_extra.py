# -*- coding: utf-8 -*-
"""Additional AMCS health-detail contract tests."""
from __future__ import annotations

import re

import allure


@allure.feature("System Management")
class TestHealthDeviceContractsExtra:
    """Extra contract checks for device rows nested inside health-check payloads."""

    @staticmethod
    def _health_map(system_api) -> dict:
        """Index health-check entries by name for focused nested-row assertions."""
        body = system_api.get_health().json()["data"]
        return {item["name"]: item for item in body}

    @allure.title("Health cameras list keeps stable nested device row contracts")
    def test_health_camera_device_rows_keep_expected_nested_contracts(self, system_api):
        """Verify camera-device rows keep stable flag, code, and IP-field contracts."""
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

    @allure.title("Health device list keeps expected NVR and communication-device contracts")
    def test_health_device_group_keeps_expected_device_row_contracts(self, system_api):
        """Verify the device health group keeps IP-based equipment rows for NVR and communication devices."""
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
