# -*- coding: utf-8 -*-
"""AMCS 巡检运行时补充契约测试。"""
from __future__ import annotations

import re

import allure
import pytest


@allure.feature("巡检管理")
class TestPatrolRuntimeContractsExtra:
    """补充校验巡检计划和卡片中的运行时稳定字段。"""

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
    def _plans_or_skip(patrol_api):
        """返回巡检计划；如果当前环境没有数据则跳过。"""
        plans = patrol_api.list_patrol_plans().json()
        if not plans:
            pytest.skip("当前环境没有巡检计划。")
        return plans

    @allure.title("巡检计划前几条记录保持 cron 与 weeks 调度字段格式")
    def test_patrol_plan_first_rows_keep_schedule_field_formats(self, auth_api, patrol_api, test_user):
        """校验前几条巡检计划仍保留调度表达式和周配置格式。"""
        self._login(auth_api, test_user)

        for plan in self._plans_or_skip(patrol_api)[:3]:
            assert isinstance(plan["cron"], str) and plan["cron"]
            assert plan["weeks"] is None or re.fullmatch(r"\d+(,\d+)*", plan["weeks"])
            assert isinstance(plan["residenceTime"], int)
            assert plan["residenceTime"] >= 0

    @allure.title("巡检计划前几条详情记录保持预置位与抓拍字段契约")
    def test_patrol_plan_first_details_keep_preset_and_capture_contracts(self, auth_api, patrol_api, test_user):
        """校验前几条巡检详情记录仍保持预置位、抓拍和空扩展字段模式。"""
        self._login(auth_api, test_user)

        for plan in self._plans_or_skip(patrol_api)[:2]:
            details = plan["details"]
            if not details:
                continue

            for detail in details[:5]:
                assert isinstance(detail["monitorName"], str) and detail["monitorName"]
                assert isinstance(detail["presetCode"], int)
                assert detail["presetCode"] >= 0
                assert isinstance(detail["pictureCount"], int)
                assert detail["pictureCount"] >= 0
                assert detail["captureTime"] is None or isinstance(detail["captureTime"], int)
                assert detail["picsPath"] is None or isinstance(detail["picsPath"], str)
                assert detail["ext"] == {}

    @allure.title("巡检卡片列表保持非空名称和不为零的点位数量")
    def test_patrol_cards_keep_non_empty_names_and_positive_point_counts(self, auth_api, patrol_api, test_user):
        """校验巡检卡片仍保留非空名称，且每张卡片至少包含一个点位。"""
        self._login(auth_api, test_user)

        rows = patrol_api.list_patrol_cards().json()
        assert len(rows) > 0
        for row in rows:
            assert isinstance(row["text"], str) and row["text"]
            assert isinstance(row["pointamount"], int)
            assert row["pointamount"] > 0
            assert isinstance(row["equipamount"], int)
            assert row["equipamount"] > 0
