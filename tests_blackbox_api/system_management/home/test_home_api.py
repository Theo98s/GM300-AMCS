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
