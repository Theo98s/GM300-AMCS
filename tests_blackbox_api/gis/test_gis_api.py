# -*- coding: utf-8 -*-
"""AMCS 地图与三维配置接口测试。"""
from __future__ import annotations

import allure
import re


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

    @allure.title("GIS 全局配置返回本地服务和视角参数")
    def test_d3_gis_config_contains_local_server_and_view_fields(self, auth_api, gis_api, test_user):
        """校验 GIS 全局配置包含本地服务开关、地址和三维视角参数。"""
        login_response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert login_response.json()["status"] == 0

        response = gis_api.get_d3_gis_config()
        body = response.json()

        assert body["status"] == 0
        assert body["data"]["localServerEnable"] in {"true", "false"}
        assert body["data"]["localServerUrl"].startswith("http")
        assert body["data"]["d3View"].startswith("[[")
        assert body["data"]["d3View"].endswith("]]")

    @allure.title("二维和三维地图属性包含审计时间字段")
    def test_map_props_contain_audit_timestamps(self, auth_api, gis_api, test_user):
        """校验二维和三维地图属性都保留创建时间和更新时间字符串。"""
        login_response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert login_response.json()["status"] == 0

        d2_body = gis_api.get_d2_map_prop().json()["data"]
        d3_body = gis_api.get_d3_map_prop().json()["data"]
        datetime_pattern = r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}"

        assert re.fullmatch(datetime_pattern, d2_body["createTime"])
        assert re.fullmatch(datetime_pattern, d2_body["updateTime"])
        assert re.fullmatch(datetime_pattern, d3_body["createTime"])
        assert re.fullmatch(datetime_pattern, d3_body["updateTime"])

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

    @allure.title("二维地图属性返回二维地图来源分类")
    def test_d2_map_prop_contains_source_category(self, auth_api, gis_api, test_user):
        """校验二维地图属性中保留来源分类和二维类型标识。"""
        login_response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert login_response.json()["status"] == 0

        response = gis_api.get_d2_map_prop()
        body = response.json()

        assert body["status"] == 0
        assert body["data"]["typeCode"] == "2d"
        assert body["data"]["sourceCategory"] == "二维地图"

    @allure.title("二维和三维地图属性包含创建人与未删除标记")
    def test_map_props_contain_creator_and_deleted_flag(self, auth_api, gis_api, test_user):
        """校验二维和三维地图属性都保留创建人字段和未删除标记。"""
        login_response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert login_response.json()["status"] == 0

        d2_body = gis_api.get_d2_map_prop().json()["data"]
        d3_body = gis_api.get_d3_map_prop().json()["data"]

        assert d2_body["creator"]
        assert d3_body["creator"]
        assert d2_body["deleted"] == 0
        assert d3_body["deleted"] == 0

    @allure.title("3D map path keeps cesium-data directory convention")
    def test_d3_map_prop_path_uses_cesium_data_directory(self, auth_api, gis_api, test_user):
        """校验三维地图资源路径仍遵循 cesium-data 部署约定。"""
        login_response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert login_response.json()["status"] == 0

        response = gis_api.get_d3_map_prop()
        body = response.json()["data"]

        assert body["d3DataName"].startswith("3dtiles")
        assert body["d3DataPath"].startswith("/cesium-data/")

    @allure.title("GIS 配置保留本地服务地址与 d3 视角坐标格式")
    def test_d3_gis_config_view_and_server_fields_use_expected_formats(self, auth_api, gis_api, test_user):
        """校验 GIS 配置仍保留 HTTP 本地服务地址和双段坐标视角字符串。"""
        login_response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert login_response.json()["status"] == 0

        response = gis_api.get_d3_gis_config()
        body = response.json()["data"]

        assert body["localServerUrl"].startswith("http://")
        assert "127.0.0.1" in body["localServerUrl"]
        assert re.fullmatch(r"\[\[[^]]+\],\[[^]]+\]\]", body["d3View"])
