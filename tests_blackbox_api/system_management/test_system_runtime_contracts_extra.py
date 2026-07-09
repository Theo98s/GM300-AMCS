# -*- coding: utf-8 -*-
"""AMCS 系统运行时补充契约测试。"""
from __future__ import annotations

import allure


@allure.feature("系统管理")
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
