# -*- coding: utf-8 -*-
"""AMCS 巡检调度补充契约测试。"""
from __future__ import annotations

import allure
import pytest


@allure.feature("巡检管理")
class TestPatrolScheduleContractsMore:
    """补充校验巡检计划状态、调度和详情时间对齐关系。"""

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

    @allure.title("巡检计划保持段级中心和固定可启动标记")
    def test_patrol_plan_rows_keep_center_type_and_start_flag(self, auth_api, patrol_api, test_user):
        """校验当前巡检计划仍使用段级中心类型，并保持可启动布尔标记。"""
        self._login(auth_api, test_user)

        for plan in self._plans_or_skip(patrol_api)[:5]:
            assert plan["centerType"] == "DUAN"
            assert plan["executeType"] == "0"
            assert plan["canBeStarted"] is True
            assert plan["movable"] is False

    @allure.title("巡检计划状态与调度字段保持当前空值分支")
    def test_patrol_plan_rows_keep_schedule_nullability_by_execute_state(self, auth_api, patrol_api, test_user):
        """校验运行中计划和结束计划仍保持当前调度字段空值分支。"""
        self._login(auth_api, test_user)

        for plan in self._plans_or_skip(patrol_api)[:5]:
            if plan["executeState"] is None:
                assert isinstance(plan["cron"], str) and plan["cron"]
                assert isinstance(plan["weeks"], str) and plan["weeks"]
                assert plan["recordId"] is None
            else:
                assert plan["executeState"] == "END"
                assert plan["cron"] is None
                assert plan["weeks"] is None
                assert isinstance(plan["recordId"], str) and plan["recordId"]

    @allure.title("巡检详情前几条记录保持与计划停留时长对齐")
    def test_patrol_plan_details_keep_residence_time_aligned_with_plan(self, auth_api, patrol_api, test_user):
        """校验巡检详情前几条记录仍与父计划保持相同停留时长。"""
        self._login(auth_api, test_user)

        for plan in self._plans_or_skip(patrol_api)[:3]:
            details = plan["details"]
            if not details:
                continue
            for detail in details[:5]:
                assert detail["residenceTime"] == plan["residenceTime"]
                assert detail["channelNum"] is None
                assert detail["visibleChannelNum"] is None
                assert detail["nvrSerialNum"] is None
                assert detail["visibleNvrSerialNum"] is None
