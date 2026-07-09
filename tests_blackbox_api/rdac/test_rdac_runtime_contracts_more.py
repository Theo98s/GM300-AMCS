# -*- coding: utf-8 -*-
"""AMCS RDAC 运行时补充契约测试。"""
from __future__ import annotations

import allure


@allure.feature("基础数据-RDAC")
class TestRdacRuntimeContractsMore:
    """补充校验 RDAC 首条点位记录中的默认空值模式。"""

    @staticmethod
    def _rdac_target(target_config):
        """从外部配置读取 RDAC 目标所亭和协议。"""
        sub_name = target_config.get("substation_name")
        protocol = target_config.get("rdac_protocol", "104")
        assert sub_name, "请在外部配置中设置 targets.substation_name。"
        return sub_name, protocol

    @allure.title("RDAC 首条遥测记录保持空比例偏移与扩展字段")
    def test_rdac_first_telemetry_item_keeps_nullable_ratio_offset_fields(
        self,
        auth_api,
        rdac_api,
        test_user,
        target_config,
    ):
        """校验首条遥测记录仍保持空比例、偏移和扩展字段。"""
        target_sub_name, target_protocol = self._rdac_target(target_config)
        login_response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert login_response.json()["status"] == 0

        telemetry_item = rdac_api.list_station_items(target_sub_name, target_protocol).json()["data"]["telemetryItems"][0]
        assert telemetry_item["ratio"] is None
        assert telemetry_item["offset"] is None
        assert telemetry_item["extend"] is None
        assert telemetry_item["rate"] is None
        assert telemetry_item["store"] == "1"
        assert telemetry_item["cache"] == "1"

    @allure.title("RDAC 首条遥信记录保持空真值标签与固定周期")
    def test_rdac_first_telesignal_item_keeps_null_labels_and_period(
        self,
        auth_api,
        rdac_api,
        test_user,
        target_config,
    ):
        """校验首条遥信记录仍保持空真值标签和固定周期字段。"""
        target_sub_name, target_protocol = self._rdac_target(target_config)
        login_response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert login_response.json()["status"] == 0

        telesignal_item = rdac_api.list_station_items(target_sub_name, target_protocol).json()["data"]["telesignalItems"][0]
        assert telesignal_item["type"] == "DEE"
        assert telesignal_item["extend"] is None
        assert telesignal_item["trueLabel"] is None
        assert telesignal_item["falseLabel"] is None
        assert telesignal_item["store"] == "1"
        assert telesignal_item["cache"] == "1"
        assert telesignal_item["period"] == 600
