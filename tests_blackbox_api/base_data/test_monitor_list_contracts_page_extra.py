# -*- coding: utf-8 -*-
"""AMCS 监控点列表分页补充契约测试。"""
from __future__ import annotations

import json

import allure


@allure.feature("基础数据库")
class TestMonitorListPageContractsExtra:
    """补充校验监控点列表第一页记录。"""

    @staticmethod
    def _login(auth_api, test_user):
        """每条用例先登录，并确认会话已建立。"""
        login_response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert login_response.status_code == 200
        assert login_response.json()["status"] == 0

    @allure.title("监控点列表前几行 id 保持唯一")
    def test_monitor_list_first_page_ids_are_unique(self, auth_api, database_api, test_user):
        """校验监控点列表第一页记录的 id 保持唯一。"""
        self._login(auth_api, test_user)

        rows = database_api.list_monitors(rows=5).json()["rows"]
        ids = [row["id"] for row in rows]
        assert len(ids) == len(set(ids))

    @allure.title("监控点列表 yx 标签值保持非空")
    def test_monitor_list_yx_labels_are_non_empty(self, auth_api, database_api, test_user):
        """校验首条监控点记录中解析出的 yx 标签保持非空字符串。"""
        self._login(auth_api, test_user)

        first_row = database_api.list_monitors(rows=1).json()["rows"][0]
        yx_config = json.loads(first_row["yx"])
        assert yx_config["TRUE_LABEL"]
        assert yx_config["FALSE_LABEL"]
