# -*- coding: utf-8 -*-
"""AMCS 插件运行时补充契约测试。"""
from __future__ import annotations

import xml.etree.ElementTree as element_tree

import allure


@allure.feature("菜单与插件")
class TestPluginRuntimeContractsExtra:
    """补充校验主插件定义与 menuContent 的运行时属性。"""

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
        """返回主 AMCS 插件定义，供断言复用。"""
        body = plugin_api.find_plugin().json()
        return next(item for item in body if item["pkey"] == "GM300-AMCS")

    @staticmethod
    def _menu_groups(plugin_api):
        """解析主插件 menuContent，并返回分组列表。"""
        plugin = TestPluginRuntimeContractsExtra._main_plugin(plugin_api)
        root = element_tree.fromstring(plugin["menuContent"])
        return root.findall("./group")

    @allure.title("主插件定义保持默认空扩展字段和启用标记")
    def test_main_plugin_keeps_nullable_extension_fields(self, auth_api, plugin_api, test_user):
        """校验主插件定义仍保持默认空扩展字段与启用标记。"""
        self._login(auth_api, test_user)

        plugin = self._main_plugin(plugin_api)
        assert isinstance(plugin["id"], str) and plugin["id"]
        assert plugin["deleted"] == 0
        assert plugin["isEnabled"] == 1
        assert plugin["icon"] is None
        assert plugin["menus"] is None

    @allure.title("插件 XML 分组保持稳定顺序编号和启用状态")
    def test_plugin_menu_groups_keep_seq_order_and_enabled_state(self, auth_api, plugin_api, test_user):
        """校验插件 XML 分组仍保持当前顺序编号和启用状态字段。"""
        self._login(auth_api, test_user)

        groups = self._menu_groups(plugin_api)
        assert [group.attrib["seq"] for group in groups] == ["1", "2", "3", "4", "5", "8", "9", "10"]
        assert all(group.attrib["state"] == "1" for group in groups)

    @allure.title("插件 XML 页面节点保持非空名称和启用状态")
    def test_plugin_menu_pages_keep_name_and_enabled_state(self, auth_api, plugin_api, test_user):
        """校验插件 XML 各页面节点仍保留非空名称和启用状态。"""
        self._login(auth_api, test_user)

        groups = self._menu_groups(plugin_api)
        for group in groups:
            for page in group.findall("./page")[:3]:
                assert isinstance(page.attrib["id"], str) and page.attrib["id"]
                assert isinstance(page.attrib["name"], str) and page.attrib["name"]
                assert page.attrib["state"] == "1"
                assert page.attrib["seq"].isdigit()
