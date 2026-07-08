# -*- coding: utf-8 -*-
"""AMCS 菜单与插件接口测试。"""
from __future__ import annotations

import allure


@allure.feature("菜单与插件")
class TestMenuPluginApi:
    """菜单树和插件定义一致性校验。"""

    @allure.title("用户菜单树包含首页和实时视频")
    def test_user_menu_tree_contains_expected_nodes(self, auth_api, menu_api, test_user):
        """校验当前用户菜单树包含基础可见菜单。"""
        login_response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert login_response.json()["status"] == 0

        response = menu_api.get_user_menu_tree()
        assert response.status_code == 200

        body = response.json()
        assert isinstance(body, list)
        root = body[0]
        child_names = [item["text"] for item in root["children"]]
        assert "首页" in child_names
        assert "视频监控" in child_names

    @allure.title("插件列表包含 GM300-AMCS 主插件")
    def test_plugin_list_contains_main_plugin(self, auth_api, plugin_api, test_user):
        """校验插件接口能返回当前系统主插件。"""
        login_response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert login_response.json()["status"] == 0

        response = plugin_api.find_plugin()
        assert response.status_code == 200

        body = response.json()
        assert isinstance(body, list)
        plugin = next(item for item in body if item["pkey"] == "GM300-AMCS")
        assert plugin["name"] == "牵引变电所辅助监控被控站系统"
        assert plugin["isEnabled"] == 1

    @allure.title("插件 XML 定义包含实时视频页面地址")
    def test_plugin_menu_content_contains_video_preview_route(self, auth_api, plugin_api, test_user):
        """校验插件菜单定义里包含视频监控页面配置。"""
        login_response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert login_response.json()["status"] == 0

        response = plugin_api.find_plugin()
        body = response.json()
        plugin = next(item for item in body if item["pkey"] == "GM300-AMCS")

        assert "/amcs/video/preview" in plugin["menuContent"]
        assert "video_playback" in plugin["menuContent"]

    @allure.title("用户菜单树根节点包含系统标识与关闭状态")
    def test_user_menu_tree_root_contains_identity_fields(self, auth_api, menu_api, test_user):
        """校验用户菜单树根节点保留系统标识、文本和折叠状态字段。"""
        login_response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert login_response.json()["status"] == 0

        response = menu_api.get_user_menu_tree()
        body = response.json()
        root = body[0]

        assert set(root.keys()) >= {"id", "text", "state", "children"}
        assert root["id"] == "GM300-AMCS"
        assert root["text"] == "牵引变电所辅助监控被控站系统"
        assert root["state"] in {"open", "closed"}

    @allure.title("用户菜单树首个子菜单保留首页路由")
    def test_user_menu_tree_first_child_contains_home_route(self, auth_api, menu_api, test_user):
        """校验用户菜单树首个子菜单仍指向首页路由。"""
        login_response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert login_response.json()["status"] == 0

        response = menu_api.get_user_menu_tree()
        body = response.json()
        first_child = body[0]["children"][0]

        assert set(first_child.keys()) >= {"id", "text", "state", "url"}
        assert first_child["id"] == "GM300-AMCS:amcs_welcome"
        assert first_child["text"] == "首页"
        assert first_child["url"] == "/das/home"
        assert first_child["state"] == "open"

    @allure.title("用户菜单树保留核心一级菜单 ID")
    def test_user_menu_tree_contains_expected_top_level_ids(self, auth_api, menu_api, test_user):
        """校验用户菜单树一级子菜单仍包含视频、巡检、历史、基础、配置和系统管理模块。"""
        login_response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert login_response.json()["status"] == 0

        response = menu_api.get_user_menu_tree()
        body = response.json()
        child_ids = {item["id"] for item in body[0]["children"]}

        assert {
            "GM300-AMCS:video",
            "GM300-AMCS:amcs_patrol",
            "GM300-AMCS:history",
            "GM300-AMCS:base",
            "GM300-AMCS:config",
            "GM300-AMCS:sys",
        } <= child_ids

    @allure.title("主插件定义包含欢迎页和图标字段")
    def test_plugin_definition_contains_welcome_url_and_icon(self, auth_api, plugin_api, test_user):
        """校验主插件定义保留欢迎页路由和图标字段。"""
        login_response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert login_response.json()["status"] == 0

        response = plugin_api.find_plugin()
        body = response.json()
        plugin = next(item for item in body if item["pkey"] == "GM300-AMCS")

        assert set(plugin.keys()) >= {"pkey", "name", "welcomeUrl", "icon", "isEnabled"}
        assert plugin["welcomeUrl"] == "/amcs/index"
        assert plugin["isEnabled"] == 1

    @allure.title("主插件菜单定义包含巡检监控报警和预置位路由")
    def test_plugin_menu_content_contains_core_business_routes(self, auth_api, plugin_api, test_user):
        """校验主插件 XML 菜单定义仍包含巡检、监控点、报警记录和预置位配置路由。"""
        login_response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert login_response.json()["status"] == 0

        response = plugin_api.find_plugin()
        body = response.json()
        plugin = next(item for item in body if item["pkey"] == "GM300-AMCS")

        assert "/amcs/patrol/plan" in plugin["menuContent"]
        assert "/monitor/index" in plugin["menuContent"]
        assert "/amcs/alarm/index" in plugin["menuContent"]
        assert "/amcs/video/preset" in plugin["menuContent"]

    @allure.title("用户菜单树视频模块默认折叠且无直接路由")
    def test_user_menu_tree_video_module_is_closed_container(self, auth_api, menu_api, test_user):
        """校验用户菜单树中的视频监控一级节点是折叠容器节点而不是直接页面路由。"""
        login_response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert login_response.json()["status"] == 0

        response = menu_api.get_user_menu_tree()
        body = response.json()
        video_node = next(item for item in body[0]["children"] if item["id"] == "GM300-AMCS:video")

        assert video_node["text"] == "视频监控"
        assert video_node["state"] == "closed"
        assert video_node["url"] is None

    @allure.title("User menu realtime module stays as closed container")
    def test_user_menu_tree_realtime_module_is_closed_container(self, auth_api, menu_api, test_user):
        """Verify the realtime-monitor node in the user menu tree stays collapsed and route-less."""
        login_response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert login_response.json()["status"] == 0

        response = menu_api.get_user_menu_tree()
        body = response.json()
        realtime_node = next(item for item in body[0]["children"] if item["id"] == "GM300-AMCS:amcs_das")

        assert realtime_node["text"] == "实时监控"
        assert realtime_node["state"] == "closed"
        assert realtime_node["url"] is None
