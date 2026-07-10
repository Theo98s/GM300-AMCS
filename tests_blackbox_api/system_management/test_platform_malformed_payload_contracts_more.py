# -*- coding: utf-8 -*-
"""平台菜单及插件接口的损坏 JSON 异常契约测试。"""
from __future__ import annotations

import allure


@allure.feature("系统管理")
class TestPlatformMalformedPayloadContractsMore:
    """校验平台初始化、菜单和插件查询对损坏 JSON 的兼容行为。"""

    @staticmethod
    def _login(auth_api, test_user):
        """先建立登录会话，确保请求命中平台业务接口。"""
        response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert response.status_code == 200
        assert response.json()["status"] == 0

    @staticmethod
    def _malformed_json_request(request_util, url):
        """发送声明为 JSON 但内容无法解析的请求。"""
        return request_util.send_request(
            "post",
            url,
            data="{bad-json",
            headers={"Content-Type": "application/json"},
        )

    @allure.title("首页初始化接口收到损坏 JSON 时仍返回菜单数据")
    def test_home_init_menu_malformed_json_keeps_success_contract(
        self,
        auth_api,
        request_util,
        config,
        test_user,
    ):
        """校验损坏请求体不会阻断首页菜单的默认初始化流程。"""
        self._login(auth_api, test_user)

        response = self._malformed_json_request(
            request_util,
            config["home"]["init_menu_url"],
        )

        assert response.status_code == 200
        body = response.json()
        assert body["status"] == 0
        assert body["message"] == "数据查询成功!"
        assert set(body["data"]) == {"moduleMenu", "otherMenuList", "hostMenuList"}

    @allure.title("用户菜单树接口收到损坏 JSON 时仍返回菜单列表")
    def test_user_menu_tree_malformed_json_keeps_list_contract(
        self,
        auth_api,
        request_util,
        config,
        test_user,
    ):
        """校验用户菜单树忽略损坏请求体并保持列表响应。"""
        self._login(auth_api, test_user)

        response = self._malformed_json_request(
            request_util,
            config["menu"]["user_menu_tree_url"],
        )

        assert response.status_code == 200
        assert "application/json" in response.headers.get("Content-Type", "")
        assert isinstance(response.json(), list)

    @allure.title("插件查询接口收到损坏 JSON 时仍返回插件列表")
    def test_plugin_find_malformed_json_keeps_list_contract(
        self,
        auth_api,
        request_util,
        config,
        test_user,
    ):
        """校验插件查询不会因无法解析的附加请求体产生服务端错误。"""
        self._login(auth_api, test_user)

        response = self._malformed_json_request(
            request_util,
            config["plugin"]["find_plugin_url"],
        )

        assert response.status_code == 200
        assert "application/json" in response.headers.get("Content-Type", "")
        assert isinstance(response.json(), list)
