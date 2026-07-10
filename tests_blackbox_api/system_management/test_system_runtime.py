# -*- coding: utf-8 -*-
"""系统状态匿名访问、标识与运行时契约测试。"""
from __future__ import annotations

import allure


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


class TestSystemLogoContracts:
    """补充校验系统公共接口契约。"""

    @allure.title("系统 logo 公共接口返回标准成功消息")
    def test_sys_logo_public_message_is_success_text(self, system_api):
        """校验公共 logo 接口保持标准成功提示文案。"""
        response = system_api.get_sys_logo()
        assert response.status_code == 200

        body = response.json()
        assert body["status"] == 0
        assert body["message"] == "数据查询成功!"


class TestSystemRuntimeContractsExtra:
    """补充校验系统公共接口和运行时字段。"""

    @allure.title("系统 logo 公共接口默认值保持空字符串")
    def test_sys_logo_public_default_values_are_empty_strings(self, system_api):
        """校验系统 logo 公共接口在当前环境下仍返回空字符串默认值。"""
        body = system_api.get_sys_logo().json()

        assert body["status"] == 0
        assert body["data"]["sys_logo_a"] == ""
        assert body["data"]["sys_logo_b"] == ""

    @allure.title("告警数量接口登录后返回标准三段式结果")
    def test_alarm_count_after_login_keeps_standard_result_keys(self, auth_api, system_api, test_user):
        """校验登录后的告警数量接口仍返回 status、message、data 三段式结果。"""
        login_response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert login_response.json()["status"] == 0

        body = system_api.get_alarm_count().json()
        assert set(body.keys()) == {"status", "message", "data"}
        assert body["status"] == 0
        assert body["message"] == "数据查询成功!"
        assert isinstance(body["data"], int)

    @allure.title("时间戳接口登录后返回 13 位毫秒时间戳")
    def test_timestamp_after_login_returns_exact_13_digit_epoch_millis(self, auth_api, system_api, test_user):
        """校验登录后的时间戳接口仍返回 13 位毫秒级 Unix 时间戳。"""
        login_response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert login_response.json()["status"] == 0

        timestamp = system_api.get_timestamp().json()
        assert isinstance(timestamp, int)
        assert len(str(timestamp)) == 13
