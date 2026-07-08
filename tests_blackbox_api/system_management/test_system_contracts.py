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

    @allure.title("系统 logo 公共接口返回字符串类型字段")
    def test_sys_logo_public_data_uses_string_fields(self, system_api):
        """Verify logo fields remain string values even when empty."""
        response = system_api.get_sys_logo()
        body = response.json()

        assert isinstance(body["data"]["sys_logo_a"], str)
        assert isinstance(body["data"]["sys_logo_b"], str)

    @allure.title("健康检查首项服务结构包含设备列表布尔状态")
    def test_health_check_first_service_contains_device_list_and_flag(self, system_api):
        """Verify the first health-check service item keeps a boolean service flag and list payload."""
        response = system_api.get_health()
        body = response.json()

        if not body["data"]:
            return

        first_service = body["data"][0]
        assert isinstance(first_service["serviceUp"], bool)
        assert isinstance(first_service["deviceList"], list)
        assert first_service["name"]

    @allure.title("健康检查所有服务项使用统一字段结构")
    def test_health_check_all_services_share_same_keys(self, system_api):
        """Verify every health-check service entry keeps the same response-key shape."""
        response = system_api.get_health()
        body = response.json()

        if not body["data"]:
            return

        expected_keys = set(body["data"][0].keys())
        for item in body["data"]:
            assert set(item.keys()) == expected_keys
            assert isinstance(item["serviceUp"], bool)

    @allure.title("健康检查服务名称非空且不重复")
    def test_health_check_service_names_are_non_empty_and_unique(self, system_api):
        """Verify health-check service names remain non-empty and unique in the response list."""
        response = system_api.get_health()
        body = response.json()

        names = [item["name"] for item in body["data"]]
        assert all(names)
        assert len(names) == len(set(names))
