# -*- coding: utf-8 -*-
"""AMCS 菜单树运行时补充契约测试。"""
from __future__ import annotations

import allure


@allure.feature("菜单与插件")
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
