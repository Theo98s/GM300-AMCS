# -*- coding: utf-8 -*-
"""AMCS 巡检管理更多契约测试。"""
from __future__ import annotations

import numbers

import allure
import pytest


@allure.feature("Patrol Management")
class TestPatrolContractsMore:
    """补充校验巡检计划及详情行契约。"""

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
            pytest.skip("Current environment has no patrol plans.")
        return plans

    @allure.title("巡检计划保留执行标记与状态契约")
    def test_patrol_plan_execution_flags_keep_expected_types(self, auth_api, patrol_api, test_user):
        """校验首条巡检计划保持字符串执行状态和布尔控制标记。"""
        self._login(auth_api, test_user)

        first_plan = self._plans_or_skip(patrol_api)[0]
        assert isinstance(first_plan["centerType"], str) and first_plan["centerType"]
        assert isinstance(first_plan["executeType"], str) and first_plan["executeType"]
        assert first_plan["executeState"] is None or isinstance(first_plan["executeState"], str)
        assert isinstance(first_plan["canBeStarted"], bool)
        assert isinstance(first_plan["movable"], bool)
        assert isinstance(first_plan["receivedFirstPointResult"], bool)

    @allure.title("巡检详情行保留可空结果字段契约")
    def test_patrol_plan_detail_result_fields_keep_nullable_text_contracts(self, auth_api, patrol_api, test_user):
        """校验首条巡检详情保持可空结果字段和数值温度契约。"""
        self._login(auth_api, test_user)

        first_plan = self._plans_or_skip(patrol_api)[0]
        if not first_plan["details"]:
            pytest.skip("Current environment has no patrol plan details.")

        first_detail = first_plan["details"][0]
        assert first_detail["result"] is None or isinstance(first_detail["result"], str)
        assert first_detail["valueResult"] is None or isinstance(first_detail["valueResult"], str)
        assert first_detail["standResult"] is None or isinstance(first_detail["standResult"], str)
        assert first_detail["valueStatus"] is None or isinstance(first_detail["valueStatus"], str)
        assert first_detail["pointTemperature"] is None or isinstance(first_detail["pointTemperature"], numbers.Real)
        assert isinstance(first_detail["ext"], dict)
