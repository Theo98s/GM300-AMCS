# -*- coding: utf-8 -*-
"""AMCS 用户菜单树形态补充契约测试。"""
from __future__ import annotations

import allure


@allure.feature("菜单与插件")
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
