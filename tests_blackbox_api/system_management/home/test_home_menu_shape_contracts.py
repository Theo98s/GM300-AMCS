# -*- coding: utf-8 -*-
"""AMCS 首页菜单形态补充契约测试。"""
from __future__ import annotations

import allure


@allure.feature("首页接口")
class TestHomeMenuShapeContracts:
    """补充校验首页菜单的路由与状态模式。"""

    @allure.title("首页顶层模块路由模式保持稳定")
    def test_init_menu_top_module_url_pattern_is_stable(self, auth_api, home_api, test_user):
        """校验首页一层模块保持当前路由模式。"""
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
        """校验首页当前所有一层模块的启用状态值都保持为 1。"""
        login_response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert login_response.json()["status"] == 0

        top_modules = home_api.init_menu().json()["data"]["hostMenuList"][0]["leaf"]
        states = [item["state"] for item in top_modules]
        assert states == [1, 1, 1, 1, 1, 1, 1, 1]
