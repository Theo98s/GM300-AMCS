# -*- coding: utf-8 -*-
"""GIS 地图跨接口功能流程测试。"""
from __future__ import annotations

import allure


class TestGisFunctionalFlowsMore:
    """补充覆盖 2D、3D 和 GIS 全局配置之间的串联功能流。"""

    @staticmethod
    def _login(auth_api, test_user):
        """统一执行登录，保证 GIS 三套查询共用同一会话。"""
        response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert response.status_code == 200
        assert response.json()["status"] == 0

    @allure.title("同一登录会话可连续完成 2D 3D 和 GIS 全局配置初始化")
    def test_single_login_session_can_bootstrap_d2_d3_and_global_gis_config(
        self,
        auth_api,
        gis_api,
        test_user,
    ):
        """登录一次后，连续加载二维地图、三维地图和 GIS 全局配置。"""
        self._login(auth_api, test_user)

        d2_body = gis_api.get_d2_map_prop().json()
        d3_body = gis_api.get_d3_map_prop().json()
        config_body = gis_api.get_d3_gis_config().json()

        assert d2_body["status"] == 0
        assert d2_body["data"]["typeCode"] == "2d"
        assert d3_body["status"] == 0
        assert d3_body["data"]["typeCode"] == "3d"
        assert config_body["status"] == 0
        assert config_body["data"]["gisEnable"] in {"true", "false"}

    @allure.title("GIS 地图属性初始化后仍可查询全局视角和本地服务配置")
    def test_gis_map_bootstrap_keeps_global_view_and_local_server_config_available(
        self,
        auth_api,
        gis_api,
        test_user,
    ):
        """先加载二维和三维地图属性，再校验全局配置中的视角和本地服务地址可用。"""
        self._login(auth_api, test_user)

        gis_api.get_d2_map_prop()
        gis_api.get_d3_map_prop()
        config_data = gis_api.get_d3_gis_config().json()["data"]

        assert config_data["localServerEnable"] in {"true", "false"}
        assert config_data["localServerUrl"].startswith("http")
        assert config_data["d3View"].startswith("[[")
        assert config_data["d3View"].endswith("]]")

    @allure.title("GIS 初始化成功后二维数据路径接口仍会返回缺参提示")
    def test_gis_bootstrap_does_not_change_d2_data_path_parameter_guard_behavior(
        self,
        auth_api,
        gis_api,
        test_user,
    ):
        """先完成 GIS 初始化，再校验二维数据路径接口的缺参保护行为保持不变。"""
        self._login(auth_api, test_user)

        gis_api.get_d2_map_prop()
        gis_api.get_d3_map_prop()
        gis_api.get_d3_gis_config()
        body = gis_api.get_d2_data_path().json()

        assert body["status"] == 0
        assert "地图类型参数" in body["message"]
