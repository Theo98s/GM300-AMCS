# -*- coding: utf-8 -*-
"""AMCS RDAC 站点名称补充契约测试。"""
from __future__ import annotations

import allure


@allure.feature("基础数据-RDAC")
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
