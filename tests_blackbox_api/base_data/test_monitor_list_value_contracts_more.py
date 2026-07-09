# -*- coding: utf-8 -*-
"""AMCS 监控点列表补充值契约测试。"""
from __future__ import annotations

import allure


@allure.feature("基础数据库")
class TestMonitorListValueContractsMore:
    """补充校验监控点列表第一页字段值稳定性。"""

    @staticmethod
    def _login(auth_api, test_user):
        """每条用例先登录，并确认会话已建立。"""
        login_response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert login_response.status_code == 200
        assert login_response.json()["status"] == 0

    @allure.title("监控点列表前几行 isStored 字段保持 0/1 字符串")
    def test_monitor_list_first_rows_keep_is_stored_string_flags(self, auth_api, database_api, test_user):
        """校验前几条监控点记录中的 isStored 仍使用字符串标记值。"""
        self._login(auth_api, test_user)

        rows = database_api.list_monitors(rows=5).json()["rows"]
        for row in rows:
            assert row["isStored"] in {"0", "1"}

    @allure.title("监控点列表前几行告警数据类型字段保持非空")
    def test_monitor_list_first_rows_keep_non_empty_alarm_datatype(self, auth_api, database_api, test_user):
        """校验前几条监控点记录中的 alarmDatatype 保持非空。"""
        self._login(auth_api, test_user)

        rows = database_api.list_monitors(rows=5).json()["rows"]
        for row in rows:
            assert isinstance(row["alarmDatatype"], str)
            assert row["alarmDatatype"]
