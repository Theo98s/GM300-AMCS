# -*- coding: utf-8 -*-
"""AMCS 业务入口功能流补充测试。"""
from __future__ import annotations

import allure


@allure.feature("系统接口")
class TestBusinessEntryFunctionalFlowsMore:
    """补充覆盖首页导航元数据到真实业务接口的跨模块串联功能流。"""

    @staticmethod
    def _login(auth_api, test_user):
        """统一执行登录，保证多个业务模块接口都复用同一会话。"""
        response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert response.status_code == 200
        assert response.json()["status"] == 0

    @staticmethod
    def _main_plugin(plugin_api) -> dict:
        """返回主插件定义，便于校验菜单路由与业务接口入口对齐。"""
        plugins = plugin_api.find_plugin().json()
        return next(item for item in plugins if item["pkey"] == "GM300-AMCS")

    @allure.title("首页导航可串联到视频告警和基础数据模块接口")
    def test_navigation_can_bootstrap_video_alarm_and_base_data_modules(
        self,
        auth_api,
        home_api,
        plugin_api,
        video_api,
        alarm_api,
        database_api,
        test_user,
    ):
        """登录后先拿到首页导航，再连续访问视频、告警和基础数据模块接口。"""
        self._login(auth_api, test_user)

        init_menu_body = home_api.init_menu().json()
        plugin = self._main_plugin(plugin_api)
        camera_tree = video_api.get_camera_tree().json()
        alarm_rows = alarm_api.get_alarm_record_page().json()
        monitor_body = database_api.list_monitors(page=1, rows=5).json()

        top_ids = {item["id"] for item in init_menu_body["data"]["hostMenuList"][0]["leaf"]}
        assert "GM300-AMCS:video" in top_ids
        assert "GM300-AMCS:base" in top_ids
        assert "/amcs/video/preview" in plugin["menuContent"]
        assert "/amcs/alarm/index" in plugin["menuContent"]
        assert "/monitor/index" in plugin["menuContent"]
        assert isinstance(camera_tree, list)
        assert len(camera_tree) > 0
        assert isinstance(alarm_rows, list)
        assert isinstance(monitor_body["rows"], list)
        assert monitor_body["total"] >= len(monitor_body["rows"])

    @allure.title("首页导航可串联到巡检历史和 GIS 模块接口")
    def test_navigation_can_bootstrap_patrol_history_and_gis_modules(
        self,
        auth_api,
        home_api,
        plugin_api,
        patrol_api,
        history_api,
        gis_api,
        test_user,
    ):
        """登录后先拿到首页导航，再连续访问巡检、历史记录和 GIS 模块接口。"""
        self._login(auth_api, test_user)

        init_menu_body = home_api.init_menu().json()
        plugin = self._main_plugin(plugin_api)
        patrol_cards = patrol_api.list_patrol_cards().json()
        history_body = history_api.find_monitor_link_history({"rows": 3}).json()
        gis_config = gis_api.get_d3_gis_config().json()

        top_ids = {item["id"] for item in init_menu_body["data"]["hostMenuList"][0]["leaf"]}
        assert "GM300-AMCS:amcs_patrol" in top_ids
        assert "GM300-AMCS:history" in top_ids
        assert "/amcs/patrol/plan" in plugin["menuContent"]
        assert "/amcs/monitorLink/index" in plugin["menuContent"]
        assert isinstance(patrol_cards, list)
        assert len(patrol_cards) > 0
        assert isinstance(history_body["rows"], list)
        assert history_body["total"] >= len(history_body["rows"])
        assert gis_config["status"] == 0
        assert gis_config["data"]["gisEnable"] in {"true", "false"}

    @allure.title("首页导航可串联到 RDAC 和系统状态模块接口")
    def test_navigation_can_bootstrap_rdac_and_system_status_modules(
        self,
        auth_api,
        home_api,
        plugin_api,
        rdac_api,
        system_api,
        test_user,
    ):
        """登录后先拿到首页导航，再连续访问 RDAC 站点列表和系统状态接口。"""
        self._login(auth_api, test_user)

        init_menu_body = home_api.init_menu().json()
        plugin = self._main_plugin(plugin_api)
        station_rows = rdac_api.list_stations().json()
        alarm_count_body = system_api.get_alarm_count().json()
        health_body = system_api.get_health().json()

        top_ids = {item["id"] for item in init_menu_body["data"]["hostMenuList"][0]["leaf"]}
        assert "GM300-AMCS:sys" in top_ids
        assert "/menu" in plugin["menuContent"]
        assert isinstance(station_rows, list)
        assert len(station_rows) > 0
        assert alarm_count_body["status"] == 0
        assert isinstance(alarm_count_body["data"], int)
        assert health_body["status"] == 0
        assert isinstance(health_body["data"], list)
