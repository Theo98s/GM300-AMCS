# -*- coding: utf-8 -*-
"""AMCS RDAC 类型格式更多契约测试。"""
from __future__ import annotations

import re

import allure


@allure.feature("基础数据-RDAC")
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
