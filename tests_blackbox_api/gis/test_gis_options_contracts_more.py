# -*- coding: utf-8 -*-
"""GIS 查询接口的 OPTIONS 方法契约测试。"""
from __future__ import annotations

import allure
import pytest


@allure.feature("GIS 地图")
class TestGisOptionsContractsMore:
    """校验二维、三维地图属性和全局配置接口的预检响应。"""

    @staticmethod
    def _login(auth_api, test_user):
        """先建立登录会话，使预检请求进入 GIS 路由。"""
        response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert response.status_code == 200
        assert response.json()["status"] == 0

    @pytest.mark.parametrize(
        ("config_key", "case_name"),
        [
            pytest.param("d2_data_path_url", "二维地图路径", id="d2-data-path"),
            pytest.param("d2_map_prop_url", "二维地图属性", id="d2-map-prop"),
            pytest.param("d3_map_prop_url", "三维地图属性", id="d3-map-prop"),
            pytest.param("d3_gis_config_url", "三维地图配置", id="d3-config"),
        ],
    )
    @allure.title("GIS 接口使用 OPTIONS 时返回空成功响应")
    def test_gis_endpoint_options_returns_empty_success(
        self,
        auth_api,
        request_util,
        config,
        test_user,
        config_key,
        case_name,
    ):
        """逐项校验 GIS 预检请求不会返回地图路径或配置业务数据。"""
        self._login(auth_api, test_user)
        allure.dynamic.parameter("接口名称", case_name)

        response = request_util.send_request(
            "options",
            config["gis"][config_key],
        )

        assert response.status_code == 200
        assert response.content == b""
