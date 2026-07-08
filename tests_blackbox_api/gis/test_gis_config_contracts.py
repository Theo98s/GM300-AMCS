# -*- coding: utf-8 -*-
"""Additional AMCS GIS config contract tests."""
from __future__ import annotations

import allure


@allure.feature("系统配置-GIS")
class TestGisConfigContracts:
    """Extra contract checks for GIS global configuration."""

    @allure.title("GIS 配置布尔开关使用字符串布尔值且主题非空")
    def test_d3_gis_config_boolean_switches_and_theme_are_stable(self, auth_api, gis_api, test_user):
        """Verify GIS switch fields stay string booleans and the theme field remains non-empty."""
        login_response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert login_response.json()["status"] == 0

        response = gis_api.get_d3_gis_config()
        body = response.json()["data"]

        assert body["gisEnable"] in {"true", "false"}
        assert body["gisD3PatrolEnable"] in {"true", "false"}
        assert body["localServerEnable"] in {"true", "false"}
        assert isinstance(body["d3Theme"], str)
        assert body["d3Theme"]

