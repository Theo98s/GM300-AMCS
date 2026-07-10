# -*- coding: utf-8 -*-
"""用户菜单树字段、层级、顺序与运行时契约测试。"""
from __future__ import annotations

import allure


class TestMenuTreeContractsMore:
    """补充校验用户菜单树的顺序与数量。"""

    @allure.title("用户菜单树顶层子模块顺序保持稳定")
    def test_user_menu_tree_top_child_order_is_stable(self, auth_api, menu_api, test_user):
        """校验用户菜单树的一层子模块保持预期顺序。"""
        login_response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert login_response.json()["status"] == 0

        body = menu_api.get_user_menu_tree().json()
        top_texts = [item["text"] for item in body[0]["children"]]
        assert top_texts == [
            "首页",
            "视频监控",
            "实时监控",
            "巡检管理",
            "历史记录",
            "基础数据",
            "系统配置",
            "系统管理",
        ]

    @allure.title("用户菜单树顶层子模块数量保持为八个")
    def test_user_menu_tree_top_child_count_is_stable(self, auth_api, menu_api, test_user):
        """校验用户菜单树当前仍暴露八个一层子模块。"""
        login_response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert login_response.json()["status"] == 0

        body = menu_api.get_user_menu_tree().json()
        assert len(body[0]["children"]) == 8


class TestMenuTreeNestedContractsMore:
    """补充校验菜单树二级和三级节点。"""

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
    def _root(menu_api):
        """返回用户菜单树根节点。"""
        return menu_api.get_user_menu_tree().json()[0]

    @allure.title("用户菜单树根节点保留精确的一层子节点数量")
    def test_user_menu_tree_root_keeps_exact_top_level_child_count(self, auth_api, menu_api, test_user):
        """校验根菜单当前仍精确暴露八个一层业务模块。"""
        self._login(auth_api, test_user)

        root = self._root(menu_api)
        assert len(root["children"]) == 8

    @allure.title("用户菜单树视频模块保留稳定的子节点顺序与数量")
    def test_user_menu_tree_video_module_keeps_stable_child_order_and_counts(
        self,
        auth_api,
        menu_api,
        test_user,
    ):
        """校验视频模块仍保留当前三个子节点及其嵌套权限数量。"""
        self._login(auth_api, test_user)

        root = self._root(menu_api)
        video_node = next(item for item in root["children"] if item["id"] == "GM300-AMCS:video")
        assert [(item["id"], len(item["children"])) for item in video_node["children"]] == [
            ("GM300-AMCS:video:video_realtime", 2),
            ("GM300-AMCS:video:video_playback", 1),
            ("GM300-AMCS:video:realtime_thermometry", 0),
        ]

    @allure.title("用户菜单树视频权限节点保留预期路由")
    def test_user_menu_tree_video_permission_nodes_keep_expected_routes(self, auth_api, menu_api, test_user):
        """校验嵌套视频权限节点仍暴露当前预览与回放权限路由。"""
        self._login(auth_api, test_user)

        root = self._root(menu_api)
        video_node = next(item for item in root["children"] if item["id"] == "GM300-AMCS:video")
        realtime_node = next(item for item in video_node["children"] if item["id"] == "GM300-AMCS:video:video_realtime")
        playback_node = next(item for item in video_node["children"] if item["id"] == "GM300-AMCS:video:video_playback")

        assert [(item["id"], item["url"]) for item in realtime_node["children"]] == [
            ("GM300-AMCS:video:video_realtime:view", "/amcs/video/preview/view"),
            ("GM300-AMCS:video:video_realtime:goto", "/amcs/video/preview/goto"),
        ]
        assert [(item["id"], item["url"]) for item in playback_node["children"]] == [
            ("GM300-AMCS:video:video_playback:view", "/amcs/video/playback/view"),
        ]


class TestMenuTreeRuntimeContractsExtra:
    """补充校验用户菜单树默认字段和值模式。"""

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
    def _root(menu_api) -> dict:
        """返回用户菜单树根节点。"""
        body = menu_api.get_user_menu_tree().json()
        assert isinstance(body, list) and body
        return body[0]

    @allure.title("菜单树根节点保持未勾选和空路由默认值")
    def test_user_menu_tree_root_keeps_unchecked_and_empty_route(self, auth_api, menu_api, test_user):
        """校验菜单树根节点仍保持未勾选和主插件首页路由默认值。"""
        self._login(auth_api, test_user)

        root = self._root(menu_api)
        assert root["checked"] is False
        assert root["url"] == "/amcs/index"
        assert isinstance(root["children"], list)
        assert len(root["children"]) >= 8

    @allure.title("菜单树一级节点保持默认空图标和扩展属性")
    def test_user_menu_tree_top_children_keep_null_icon_and_attributes(self, auth_api, menu_api, test_user):
        """校验菜单树一级节点仍保持默认空图标和扩展属性字段。"""
        self._login(auth_api, test_user)

        children = self._root(menu_api)["children"][:8]
        for row in children:
            assert row["checked"] is False
            assert row.get("iconCls") is None
            assert row.get("attributes") is None

    @allure.title("菜单树二级节点保持未勾选和稳定路由模式")
    def test_user_menu_tree_second_level_nodes_keep_unchecked_route_contract(self, auth_api, menu_api, test_user):
        """校验菜单树二级节点仍保持未勾选，并按当前模块使用稳定路由模式。"""
        self._login(auth_api, test_user)

        children = self._root(menu_api)["children"]
        for parent in children[1:]:
            for row in parent["children"][:5]:
                assert row["checked"] is False
                assert isinstance(row["text"], str) and row["text"]
                assert row["url"] is None or isinstance(row["url"], str)
                assert row["state"] in {"open", "closed"}


class TestMenuTreeShapeContracts:
    """补充校验用户菜单树一层节点的路由与状态模式。"""

    @allure.title("用户菜单树顶层模块路由模式保持稳定")
    def test_user_menu_tree_top_child_url_pattern_is_stable(self, auth_api, menu_api, test_user):
        """校验用户菜单树一层子节点保持当前路由模式。"""
        login_response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert login_response.json()["status"] == 0

        children = menu_api.get_user_menu_tree().json()[0]["children"]
        urls = [item["url"] for item in children]
        assert urls == ["/das/home", None, None, None, "", "", "", ""]

    @allure.title("用户菜单树顶层模块状态模式保持稳定")
    def test_user_menu_tree_top_child_state_pattern_is_stable(self, auth_api, menu_api, test_user):
        """校验用户菜单树一层子节点保持预期的展开/折叠状态模式。"""
        login_response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert login_response.json()["status"] == 0

        children = menu_api.get_user_menu_tree().json()[0]["children"]
        states = [item["state"] for item in children]
        assert states == ["open", "closed", "closed", "closed", "closed", "closed", "closed", "closed"]
