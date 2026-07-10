# -*- coding: utf-8 -*-
"""菜单与插件接口异常方法和参数契约测试。"""
from __future__ import annotations

import allure


class TestMenuPluginAbnormalContractsMore:
    """补充菜单树和插件列表在异常方法、异常参数、匿名访问下的行为。"""

    @staticmethod
    def _login(auth_api, test_user):
        """每条用例先登录，避免匿名拦截影响业务断言。"""
        login_response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert login_response.status_code == 200
        assert login_response.json()["status"] == 0

    @staticmethod
    def _assert_json_list(response):
        """统一校验接口返回 JSON 列表。"""
        assert response.status_code == 200
        assert "application/json" in response.headers.get("Content-Type", "")
        assert isinstance(response.json(), list)

    @allure.title("用户菜单树接口使用 POST 方法时仍返回菜单树")
    def test_user_menu_tree_post_method_keeps_tree_contract(self, auth_api, request_util, config, test_user):
        """校验用户菜单树接口兼容 POST 方法，不因方法变化破坏菜单加载。"""
        self._login(auth_api, test_user)

        response = request_util.send_request("post", config["menu"]["user_menu_tree_url"])

        self._assert_json_list(response)

    @allure.title("用户菜单树接口接收无关参数时仍返回菜单树")
    def test_user_menu_tree_unknown_param_keeps_tree_contract(self, auth_api, request_util, config, test_user):
        """校验无关查询参数不会改变用户菜单树响应结构。"""
        self._login(auth_api, test_user)

        response = request_util.send_request(
            "get",
            config["menu"]["user_menu_tree_url"],
            params={"unexpected": "NO_SUCH_VALUE"},
        )

        self._assert_json_list(response)

    @allure.title("插件列表接口使用 POST 方法时仍返回插件列表")
    def test_plugin_find_post_method_keeps_list_contract(self, auth_api, request_util, config, test_user):
        """校验插件列表接口兼容 POST 方法，仍返回插件定义列表。"""
        self._login(auth_api, test_user)

        response = request_util.send_request("post", config["plugin"]["find_plugin_url"])

        self._assert_json_list(response)

    @allure.title("插件列表接口接收无关参数时仍返回插件列表")
    def test_plugin_find_unknown_param_keeps_list_contract(self, auth_api, request_util, config, test_user):
        """校验无关查询参数不会影响插件列表基础响应。"""
        self._login(auth_api, test_user)

        response = request_util.send_request(
            "get",
            config["plugin"]["find_plugin_url"],
            params={"unexpected": "NO_SUCH_VALUE"},
        )

        self._assert_json_list(response)

    @allure.title("匿名访问插件列表接口时返回 SQL 参数缺失错误文本")
    def test_plugin_find_anonymous_request_returns_sql_parameter_error(self, request_util, config):
        """记录当前匿名访问插件列表的异常返回，便于后续发现权限拦截行为变化。"""
        response = request_util.send_request(
            "get",
            config["plugin"]["find_plugin_url"],
            allow_redirects=False,
        )

        assert response.status_code == 200
        assert "No value supplied for the SQL parameter 'id'" in response.text
