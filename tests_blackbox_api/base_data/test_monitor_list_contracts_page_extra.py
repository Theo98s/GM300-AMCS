# -*- coding: utf-8 -*-
"""Additional AMCS monitor-list page contract tests."""
from __future__ import annotations

import json

import allure


@allure.feature("基础数据库")
class TestMonitorListPageContractsExtra:
    """Extra checks for the first page of monitor-list rows."""

    @staticmethod
    def _login(auth_api, test_user):
        """Log in once per test and assert the session is established."""
        login_response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert login_response.status_code == 200
        assert login_response.json()["status"] == 0

    @allure.title("监控点列表前几行 id 保持唯一")
    def test_monitor_list_first_page_ids_are_unique(self, auth_api, database_api, test_user):
        """Verify the first page of monitor rows keeps unique ids."""
        self._login(auth_api, test_user)

        rows = database_api.list_monitors(rows=5).json()["rows"]
        ids = [row["id"] for row in rows]
        assert len(ids) == len(set(ids))

    @allure.title("监控点列表 yx 标签值保持非空")
    def test_monitor_list_yx_labels_are_non_empty(self, auth_api, database_api, test_user):
        """Verify the parsed yx labels in the first monitor row stay non-empty strings."""
        self._login(auth_api, test_user)

        first_row = database_api.list_monitors(rows=1).json()["rows"][0]
        yx_config = json.loads(first_row["yx"])
        assert yx_config["TRUE_LABEL"]
        assert yx_config["FALSE_LABEL"]

