# -*- coding: utf-8 -*-
"""Additional AMCS history-record contract tests."""
from __future__ import annotations

import re

import allure


@allure.feature("历史记录")
class TestHistoryContractsExtra:
    """Extra contract checks for monitor-link history rows."""

    @allure.title("联动历史展示字段保持非空")
    def test_monitor_link_history_display_fields_are_non_empty(self, auth_api, history_api, test_user):
        """Verify history rows keep non-empty equipment, description, and status display fields."""
        login_response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert login_response.json()["status"] == 0

        response = history_api.find_monitor_link_history({"rows": 3})
        body = response.json()
        assert len(body["rows"]) >= 1

        for row in body["rows"]:
            assert isinstance(row["equipName"], str)
            assert isinstance(row["description"], str)
            assert isinstance(row["status"], str)
            assert row["equipName"]
            assert row["description"]
            assert row["status"]

    @allure.title("联动历史状态与时间字段保持稳定格式")
    def test_monitor_link_history_status_and_time_fields_keep_expected_formats(self, auth_api, history_api, test_user):
        """Verify history status remains a digit string and createTime stays a millisecond timestamp."""
        login_response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert login_response.json()["status"] == 0

        response = history_api.find_monitor_link_history({"rows": 3})
        body = response.json()
        assert len(body["rows"]) >= 1

        for row in body["rows"]:
            assert re.fullmatch(r"\d+", row["status"])
            assert isinstance(row["createTime"], int)
            assert row["createTime"] >= 10**12

