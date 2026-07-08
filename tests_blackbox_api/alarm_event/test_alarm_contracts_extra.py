# -*- coding: utf-8 -*-
"""Additional AMCS alarm-record contract tests."""
from __future__ import annotations

import re

import allure
import pytest


@allure.feature("报警事件")
class TestAlarmContractsExtra:
    """Extra contract checks for alarm-record list payloads."""

    @allure.title("报警记录展示字段保持非空字符串")
    def test_alarm_record_display_fields_are_non_empty(self, auth_api, alarm_api, test_user):
        """Verify alarm list rows keep non-empty display text for equipment and warning content."""
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
            assert isinstance(row["equipName"], str)
            assert isinstance(row["warnContent"], str)
            assert row["equipName"]
            assert row["warnContent"]

    @allure.title("报警记录码值字段保持数字字符串格式")
    def test_alarm_record_code_fields_match_digit_patterns(self, auth_api, alarm_api, test_user):
        """Verify alarm code fields remain digit-string codes expected by the frontend."""
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
            assert re.fullmatch(r"\d{2}", row["alarmLevel"])
            assert re.fullmatch(r"\d{2}", row["alarmSource"])
            assert re.fullmatch(r"\d+", row["status"])
            assert row["hasLink"] in {"0", "1"}
            assert row["isPatrol"] in {"0", "1"}

