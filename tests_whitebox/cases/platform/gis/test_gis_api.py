# -*- coding: utf-8 -*-
"""AMCS 地图与三维配置接口测试。"""
from __future__ import annotations

import allure


@allure.feature("系统配置-GIS")
class TestGisApi:
    """二维地图、三维地图和 GIS 全局配置查询用例。"""

    @allure.title("二维地图属性接口返回 SVG 文件路径")
    def test_d2_map_prop_returns_svg_path(self, auth_api, gis_api, test_user):
        """校验二维地图属性接口返回结构稳定，有文件时再校验 SVG 路径。"""
        login_response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert login_response.json()["status"] == 0

        response = gis_api.get_d2_map_prop()
        assert response.status_code == 200

        body = response.json()
        assert body["status"] == 0
        assert body["data"]["typeCode"] == "2d"
        assert "filePath" in body["data"]
        assert "mapProperty" in body["data"]
        if body["data"]["filePath"]:
            assert body["data"]["filePath"].endswith(".svg")

    @allure.title("三维地图属性接口返回三维数据目录")
    def test_d3_map_prop_returns_tiles_path(self, auth_api, gis_api, test_user):
        """校验三维地图属性里包含三维数据目录。"""
        login_response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert login_response.json()["status"] == 0

        response = gis_api.get_d3_map_prop()
        body = response.json()

        assert body["status"] == 0
        assert body["data"]["typeCode"] == "3d"
        assert "3dtiles" in body["data"]["d3DataName"]
        assert body["data"]["d3DataPath"].startswith("/")

    @allure.title("GIS 全局配置接口返回开关配置")
    def test_d3_gis_config_returns_feature_flags(self, auth_api, gis_api, test_user):
        """校验 GIS 全局配置中包含启用开关。"""
        login_response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert login_response.json()["status"] == 0

        response = gis_api.get_d3_gis_config()
        body = response.json()

        assert body["status"] == 0
        assert set(body["data"].keys()) >= {"gisEnable", "gisD3PatrolEnable", "d3Theme"}
        assert body["data"]["gisEnable"] in {"true", "false"}

    @allure.title("二维地图数据路径接口缺少参数时返回业务提示")
    def test_d2_data_path_without_type_returns_prompt(self, auth_api, gis_api, test_user):
        """校验二维地图数据路径接口对缺失参数有明确提示。"""
        login_response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert login_response.json()["status"] == 0

        response = gis_api.get_d2_data_path()
        body = response.json()

        assert body["status"] == 0
        assert "地图类型参数" in body["message"]
