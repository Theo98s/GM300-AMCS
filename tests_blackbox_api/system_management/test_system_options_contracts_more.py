# -*- coding: utf-8 -*-
"""系统公共状态接口的 OPTIONS 方法契约测试。"""
from __future__ import annotations

import allure
import pytest


@allure.feature("系统管理")
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
