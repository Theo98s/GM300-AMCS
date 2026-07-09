# -*- coding: utf-8 -*-
"""AMCS 报警记录顺序补充契约测试。"""
from __future__ import annotations

import allure
import pytest


@allure.feature("报警事件")
class TestAlarmOrderContractsExtra:
    """补充校验报警记录列表的顺序与可空字段契约。"""

    @staticmethod
    def _login(auth_api, test_user):
        """每条用例先登录，并确认会话已建立。"""
        login_response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert login_response.status_code == 200
        assert login_response.json()["status"] == 0

    @staticmethod
    def _rows_or_skip(alarm_api):
        """返回报警记录；如果当前环境无数据则跳过。"""
        rows = alarm_api.get_alarm_record_page().json()
        if not rows:
            pytest.skip("当前环境没有报警记录。")
        return rows

    @allure.title("报警记录第一页保持按时间倒序排列")
    def test_alarm_record_rows_keep_descending_alarm_time_order(self, auth_api, alarm_api, test_user):
        """校验报警记录列表仍按最新时间优先排序。"""
        self._login(auth_api, test_user)

        rows = self._rows_or_skip(alarm_api)[:5]
        alarm_times = [row["alarmDt"] for row in rows]
        assert alarm_times == sorted(alarm_times, reverse=True)

    @allure.title("报警记录可空处理字段保持可空字符串契约")
    def test_alarm_record_rows_keep_nullable_deal_fields_contract(self, auth_api, alarm_api, test_user):
        """校验处理人、处理时间等可空字段仍保持可空字符串契约。"""
        self._login(auth_api, test_user)

        for row in self._rows_or_skip(alarm_api)[:5]:
            assert row["dealTime"] is None or isinstance(row["dealTime"], str)
            assert row["dealUser"] is None or isinstance(row["dealUser"], str)
            assert row["dealUserName"] is None or isinstance(row["dealUserName"], str)
            assert row["recoverDt"] is None or isinstance(row["recoverDt"], str)
            assert row["monitorId"] is None or isinstance(row["monitorId"], str)
            assert row["conditionId"] is None or isinstance(row["conditionId"], str)
