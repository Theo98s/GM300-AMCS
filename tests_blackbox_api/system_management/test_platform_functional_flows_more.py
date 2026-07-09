# -*- coding: utf-8 -*-
"""AMCS 平台功能流补充测试。"""
from __future__ import annotations

import allure


@allure.feature("系统接口")
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
