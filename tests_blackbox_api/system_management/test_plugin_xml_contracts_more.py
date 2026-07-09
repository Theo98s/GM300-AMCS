# -*- coding: utf-8 -*-
"""AMCS 插件 XML 更多契约测试。"""
from __future__ import annotations

import xml.etree.ElementTree as element_tree

import allure


@allure.feature("菜单与插件")
class TestPluginXmlContractsMore:
    """补充校验插件 menuContent XML 结构。"""

    @staticmethod
    def _login(auth_api, test_user):
        """每条用例先登录，并确认会话已建立。"""
        login_response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert login_response.status_code == 200
        assert login_response.json()["status"] == 0

    @staticmethod
    def _main_plugin(plugin_api) -> dict:
        """返回主 AMCS 插件定义，供 XML 解析断言使用。"""
        body = plugin_api.find_plugin().json()
        return next(item for item in body if item["pkey"] == "GM300-AMCS")

    @staticmethod
    def _menu_root(plugin_api):
        """解析主插件的 menuContent XML。"""
        plugin = TestPluginXmlContractsMore._main_plugin(plugin_api)
        return element_tree.fromstring(plugin["menuContent"])

    @allure.title("插件 menuContent 保持可解析的 resource XML")
    def test_plugin_menu_content_remains_parseable_resource_xml(self, auth_api, plugin_api, test_user):
        """校验插件菜单定义仍是带有预期根节点和顶层分组的合法 XML。"""
        self._login(auth_api, test_user)

        root = self._menu_root(plugin_api)
        groups = root.findall("./group")
        assert root.tag == "resource"
        assert len(groups) == 8
        assert [group.attrib["id"] for group in groups] == [
            "amcs_welcome",
            "video",
            "amcs_das",
            "amcs_patrol",
            "history",
            "base",
            "config",
            "sys",
        ]

    @allure.title("插件 XML 分组页面数量保持预期分布")
    def test_plugin_menu_content_group_page_counts_keep_expected_distribution(
        self,
        auth_api,
        plugin_api,
        test_user,
    ):
        """校验主菜单分组仍暴露导航所依赖的当前页面数量布局。"""
        self._login(auth_api, test_user)

        root = self._menu_root(plugin_api)
        page_counts = {
            group.attrib["id"]: len(group.findall("./page"))
            for group in root.findall("./group")
        }
        assert page_counts == {
            "amcs_welcome": 0,
            "video": 3,
            "amcs_das": 5,
            "amcs_patrol": 3,
            "history": 3,
            "base": 9,
            "config": 5,
            "sys": 5,
        }

    @allure.title("插件 XML 核心分组路由保持预期集合")
    def test_plugin_menu_content_core_group_routes_keep_expected_endpoint_sets(
        self,
        auth_api,
        plugin_api,
        test_user,
    ):
        """校验视频、巡检、历史、基础、配置和系统分组保持当前页面路由集合。"""
        self._login(auth_api, test_user)

        root = self._menu_root(plugin_api)
        route_map = {
            group.attrib["id"]: [page.attrib.get("url", "") for page in group.findall("./page")]
            for group in root.findall("./group")
        }
        assert route_map["video"] == [
            "/amcs/video/preview",
            "/amcs/video/playback",
            "/amcs/video/thermometry",
        ]
        assert route_map["amcs_patrol"] == [
            "/amcs/patrol/plan",
            "/amcs/patrol/card",
            "/amcs/patrol/record",
        ]
        assert route_map["history"] == [
            "/amcs/monitorLink/index",
            "/amcs/trend/index",
            "/amcs/alarm/index",
        ]
        assert "/monitor/index" in route_map["base"]
        assert "/amcs/video/preset" in route_map["config"]
        assert "/menu" in route_map["sys"]
