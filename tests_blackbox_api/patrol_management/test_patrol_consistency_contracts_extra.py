# -*- coding: utf-8 -*-
"""Additional AMCS patrol consistency contract tests."""
from __future__ import annotations

import allure
import pytest


@allure.feature("Patrol Management")
class TestPatrolConsistencyContractsExtra:
    """Extra consistency checks for patrol-plan rows and nested details."""

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

    @allure.title("Patrol plan multi field keeps card name and code alignment")
    def test_patrol_plan_multi_field_keeps_card_name_and_code_alignment(self, auth_api, patrol_api, test_user):
        """Verify each patrol plan keeps its card name and card code embedded in the multi field."""
        self._login(auth_api, test_user)

        for plan in self._plans_or_skip(patrol_api):
            assert isinstance(plan["multi"], str) and plan["multi"]
            assert plan["cardName"] in plan["multi"]
            assert plan["cardCode"] in plan["multi"]

    @allure.title("Patrol plan times keep nullable end-time ordering contract")
    def test_patrol_plan_times_keep_nullable_end_time_ordering_contract(self, auth_api, patrol_api, test_user):
        """Verify patrol plans keep millisecond begin times and optional end times that do not precede beginTime."""
        self._login(auth_api, test_user)

        for plan in self._plans_or_skip(patrol_api):
            assert isinstance(plan["beginTime"], int)
            assert plan["beginTime"] > 0
            assert plan["endTime"] is None or isinstance(plan["endTime"], int)
            if plan["endTime"] is not None:
                assert plan["endTime"] >= plan["beginTime"]

    @allure.title("Patrol detail rows keep parent recordId and sequential seq values")
    def test_patrol_plan_details_keep_parent_recordid_and_sequential_seq(self, auth_api, patrol_api, test_user):
        """Verify nested patrol details keep the parent recordId contract and sequential string seq values."""
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
