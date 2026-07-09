# -*- coding: utf-8 -*-
"""AMCS 报警展示补充契约测试。"""
from __future__ import annotations

import re

import allure
import pytest


@allure.feature("报警事件")
class TestAlarmDisplayContractsMore:
    """补充校验报警记录中的展示字段和值模式。"""

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
        """返回报警记录；如果当前环境没有数据则跳过。"""
        rows = alarm_api.get_alarm_record_page().json()
        if not rows:
            pytest.skip("当前环境没有报警记录。")
        return rows

    @allure.title("报警记录前几条温度展示值保持数字加摄氏度格式")
    def test_alarm_record_first_rows_keep_temperature_display_pattern(self, auth_api, alarm_api, test_user):
        """校验前几条报警记录的展示值仍保持数字加摄氏度格式。"""
        self._login(auth_api, test_user)

        rows = self._rows_or_skip(alarm_api)[:5]
        for row in rows:
            assert re.fullmatch(r"\d+\.\d+℃", row["warnContent"])

    @allure.title("报警记录前几条保持默认空关联字段")
    def test_alarm_record_first_rows_keep_nullable_relation_fields(self, auth_api, alarm_api, test_user):
        """校验前几条报警记录仍保持默认空关联字段。"""
        self._login(auth_api, test_user)

        rows = self._rows_or_skip(alarm_api)[:5]
        for row in rows:
            assert row["dealUser"] is None
            assert row["dealUserName"] is None
            assert row["recoverDt"] is None
            assert row["monitorId"] is None
            assert row["conditionId"] is None
