# -*- coding: utf-8 -*-
"""RDAC 页面、站点、名称与类型契约测试。"""
from __future__ import annotations

import allure
import re


class TestRdacPageContractsExtra:
    """补充校验 RDAC 页面上下文和点位包装结构。"""

    @staticmethod
    def _login(auth_api, test_user):
        """每条用例先登录，并确认会话已建立。"""
        login_response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert login_response.status_code == 200
        assert login_response.json()["status"] == 0

    @staticmethod
    def _rdac_target(target_config):
        """从外部配置读取 RDAC 目标所亭和协议。"""
        sub_name = target_config.get("substation_name")
        protocol = target_config.get("rdac_protocol", "104")
        assert sub_name, "请在测试配置中设置 targets.substation_name。"
        return sub_name, protocol

    @allure.title("RDAC 点位页面保留目标所亭变量和初始化函数")
    def test_rdac_station_items_page_keeps_context_vars_and_init_functions(
        self,
        auth_api,
        rdac_api,
        test_user,
        target_config,
    ):
        """校验 RDAC 点位页面仍保留目标所亭上下文变量和初始化函数。"""
        target_sub_name, target_protocol = self._rdac_target(target_config)
        self._login(auth_api, test_user)

        page_text = rdac_api.get_station_items_page(target_sub_name, target_protocol).text
        assert f"var subName = '{target_sub_name}'" in page_text
        assert f"var protocol = '{target_protocol}'" in page_text
        assert "function initTelemetry(" in page_text
        assert "function initTelesignal(" in page_text
        assert "function initRemoteControl(" in page_text
        assert "function initRemoteAdjust(" in page_text
        assert "function initPartialDischarge(" in page_text

    @allure.title("RDAC 点位列表返回包装结构保持稳定")
    def test_rdac_station_item_list_wrapper_keeps_status_message_and_data_contract(
        self,
        auth_api,
        rdac_api,
        test_user,
        target_config,
    ):
        """校验 RDAC 点位列表接口返回的外层包装结构保持稳定。"""
        target_sub_name, target_protocol = self._rdac_target(target_config)
        self._login(auth_api, test_user)

        body = rdac_api.list_station_items(target_sub_name, target_protocol).json()
        assert set(body.keys()) == {"status", "message", "data"}
        assert body["status"] == 0
        assert body["message"] is None or isinstance(body["message"], str)
        assert isinstance(body["data"], dict)

    @allure.title("RDAC 点位分类列表保持数量与列表类型契约")
    def test_rdac_station_item_lists_keep_count_and_list_type_contract(
        self,
        auth_api,
        rdac_api,
        test_user,
        target_config,
    ):
        """校验 RDAC 点位分类字段仍返回列表，且核心分类保持有数据。"""
        target_sub_name, target_protocol = self._rdac_target(target_config)
        self._login(auth_api, test_user)

        data = rdac_api.list_station_items(target_sub_name, target_protocol).json()["data"]
        assert isinstance(data["telemetryItems"], list) and len(data["telemetryItems"]) > 0
        assert isinstance(data["telesignalItems"], list) and len(data["telesignalItems"]) > 0
        assert isinstance(data["remoteControlItems"], list) and len(data["remoteControlItems"]) > 0
        assert isinstance(data["remoteAdjustItems"], list) and len(data["remoteAdjustItems"]) > 0
        assert isinstance(data["partialDischargeItems"], list)


class TestRdacStationContractsMore:
    """补充校验 RDAC 站点列表返回结构。"""

    @allure.title("RDAC 站点列表站点名保持唯一")
    def test_rdac_station_list_sub_names_are_unique(self, auth_api, rdac_api, test_user):
        """校验当前 RDAC 站点列表中的所亭名称保持唯一。"""
        login_response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert login_response.json()["status"] == 0

        body = rdac_api.list_stations().json()
        sub_names = [item["subName"] for item in body]
        assert len(sub_names) == len(set(sub_names))

    @allure.title("RDAC 站点列表协议字段保持非空")
    def test_rdac_station_list_protocol_names_are_non_empty(self, auth_api, rdac_api, test_user):
        """校验每条 RDAC 站点记录都保留非空协议名称。"""
        login_response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert login_response.json()["status"] == 0

        body = rdac_api.list_stations().json()
        for item in body:
            assert isinstance(item["protocolName"], str)
            assert item["protocolName"]


class TestRdacStationNameContracts:
    """补充校验 RDAC 站点名称组成。"""

    @staticmethod
    def _rdac_target(target_config):
        """从外部配置读取 RDAC 目标站点名称。"""
        sub_name = target_config.get("substation_name")
        assert sub_name, "请在 AMCS_CONFIG_FILE 对应配置的 targets.substation_name 中设置目标所亭"
        return sub_name

    @allure.title("RDAC 站点列表包含读写两类所亭名称")
    def test_rdac_station_names_cover_read_and_write_entries(self, auth_api, rdac_api, test_user, target_config):
        """校验站点列表仍同时保留目标站点和对应的写入站点。"""
        target_sub_name = self._rdac_target(target_config)
        login_response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert login_response.json()["status"] == 0

        body = rdac_api.list_stations().json()
        sub_names = {item["subName"] for item in body}
        assert target_sub_name in sub_names
        assert f"{target_sub_name}_write" in sub_names


class TestRdacTypeContractsMore:
    """补充校验 RDAC 站点协议和类型编码格式。"""

    @staticmethod
    def _rdac_target(target_config):
        """从外部配置读取 RDAC 目标所亭和协议。"""
        sub_name = target_config.get("substation_name")
        protocol = target_config.get("rdac_protocol", "104")
        assert sub_name, "请在 AMCS_CONFIG_FILE 对应配置的 targets.substation_name 中设置目标所亭"
        return sub_name, protocol

    @allure.title("RDAC 站点列表协议名与目标协议保持一致")
    def test_rdac_station_protocols_match_target_protocol(self, auth_api, rdac_api, test_user, target_config):
        """校验所有 RDAC 站点记录都使用外部配置中的目标协议。"""
        _, target_protocol = self._rdac_target(target_config)
        login_response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert login_response.json()["status"] == 0

        body = rdac_api.list_stations().json()
        for item in body:
            assert item["protocolName"] == target_protocol

    @allure.title("RDAC 遥测类型字段保持大写字母编码格式")
    def test_rdac_telemetry_type_codes_match_uppercase_pattern(self, auth_api, rdac_api, test_user, target_config):
        """校验前几条遥测类型编码保持大写字母格式。"""
        target_sub_name, target_protocol = self._rdac_target(target_config)
        login_response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert login_response.json()["status"] == 0

        rows = rdac_api.list_station_items(target_sub_name, target_protocol).json()["data"]["telemetryItems"][:5]
        for item in rows:
            assert re.fullmatch(r"[A-Z]{3}", item["type"])
