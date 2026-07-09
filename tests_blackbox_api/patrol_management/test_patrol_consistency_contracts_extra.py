# -*- coding: utf-8 -*-
"""AMCS 巡检一致性补充契约测试。"""
from __future__ import annotations

import allure
import pytest


@allure.feature("Patrol Management")
class TestPatrolConsistencyContractsExtra:
    """补充校验巡检计划与其嵌套详情的一致性。"""

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

    @allure.title("巡检计划 multi 字段保持卡片名称与编码对齐")
    def test_patrol_plan_multi_field_keeps_card_name_and_code_alignment(self, auth_api, patrol_api, test_user):
        """校验每条巡检计划的 multi 字段都包含卡片名称和卡片编码。"""
        self._login(auth_api, test_user)

        for plan in self._plans_or_skip(patrol_api):
            assert isinstance(plan["multi"], str) and plan["multi"]
            assert plan["cardName"] in plan["multi"]
            assert plan["cardCode"] in plan["multi"]

    @allure.title("巡检计划时间字段保持可空结束时间顺序契约")
    def test_patrol_plan_times_keep_nullable_end_time_ordering_contract(self, auth_api, patrol_api, test_user):
        """校验巡检计划保持毫秒 beginTime，且 endTime 为空或不早于 beginTime。"""
        self._login(auth_api, test_user)

        for plan in self._plans_or_skip(patrol_api):
            assert isinstance(plan["beginTime"], int)
            assert plan["beginTime"] > 0
            assert plan["endTime"] is None or isinstance(plan["endTime"], int)
            if plan["endTime"] is not None:
                assert plan["endTime"] >= plan["beginTime"]

    @allure.title("巡检详情行保持父级 recordId 和顺序 seq 值")
    def test_patrol_plan_details_keep_parent_recordid_and_sequential_seq(self, auth_api, patrol_api, test_user):
        """校验嵌套巡检详情保持父级 recordId 契约和顺序递增的字符串 seq。"""
        self._login(auth_api, test_user)

        for plan in self._plans_or_skip(patrol_api)[:3]:
            details = plan["details"]
            if not details:
                continue

            expected_seq = [str(index) for index in range(len(details))]
            assert [detail["seq"] for detail in details] == expected_seq
            for detail in details:
                assert detail["recordId"] == plan["recordId"]
                assert isinstance(detail["presetCode"], int)
                assert detail["presetCode"] >= 0
