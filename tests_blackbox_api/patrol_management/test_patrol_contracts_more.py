# -*- coding: utf-8 -*-
"""More AMCS patrol-management contract tests."""
from __future__ import annotations

import numbers

import allure
import pytest


@allure.feature("Patrol Management")
class TestPatrolContractsMore:
    """Extra contract checks for patrol plans and detail rows."""

    @staticmethod
    def _login(auth_api, test_user):
        """Log in once per test and assert the session is ready."""
        login_response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert login_response.status_code == 200
        assert login_response.json()["status"] == 0

    @staticmethod
    def _plans_or_skip(patrol_api):
        """Return patrol plans or skip when the environment currently has none."""
        plans = patrol_api.list_patrol_plans().json()
        if not plans:
            pytest.skip("Current environment has no patrol plans.")
        return plans

    @allure.title("Patrol plans keep execution flag and state contracts")
    def test_patrol_plan_execution_flags_keep_expected_types(self, auth_api, patrol_api, test_user):
        """Verify the first patrol plan keeps string-based execution states and boolean control flags."""
        self._login(auth_api, test_user)

        first_plan = self._plans_or_skip(patrol_api)[0]
        assert isinstance(first_plan["centerType"], str) and first_plan["centerType"]
        assert isinstance(first_plan["executeType"], str) and first_plan["executeType"]
        assert isinstance(first_plan["executeState"], str) and first_plan["executeState"]
        assert isinstance(first_plan["canBeStarted"], bool)
        assert isinstance(first_plan["movable"], bool)
        assert isinstance(first_plan["receivedFirstPointResult"], bool)

    @allure.title("Patrol detail rows keep nullable result field contracts")
    def test_patrol_plan_detail_result_fields_keep_nullable_text_contracts(self, auth_api, patrol_api, test_user):
        """Verify the first patrol detail keeps nullable result fields and numeric temperature contracts."""
        self._login(auth_api, test_user)

        first_plan = self._plans_or_skip(patrol_api)[0]
        if not first_plan["details"]:
            pytest.skip("Current environment has no patrol plan details.")

        first_detail = first_plan["details"][0]
        assert first_detail["result"] is None or isinstance(first_detail["result"], str)
        assert isinstance(first_detail["valueResult"], str)
        assert isinstance(first_detail["standResult"], str)
        assert isinstance(first_detail["valueStatus"], str)
        assert first_detail["pointTemperature"] is None or isinstance(first_detail["pointTemperature"], numbers.Real)
        assert isinstance(first_detail["ext"], dict)
