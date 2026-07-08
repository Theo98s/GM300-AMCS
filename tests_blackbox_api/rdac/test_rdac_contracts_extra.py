# -*- coding: utf-8 -*-
"""Additional AMCS RDAC contract tests."""
from __future__ import annotations

import allure


@allure.feature("基础数据-RDAC")
class TestRdacContractsExtra:
    """Extra structure and type checks for RDAC point payloads."""

    @staticmethod
    def _rdac_target(target_config):
        """Read the RDAC target station and protocol from external config."""
        sub_name = target_config.get("substation_name")
        protocol = target_config.get("rdac_protocol", "104")
        assert sub_name, "请在 AMCS_CONFIG_FILE 对应配置的 targets.substation_name 中设置目标所亭"
        return sub_name, protocol

    @allure.title("RDAC 遥测扩展字段保持存储与缓存契约")
    def test_rdac_telemetry_item_extended_fields_use_expected_types(self, auth_api, rdac_api, test_user, target_config):
        """Verify telemetry storage, cache, period, and nullable extension fields keep stable types."""
        target_sub_name, target_protocol = self._rdac_target(target_config)
        login_response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert login_response.json()["status"] == 0

        response = rdac_api.list_station_items(target_sub_name, target_protocol)
        telemetry_item = response.json()["data"]["telemetryItems"][0]

        assert telemetry_item["store"] in {"0", "1"}
        assert telemetry_item["cache"] in {"0", "1"}
        assert isinstance(telemetry_item["period"], int)
        assert telemetry_item["period"] > 0
        assert telemetry_item["extend"] is None or isinstance(telemetry_item["extend"], str)
        assert telemetry_item["rate"] is None or isinstance(telemetry_item["rate"], (int, float))

    @allure.title("RDAC 遥控标签字段保持非空")
    def test_rdac_remote_control_labels_are_non_empty(self, auth_api, rdac_api, test_user, target_config):
        """Verify remote-control label fields remain non-empty strings."""
        target_sub_name, target_protocol = self._rdac_target(target_config)
        login_response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert login_response.json()["status"] == 0

        response = rdac_api.list_station_items(target_sub_name, target_protocol)
        remote_control_item = response.json()["data"]["remoteControlItems"][0]

        assert isinstance(remote_control_item["trueLabel"], str)
        assert isinstance(remote_control_item["falseLabel"], str)
        assert remote_control_item["trueLabel"]
        assert remote_control_item["falseLabel"]

    @allure.title("RDAC 局放点位列表保持列表契约")
    def test_rdac_partial_discharge_items_keep_list_contract(self, auth_api, rdac_api, test_user, target_config):
        """Verify partial-discharge items keep a list payload even when the current environment has none."""
        target_sub_name, target_protocol = self._rdac_target(target_config)
        login_response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert login_response.json()["status"] == 0

        response = rdac_api.list_station_items(target_sub_name, target_protocol)
        partial_discharge_items = response.json()["data"]["partialDischargeItems"]

        assert isinstance(partial_discharge_items, list)

