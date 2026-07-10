# -*- coding: utf-8 -*-
"""平台菜单与导航接口损坏请求体和预检契约测试。"""
from __future__ import annotations

import allure
import pytest


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


class TestPlatformOptionsContractsMore:
    """校验首页、字典、菜单和插件接口的浏览器预检响应。"""

    @staticmethod
    def _login(auth_api, test_user):
        """先建立登录会话，使预检请求进入平台业务路由。"""
        response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert response.status_code == 200
        assert response.json()["status"] == 0

    @pytest.mark.parametrize(
        ("url_factory", "case_name"),
        [
            pytest.param(lambda config: config["home"]["init_menu_url"], "首页初始化", id="home"),
            pytest.param(
                lambda config: f'{config["home"]["dict_list_url_prefix"]}/equipArea',
                "设备区域字典",
                id="dict",
            ),
            pytest.param(lambda config: config["menu"]["user_menu_tree_url"], "用户菜单树", id="menu"),
            pytest.param(lambda config: config["plugin"]["find_plugin_url"], "插件查询", id="plugin"),
        ],
    )
    @allure.title("平台查询接口使用 OPTIONS 时返回空成功响应")
    def test_platform_endpoint_options_returns_empty_success(
        self,
        auth_api,
        request_util,
        config,
        test_user,
        url_factory,
        case_name,
    ):
        """逐项校验平台查询预检请求不会返回菜单或字典业务数据。"""
        self._login(auth_api, test_user)
        allure.dynamic.parameter("接口名称", case_name)

        response = request_util.send_request("options", url_factory(config))

        assert response.status_code == 200
        assert response.content == b""
