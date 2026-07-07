# -*- coding: utf-8 -*-
"""AMCS system interface contract tests."""
from __future__ import annotations

import allure


@allure.feature("系统管理")
class TestSystemContracts:
    """Contract checks for public and login-protected system endpoints."""

    @allure.title("系统 logo 公共接口返回标准 Result 结构")
    def test_sys_logo_public_contract(self, system_api):
        """Verify the public logo endpoint keeps the standard Result response shape."""
        response = system_api.get_sys_logo()
        assert response.status_code == 200

        body = response.json()
        assert set(body.keys()) >= {"status", "message", "data"}
        assert body["status"] == 0
        assert isinstance(body["message"], str)
        assert isinstance(body["data"], dict)
        assert set(body["data"].keys()) >= {"sys_logo_a", "sys_logo_b"}

    @allure.title("时间戳接口未登录时跳转登录页")
    def test_timestamp_requires_login(self, system_api):
        """Verify timestamp endpoint is protected when there is no login session."""
        response = system_api.get_timestamp()

        assert response.status_code == 302
        assert response.headers["Location"].startswith("/amcs/login")

    @allure.title("实时报警数量接口未登录时跳转登录页")
    def test_alarm_count_requires_login_contract(self, system_api):
        """Verify alarm-count endpoint is protected when there is no login session."""
        response = system_api.get_alarm_count()

        assert response.status_code == 302
        assert response.headers["Location"].startswith("/amcs/login")

    @allure.title("健康检查公共接口返回列表结构")
    def test_health_check_public_contract(self, system_api):
        """Verify health endpoint stays public and returns a list payload."""
        response = system_api.get_health()
        assert response.status_code == 200

        body = response.json()
        assert set(body.keys()) >= {"status", "message", "data"}
        assert body["status"] == 0
        assert isinstance(body["message"], str)
        assert isinstance(body["data"], list)
        if body["data"]:
            assert set(body["data"][0].keys()) >= {"name", "serviceUp", "deviceList"}
