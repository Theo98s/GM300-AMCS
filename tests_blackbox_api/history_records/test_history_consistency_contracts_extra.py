# -*- coding: utf-8 -*-
"""AMCS 历史记录一致性补充契约测试。"""
from __future__ import annotations

import re

import allure


@allure.feature("History Records")
class TestHistoryConsistencyContractsExtra:
    """补充校验联动历史分页结果的一致性。"""

    @staticmethod
    def _login(auth_api, test_user):
        """每条用例先登录，并确认会话已建立。"""
        login_response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert login_response.status_code == 200
        assert login_response.json()["status"] == 0

    @allure.title("历史记录第一页保持目标所亭名称")
    def test_monitor_link_history_first_page_keeps_non_empty_substation_names(
        self,
        auth_api,
        history_api,
        test_user,
    ):
        """校验历史记录第一页数据仍属于外部配置中的目标所亭。"""
        self._login(auth_api, test_user)

        rows = history_api.find_monitor_link_history({"rows": 5}).json()["rows"]
        assert len(rows) >= 1

        for row in rows:
            assert isinstance(row["subId"], str)
            assert row["subId"]

    @allure.title("历史记录第一页保持非空标识与报警数据编码")
    def test_monitor_link_history_first_page_keeps_identity_and_alarmdata_codes(
        self,
        auth_api,
        history_api,
        test_user,
    ):
        """校验历史记录第一页保持稳定的标识字段和数字字符串 alarmdataType。"""
        self._login(auth_api, test_user)

        rows = history_api.find_monitor_link_history({"rows": 5}).json()["rows"]
        assert len(rows) >= 1

        for row in rows:
            assert isinstance(row["id"], str) and row["id"]
            assert isinstance(row["equipId"], str) and row["equipId"]
            assert isinstance(row["equipName"], str) and row["equipName"]
            assert re.fullmatch(r"\d+", row["alarmdataType"])
