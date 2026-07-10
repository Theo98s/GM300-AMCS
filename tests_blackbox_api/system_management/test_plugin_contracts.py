# -*- coding: utf-8 -*-
"""菜单插件一致性、路由、XML 与运行时契约测试。"""
from __future__ import annotations

import xml.etree.ElementTree as element_tree
import allure


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
