# -*- coding: utf-8 -*-
"""Additional AMCS GIS service-URL contract tests."""
from __future__ import annotations

import allure


@allure.feature("系统配置-GIS")
class TestGisServiceUrlContracts:
    """Extra checks for GIS service URL fields."""

    @allure.title("GIS 服务 URL 字段保持预期后缀")
    def test_d3_gis_config_service_urls_keep_expected_suffixes(self, auth_api, gis_api, test_user):
        """Verify GIS service URLs keep their current endpoint suffix conventions."""
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

