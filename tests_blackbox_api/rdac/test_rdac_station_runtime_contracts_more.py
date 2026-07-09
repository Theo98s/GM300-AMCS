# -*- coding: utf-8 -*-
"""AMCS RDAC 站点运行时补充契约测试。"""
from __future__ import annotations

import allure


@allure.feature("基础数据-RDAC")
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
