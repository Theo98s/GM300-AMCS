# -*- coding: utf-8 -*-
"""平台导航与核心业务入口功能流程测试。"""
from __future__ import annotations

import allure


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


class TestPlatformFunctionalFlowsMore:
    """补充覆盖登录会话在首页、菜单、插件和系统接口之间的串联功能流。"""

    @staticmethod
    def _login(auth_api, test_user):
        """统一执行登录，保证后续平台接口都复用同一会话。"""
        response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert response.status_code == 200
        assert response.json()["status"] == 0

    @allure.title("同一登录会话可串行访问首页菜单插件和系统核心接口")
    def test_single_login_session_can_traverse_core_platform_apis(
        self,
        auth_api,
        home_api,
        menu_api,
        plugin_api,
        system_api,
        test_user,
    ):
        """登录一次后，依次访问首页、菜单树、插件、告警数、时间戳和健康检查接口。"""
        self._login(auth_api, test_user)

        init_menu_body = home_api.init_menu().json()
        menu_tree_body = menu_api.get_user_menu_tree().json()
        plugin_list = plugin_api.find_plugin().json()
        alarm_count_body = system_api.get_alarm_count().json()
        timestamp_value = system_api.get_timestamp().json()
        health_body = system_api.get_health().json()

        init_ids = [item["id"] for item in init_menu_body["data"]["hostMenuList"][0]["leaf"]]
        tree_ids = [item["id"] for item in menu_tree_body[0]["children"]]
        main_plugin = next(item for item in plugin_list if item["pkey"] == "GM300-AMCS")

        assert init_menu_body["status"] == 0
        assert menu_tree_body[0]["id"] == "GM300-AMCS"
        assert init_ids == tree_ids
        assert main_plugin["welcomeUrl"] == "/amcs/index"
        assert "/amcs/video/preview" in main_plugin["menuContent"]
        assert alarm_count_body["status"] == 0
        assert isinstance(alarm_count_body["data"], int)
        assert alarm_count_body["data"] >= 0
        assert isinstance(timestamp_value, int)
        assert timestamp_value >= 10**12
        assert health_body["status"] == 0
        assert health_body["message"] == "查询成功"
        assert isinstance(health_body["data"], list)

    @allure.title("同一会话可从匿名登录页切换为已登录首页菜单 JSON")
    def test_same_session_can_upgrade_from_login_html_to_home_json_after_login(
        self,
        request_util,
        config,
        auth_api,
        home_api,
        test_user,
    ):
        """先以匿名方式访问首页菜单，再在同一会话登录并校验返回内容切换为 JSON。"""
        anonymous_response = request_util.send_request(
            "post",
            config["home"]["init_menu_url"],
            data={},
        )
        assert anonymous_response.status_code == 200
        assert "text/html" in anonymous_response.headers.get("Content-Type", "")
        assert "window.top" in anonymous_response.text

        # 这里复用同一个 request_util/session，验证登录确实写入了会话态。
        self._login(auth_api, test_user)

        logged_in_response = home_api.init_menu()
        assert logged_in_response.status_code == 200
        assert "application/json" in logged_in_response.headers.get("Content-Type", "")

        body = logged_in_response.json()
        assert body["status"] == 0
        assert body["data"]["hostMenuList"][0]["leaf"][0]["url"] == "/das/home"

    @allure.title("登录后平台导航和字典接口可在同一会话内连续完成初始化")
    def test_login_session_can_finish_navigation_and_dictionary_bootstrap(
        self,
        auth_api,
        home_api,
        menu_api,
        plugin_api,
        test_user,
    ):
        """登录后连续获取首页菜单、用户菜单树、插件定义和区域字典，校验前端初始化所需数据闭环可用。"""
        self._login(auth_api, test_user)

        init_menu_body = home_api.init_menu().json()
        menu_tree_body = menu_api.get_user_menu_tree().json()
        plugin_list = plugin_api.find_plugin().json()
        equip_area_rows = home_api.list_dict_no_root("EQUIP_AREA").json()

        home_leaf = init_menu_body["data"]["hostMenuList"][0]["leaf"][0]
        menu_root = menu_tree_body[0]
        first_tree_child = menu_root["children"][0]
        main_plugin = next(item for item in plugin_list if item["pkey"] == "GM300-AMCS")
        area_map = {item["code"]: item["name"] for item in equip_area_rows}

        assert init_menu_body["status"] == 0
        assert home_leaf["id"] == "GM300-AMCS:amcs_welcome"
        assert home_leaf["url"] == "/das/home"
        assert menu_root["id"] == "GM300-AMCS"
        assert first_tree_child["id"] == home_leaf["id"]
        assert first_tree_child["url"] == home_leaf["url"]
        assert "/monitor/index" in main_plugin["menuContent"]
        assert "/amcs/alarm/index" in main_plugin["menuContent"]
        assert area_map["00"] == "全区"
        assert area_map["01"] == "进线区"
