# -*- coding: utf-8 -*-
"""More AMCS monitor-list format contract tests."""
from __future__ import annotations

import json
import re

import allure


@allure.feature("基础数据库")
class TestMonitorListFormatContractsMore:
    """Extra checks for list-row formatting in the monitor table."""

    @staticmethod
    def _login(auth_api, test_user):
        """Log in once per test and assert the session is established."""
        login_response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert login_response.status_code == 200
        assert login_response.json()["status"] == 0

    @allure.title("监控点列表前几行分类字段保持数字字符串")
    def test_monitor_list_first_rows_keep_code_field_patterns(self, auth_api, database_api, test_user):
        """Verify alarm class and security-equipment type keep digit-string formats on the first rows."""
        self._login(auth_api, test_user)

        rows = database_api.list_monitors(rows=5).json()["rows"]
        for row in rows:
            assert re.fullmatch(r"\d{2}", row["alarmClass"])
            assert re.fullmatch(r"\d{2}", row["securityequiptype"])

    @allure.title("监控点列表前几行 yx 配置键集合保持一致")
    def test_monitor_list_first_rows_keep_consistent_yx_keys(self, auth_api, database_api, test_user):
        """Verify the first few monitor rows keep the same parsed yx key set."""
        self._login(auth_api, test_user)

        rows = database_api.list_monitors(rows=5).json()["rows"]
        key_sets = [set(json.loads(row["yx"]).keys()) for row in rows]
        assert all(keys == {"TRUE_LABEL", "FALSE_LABEL"} for keys in key_sets)

