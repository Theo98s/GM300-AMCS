# -*- coding: utf-8 -*-
"""AMCS 菜单树嵌套层级更多契约测试。"""
from __future__ import annotations

import allure


@allure.feature("Menu And Plugin")
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
