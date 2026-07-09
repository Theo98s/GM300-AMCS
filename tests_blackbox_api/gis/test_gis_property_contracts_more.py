# -*- coding: utf-8 -*-
"""AMCS GIS 属性更多契约测试。"""
from __future__ import annotations

import json

import allure


@allure.feature("系统配置-GIS")
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
