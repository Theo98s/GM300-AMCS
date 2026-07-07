# -*- coding: utf-8 -*-
"""AMCS 报警事件接口测试。"""
from __future__ import annotations

import allure
import pytest


@allure.feature("报警事件")
class TestAlarmApi:
    """报警记录查询 smoke 用例。"""

    @allure.title("报警记录接口返回列表")
    def test_alarm_record_page_returns_rows(self, auth_api, alarm_api, test_user):
        """校验报警记录接口至少能稳定返回列表结构。"""
        login_response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert login_response.json()["status"] == 0

        response = alarm_api.get_alarm_record_page()
        assert response.status_code == 200

        body = response.json()
        assert isinstance(body, list)

    @allure.title("报警记录首条数据包含关键告警字段")
    def test_alarm_record_first_row_contains_expected_fields(self, auth_api, alarm_api, test_user):
        """有报警数据时校验首条记录包含关键字段，无数据则跳过该断言。"""
        login_response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert login_response.json()["status"] == 0

        response = alarm_api.get_alarm_record_page()
        body = response.json()
        if not body:
            pytest.skip("当前环境没有报警记录，跳过首条数据字段校验")

        first_row = body[0]

        assert set(first_row.keys()) >= {
            "alarmDt",
            "alarmLevel",
            "warnContent",
            "alarmDataType",
            "status",
            "equipName",
        }
        assert first_row["alarmDt"]
        assert first_row["warnContent"]
