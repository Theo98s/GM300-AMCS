# -*- coding: utf-8 -*-
"""AMCS 监控点列表更多格式契约测试。"""
from __future__ import annotations

import json
import re

import allure


@allure.feature("基础数据库")
class TestMonitorListFormatContractsMore:
    """补充校验监控点列表表格中的行级格式。"""

    @staticmethod
    def _login(auth_api, test_user):
        """每条用例先登录，并确认会话已建立。"""
        login_response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert login_response.status_code == 200
        assert login_response.json()["status"] == 0

    @allure.title("监控点列表前几行分类字段保持数字字符串")
    def test_monitor_list_first_rows_keep_code_field_patterns(self, auth_api, database_api, test_user):
        """校验前几条记录中的 alarmClass 和 securityequiptype 保持数字字符串格式。"""
        self._login(auth_api, test_user)

        rows = database_api.list_monitors(rows=5).json()["rows"]
        for row in rows:
            assert re.fullmatch(r"\d{2}", row["alarmClass"])
            assert re.fullmatch(r"\d{2}", row["securityequiptype"])

    @allure.title("监控点列表前几行 yx 配置键集合保持一致")
    def test_monitor_list_first_rows_keep_consistent_yx_keys(self, auth_api, database_api, test_user):
        """校验前几条监控点记录解析后的 yx 键集合保持一致。"""
        self._login(auth_api, test_user)

        rows = database_api.list_monitors(rows=5).json()["rows"]
        key_sets = [set(json.loads(row["yx"]).keys()) for row in rows]
        assert all(keys == {"TRUE_LABEL", "FALSE_LABEL"} for keys in key_sets)
