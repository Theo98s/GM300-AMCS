# -*- coding: utf-8 -*-
"""系统公共接口错误请求方法契约测试。"""
from __future__ import annotations

import allure


@allure.feature("系统管理")
class TestSystemMethodAbnormalContractsMore:
    """补充系统公共接口对错误 HTTP 方法的响应校验。"""

    @staticmethod
    def _assert_method_not_supported(response):
        """统一校验错误 POST 方法返回 405。"""
        assert response.status_code == 405
        assert "Request method 'POST' not supported" in response.text

    @allure.title("系统 logo 接口使用 POST 方法时返回 405")
    def test_sys_logo_post_method_returns_method_not_supported(self, request_util, config):
        """校验系统 logo 公共接口只接受既定读取方法。"""
        response = request_util.send_request(
            "post",
            config["system"]["sys_logo_url"],
            allow_redirects=False,
        )

        self._assert_method_not_supported(response)

    @allure.title("健康检查接口使用 POST 方法时返回 405")
    def test_health_post_method_returns_method_not_supported(self, request_util, config):
        """校验健康检查接口的错误 POST 方法有明确失败响应。"""
        response = request_util.send_request(
            "post",
            config["system"]["health_url"],
            allow_redirects=False,
        )

        self._assert_method_not_supported(response)

    @allure.title("时间戳接口匿名 POST 访问时重定向到登录页")
    def test_timestamp_anonymous_post_method_redirects_to_login(self, request_util, config):
        """校验受保护时间戳接口在匿名错误方法下优先执行登录拦截。"""
        response = request_util.send_request(
            "post",
            config["system"]["timestamp_url"],
            allow_redirects=False,
        )

        assert response.status_code == 302
        assert response.headers["Location"].endswith("/amcs/login")
