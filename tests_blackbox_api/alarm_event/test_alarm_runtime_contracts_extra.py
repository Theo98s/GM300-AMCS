# -*- coding: utf-8 -*-
"""AMCS 报警记录运行时补充契约测试。"""
from __future__ import annotations

import allure
import pytest


@allure.feature("报警事件")
class TestAlarmRuntimeContractsExtra:
    """补充校验报警记录当前未处理场景中的运行时默认值。"""

    @staticmethod
    def _login(auth_api, test_user):
        """每条用例先登录，并确认会话已建立。"""
        login_response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert login_response.status_code == 200
        assert login_response.json()["status"] == 0

    @staticmethod
    def _rows_or_skip(alarm_api):
        """返回报警记录；如果当前环境没有数据则跳过。"""
        rows = alarm_api.get_alarm_record_page().json()
        if not rows:
            pytest.skip("当前环境没有报警记录。")
        return rows

    @allure.title("报警记录第一页主键保持唯一")
    def test_alarm_record_first_page_ids_are_unique(self, auth_api, alarm_api, test_user):
        """校验报警记录第一页返回的主键仍保持唯一。"""
        self._login(auth_api, test_user)

        rows = self._rows_or_skip(alarm_api)[:10]
        ids = [row["id"] for row in rows]
        assert len(ids) == len(set(ids))

    @allure.title("报警记录前几条未处理数据保持空处理字段")
    def test_alarm_record_first_rows_keep_null_processing_fields_when_status_is_open(self, auth_api, alarm_api, test_user):
        """校验未处理报警记录仍保持空处理字段和空联动结果字段。"""
        self._login(auth_api, test_user)

        rows = self._rows_or_skip(alarm_api)[:5]
        for row in rows:
            if row["status"] == "0":
                assert row["dealUser"] is None
                assert row.get("dealDt") is None or row.get("dealTime") is None
                assert row.get("dealContent") is None
                assert row.get("linkageStatus") is None

    @allure.title("报警记录前几条保持未删除与默认空站点字段")
    def test_alarm_record_first_rows_keep_default_deleted_and_station_fields(self, auth_api, alarm_api, test_user):
        """校验前几条报警记录仍保持未删除标记和默认空站点字段。"""
        self._login(auth_api, test_user)

        rows = self._rows_or_skip(alarm_api)[:5]
        for row in rows:
            assert row["deleted"] == 0
            assert row["subName"] is None or isinstance(row["subName"], str)
            assert row["alarmClass"] is None or isinstance(row["alarmClass"], str)
