# -*- coding: utf-8 -*-
"""AMCS RDAC 站点列表更多契约测试。"""
from __future__ import annotations

import allure


@allure.feature("基础数据-RDAC")
class TestRdacStationContractsMore:
    """补充校验 RDAC 站点列表返回结构。"""

    @allure.title("RDAC 站点列表站点名保持唯一")
    def test_rdac_station_list_sub_names_are_unique(self, auth_api, rdac_api, test_user):
        """校验当前 RDAC 站点列表中的所亭名称保持唯一。"""
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
        """校验每条 RDAC 站点记录都保留非空协议名称。"""
        login_response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert login_response.json()["status"] == 0

        body = rdac_api.list_stations().json()
        for item in body:
            assert isinstance(item["protocolName"], str)
            assert item["protocolName"]
