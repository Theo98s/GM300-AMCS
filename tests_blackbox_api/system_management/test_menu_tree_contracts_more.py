# -*- coding: utf-8 -*-
"""AMCS 用户菜单树更多契约测试。"""
from __future__ import annotations

import allure


@allure.feature("菜单与插件")
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
