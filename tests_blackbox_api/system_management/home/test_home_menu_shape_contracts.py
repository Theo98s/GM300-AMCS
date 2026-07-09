# -*- coding: utf-8 -*-
"""Additional AMCS home-menu shape contract tests."""
from __future__ import annotations

import allure


@allure.feature("首页接口")
class TestHomeMenuShapeContracts:
    """Extra checks for home-menu route and state patterns."""

    @allure.title("首页顶层模块路由模式保持稳定")
    def test_init_menu_top_module_url_pattern_is_stable(self, auth_api, home_api, test_user):
        """Verify top-level home-menu modules keep the current route pattern."""
        login_response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert login_response.json()["status"] == 0

        top_modules = home_api.init_menu().json()["data"]["hostMenuList"][0]["leaf"]
        urls = [item["url"] for item in top_modules]
        assert urls == ["/das/home", None, None, None, "", "", "", ""]

    @allure.title("首页顶层模块状态值保持全启用")
    def test_init_menu_top_module_state_pattern_is_stable(self, auth_api, home_api, test_user):
        """Verify all current top-level home-menu modules keep the enabled state value 1."""
        login_response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert login_response.json()["status"] == 0

        top_modules = home_api.init_menu().json()["data"]["hostMenuList"][0]["leaf"]
        states = [item["state"] for item in top_modules]
        assert states == [1, 1, 1, 1, 1, 1, 1, 1]

