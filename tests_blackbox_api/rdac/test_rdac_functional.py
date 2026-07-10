# -*- coding: utf-8 -*-
"""RDAC 跨接口功能流程测试。"""
from __future__ import annotations

import allure


class TestRdacFunctionalFlowsMore:
    """补充覆盖 RDAC 站点列表、点位页和点位 JSON 之间的串联功能流。"""

    @staticmethod
    def _login(auth_api, test_user):
        """统一执行登录，保证 RDAC 页面和数据接口使用同一会话。"""
        response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert response.status_code == 200
        assert response.json()["status"] == 0

    @staticmethod
    def _rdac_target(target_config) -> tuple[str, str]:
        """从外部配置读取当前要验证的 RDAC 所亭和协议。"""
        sub_name = target_config.get("substation_name")
        protocol = target_config.get("rdac_protocol", "104")
        assert sub_name, "请在 AMCS_CONFIG_FILE 对应配置里设置 targets.substation_name"
        return sub_name, protocol

    @staticmethod
    def _item_total_count(item_body: dict) -> int:
        """统计 RDAC 五类点位总数，便于判断点位页初始化是否完整。"""
        data = item_body["data"]
        return sum(len(data[key]) for key in data)

    @allure.title("RDAC 目标站点可完成列表到点位页再到点位 JSON 的初始化闭环")
    def test_target_station_can_finish_list_page_and_item_json_bootstrap(
        self,
        auth_api,
        rdac_api,
        test_user,
        target_config,
    ):
        """登录后先查询站点列表，再打开目标站点点位页，并拉取点位 JSON。"""
        target_sub_name, target_protocol = self._rdac_target(target_config)
        self._login(auth_api, test_user)

        station_rows = rdac_api.list_stations().json()
        target_row = next(
            row for row in station_rows
            if row["subName"] == target_sub_name and row["protocolName"] == target_protocol
        )
        page_response = rdac_api.get_station_items_page(target_sub_name, target_protocol)
        item_body = rdac_api.list_station_items(target_sub_name, target_protocol).json()

        assert target_row["status"] in {"REGISTERED", "UNREGISTERED"}
        assert page_response.status_code == 200
        assert target_sub_name in page_response.text
        assert f"var protocol = '{target_protocol}'" in page_response.text
        assert item_body["status"] == 0
        assert self._item_total_count(item_body) > 0

    @allure.title("RDAC 读写站点可在同一会话内连续完成点位初始化")
    def test_read_and_write_stations_can_bootstrap_items_in_same_session(
        self,
        auth_api,
        rdac_api,
        test_user,
        target_config,
    ):
        """连续拉起读站和写站点位数据，校验两边都能在同一登录态下完成初始化。"""
        target_sub_name, target_protocol = self._rdac_target(target_config)
        write_sub_name = f"{target_sub_name}_write"
        self._login(auth_api, test_user)

        station_rows = rdac_api.list_stations().json()
        read_row = next(
            row for row in station_rows
            if row["subName"] == target_sub_name and row["protocolName"] == target_protocol
        )
        write_row = next(
            row for row in station_rows
            if row["subName"] == write_sub_name and row["protocolName"] == target_protocol
        )

        read_items = rdac_api.list_station_items(target_sub_name, target_protocol).json()
        write_items = rdac_api.list_station_items(write_sub_name, target_protocol).json()

        assert read_row["status"] in {"REGISTERED", "UNREGISTERED"}
        assert write_row["status"] in {"REGISTERED", "UNREGISTERED"}
        assert read_items["status"] == 0
        assert write_items["status"] == 0
        assert set(read_items["data"].keys()) == set(write_items["data"].keys())
        assert self._item_total_count(read_items) > 0
        assert self._item_total_count(write_items) > 0

    @allure.title("RDAC 目标站点点位页上下文与点位 JSON 查询参数保持一致")
    def test_target_station_page_context_matches_item_json_query(
        self,
        auth_api,
        rdac_api,
        test_user,
        target_config,
    ):
        """校验点位页展示的站点和协议上下文，与后续点位 JSON 查询目标一致。"""
        target_sub_name, target_protocol = self._rdac_target(target_config)
        self._login(auth_api, test_user)

        page_response = rdac_api.get_station_items_page(target_sub_name, target_protocol)
        item_body = rdac_api.list_station_items(target_sub_name, target_protocol).json()
        telemetry_items = item_body["data"]["telemetryItems"]

        assert page_response.status_code == 200
        assert target_sub_name in page_response.text
        assert f"var protocol = '{target_protocol}'" in page_response.text
        assert item_body["status"] == 0
        assert len(telemetry_items) > 0
        assert telemetry_items[0]["reference"].startswith(("AIU_", "DIU_", "DOU_", "AOU_"))
