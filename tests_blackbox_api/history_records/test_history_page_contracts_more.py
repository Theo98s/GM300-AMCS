# -*- coding: utf-8 -*-
"""AMCS 历史记录分页补充契约测试。"""
from __future__ import annotations

import allure


@allure.feature("历史记录")
class TestHistoryPageContractsMore:
    """补充校验联动历史第一页中的稳定分页特征。"""

    @staticmethod
    def _login(auth_api, test_user):
        """每条用例先登录，并确认会话已建立。"""
        login_response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert login_response.status_code == 200
        assert login_response.json()["status"] == 0

    @allure.title("联动历史第一页记录主键保持唯一")
    def test_monitor_link_history_first_page_ids_are_unique(self, auth_api, history_api, test_user):
        """校验联动历史第一页返回的记录主键仍保持唯一。"""
        self._login(auth_api, test_user)

        rows = history_api.find_monitor_link_history({"rows": 20}).json()["rows"]
        ids = [row["id"] for row in rows]
        assert len(ids) == len(set(ids))

    @allure.title("联动历史第一页记录保持同一所亭名称")
    def test_monitor_link_history_first_page_keeps_same_substation_name(self, auth_api, history_api, test_user):
        """校验联动历史第一页记录仍保持当前环境的统一所亭名称。"""
        self._login(auth_api, test_user)

        rows = history_api.find_monitor_link_history({"rows": 20}).json()["rows"]
        assert len(rows) > 0
        substation_names = {row["subId"] for row in rows}
        assert len(substation_names) == 1
