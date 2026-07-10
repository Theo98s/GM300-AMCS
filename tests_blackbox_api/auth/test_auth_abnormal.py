# -*- coding: utf-8 -*-
"""登录提交与登录页面方法异常测试。"""
from __future__ import annotations

import allure
import pytest


class TestAuthAbnormalContractsMore:
    """补充登录提交接口在缺参和错误请求方式下的异常返回。"""

    @staticmethod
    def _assert_illegal_request_text(response):
        """统一校验登录异常提交返回非 JSON 的非法请求文本。"""
        assert response.status_code == 200
        assert "application/json" in response.headers.get("Content-Type", "")
        assert response.text == "非法请求"
        with pytest.raises(ValueError):
            response.json()

    @allure.title("登录提交接口使用 GET 方式时返回非法请求文本")
    def test_login_submit_get_method_returns_illegal_request_text(self, request_util, config):
        """校验登录提交地址不支持 GET 业务提交，且异常体不是标准 JSON。"""
        response = request_util.send_request(
            "get",
            config["auth"]["login_submit_url"],
            allow_redirects=False,
        )

        self._assert_illegal_request_text(response)

    @allure.title("登录提交接口空表单提交时返回非法请求文本")
    def test_login_submit_empty_form_returns_illegal_request_text(self, request_util, config):
        """校验缺少账号、密码和 CSRFToken 时返回非法请求文本。"""
        response = request_util.send_request(
            "post",
            config["auth"]["login_submit_url"],
            data={},
            allow_redirects=False,
        )

        self._assert_illegal_request_text(response)

    @allure.title("登录提交接口缺少 CSRFToken 时返回非法请求文本")
    def test_login_submit_missing_csrf_returns_illegal_request_text(self, request_util, config):
        """校验缺少 CSRFToken 的表单不会进入账号密码校验逻辑。"""
        response = request_util.send_request(
            "post",
            config["auth"]["login_submit_url"],
            data={"account": "NO_SUCH_USER_001", "password": "bad-password"},
            allow_redirects=False,
        )

        self._assert_illegal_request_text(response)

    @allure.title("登录提交接口错误 CSRFToken 时返回非法请求文本")
    def test_login_submit_invalid_csrf_returns_illegal_request_text(self, request_util, config):
        """校验错误 CSRFToken 会被安全校验拦截为非法请求。"""
        response = request_util.send_request(
            "post",
            config["auth"]["login_submit_url"],
            data={
                "account": "NO_SUCH_USER_001",
                "password": "bad-password",
                "CSRFToken": "bad-token",
            },
            allow_redirects=False,
        )

        self._assert_illegal_request_text(response)

    @allure.title("登录提交接口接收文本请求体时返回非法请求文本")
    def test_login_submit_plain_text_body_returns_illegal_request_text(self, request_util, config):
        """校验非表单文本请求体不会被当作正常登录请求处理。"""
        response = request_util.send_request(
            "post",
            config["auth"]["login_submit_url"],
            data="not-form",
            headers={"Content-Type": "text/plain"},
            allow_redirects=False,
        )

        self._assert_illegal_request_text(response)


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
