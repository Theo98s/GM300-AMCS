# -*- coding: utf-8 -*-
"""Additional AMCS GIS proxy-config contract tests."""
from __future__ import annotations

import allure


@allure.feature("系统配置-GIS")
class TestGisProxyContractsExtra:
    """Extra checks for GIS proxy-related config fields."""

    @allure.title("GIS 代理动态开关与投影字段保持稳定")
    def test_d3_gis_config_proxy_switch_and_projection_are_stable(self, auth_api, gis_api, test_user):
        """Verify proxy-dynamic switch and tile projection keep the expected string contract."""
        login_response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert login_response.json()["status"] == 0

        body = gis_api.get_d3_gis_config().json()["data"]
        assert body["gisSzgdUrlProxyDynamic"] in {"true", "false"}
        assert body["gisSzgdUrlTileproj"].startswith("EPSG:")

