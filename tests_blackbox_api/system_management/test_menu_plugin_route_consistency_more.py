# -*- coding: utf-8 -*-
"""AMCS 菜单与插件路由一致性补充契约测试。"""
from __future__ import annotations

import xml.etree.ElementTree as element_tree

import allure


@allure.feature("菜单与插件")
class TestMenuPluginRouteConsistencyMore:
    """补充校验首页菜单、用户菜单树与插件 XML 的路由和标识一致性。"""

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

    @allure.title("历史基础配置系统模块在三视图中保持相同子路由顺序")
    def test_core_modules_keep_same_child_route_order_across_views(
        self,
        auth_api,
        home_api,
        menu_api,
        plugin_api,
        test_user,
    ):
        """校验历史、基础、配置和系统模块在三份导航数据中的子路由顺序保持一致。"""
        self._login(auth_api, test_user)

        init_leaf, tree_children, xml_root = self._load_views(home_api, menu_api, plugin_api)
        for group_id in ("history", "base", "config", "sys"):
            home_routes = [item["url"] for item in next(item for item in init_leaf if item["id"] == f"GM300-AMCS:{group_id}")["leaf"]]
            tree_routes = [item["url"] for item in next(item for item in tree_children if item["id"] == f"GM300-AMCS:{group_id}")["children"]]
            xml_routes = [
                page.attrib.get("url", "")
                for page in next(group for group in xml_root.findall("./group") if group.attrib["id"] == group_id).findall("./page")
            ]
            assert home_routes == tree_routes == xml_routes

    @allure.title("历史基础配置系统模块在三视图中保持相同子节点标识顺序")
    def test_core_modules_keep_same_child_id_order_across_views(
        self,
        auth_api,
        home_api,
        menu_api,
        plugin_api,
        test_user,
    ):
        """校验历史、基础、配置和系统模块在三份导航数据中的子节点标识顺序保持一致。"""
        self._login(auth_api, test_user)

        init_leaf, tree_children, xml_root = self._load_views(home_api, menu_api, plugin_api)
        for group_id in ("history", "base", "config", "sys"):
            home_ids = [item["id"] for item in next(item for item in init_leaf if item["id"] == f"GM300-AMCS:{group_id}")["leaf"]]
            tree_ids = [item["id"] for item in next(item for item in tree_children if item["id"] == f"GM300-AMCS:{group_id}")["children"]]
            xml_ids = [
                f"GM300-AMCS:{group_id}:{page.attrib['id']}"
                for page in next(group for group in xml_root.findall("./group") if group.attrib["id"] == group_id).findall("./page")
            ]
            assert home_ids == tree_ids == xml_ids

    @allure.title("插件 XML 顶层分组路由与首页菜单顶层路由保持对齐")
    def test_top_level_group_routes_keep_alignment_between_home_and_plugin_xml(
        self,
        auth_api,
        home_api,
        menu_api,
        plugin_api,
        test_user,
    ):
        """校验插件 XML 顶层分组路由与首页菜单、用户菜单树顶层路由保持一致。"""
        self._login(auth_api, test_user)

        init_leaf, tree_children, xml_root = self._load_views(home_api, menu_api, plugin_api)
        xml_route_map = {
            f"GM300-AMCS:{group.attrib['id']}": group.attrib.get("url")
            for group in xml_root.findall("./group")
        }

        for group_id in ("amcs_welcome", "history", "base", "config", "sys"):
            menu_id = f"GM300-AMCS:{group_id}"
            home_node = next(item for item in init_leaf if item["id"] == menu_id)
            tree_node = next(item for item in tree_children if item["id"] == menu_id)
            assert home_node["url"] == tree_node["url"] == xml_route_map[menu_id]
