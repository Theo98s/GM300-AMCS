# -*- coding: utf-8 -*-
"""AMCS GIS 服务地址补充契约测试。"""
from __future__ import annotations

import allure


@allure.feature("系统配置-GIS")
class TestGisServiceUrlContracts:
    """补充校验 GIS 服务地址字段。"""

    @allure.title("GIS 服务 URL 字段保持预期后缀")
    def test_d3_gis_config_service_urls_keep_expected_suffixes(self, auth_api, gis_api, test_user):
        """校验 GIS 服务地址仍保持当前接口后缀约定。"""
        login_response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert login_response.json()["status"] == 0

        body = gis_api.get_d3_gis_config().json()["data"]
        assert body["gisSzgdUrlGeoserver"].endswith("/geoserver")
        assert body["gisSzgdUrlGistile"].endswith("/gistile")
        assert body["gisSzgdUrlGisother"].endswith("/gisother")
        assert body["gisSzgdUrlProxy"].endswith("/")
