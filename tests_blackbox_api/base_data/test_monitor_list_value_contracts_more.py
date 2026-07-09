# -*- coding: utf-8 -*-
"""Additional AMCS monitor-list value contract tests."""
from __future__ import annotations

import allure


@allure.feature("基础数据库")
class TestMonitorListValueContractsMore:
    """Extra checks for value stability in the first page of monitor rows."""

    @staticmethod
    def _login(auth_api, test_user):
        """Log in once per test and assert the session is established."""
        login_response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert login_response.status_code == 200
        assert login_response.json()["status"] == 0

    @allure.title("监控点列表前几行 isStored 字段保持 0/1 字符串")
    def test_monitor_list_first_rows_keep_is_stored_string_flags(self, auth_api, database_api, test_user):
        """Verify the first few monitor rows keep isStored as string flags."""
        self._login(auth_api, test_user)

        rows = database_api.list_monitors(rows=5).json()["rows"]
        for row in rows:
            assert row["isStored"] in {"0", "1"}

    @allure.title("监控点列表前几行告警数据类型字段保持非空")
    def test_monitor_list_first_rows_keep_non_empty_alarm_datatype(self, auth_api, database_api, test_user):
        """Verify the first few monitor rows keep non-empty alarmDatatype values."""
        self._login(auth_api, test_user)

        rows = database_api.list_monitors(rows=5).json()["rows"]
        for row in rows:
            assert isinstance(row["alarmDatatype"], str)
            assert row["alarmDatatype"]

