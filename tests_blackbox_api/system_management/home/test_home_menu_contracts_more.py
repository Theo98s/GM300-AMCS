# -*- coding: utf-8 -*-
"""More AMCS home-menu contract tests."""
from __future__ import annotations

import allure


@allure.feature("首页接口")
class TestHomeMenuContractsMore:
    """Extra checks for home-menu ordering and module shape."""

    @allure.title("首页顶层模块顺序保持稳定")
    def test_init_menu_top_module_order_is_stable(self, auth_api, home_api, test_user):
        """Verify the first-level home modules keep the expected display order."""
        login_response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert login_response.json()["status"] == 0

        body = home_api.init_menu().json()
        top_texts = [item["text"] for item in body["data"]["hostMenuList"][0]["leaf"]]
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

    @allure.title("首页顶层模块数量保持为八个")
    def test_init_menu_top_module_count_is_stable(self, auth_api, home_api, test_user):
        """Verify the home menu currently exposes eight first-level modules."""
        login_response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert login_response.json()["status"] == 0

        body = home_api.init_menu().json()
        top_modules = body["data"]["hostMenuList"][0]["leaf"]
        assert len(top_modules) == 8

