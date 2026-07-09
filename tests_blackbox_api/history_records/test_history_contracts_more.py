# -*- coding: utf-8 -*-
"""AMCS 联动历史更多契约测试。"""
from __future__ import annotations

import re

import allure


@allure.feature("History Records")
class TestHistoryContractsMore:
    """补充校验联动历史记录行级契约。"""

    @staticmethod
    def _login(auth_api, test_user):
        """每条用例先登录，并确认会话已建立。"""
        login_response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert login_response.status_code == 200
        assert login_response.json()["status"] == 0

    @allure.title("历史记录行保持操作时间与编码格式")
    def test_monitor_link_history_rows_keep_operation_time_and_code_formats(
        self,
        auth_api,
        history_api,
        test_user,
    ):
        """校验第一页记录保持毫秒级时间字符串和数字编码状态字段。"""
        self._login(auth_api, test_user)

        rows = history_api.find_monitor_link_history({"rows": 3}).json()["rows"]
        assert len(rows) >= 1

        for row in rows:
            assert re.fullmatch(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{3}", row["operationDt"])
            assert re.fullmatch(r"\d+", row["status"])
            assert re.fullmatch(r"\d+", row["linktype"])
            assert isinstance(row["creator"], str)
            assert row["creator"]

    @allure.title("历史记录第一页保持 createTime 非递增顺序")
    def test_monitor_link_history_first_page_create_time_is_non_increasing(
        self,
        auth_api,
        history_api,
        test_user,
    ):
        """校验第一页记录仍按 createTime 倒序排列。"""
        self._login(auth_api, test_user)

        rows = history_api.find_monitor_link_history({"rows": 5}).json()["rows"]
        assert len(rows) >= 2

        create_times = [row["createTime"] for row in rows]
        assert create_times == sorted(create_times, reverse=True)
