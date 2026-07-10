# -*- coding: utf-8 -*-
"""GIS 配置、属性、代理与运行时契约测试。"""
from __future__ import annotations

import allure
import json


class TestGisConfigContracts:
    """补充校验 GIS 全局配置契约。"""

    @allure.title("GIS 配置布尔开关使用字符串布尔值且主题非空")
    def test_d3_gis_config_boolean_switches_and_theme_are_stable(self, auth_api, gis_api, test_user):
        """校验 GIS 开关字段保持字符串布尔值，主题字段保持非空。"""
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


class TestGisPropertyContractsMore:
    """补充校验 GIS 地图属性中的 JSON 字段与来源分类。"""

    @staticmethod
    def _login(auth_api, test_user):
        """每条用例先登录，并确认会话已建立。"""
        login_response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert login_response.status_code == 200
        assert login_response.json()["status"] == 0

    @allure.title("二维地图属性 mapProperty 保持可解析 JSON")
    def test_d2_map_prop_map_property_remains_parseable_json(self, auth_api, gis_api, test_user):
        """校验二维地图属性中的 mapProperty 字段仍是可解析 JSON。"""
        self._login(auth_api, test_user)

        data = gis_api.get_d2_map_prop().json()["data"]
        map_property = json.loads(data["mapProperty"])
        assert isinstance(map_property, dict)
        assert "zoneCamera" in map_property
        assert isinstance(map_property["zoneCamera"], dict)

    @allure.title("三维地图属性 d3DataProp 保持可解析 JSON")
    def test_d3_map_prop_data_prop_remains_parseable_json(self, auth_api, gis_api, test_user):
        """校验三维地图属性中的 d3DataProp 字段仍是可解析 JSON。"""
        self._login(auth_api, test_user)

        data = gis_api.get_d3_map_prop().json()["data"]
        d3_data_prop = json.loads(data["d3DataProp"])
        assert set(d3_data_prop.keys()) == {"transparentModel", "unavailableModel", "railCamera", "robot"}
        assert all(isinstance(d3_data_prop[key], list) for key in d3_data_prop)

    @allure.title("二维与三维地图属性保持来源分类和类型编码一致")
    def test_map_props_keep_source_category_and_type_code_alignment(self, auth_api, gis_api, test_user):
        """校验二维和三维地图属性的来源分类与类型编码保持对齐。"""
        self._login(auth_api, test_user)

        d2_data = gis_api.get_d2_map_prop().json()["data"]
        d3_data = gis_api.get_d3_map_prop().json()["data"]

        assert d2_data["typeCode"] == "2d"
        assert d2_data["sourceCategory"] == "二维地图"
        assert d3_data["typeCode"] == "3d"
        assert d3_data["sourceCategory"] == "三维地图"


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


class TestGisRuntimeContractsMore:
    """补充校验 GIS 地图属性和配置中的默认空值模式。"""

    @staticmethod
    def _login(auth_api, test_user):
        """每条用例先登录，并确认会话已建立。"""
        login_response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert login_response.status_code == 200
        assert login_response.json()["status"] == 0

    @allure.title("二维地图属性保持空三维扩展字段和未转换状态")
    def test_d2_map_prop_keeps_null_3d_fields_and_default_convert_state(self, auth_api, gis_api, test_user):
        """校验二维地图属性仍保持空三维扩展字段和默认转换状态。"""
        self._login(auth_api, test_user)

        data = gis_api.get_d2_map_prop().json()["data"]
        assert data["convertState"] == 0
        assert data["sourceName"] is None
        assert data["mapId"] is None
        assert data["remark"] is None
        assert data["d3DataName"] is None
        assert data["d3DataPath"] is None
        assert data["d3DataProp"] is None

    @allure.title("三维地图属性保持空二维文件字段和未删除审计字段")
    def test_d3_map_prop_keeps_null_2d_file_fields_and_delete_audit_defaults(self, auth_api, gis_api, test_user):
        """校验三维地图属性仍保持空二维文件字段和默认删除审计字段。"""
        self._login(auth_api, test_user)

        data = gis_api.get_d3_map_prop().json()["data"]
        assert data["convertState"] == 0
        assert data["fileName"] is None
        assert data["filePath"] is None
        assert data["sourceName"] is None
        assert data["mapId"] is None
        assert data["deleter"] is None
        assert data["deleteTime"] is None

    @allure.title("GIS 全局配置保持当前主题与开关默认值")
    def test_d3_gis_config_keeps_current_theme_and_switch_defaults(self, auth_api, gis_api, test_user):
        """校验 GIS 全局配置仍保持当前主题和开关默认值。"""
        self._login(auth_api, test_user)

        data = gis_api.get_d3_gis_config().json()["data"]
        assert data["gisEnable"] == "true"
        assert data["gisD3PatrolEnable"] == "true"
        assert data["localServerEnable"] == "false"
        assert data["d3Theme"] == "default"


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
