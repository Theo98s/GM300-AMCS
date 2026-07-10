# -*- coding: utf-8 -*-
"""认证接口异常提交契约测试。"""
from __future__ import annotations

import allure
import pytest


@allure.feature("认证")
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
