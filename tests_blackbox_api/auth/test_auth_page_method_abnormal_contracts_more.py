# -*- coding: utf-8 -*-
"""登录页异常请求方法契约测试。"""
from __future__ import annotations

import allure


@allure.feature("认证")
class TestAuthPageMethodAbnormalContractsMore:
    """补充登录页对 POST 和 OPTIONS 方法的响应契约。"""

    @staticmethod
    def _assert_login_html(response):
        """统一校验登录页 HTML 核心内容。"""
        assert response.status_code == 200
        assert "text/html" in response.headers.get("Content-Type", "")
        assert 'id="loginForm"' in response.text
        assert 'name="account"' in response.text
        assert 'name="password"' in response.text
        assert "/sso/ajaxcheck" in response.text

    @allure.title("登录页使用 POST 方法访问时仍返回登录 HTML")
    def test_login_page_post_method_returns_login_html(self, request_util, config):
        """校验登录页 POST 访问不会报错，仍返回可渲染的登录页面。"""
        response = request_util.send_request(
            "post",
            config["auth"]["login_page_url"],
            allow_redirects=False,
        )

        self._assert_login_html(response)

    @allure.title("登录页使用 OPTIONS 方法访问时返回空成功响应")
    def test_login_page_options_method_returns_empty_success(self, request_util, config):
        """记录登录页当前 OPTIONS 探测行为，便于发现网关策略变化。"""
        response = request_util.send_request(
            "options",
            config["auth"]["login_page_url"],
            allow_redirects=False,
        )

        assert response.status_code == 200
        assert response.content == b""
