# -*- coding: utf-8 -*-
"""More AMCS home init-menu payload contract tests."""
from __future__ import annotations

import allure


@allure.feature("Home API")
class TestHomePayloadContractsMore:
    """Extra contract checks for the init-menu response envelope."""

    @staticmethod
    def _login(auth_api, test_user):
        """Log in once per test and assert the session is ready."""
        login_response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert login_response.status_code == 200
        assert login_response.json()["status"] == 0

    @allure.title("Init menu response keeps stable envelope fields")
    def test_init_menu_response_keeps_stable_envelope_fields(self, auth_api, home_api, test_user):
        """Verify the init-menu endpoint still returns status, message, and the expected nested data keys."""
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

    @allure.title("Init menu host plugin keeps welcome route and top-level count aligned")
    def test_init_menu_host_plugin_keeps_basic_identity_and_child_count_alignment(
        self,
        auth_api,
        home_api,
        menu_api,
        test_user,
    ):
        """Verify the host plugin in init-menu stays aligned with the user-menu root on id, route, and module count."""
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
