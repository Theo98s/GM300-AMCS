# -*- coding: utf-8 -*-
"""AMCS 监控点列表可空字段补充契约测试。"""
from __future__ import annotations

import allure


@allure.feature("基础数据")
class TestMonitorListNullableContractsMore:
    """补充校验监控点列表前几条记录的可空字段和默认空值。"""

    @staticmethod
    def _login(auth_api, test_user):
        """每条用例先登录，并确认会话已建立。"""
        login_response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert login_response.status_code == 200
        assert login_response.json()["status"] == 0

    @allure.title("监控点列表前几条记录保持空十六进制地址字段")
    def test_monitor_list_first_rows_keep_nullable_scada_addr16(self, auth_api, database_api, test_user):
        """校验前几条监控点记录仍保持空 scadaAddr16 字段。"""
        self._login(auth_api, test_user)

        rows = database_api.list_monitors(rows=5).json()["rows"]
        for row in rows:
            assert row["scadaAddr16"] is None

    @allure.title("监控点列表前几条遥信记录保持空量测控制字段")
    def test_monitor_list_first_rows_keep_empty_yc_yk_yt_fields(self, auth_api, database_api, test_user):
        """校验前几条遥信记录仍未填充 yc、yk、yt 扩展字段。"""
        self._login(auth_api, test_user)

        rows = database_api.list_monitors(rows=5).json()["rows"]
        for row in rows:
            assert row["yc"] is None
            assert row["yk"] is None
            assert row["yt"] is None

    @allure.title("监控点列表前几条记录保持空偏移与变化阈值字段")
    def test_monitor_list_first_rows_keep_empty_offset_threshold_fields(self, auth_api, database_api, test_user):
        """校验前几条记录在当前环境下仍未配置偏移和变化阈值字段。"""
        self._login(auth_api, test_user)

        rows = database_api.list_monitors(rows=5).json()["rows"]
        for row in rows:
            assert row["offset"] == ""
            assert row["changeRatio"] == ""
            assert row["changeThreshold"] == ""
