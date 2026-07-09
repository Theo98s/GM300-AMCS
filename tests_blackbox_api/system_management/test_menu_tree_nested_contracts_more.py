# -*- coding: utf-8 -*-
"""More AMCS nested menu-tree contract tests."""
from __future__ import annotations

import allure


@allure.feature("Menu And Plugin")
class TestMenuTreeNestedContractsMore:
    """Extra checks for second- and third-level menu-tree nodes."""

    @staticmethod
    def _login(auth_api, test_user):
        """Log in once per test and assert the session is ready."""
        login_response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert login_response.status_code == 200
        assert login_response.json()["status"] == 0

    @staticmethod
    def _root(menu_api):
        """Return the root user-menu node."""
        return menu_api.get_user_menu_tree().json()[0]

    @allure.title("User menu root keeps exact top-level child count")
    def test_user_menu_tree_root_keeps_exact_top_level_child_count(self, auth_api, menu_api, test_user):
        """Verify the root menu still exposes exactly eight top-level business modules."""
        self._login(auth_api, test_user)

        root = self._root(menu_api)
        assert len(root["children"]) == 8

    @allure.title("User menu video module keeps stable child order and counts")
    def test_user_menu_tree_video_module_keeps_stable_child_order_and_counts(
        self,
        auth_api,
        menu_api,
        test_user,
    ):
        """Verify the video module keeps the current three children and their nested permission counts."""
        self._login(auth_api, test_user)

        root = self._root(menu_api)
        video_node = next(item for item in root["children"] if item["id"] == "GM300-AMCS:video")
        assert [(item["id"], len(item["children"])) for item in video_node["children"]] == [
            ("GM300-AMCS:video:video_realtime", 2),
            ("GM300-AMCS:video:video_playback", 1),
            ("GM300-AMCS:video:realtime_thermometry", 0),
        ]

    @allure.title("User menu video permission nodes keep expected routes")
    def test_user_menu_tree_video_permission_nodes_keep_expected_routes(self, auth_api, menu_api, test_user):
        """Verify the nested video permission nodes still expose the current preview and playback permission routes."""
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
