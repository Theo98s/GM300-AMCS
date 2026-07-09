# -*- coding: utf-8 -*-
"""More AMCS RDAC station-list contract tests."""
from __future__ import annotations

import allure


@allure.feature("基础数据-RDAC")
class TestRdacStationContractsMore:
    """Extra checks for RDAC station list payloads."""

    @allure.title("RDAC 站点列表站点名保持唯一")
    def test_rdac_station_list_sub_names_are_unique(self, auth_api, rdac_api, test_user):
        """Verify the current RDAC station list keeps unique substation names."""
        login_response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert login_response.json()["status"] == 0

        body = rdac_api.list_stations().json()
        sub_names = [item["subName"] for item in body]
        assert len(sub_names) == len(set(sub_names))

    @allure.title("RDAC 站点列表协议字段保持非空")
    def test_rdac_station_list_protocol_names_are_non_empty(self, auth_api, rdac_api, test_user):
        """Verify every RDAC station entry keeps a non-empty protocol name."""
        login_response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert login_response.json()["status"] == 0

        body = rdac_api.list_stations().json()
        for item in body:
            assert isinstance(item["protocolName"], str)
            assert item["protocolName"]

