# -*- coding: utf-8 -*-
"""AMCS RDAC 接口测试。"""
from __future__ import annotations

import allure


@allure.feature("基础数据-RDAC")
class TestRdacApi:
    """RDAC 站点和点位配置查询用例。"""

    @staticmethod
    def _rdac_target(target_config):
        """从外部配置读取 RDAC 目标所亭和协议，便于切换不同测试环境。"""
        sub_name = target_config.get("substation_name")
        protocol = target_config.get("rdac_protocol", "104")
        assert sub_name, "请在 AMCS_CONFIG_FILE 对应配置的 targets.substation_name 中设置目标所亭"
        return sub_name, protocol

    @allure.title("RDAC 站点列表包含目标站点")
    def test_rdac_station_list_contains_target_station(self, auth_api, rdac_api, test_user, target_config):
        """校验 RDAC 站点列表包含当前页面默认站点。

        目标所亭和协议来自外部配置，避免换环境时修改测试代码。
        站点注册状态会随环境变化，因此只校验状态值在系统允许范围内。
        """
        target_sub_name, target_protocol = self._rdac_target(target_config)
        login_response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert login_response.json()["status"] == 0

        response = rdac_api.list_stations()
        assert response.status_code == 200

        body = response.json()
        assert isinstance(body, list)
        matched = next(
            item for item in body
            if item["subName"] == target_sub_name and item["protocolName"] == target_protocol
        )
        assert matched["status"] in {"REGISTERED", "UNREGISTERED"}

    @allure.title("RDAC 站点列表返回标准字段结构")
    def test_rdac_station_list_entries_contain_expected_keys(self, auth_api, rdac_api, test_user):
        """校验 RDAC 站点列表中的首条数据包含站点名、协议和状态字段。"""
        login_response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert login_response.json()["status"] == 0

        response = rdac_api.list_stations()
        body = response.json()

        assert len(body) > 0
        assert set(body[0].keys()) >= {"subName", "protocolName", "status"}
        assert body[0]["subName"]
        assert body[0]["protocolName"]
        assert body[0]["status"] in {"REGISTERED", "UNREGISTERED"}

    @allure.title("RDAC 点位页面 HTML 包含当前站点和协议")
    def test_rdac_station_items_page_contains_context(self, auth_api, rdac_api, test_user, target_config):
        """校验站点点位页面能按外部配置中的站点和协议正常打开。"""
        target_sub_name, target_protocol = self._rdac_target(target_config)
        login_response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert login_response.json()["status"] == 0

        response = rdac_api.get_station_items_page(target_sub_name, target_protocol)
        assert response.status_code == 200
        assert "站点属性列表主页面" in response.text
        assert target_sub_name in response.text
        assert f"var protocol = '{target_protocol}'" in response.text

    @allure.title("RDAC 点位列表接口返回标准结构")
    def test_rdac_station_item_list_returns_standard_keys(self, auth_api, rdac_api, test_user, target_config):
        """校验外部配置所亭的 RDAC 点位配置 JSON 结构完整。"""
        target_sub_name, target_protocol = self._rdac_target(target_config)
        login_response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert login_response.json()["status"] == 0

        response = rdac_api.list_station_items(target_sub_name, target_protocol)
        assert response.status_code == 200

        body = response.json()
        assert body["status"] == 0
        assert set(body["data"].keys()) == {
            "telemetryItems",
            "telesignalItems",
            "remoteControlItems",
            "remoteAdjustItems",
            "partialDischargeItems",
        }

    @allure.title("RDAC 遥测点位包含名称引用与精度字段")
    def test_rdac_telemetry_item_contains_expected_fields(self, auth_api, rdac_api, test_user, target_config):
        """校验 RDAC 遥测点位首条数据包含名称、引用号、精度和单位等字段。"""
        target_sub_name, target_protocol = self._rdac_target(target_config)
        login_response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert login_response.json()["status"] == 0

        response = rdac_api.list_station_items(target_sub_name, target_protocol)
        body = response.json()
        telemetry_items = body["data"]["telemetryItems"]

        assert len(telemetry_items) > 0
        assert set(telemetry_items[0].keys()) >= {
            "name",
            "reference",
            "type",
            "precision",
            "unit",
            "variation",
        }
        assert telemetry_items[0]["name"]
        assert telemetry_items[0]["reference"]

    @allure.title("RDAC 站点列表所有状态值都在允许范围内")
    def test_rdac_station_list_status_values_are_allowed(self, auth_api, rdac_api, test_user):
        """校验 RDAC 站点列表中的所有状态值都在系统允许范围内。"""
        login_response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert login_response.json()["status"] == 0

        response = rdac_api.list_stations()
        body = response.json()

        for item in body:
            assert item["status"] in {"REGISTERED", "UNREGISTERED"}
            assert item["protocolName"]

    @allure.title("RDAC telemetry precision and variation stay numeric")
    def test_rdac_telemetry_item_precision_and_variation_are_numeric(self, auth_api, rdac_api, test_user, target_config):
        """Verify telemetry precision and variation fields stay numeric for downstream formatting."""
        target_sub_name, target_protocol = self._rdac_target(target_config)
        login_response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert login_response.json()["status"] == 0

        response = rdac_api.list_station_items(target_sub_name, target_protocol)
        telemetry_item = response.json()["data"]["telemetryItems"][0]

        assert isinstance(telemetry_item["precision"], int)
        assert telemetry_item["precision"] >= 0
        assert isinstance(telemetry_item["variation"], (int, float))

    @allure.title("RDAC telemetry unit and reference stay populated")
    def test_rdac_telemetry_item_unit_and_reference_are_non_empty(self, auth_api, rdac_api, test_user, target_config):
        """Verify telemetry preview rows keep non-empty unit and reference metadata."""
        target_sub_name, target_protocol = self._rdac_target(target_config)
        login_response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert login_response.json()["status"] == 0

        response = rdac_api.list_station_items(target_sub_name, target_protocol)
        telemetry_item = response.json()["data"]["telemetryItems"][0]

        assert telemetry_item["name"]
        assert telemetry_item["unit"]
        assert telemetry_item["reference"].startswith(("AIU_", "DIU_", "DOU_", "AOU_"))

    @allure.title("RDAC 遥信点位保持布尔标签与存储字段结构")
    def test_rdac_telesignal_item_contains_expected_fields(self, auth_api, rdac_api, test_user, target_config):
        """校验 RDAC 遥信点位列表中的首条记录保留名称、引用、真假标签和存储字段。"""
        target_sub_name, target_protocol = self._rdac_target(target_config)
        login_response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert login_response.json()["status"] == 0

        response = rdac_api.list_station_items(target_sub_name, target_protocol)
        telesignal_item = response.json()["data"]["telesignalItems"][0]

        assert set(telesignal_item.keys()) >= {
            "name",
            "reference",
            "type",
            "trueLabel",
            "falseLabel",
            "store",
            "cache",
            "period",
        }
        assert telesignal_item["reference"].startswith("SCS_")
        assert isinstance(telesignal_item["period"], int)

    @allure.title("RDAC 遥控点位保持开合标签与选择字段")
    def test_rdac_remote_control_item_contains_expected_fields(self, auth_api, rdac_api, test_user, target_config):
        """校验 RDAC 遥控点位列表中的首条记录保留开关标签和选择控制字段。"""
        target_sub_name, target_protocol = self._rdac_target(target_config)
        login_response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert login_response.json()["status"] == 0

        response = rdac_api.list_station_items(target_sub_name, target_protocol)
        remote_control_item = response.json()["data"]["remoteControlItems"][0]

        assert set(remote_control_item.keys()) >= {
            "name",
            "reference",
            "trueLabel",
            "falseLabel",
            "select",
        }
        assert remote_control_item["reference"].startswith("DOS_")
        assert remote_control_item["select"] in {"0", "1"}

    @allure.title("RDAC 遥调点位上下限与单位字段可用")
    def test_rdac_remote_adjust_item_contains_range_and_unit(self, auth_api, rdac_api, test_user, target_config):
        """校验 RDAC 遥调点位列表中的首条记录保留上下限范围和单位字段。"""
        target_sub_name, target_protocol = self._rdac_target(target_config)
        login_response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert login_response.json()["status"] == 0

        response = rdac_api.list_station_items(target_sub_name, target_protocol)
        remote_adjust_item = response.json()["data"]["remoteAdjustItems"][0]

        assert set(remote_adjust_item.keys()) >= {"name", "reference", "min", "max", "unit"}
        assert remote_adjust_item["reference"].startswith(("SIP_", "AOP_"))
        assert remote_adjust_item["min"] <= remote_adjust_item["max"]
        assert remote_adjust_item["unit"]
