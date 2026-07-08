# -*- coding: utf-8 -*-
"""AMCS 报警事件接口测试。"""
from __future__ import annotations

import allure
import pytest
import re


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

    @allure.title("报警记录首条数据包含标识与状态字段")
    def test_alarm_record_first_row_contains_identity_and_status_fields(self, auth_api, alarm_api, test_user):
        """有报警数据时校验首条记录包含主键、设备标识和状态类字段。"""
        login_response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert login_response.json()["status"] == 0

        response = alarm_api.get_alarm_record_page()
        body = response.json()
        if not body:
            pytest.skip("当前环境没有报警记录，跳过标识字段校验")

        first_row = body[0]
        assert first_row["id"]
        assert first_row["equipId"]
        assert first_row["alarmSource"]
        assert first_row["alarmLevel"]
        assert first_row["status"] is not None
        assert first_row["hasLink"] in {"0", "1"}
        assert first_row["isPatrol"] in {"0", "1"}

    @allure.title("报警记录时间字段使用标准日期时间字符串")
    def test_alarm_record_datetime_uses_timestamp_string(self, auth_api, alarm_api, test_user):
        """有报警数据时校验 alarmDt 字段使用标准日期时间字符串格式。"""
        login_response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert login_response.json()["status"] == 0

        response = alarm_api.get_alarm_record_page()
        body = response.json()
        if not body:
            pytest.skip("当前环境没有报警记录，跳过时间格式校验")

        alarm_dt = body[0]["alarmDt"]
        assert re.fullmatch(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{3}", alarm_dt)

    @allure.title("Alarm record codes and flags keep string-code types")
    def test_alarm_record_code_fields_use_string_types(self, auth_api, alarm_api, test_user):
        """Verify alarm code and flag fields remain string-based codes for frontend rendering."""
        login_response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert login_response.json()["status"] == 0

        response = alarm_api.get_alarm_record_page()
        body = response.json()
        if not body:
            pytest.skip("Current environment has no alarm records.")

        for row in body[:3]:
            assert isinstance(row["alarmLevel"], str)
            assert isinstance(row["status"], str)
            assert isinstance(row["hasLink"], str)
            assert isinstance(row["isPatrol"], str)
            assert isinstance(row["alarmSource"], str)
