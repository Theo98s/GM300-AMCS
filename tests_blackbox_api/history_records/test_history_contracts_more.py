# -*- coding: utf-8 -*-
"""More AMCS linkage-history contract tests."""
from __future__ import annotations

import re

import allure


@allure.feature("History Records")
class TestHistoryContractsMore:
    """Extra contract checks for linkage-history rows."""

    @staticmethod
    def _login(auth_api, test_user):
        """Log in once per test and assert the session is ready."""
        login_response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert login_response.status_code == 200
        assert login_response.json()["status"] == 0

    @allure.title("History rows keep operation time and code formats")
    def test_monitor_link_history_rows_keep_operation_time_and_code_formats(
        self,
        auth_api,
        history_api,
        test_user,
    ):
        """Verify the first page keeps millisecond datetime strings and digit-code status fields."""
        self._login(auth_api, test_user)

        rows = history_api.find_monitor_link_history({"rows": 3}).json()["rows"]
        assert len(rows) >= 1

        for row in rows:
            assert re.fullmatch(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{3}", row["operationDt"])
            assert re.fullmatch(r"\d+", row["status"])
            assert re.fullmatch(r"\d+", row["linktype"])
            assert isinstance(row["creator"], str)
            assert row["creator"]

    @allure.title("History first page keeps non-increasing createTime ordering")
    def test_monitor_link_history_first_page_create_time_is_non_increasing(
        self,
        auth_api,
        history_api,
        test_user,
    ):
        """Verify the first page remains sorted by newest-first createTime values."""
        self._login(auth_api, test_user)

        rows = history_api.find_monitor_link_history({"rows": 5}).json()["rows"]
        assert len(rows) >= 2

        create_times = [row["createTime"] for row in rows]
        assert create_times == sorted(create_times, reverse=True)
