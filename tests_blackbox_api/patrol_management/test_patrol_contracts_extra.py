# -*- coding: utf-8 -*-
"""Additional AMCS patrol-management contract tests."""
from __future__ import annotations

import allure
import pytest


@allure.feature("巡检管理")
class TestPatrolContractsExtra:
    """Extra contract checks for patrol plans and details."""

    @allure.title("巡检计划开始时间保持毫秒时间戳")
    def test_patrol_plan_begin_time_uses_millisecond_timestamp(self, auth_api, patrol_api, test_user):
        """Verify beginTime stays a positive millisecond timestamp when patrol plans exist."""
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
