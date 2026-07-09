# -*- coding: utf-8 -*-
"""Additional AMCS user-menu-tree shape contract tests."""
from __future__ import annotations

import allure


@allure.feature("菜单与插件")
class TestMenuTreeShapeContracts:
    """Extra checks for top-level user-menu-tree route and state patterns."""

    @allure.title("用户菜单树顶层模块路由模式保持稳定")
    def test_user_menu_tree_top_child_url_pattern_is_stable(self, auth_api, menu_api, test_user):
        """Verify top-level user-menu-tree children keep the current route pattern."""
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
        """Verify top-level user-menu-tree children keep the expected open/closed state pattern."""
        login_response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert login_response.json()["status"] == 0

        children = menu_api.get_user_menu_tree().json()[0]["children"]
        states = [item["state"] for item in children]
        assert states == ["open", "closed", "closed", "closed", "closed", "closed", "closed", "closed"]

