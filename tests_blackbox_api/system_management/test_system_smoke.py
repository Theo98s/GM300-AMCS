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

    @allure.title("告警数量接口登录后返回标准成功消息")
    def test_alarm_count_after_login_returns_success_message(self, auth_api, system_api, test_user):
        """校验告警数量接口登录后返回固定成功消息，便于前端统一处理。"""
        login_response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert login_response.json()["status"] == 0

        response = system_api.get_alarm_count()
        body = response.json()

        assert body["status"] == 0
        assert body["message"] == "数据查询成功!"

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

    @allure.title("时间戳接口登录后返回毫秒级时间戳")
    def test_timestamp_after_login_returns_millisecond_precision(self, auth_api, system_api, test_user):
        """校验时间戳接口返回 13 位毫秒级时间戳。"""
        login_response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert login_response.json()["status"] == 0

        response = system_api.get_timestamp()
        body = response.json()

        assert isinstance(body, int)
        assert body >= 10**12

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

    @allure.title("时间戳接口连续请求保持非递减")
    def test_timestamp_after_login_is_monotonic(self, auth_api, system_api, test_user):
        """校验同一会话下连续两次获取时间戳时，后一次结果不小于前一次。"""
        login_response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert login_response.json()["status"] == 0

        first_response = system_api.get_timestamp()
        second_response = system_api.get_timestamp()

        first_value = first_response.json()
        second_value = second_response.json()
        assert isinstance(first_value, int)
        assert isinstance(second_value, int)
        assert second_value >= first_value

    @allure.title("健康检查 deviceList 字段允许为空或列表")
    def test_health_check_device_list_uses_nullable_list_contract(self, system_api):
        """校验健康检查中的 deviceList 字段保持列表或空值契约，避免前端解析出错。"""
        response = system_api.get_health()
        body = response.json()

        for item in body["data"]:
            assert isinstance(item["serviceUp"], bool)
            assert item["deviceList"] is None or isinstance(item["deviceList"], list)
