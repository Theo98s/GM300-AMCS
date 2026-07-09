# -*- coding: utf-8 -*-
"""AMCS RDAC 页面补充契约测试。"""
from __future__ import annotations

import allure


@allure.feature("基础数据-RDAC")
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
