# -*- coding: utf-8 -*-
"""AMCS RDAC 信号明细补充契约测试。"""
from __future__ import annotations

import allure


@allure.feature("基础数据-RDAC")
class TestRdacSignalContractsExtra:
    """补充校验 RDAC 信号返回明细。"""

    @staticmethod
    def _rdac_target(target_config):
        """从外部配置读取 RDAC 目标所亭和协议。"""
        sub_name = target_config.get("substation_name")
        protocol = target_config.get("rdac_protocol", "104")
        assert sub_name, "请在 AMCS_CONFIG_FILE 对应配置的 targets.substation_name 中设置目标所亭"
        return sub_name, protocol

    @allure.title("RDAC 遥信存储与缓存字段保持数字字符串")
    def test_rdac_telesignal_store_and_cache_use_string_flags(self, auth_api, rdac_api, test_user, target_config):
        """校验遥信点的 store/cache 字段保持字符串标记，period 保持正数。"""
        target_sub_name, target_protocol = self._rdac_target(target_config)
        login_response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert login_response.json()["status"] == 0

        telesignal_item = rdac_api.list_station_items(target_sub_name, target_protocol).json()["data"]["telesignalItems"][0]
        assert telesignal_item["store"] in {"0", "1"}
        assert telesignal_item["cache"] in {"0", "1"}
        assert telesignal_item["period"] > 0

    @allure.title("RDAC 遥调范围字段保持浮点数契约")
    def test_rdac_remote_adjust_range_fields_use_float_types(self, auth_api, rdac_api, test_user, target_config):
        """校验遥调点的最小值和最大值仍保持浮点数，便于范围校验。"""
        target_sub_name, target_protocol = self._rdac_target(target_config)
        login_response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert login_response.json()["status"] == 0

        remote_adjust_item = rdac_api.list_station_items(target_sub_name, target_protocol).json()["data"]["remoteAdjustItems"][0]
        assert isinstance(remote_adjust_item["min"], float)
        assert isinstance(remote_adjust_item["max"], float)
        assert remote_adjust_item["min"] <= remote_adjust_item["max"]
