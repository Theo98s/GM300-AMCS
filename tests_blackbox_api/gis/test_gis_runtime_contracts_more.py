# -*- coding: utf-8 -*-
"""AMCS GIS 运行时补充契约测试。"""
from __future__ import annotations

import allure


@allure.feature("系统配置-GIS")
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
