# -*- coding: utf-8 -*-
"""AMCS 系统级 smoke 用例。

这组用例优先覆盖首页和平台基础接口，适合做环境可用性检查。
"""
from __future__ import annotations

import allure


@allure.feature("系统接口")
class TestSystemSmoke:
    """首页公共接口和健康接口的 smoke 校验。"""

    @allure.title("系统 logo 接口可匿名访问")
    def test_sys_logo_public(self, system_api):
        """校验系统 logo 接口未登录也能正常返回配置。"""
        response = system_api.get_sys_logo()

        assert response.status_code == 200
        body = response.json()
        assert body["status"] == 0
        assert "data" in body
        assert set(body["data"].keys()) >= {"sys_logo_a", "sys_logo_b"}

    @allure.title("告警数量接口登录后可访问")
    def test_alarm_count_after_login(self, auth_api, system_api, test_user):
        """校验告警数量接口在已登录会话下可正常访问。"""
        login_response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert login_response.json()["status"] == 0

        response = system_api.get_alarm_count()
        assert response.status_code == 200
        body = response.json()
        assert body["status"] == 0
        assert isinstance(body["data"], int)
        assert body["data"] >= 0

    @allure.title("告警数量接口未登录时会被拦截")
    def test_alarm_count_requires_login(self, system_api):
        """校验告警数量接口具备登录态保护。"""
        response = system_api.get_alarm_count()

        assert response.status_code == 302
        assert response.headers["Location"].startswith("/amcs/login")

    @allure.title("时间戳接口登录后可访问")
    def test_timestamp_after_login(self, auth_api, system_api, test_user):
        """校验时间戳接口返回正整数时间戳。"""
        login_response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert login_response.json()["status"] == 0

        response = system_api.get_timestamp()
        assert response.status_code == 200
        body = response.json()
        assert isinstance(body, int)
        assert body > 0

    @allure.title("系统健康检查接口返回设备列表")
    def test_health_check_returns_service_data(self, system_api):
        """校验健康检查接口返回基础服务列表结构。"""
        response = system_api.get_health()

        assert response.status_code == 200
        body = response.json()
        assert body["status"] == 0
        assert isinstance(body["data"], list)
        if body["data"]:
            first_item = body["data"][0]
            assert set(first_item.keys()) >= {"name", "serviceUp", "deviceList"}
