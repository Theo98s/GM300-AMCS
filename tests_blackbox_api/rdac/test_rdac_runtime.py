# -*- coding: utf-8 -*-
"""RDAC 通用、信号与站点运行时契约测试。"""
from __future__ import annotations

import allure


class TestRdacContractsExtra:
    """补充校验 RDAC 点位返回结构与字段类型。"""

    @staticmethod
    def _rdac_target(target_config):
        """从外部配置读取 RDAC 目标所亭和协议。"""
        sub_name = target_config.get("substation_name")
        protocol = target_config.get("rdac_protocol", "104")
        assert sub_name, "请在 AMCS_CONFIG_FILE 对应配置的 targets.substation_name 中设置目标所亭"
        return sub_name, protocol

    @allure.title("RDAC 遥测扩展字段保持存储与缓存契约")
    def test_rdac_telemetry_item_extended_fields_use_expected_types(self, auth_api, rdac_api, test_user, target_config):
        """校验遥测点的存储、缓存、周期和可空扩展字段保持稳定类型。"""
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
        """校验遥控标签字段保持非空字符串。"""
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
        """校验局放点位即使当前环境无数据，也仍返回列表结构。"""
        target_sub_name, target_protocol = self._rdac_target(target_config)
        login_response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert login_response.json()["status"] == 0

        response = rdac_api.list_station_items(target_sub_name, target_protocol)
        partial_discharge_items = response.json()["data"]["partialDischargeItems"]

        assert isinstance(partial_discharge_items, list)


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


class TestRdacStationRuntimeContractsMore:
    """补充校验 RDAC 站点列表中的当前运行时模式。"""

    @staticmethod
    def _rdac_target(target_config):
        """从外部配置读取 RDAC 目标所亭名称。"""
        sub_name = target_config.get("substation_name")
        assert sub_name, "请在外部配置中设置 targets.substation_name。"
        return sub_name

    @allure.title("RDAC 站点列表保持读写两条记录和相同协议")
    def test_rdac_station_list_keeps_read_write_pair_with_same_protocol(
        self,
        auth_api,
        rdac_api,
        test_user,
        target_config,
    ):
        """校验 RDAC 站点列表仍保留同协议的读写两条记录。"""
        target_sub_name = self._rdac_target(target_config)
        login_response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert login_response.json()["status"] == 0

        rows = rdac_api.list_stations().json()
        read_row = next(item for item in rows if item["subName"] == target_sub_name)
        write_row = next(item for item in rows if item["subName"] == f"{target_sub_name}_write")
        assert read_row["protocolName"] == write_row["protocolName"]
        assert read_row["protocolName"] == "104"

    @allure.title("RDAC 站点列表保持读写站点状态值处于允许集合内")
    def test_rdac_station_list_keeps_allowed_read_write_status_values(
        self,
        auth_api,
        rdac_api,
        test_user,
        target_config,
    ):
        """校验 RDAC 站点列表中的读写站点状态值仍处于允许集合内。"""
        target_sub_name = self._rdac_target(target_config)
        login_response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert login_response.json()["status"] == 0

        rows = rdac_api.list_stations().json()
        read_row = next(item for item in rows if item["subName"] == target_sub_name)
        write_row = next(item for item in rows if item["subName"] == f"{target_sub_name}_write")
        assert read_row["status"] in {"REGISTERED", "UNREGISTERED"}
        assert write_row["status"] in {"REGISTERED", "UNREGISTERED"}
