# -*- coding: utf-8 -*-
"""AMCS 菜单与插件一致性补充契约测试。"""
from __future__ import annotations

import xml.etree.ElementTree as element_tree

import allure


@allure.feature("菜单与插件")
class TestMenuPluginConsistencyContractsExtra:
    """补充校验首页菜单、用户菜单树与插件 XML 的一致性。"""

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
    def _load_views(home_api, menu_api, plugin_api):
        """统一加载首页菜单、用户菜单树与主插件 XML。"""
        init_leaf = home_api.init_menu().json()["data"]["hostMenuList"][0]["leaf"]
        tree_children = menu_api.get_user_menu_tree().json()[0]["children"]
        plugin = next(item for item in plugin_api.find_plugin().json() if item["pkey"] == "GM300-AMCS")
        xml_root = element_tree.fromstring(plugin["menuContent"])
        return init_leaf, tree_children, xml_root

    @allure.title("视频模块在首页菜单、用户菜单树和插件 XML 中保持同序")
    def test_video_module_keeps_same_child_order_across_menu_views(
        self,
        auth_api,
        home_api,
        menu_api,
        plugin_api,
        test_user,
    ):
        """校验视频模块在三份导航数据中的子节点顺序保持一致。"""
        self._login(auth_api, test_user)

        init_leaf, tree_children, xml_root = self._load_views(home_api, menu_api, plugin_api)
        init_video_ids = [item["id"] for item in next(item for item in init_leaf if item["id"] == "GM300-AMCS:video")["leaf"]]
        tree_video_ids = [item["id"] for item in next(item for item in tree_children if item["id"] == "GM300-AMCS:video")["children"]]
        xml_video_ids = [
            f"GM300-AMCS:video:{page.attrib['id']}"
            for page in next(group for group in xml_root.findall("./group") if group.attrib["id"] == "video").findall("./page")
        ]

        assert init_video_ids == tree_video_ids == xml_video_ids

    @allure.title("巡检模块在首页菜单、用户菜单树和插件 XML 中保持同序")
    def test_patrol_module_keeps_same_child_order_across_menu_views(
        self,
        auth_api,
        home_api,
        menu_api,
        plugin_api,
        test_user,
    ):
        """校验巡检模块在三份导航数据中的子节点顺序保持一致。"""
        self._login(auth_api, test_user)

        init_leaf, tree_children, xml_root = self._load_views(home_api, menu_api, plugin_api)
        init_patrol_ids = [item["id"] for item in next(item for item in init_leaf if item["id"] == "GM300-AMCS:amcs_patrol")["leaf"]]
        tree_patrol_ids = [item["id"] for item in next(item for item in tree_children if item["id"] == "GM300-AMCS:amcs_patrol")["children"]]
        xml_patrol_ids = [
            f"GM300-AMCS:amcs_patrol:{page.attrib['id']}"
            for page in next(group for group in xml_root.findall("./group") if group.attrib["id"] == "amcs_patrol").findall("./page")
        ]

        assert init_patrol_ids == tree_patrol_ids == xml_patrol_ids

    @allure.title("基础、配置和系统模块在用户菜单树与插件 XML 中保持数量一致")
    def test_core_container_modules_keep_same_page_counts_between_tree_and_plugin_xml(
        self,
        auth_api,
        home_api,
        menu_api,
        plugin_api,
        test_user,
    ):
        """校验基础、配置和系统模块在用户菜单树与插件 XML 中的子节点数量保持一致。"""
        self._login(auth_api, test_user)

        _, tree_children, xml_root = self._load_views(home_api, menu_api, plugin_api)
        expected_group_ids = {"base", "config", "sys", "history"}
        for group_id in expected_group_ids:
            tree_node = next(item for item in tree_children if item["id"] == f"GM300-AMCS:{group_id}")
            xml_group = next(group for group in xml_root.findall("./group") if group.attrib["id"] == group_id)
            assert len(tree_node["children"]) == len(xml_group.findall("./page"))

    @allure.title("视频权限子节点在用户菜单树与插件 XML 中保持数量一致")
    def test_video_permission_nodes_keep_same_item_counts_between_tree_and_plugin_xml(
        self,
        auth_api,
        home_api,
        menu_api,
        plugin_api,
        test_user,
    ):
        """校验视频模块下的权限子节点在用户菜单树和插件 XML 中保持相同数量。"""
        self._login(auth_api, test_user)

        _, tree_children, xml_root = self._load_views(home_api, menu_api, plugin_api)
        tree_video = next(item for item in tree_children if item["id"] == "GM300-AMCS:video")
        xml_video = next(group for group in xml_root.findall("./group") if group.attrib["id"] == "video")

        tree_item_counts = {item["id"]: len(item["children"]) for item in tree_video["children"]}
        xml_item_counts = {
            f"GM300-AMCS:video:{page.attrib['id']}": len(page.findall("./item"))
            for page in xml_video.findall("./page")
        }
        assert tree_item_counts == xml_item_counts
