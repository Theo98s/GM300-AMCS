# -*- coding: utf-8 -*-
"""AMCS 监控点列表运行时补充契约测试。"""
from __future__ import annotations

import re

import allure


@allure.feature("基础数据")
class TestMonitorListRuntimeContractsMore:
    """补充校验监控点列表前几条记录中的默认值与审计字段。"""

    @staticmethod
    def _login(auth_api, test_user):
        """每条用例先登录，并确认会话已建立。"""
        login_response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert login_response.status_code == 200
        assert login_response.json()["status"] == 0

    @allure.title("监控点列表前几条记录保持默认状态标记字段契约")
    def test_monitor_list_first_rows_keep_default_flag_fields(self, auth_api, database_api, test_user):
        """校验前几条监控点记录的默认状态标记仍保持当前类型和值域。"""
        self._login(auth_api, test_user)

        rows = database_api.list_monitors(rows=5).json()["rows"]
        assert len(rows) == 5

        for row in rows:
            assert row["deleted"] in {0, 1}
            assert row["isOffset"] in {"0", "1"}
            assert row["isRatio"] in {"0", "1"}
            assert row["isVirtual"] in {"0", "1"}
            assert row["isrelease"] in {"0", "1"}

    @allure.title("监控点列表前几条遥信记录保持空趋势配置字段")
    def test_monitor_list_first_rows_keep_empty_trend_fields(self, auth_api, database_api, test_user):
        """校验前几条记录在当前环境下仍未配置趋势告警相关字段。"""
        self._login(auth_api, test_user)

        rows = database_api.list_monitors(rows=5).json()["rows"]
        for row in rows:
            assert row["trendAlarmEnable"] == ""
            assert row["trendAlarmLevel"] == ""
            assert row["trendChangeThreshold"] == ""
            assert row["trendInterval"] == ""
            assert row["linkageStatus"] is None

    @allure.title("监控点列表前几条记录保持审计时间和站点字段格式")
    def test_monitor_list_first_rows_keep_audit_and_station_field_formats(self, auth_api, database_api, test_user):
        """校验前几条记录仍保留站点标识、创建人和创建时间格式。"""
        self._login(auth_api, test_user)

        rows = database_api.list_monitors(rows=5).json()["rows"]
        for row in rows:
            assert isinstance(row["subId"], str) and row["subId"]
            assert isinstance(row["creator"], str) and row["creator"]
            assert re.fullmatch(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}", row["createTime"])
            assert row["updateTime"] is None or re.fullmatch(
                r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}",
                row["updateTime"],
            )
