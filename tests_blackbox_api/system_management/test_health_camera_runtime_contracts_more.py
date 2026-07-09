# -*- coding: utf-8 -*-
"""AMCS 健康检查摄像机分组运行时补充契约测试。"""
from __future__ import annotations

import re

import allure


@allure.feature("系统管理")
class TestHealthCameraRuntimeContractsMore:
    """补充校验健康检查中摄像机设备明细的稳定字段。"""

    @staticmethod
    def _camera_rows(system_api) -> list[dict]:
        """返回健康检查中的 cameras 明细列表。"""
        rows = system_api.get_health().json()["data"]
        cameras = next(row for row in rows if row["name"] == "cameras")
        assert isinstance(cameras["deviceList"], list)
        return cameras["deviceList"]

    @allure.title("健康检查 cameras 前十条记录保持实时视频设备契约")
    def test_health_camera_rows_keep_live_video_contract(self, system_api):
        """校验前十条摄像机记录仍保持在线视频设备的字段模式。"""
        rows = self._camera_rows(system_api)
        assert len(rows) >= 10

        for row in rows[:10]:
            assert isinstance(row["name"], str) and row["name"]
            assert row["serviceUp"] is True
            assert row["value"] == "1"
            assert row["signalTypeCode"] == "3"
            assert re.fullmatch(r"\d+\.\d+\.\d+\.\d+", row["ip"])
            assert row["desc"] == ""
            assert row.get("alarmClass") is None

    @allure.title("健康检查 cameras 前十条记录保持区域和视频厂家字段")
    def test_health_camera_rows_keep_area_and_nvr_fields(self, system_api):
        """校验前十条摄像机记录仍保留区域编码和视频厂家字段。"""
        rows = self._camera_rows(system_api)
        assert len(rows) >= 10

        for row in rows[:10]:
            assert row["areaCode"] == "00"
            assert row["areaName"] is None
            assert isinstance(row["customCode"], str) and row["customCode"].startswith("GM300_CAMS_")
            assert row["nvr"] in {"DH", "HIK"}
            assert row["parentName"] is None
