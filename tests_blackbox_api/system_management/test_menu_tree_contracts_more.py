# -*- coding: utf-8 -*-
"""More AMCS user-menu-tree contract tests."""
from __future__ import annotations

import allure


@allure.feature("菜单与插件")
class TestMenuTreeContractsMore:
    """Extra checks for user-menu-tree ordering and size."""

    @allure.title("用户菜单树顶层子模块顺序保持稳定")
    def test_user_menu_tree_top_child_order_is_stable(self, auth_api, menu_api, test_user):
        """Verify the top-level child modules in the user menu tree keep the expected order."""
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
        """Verify the user menu tree currently exposes eight top-level child modules."""
        login_response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert login_response.json()["status"] == 0

        body = menu_api.get_user_menu_tree().json()
        assert len(body[0]["children"]) == 8

