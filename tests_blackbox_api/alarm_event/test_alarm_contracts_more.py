# -*- coding: utf-8 -*-
"""AMCS 报警记录更多契约测试。"""
from __future__ import annotations

import re

import allure
import pytest


@allure.feature("Alarm Event")
class TestAlarmContractsMore:
    """补充校验报警记录列表行级契约。"""

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
            pytest.skip("Current environment has no alarm records.")
        return rows

    @allure.title("报警记录行保持 alarmDt 与 alarmDtStr 镜像字段")
    def test_alarm_record_time_fields_keep_mirrored_display_values(self, auth_api, alarm_api, test_user):
        """校验前几条报警记录中的原始时间与展示时间字段保持一致。"""
        self._login(auth_api, test_user)

        for row in self._rows_or_skip(alarm_api)[:3]:
            assert re.fullmatch(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{3}", row["alarmDt"])
            assert row["alarmDtStr"] == row["alarmDt"]

    @allure.title("报警记录行保持稳定的编码与可空字段契约")
    def test_alarm_record_first_rows_keep_code_and_nullable_field_contracts(
        self,
        auth_api,
        alarm_api,
        test_user,
    ):
        """校验报警编码字段保持数字字符串，可空展示字段仍保持可空字符串契约。"""
        self._login(auth_api, test_user)

        for row in self._rows_or_skip(alarm_api)[:3]:
            assert row["deleted"] == 0
            assert re.fullmatch(r"\d{2}", row["securityequiptype"])
            assert re.fullmatch(r"\d{2}", row["alarmType"])
            assert re.fullmatch(r"\d{2}", row["alarmSource"])
            assert row["subName"] is None or isinstance(row["subName"], str)
            assert row["alarmClass"] is None or isinstance(row["alarmClass"], str)
