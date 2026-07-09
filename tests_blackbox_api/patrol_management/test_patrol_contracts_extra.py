# -*- coding: utf-8 -*-
"""AMCS 巡检管理补充契约测试。"""
from __future__ import annotations

import allure
import pytest


@allure.feature("巡检管理")
class TestPatrolContractsExtra:
    """补充校验巡检计划与详情契约。"""

    @allure.title("巡检计划开始时间保持毫秒时间戳")
    def test_patrol_plan_begin_time_uses_millisecond_timestamp(self, auth_api, patrol_api, test_user):
        """校验巡检计划存在时，beginTime 仍为正整数毫秒时间戳。"""
        login_response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert login_response.json()["status"] == 0

        response = patrol_api.list_patrol_plans()
        body = response.json()
        if not body:
            pytest.skip("Current environment has no patrol plans.")

        first_plan = body[0]
        assert isinstance(first_plan["beginTime"], int)
        assert first_plan["beginTime"] >= 10**12
