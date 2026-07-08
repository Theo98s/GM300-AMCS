# -*- coding: utf-8 -*-
"""Additional AMCS RDAC signal/detail contract tests."""
from __future__ import annotations

import allure


@allure.feature("基础数据-RDAC")
class TestRdacSignalContractsExtra:
    """Extra checks for RDAC signal payload details."""

    @staticmethod
    def _rdac_target(target_config):
        """Read the RDAC target station and protocol from external config."""
        sub_name = target_config.get("substation_name")
        protocol = target_config.get("rdac_protocol", "104")
        assert sub_name, "请在 AMCS_CONFIG_FILE 对应配置的 targets.substation_name 中设置目标所亭"
        return sub_name, protocol

    @allure.title("RDAC 遥信存储与缓存字段保持数字字符串")
    def test_rdac_telesignal_store_and_cache_use_string_flags(self, auth_api, rdac_api, test_user, target_config):
        """Verify telesignal store/cache fields stay string flags and period stays positive."""
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
        """Verify remote-adjust min/max fields remain numeric floats for range validation."""
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

