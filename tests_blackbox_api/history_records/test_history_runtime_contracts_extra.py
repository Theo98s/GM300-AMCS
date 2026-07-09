# -*- coding: utf-8 -*-
"""AMCS 历史记录运行时补充契约测试。"""
from __future__ import annotations

import re

import allure


@allure.feature("历史记录")
class TestHistoryRuntimeContractsExtra:
    """补充校验联动历史记录中的空值模式和标识字段。"""

    @staticmethod
    def _login(auth_api, test_user):
        """每条用例先登录，并确认会话已建立。"""
        login_response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert login_response.status_code == 200
        assert login_response.json()["status"] == 0

    @allure.title("联动历史前几条记录保持标识字段和空值契约")
    def test_monitor_link_history_first_rows_keep_identity_and_nullable_fields(
        self,
        auth_api,
        history_api,
        test_user,
    ):
        """校验前几条联动历史记录仍保留非空标识字段和当前空值模式。"""
        self._login(auth_api, test_user)

        rows = history_api.find_monitor_link_history({"rows": 5}).json()["rows"]
        assert len(rows) == 5

        for row in rows:
            assert isinstance(row["id"], str) and row["id"]
            assert isinstance(row["equipId"], str) and row["equipId"]
            assert isinstance(row["linkEquipId"], str) and row["linkEquipId"]
            assert row["alarmId"] is None or isinstance(row["alarmId"], str)
            assert row["checkValue"] is None or isinstance(row["checkValue"], str)
            assert row["linkage"] is None or isinstance(row["linkage"], str)
            assert row["linkDt"] is None or isinstance(row["linkDt"], str)

    @allure.title("联动历史前几条记录保持分类和触发字段格式")
    def test_monitor_link_history_first_rows_keep_code_and_trigger_formats(
        self,
        auth_api,
        history_api,
        test_user,
    ):
        """校验前几条联动历史记录仍保持分类编码和触发字段格式。"""
        self._login(auth_api, test_user)

        rows = history_api.find_monitor_link_history({"rows": 5}).json()["rows"]
        for row in rows:
            assert re.fullmatch(r"\d{2}", row["securityequiptype"])
            assert re.fullmatch(r"\d+", row["alarmdataType"])
            assert re.fullmatch(r"\d+", row["linktype"])
            assert isinstance(row["triggerSignal"], str) and row["triggerSignal"]
            assert isinstance(row["alarmType"], str) and row["alarmType"]
