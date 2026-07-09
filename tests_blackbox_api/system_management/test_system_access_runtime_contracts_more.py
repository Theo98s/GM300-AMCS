# -*- coding: utf-8 -*-
"""AMCS 系统访问控制运行时补充契约测试。"""
from __future__ import annotations

import allure


@allure.feature("系统管理")
class TestSystemAccessRuntimeContractsMore:
    """补充校验系统接口在匿名和公共场景下的运行时契约。"""

    @allure.title("匿名访问时间戳接口默认落到登录页 HTML")
    def test_timestamp_default_anonymous_request_returns_login_html(self, request_util, config):
        """校验匿名访问时间戳接口时默认仍落到登录页 HTML。"""
        response = request_util.send_request(
            "get",
            config["system"]["timestamp_url"],
        )

        assert response.status_code == 200
        assert "text/html" in response.headers.get("Content-Type", "")
        assert "/sso/ajaxcheck" in response.text
        assert 'id="loginForm"' in response.text

    @allure.title("匿名访问告警数量接口默认落到登录页 HTML")
    def test_alarm_count_default_anonymous_request_returns_login_html(self, request_util, config):
        """校验匿名访问告警数量接口时默认仍落到登录页 HTML。"""
        response = request_util.send_request(
            "get",
            config["system"]["alarm_count_url"],
        )

        assert response.status_code == 200
        assert "text/html" in response.headers.get("Content-Type", "")
        assert 'name="password"' in response.text
        assert 'id="btnLogin"' in response.text

    @allure.title("健康检查公共接口保持精确成功消息与顶层字段")
    def test_health_check_public_keeps_exact_result_keys_and_message(self, system_api):
        """校验健康检查公共接口仍保持精确成功消息和顶层字段。"""
        body = system_api.get_health().json()

        assert set(body.keys()) == {"status", "message", "data"}
        assert body["status"] == 0
        assert body["message"] == "查询成功"
        assert isinstance(body["data"], list)
