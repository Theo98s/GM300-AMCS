# -*- coding: utf-8 -*-
"""Additional AMCS history consistency contract tests."""
from __future__ import annotations

import re

import allure


@allure.feature("History Records")
class TestHistoryConsistencyContractsExtra:
    """Extra consistency checks for linkage-history pages."""

    @staticmethod
    def _login(auth_api, test_user):
        """Log in once per test and assert the session is ready."""
        login_response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert login_response.status_code == 200
        assert login_response.json()["status"] == 0

    @allure.title("History first page rows keep target substation name")
    def test_monitor_link_history_first_page_keeps_target_substation_name(
        self,
        auth_api,
        history_api,
        test_user,
        target_config,
    ):
        """Verify the first history page rows still belong to the configured target substation."""
        self._login(auth_api, test_user)

        rows = history_api.find_monitor_link_history({"rows": 5}).json()["rows"]
        assert len(rows) >= 1

        expected_substation = target_config.get("substation_name")
        assert expected_substation
        assert {row["subId"] for row in rows} == {expected_substation}

    @allure.title("History first page rows keep non-empty identity and alarm-data codes")
    def test_monitor_link_history_first_page_keeps_identity_and_alarmdata_codes(
        self,
        auth_api,
        history_api,
        test_user,
    ):
        """Verify the first history page rows keep stable identity fields and digit-string alarmdataType values."""
        self._login(auth_api, test_user)

        rows = history_api.find_monitor_link_history({"rows": 5}).json()["rows"]
        assert len(rows) >= 1

        for row in rows:
            assert isinstance(row["id"], str) and row["id"]
            assert isinstance(row["equipId"], str) and row["equipId"]
            assert isinstance(row["equipName"], str) and row["equipName"]
            assert re.fullmatch(r"\d+", row["alarmdataType"])
