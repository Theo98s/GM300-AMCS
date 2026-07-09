# -*- coding: utf-8 -*-
"""More AMCS alarm-record contract tests."""
from __future__ import annotations

import re

import allure
import pytest


@allure.feature("Alarm Event")
class TestAlarmContractsMore:
    """Extra contract checks for alarm-record list rows."""

    @staticmethod
    def _login(auth_api, test_user):
        """Log in once per test and assert the session is ready."""
        login_response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert login_response.status_code == 200
        assert login_response.json()["status"] == 0

    @staticmethod
    def _rows_or_skip(alarm_api):
        """Return alarm rows or skip when the current environment has no data."""
        rows = alarm_api.get_alarm_record_page().json()
        if not rows:
            pytest.skip("Current environment has no alarm records.")
        return rows

    @allure.title("Alarm rows keep mirrored alarmDt and alarmDtStr fields")
    def test_alarm_record_time_fields_keep_mirrored_display_values(self, auth_api, alarm_api, test_user):
        """Verify the raw and display time fields stay aligned on the first few alarm rows."""
        self._login(auth_api, test_user)

        for row in self._rows_or_skip(alarm_api)[:3]:
            assert re.fullmatch(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{3}", row["alarmDt"])
            assert row["alarmDtStr"] == row["alarmDt"]

    @allure.title("Alarm rows keep stable code and nullable field contracts")
    def test_alarm_record_first_rows_keep_code_and_nullable_field_contracts(
        self,
        auth_api,
        alarm_api,
        test_user,
    ):
        """Verify alarm code fields stay digit strings and nullable display fields remain nullable strings."""
        self._login(auth_api, test_user)

        for row in self._rows_or_skip(alarm_api)[:3]:
            assert row["deleted"] == 0
            assert re.fullmatch(r"\d{2}", row["securityequiptype"])
            assert re.fullmatch(r"\d{2}", row["alarmType"])
            assert re.fullmatch(r"\d{2}", row["alarmSource"])
            assert row["subName"] is None or isinstance(row["subName"], str)
            assert row["alarmClass"] is None or isinstance(row["alarmClass"], str)
