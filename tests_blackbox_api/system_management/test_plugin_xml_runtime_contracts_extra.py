# -*- coding: utf-8 -*-
"""AMCS 插件 XML 运行时补充契约测试。"""
from __future__ import annotations

import xml.etree.ElementTree as element_tree

import allure


@allure.feature("菜单与插件")
class TestPluginXmlRuntimeContractsExtra:
    """补充校验插件 XML 的图标、状态和顶层路由属性。"""

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
    def _groups(plugin_api):
        """解析主插件 menuContent，并返回顶层分组列表。"""
        plugin = next(item for item in plugin_api.find_plugin().json() if item["pkey"] == "GM300-AMCS")
        root = element_tree.fromstring(plugin["menuContent"])
        return root.findall("./group")

    @allure.title("插件 XML 顶层分组保持 iconfont 图标前缀和启用状态")
    def test_plugin_xml_groups_keep_icon_prefix_and_enabled_state(self, auth_api, plugin_api, test_user):
        """校验插件 XML 顶层分组仍保持 iconfont 图标前缀和启用状态。"""
        self._login(auth_api, test_user)

        groups = self._groups(plugin_api)
        for group in groups:
            assert group.attrib["icon"].startswith("iconfont ")
            assert group.attrib["state"] == "1"
            assert group.attrib["seq"].isdigit()

    @allure.title("插件 XML 顶层分组保持当前顶层路由空值模式")
    def test_plugin_xml_groups_keep_top_level_url_nullability_pattern(self, auth_api, plugin_api, test_user):
        """校验插件 XML 顶层分组仍保持欢迎页直达、其余容器为空路由模式。"""
        self._login(auth_api, test_user)

        groups = {group.attrib["id"]: group for group in self._groups(plugin_api)}
        assert groups["amcs_welcome"].attrib["url"] == "/das/home"
        for group_id in ("video", "amcs_das", "amcs_patrol"):
            assert "url" not in groups[group_id].attrib
        for group_id in ("history", "base", "config", "sys"):
            assert groups[group_id].attrib["url"] == ""
