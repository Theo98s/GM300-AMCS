# -*- coding: utf-8 -*-
"""Additional AMCS RDAC station-name contract tests."""
from __future__ import annotations

import allure


@allure.feature("基础数据-RDAC")
class TestRdacStationNameContracts:
    """Extra checks for RDAC station-name composition."""

    @staticmethod
    def _rdac_target(target_config):
        """Read the RDAC target station name from external config."""
        sub_name = target_config.get("substation_name")
        assert sub_name, "请在 AMCS_CONFIG_FILE 对应配置的 targets.substation_name 中设置目标所亭"
        return sub_name

    @allure.title("RDAC 站点列表包含读写两类所亭名称")
    def test_rdac_station_names_cover_read_and_write_entries(self, auth_api, rdac_api, test_user, target_config):
        """Verify the station list keeps both the target station and its write entry."""
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

