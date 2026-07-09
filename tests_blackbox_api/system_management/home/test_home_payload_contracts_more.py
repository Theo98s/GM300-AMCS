# -*- coding: utf-8 -*-
"""AMCS 首页 init-menu 返回体更多契约测试。"""
from __future__ import annotations

import allure


@allure.feature("首页接口")
class TestHomePayloadContractsMore:
    """补充校验 init-menu 返回体外层结构。"""

    @staticmethod
    def _login(auth_api, test_user):
        """每条用例先登录，并确认会话已建立。"""
        login_response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert login_response.status_code == 200
        assert login_response.json()["status"] == 0

    @allure.title("init-menu 返回体保留稳定的外层字段")
    def test_init_menu_response_keeps_stable_envelope_fields(self, auth_api, home_api, test_user):
        """校验 init-menu 接口仍返回 status、message 以及预期的 data 子字段。"""
        self._login(auth_api, test_user)

        response = home_api.init_menu()
        assert response.status_code == 200

        body = response.json()
        assert body["status"] == 0
        assert body["message"] == "数据查询成功!"
        assert set(body["data"].keys()) >= {"moduleMenu", "otherMenuList", "hostMenuList"}
        assert body["data"]["moduleMenu"] is None
        assert body["data"]["otherMenuList"] == []
        assert isinstance(body["data"]["hostMenuList"], list)
        assert len(body["data"]["hostMenuList"]) >= 1

    @allure.title("init-menu 主插件保持欢迎页路由与一级数量对齐")
    def test_init_menu_host_plugin_keeps_basic_identity_and_child_count_alignment(
        self,
        auth_api,
        home_api,
        menu_api,
        test_user,
    ):
        """校验 init-menu 中的主插件在 id、路由和模块数量上与用户菜单树根节点保持对齐。"""
        self._login(auth_api, test_user)

        init_body = home_api.init_menu().json()
        menu_tree = menu_api.get_user_menu_tree().json()

        host_plugin = init_body["data"]["hostMenuList"][0]
        root_node = menu_tree[0]
        assert host_plugin["id"] == "GM300-AMCS"
        assert host_plugin["pageurl"] == "/amcs/index"
        assert host_plugin["pluginKey"] == "GM300-AMCS"
        assert host_plugin["text"] == host_plugin["name"]
        assert len(host_plugin["leaf"]) == len(root_node["children"])
