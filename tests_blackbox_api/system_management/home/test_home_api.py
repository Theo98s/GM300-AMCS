# -*- coding: utf-8 -*-
"""AMCS 首页与字典接口测试。"""
from __future__ import annotations

import allure


@allure.feature("首页接口")
class TestHomeApi:
    """首页菜单和公共字典查询用例。"""

    @allure.title("首页菜单初始化返回核心一级菜单")
    def test_init_menu_contains_core_top_modules(self, auth_api, home_api, test_user):
        """校验首页初始化菜单里包含核心一级菜单。

        这里不要求顺序完全一致，只要求核心模块仍然可见，避免因为菜单微调导致误报。
        """
        login_response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert login_response.json()["status"] == 0

        response = home_api.init_menu()
        assert response.status_code == 200

        body = response.json()
        assert body["status"] == 0
        host_menu_list = body["data"]["hostMenuList"]
        assert len(host_menu_list) >= 1

        first_plugin = host_menu_list[0]
        top_names = [item["name"] for item in first_plugin["leaf"]]
        assert "首页" in top_names
        assert "视频监控" in top_names
        assert "系统管理" in top_names

    @allure.title("首页菜单初始化返回首页默认地址")
    def test_init_menu_home_route_is_das_home(self, auth_api, home_api, test_user):
        """校验首页菜单的默认欢迎页地址符合当前系统配置。"""
        login_response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert login_response.json()["status"] == 0

        response = home_api.init_menu()
        body = response.json()
        welcome_menu = body["data"]["hostMenuList"][0]["leaf"][0]

        assert welcome_menu["id"] == "GM300-AMCS:amcs_welcome"
        assert welcome_menu["url"] == "/das/home"

    @allure.title("设备区域字典包含全区和进线区")
    def test_equip_area_dict_contains_expected_areas(self, auth_api, home_api, test_user):
        """校验设备区域字典至少包含首页常用区域。"""
        login_response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert login_response.json()["status"] == 0

        response = home_api.list_dict_no_root("EQUIP_AREA")
        assert response.status_code == 200

        body = response.json()
        assert isinstance(body, list)
        area_map = {item["code"]: item["name"] for item in body}
        assert area_map["00"] == "全区"
        assert area_map["01"] == "进线区"

    @allure.title("首页菜单叶子节点包含标准菜单字段")
    def test_init_menu_leaf_nodes_contain_expected_keys(self, auth_api, home_api, test_user):
        """校验首页初始化菜单的叶子节点包含菜单标识、名称、路由和展开状态字段。"""
        login_response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert login_response.json()["status"] == 0

        response = home_api.init_menu()
        body = response.json()
        first_leaf = body["data"]["hostMenuList"][0]["leaf"][0]

        assert set(first_leaf.keys()) >= {"id", "name", "text", "url", "openClosed", "pluginKey"}
        assert first_leaf["id"]
        assert first_leaf["text"]
        assert first_leaf["pluginKey"] == "GM300-AMCS"

    @allure.title("首页菜单视频监控模块包含实时视频和视频回放")
    def test_init_menu_video_module_contains_expected_routes(self, auth_api, home_api, test_user):
        """校验首页菜单中的视频监控模块保留实时视频和视频回放两个核心子菜单。"""
        login_response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert login_response.json()["status"] == 0

        response = home_api.init_menu()
        body = response.json()
        host_leaf = body["data"]["hostMenuList"][0]["leaf"]
        video_module = next(item for item in host_leaf if item["id"] == "GM300-AMCS:video")
        child_routes = {item["id"]: item["url"] for item in video_module["leaf"]}

        assert child_routes["GM300-AMCS:video:video_realtime"] == "/amcs/video/preview"
        assert child_routes["GM300-AMCS:video:video_playback"] == "/amcs/video/playback"

    @allure.title("首页菜单一级模块保留核心模块 ID")
    def test_init_menu_top_level_ids_contain_expected_modules(self, auth_api, home_api, test_user):
        """校验首页菜单一级模块仍包含首页、视频、历史、基础、配置和系统管理等核心模块。"""
        login_response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert login_response.json()["status"] == 0

        response = home_api.init_menu()
        body = response.json()
        top_ids = {item["id"] for item in body["data"]["hostMenuList"][0]["leaf"]}

        assert {
            "GM300-AMCS:amcs_welcome",
            "GM300-AMCS:video",
            "GM300-AMCS:history",
            "GM300-AMCS:base",
            "GM300-AMCS:config",
            "GM300-AMCS:sys",
        } <= top_ids

    @allure.title("首页菜单一级模块顺序与用户菜单树保持一致")
    def test_init_menu_top_level_ids_match_user_menu_tree(self, auth_api, home_api, menu_api, test_user):
        """校验首页菜单和用户菜单树的一级模块顺序保持一致。"""
        login_response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert login_response.json()["status"] == 0

        init_menu_body = home_api.init_menu().json()
        menu_tree_body = menu_api.get_user_menu_tree().json()
        init_ids = [item["id"] for item in init_menu_body["data"]["hostMenuList"][0]["leaf"]]
        tree_ids = [item["id"] for item in menu_tree_body[0]["children"]]

        assert init_ids == tree_ids

    @allure.title("首页欢迎菜单保持展开且启用状态")
    def test_init_menu_welcome_leaf_has_open_state_and_enabled_flag(self, auth_api, home_api, test_user):
        """校验首页欢迎菜单仍保持展开状态和启用标记。"""
        login_response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert login_response.json()["status"] == 0

        response = home_api.init_menu()
        body = response.json()
        welcome_leaf = body["data"]["hostMenuList"][0]["leaf"][0]

        assert welcome_leaf["id"] == "GM300-AMCS:amcs_welcome"
        assert welcome_leaf["openClosed"] == "open"
        assert welcome_leaf["state"] == 1

    @allure.title("设备区域字典项包含编码层级与展示字段")
    def test_equip_area_dict_entries_contain_expected_keys(self, auth_api, home_api, test_user):
        """校验设备区域字典项包含编码、名称、层级父节点和展示字段。"""
        login_response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert login_response.json()["status"] == 0

        response = home_api.list_dict_no_root("EQUIP_AREA")
        body = response.json()
        first_item = body[0]

        assert set(first_item.keys()) >= {"id", "code", "name", "parentId", "text", "typekey"}
        assert first_item["typekey"] == "EQUIP_AREA"
        assert first_item["text"] == first_item["name"]

    @allure.title("Init menu realtime module stays as open container")
    def test_init_menu_realtime_module_is_open_container(self, auth_api, home_api, test_user):
        """Verify the realtime-monitor top node remains an open container without a direct route."""
        login_response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert login_response.json()["status"] == 0

        response = home_api.init_menu()
        body = response.json()
        host_leaf = body["data"]["hostMenuList"][0]["leaf"]
        realtime_module = next(item for item in host_leaf if item["id"] == "GM300-AMCS:amcs_das")

        assert realtime_module["text"] == "实时监控"
        assert realtime_module["url"] is None
        assert realtime_module["openClosed"] == "open"
        assert realtime_module["state"] == 1

    @allure.title("Init menu top modules keep shared plugin key and open state")
    def test_init_menu_top_modules_keep_shared_plugin_key_and_open_state(self, auth_api, home_api, test_user):
        """Verify top-level home modules still belong to the same plugin and default to open nodes."""
        login_response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert login_response.json()["status"] == 0

        response = home_api.init_menu()
        body = response.json()
        top_modules = body["data"]["hostMenuList"][0]["leaf"][:8]

        for item in top_modules:
            assert item["pluginKey"] == "GM300-AMCS"
            assert item["openClosed"] == "open"

    @allure.title("Init menu container modules keep empty routes")
    def test_init_menu_container_modules_keep_empty_route_strings(self, auth_api, home_api, test_user):
        """Verify history, base, config, and system modules stay as open containers with empty-string routes."""
        login_response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert login_response.json()["status"] == 0

        response = home_api.init_menu()
        body = response.json()
        host_leaf = body["data"]["hostMenuList"][0]["leaf"]
        container_ids = {
            "GM300-AMCS:history",
            "GM300-AMCS:base",
            "GM300-AMCS:config",
            "GM300-AMCS:sys",
        }

        for item in host_leaf:
            if item["id"] in container_ids:
                assert item["url"] == ""
                assert item["openClosed"] == "open"
                assert item["state"] == 1

    @allure.title("Init menu patrol module stays as open container")
    def test_init_menu_patrol_module_is_open_container(self, auth_api, home_api, test_user):
        """Verify the patrol-management top node remains an open container without a direct route."""
        login_response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert login_response.json()["status"] == 0

        response = home_api.init_menu()
        body = response.json()
        host_leaf = body["data"]["hostMenuList"][0]["leaf"]
        patrol_module = next(item for item in host_leaf if item["id"] == "GM300-AMCS:amcs_patrol")

        assert patrol_module["text"] == "巡检管理"
        assert patrol_module["url"] is None
        assert patrol_module["openClosed"] == "open"
        assert patrol_module["state"] == 1
