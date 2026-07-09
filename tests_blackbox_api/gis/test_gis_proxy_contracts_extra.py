# -*- coding: utf-8 -*-
"""AMCS GIS 代理配置补充契约测试。"""
from __future__ import annotations

import allure


@allure.feature("系统配置-GIS")
class TestGisProxyContractsExtra:
    """补充校验 GIS 代理相关配置字段。"""

    @allure.title("GIS 代理动态开关与投影字段保持稳定")
    def test_d3_gis_config_proxy_switch_and_projection_are_stable(self, auth_api, gis_api, test_user):
        """校验动态代理开关和瓦片投影字段保持预期字符串契约。"""
        login_response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert login_response.json()["status"] == 0

        body = gis_api.get_d3_gis_config().json()["data"]
        assert body["gisSzgdUrlProxyDynamic"] in {"true", "false"}
        assert body["gisSzgdUrlTileproj"].startswith("EPSG:")
