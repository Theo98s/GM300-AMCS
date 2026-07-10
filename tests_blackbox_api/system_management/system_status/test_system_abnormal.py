# -*- coding: utf-8 -*-
"""系统状态接口方法与预检请求异常测试。"""
from __future__ import annotations

import allure
import pytest


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


class TestSystemOptionsContractsMore:
    """校验系统标识、健康、时间戳和报警数量接口的预检响应。"""

    @staticmethod
    def _login(auth_api, test_user):
        """建立登录会话，使受保护接口返回自身的预检响应。"""
        response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert response.status_code == 200
        assert response.json()["status"] == 0

    @pytest.mark.parametrize(
        ("config_key", "case_name"),
        [
            pytest.param("sys_logo_url", "系统标识", id="sys-logo"),
            pytest.param("health_url", "健康检查", id="health"),
            pytest.param("timestamp_url", "系统时间戳", id="timestamp"),
            pytest.param("alarm_count_url", "实时报警数量", id="alarm-count"),
        ],
    )
    @allure.title("系统接口使用 OPTIONS 时返回空成功响应")
    def test_system_endpoint_options_method_returns_empty_success(
        self,
        auth_api,
        request_util,
        config,
        test_user,
        config_key,
        case_name,
    ):
        """逐项校验系统只读接口的预检请求不会触发业务查询。"""
        self._login(auth_api, test_user)
        allure.dynamic.parameter("接口名称", case_name)

        response = request_util.send_request(
            "options",
            config["system"][config_key],
        )

        assert response.status_code == 200
        assert response.content == b""
