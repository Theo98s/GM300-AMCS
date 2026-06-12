# -*- coding: utf-8 -*-
"""AMCS RDAC 接口测试。"""
from __future__ import annotations

import allure


@allure.feature("基础数据-RDAC")
class TestRdacApi:
    """RDAC 站点和点位配置查询用例。"""

    TARGET_SUB_NAME = "青花牵引变电所"
    TARGET_PROTOCOL = "104"

    @allure.title("RDAC 站点列表包含目标站点")
    def test_rdac_station_list_contains_target_station(self, auth_api, rdac_api, test_user):
        """校验 RDAC 站点列表包含当前页面默认站点。

        这里使用当前环境里稳定存在的青花牵引变电所，避免对临时数据产生依赖。
        站点注册状态会随环境变化，因此只校验状态值在系统允许范围内。
        """
        login_response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert login_response.json()["status"] == 0

        response = rdac_api.list_stations()
        assert response.status_code == 200

        body = response.json()
        assert isinstance(body, list)
        matched = next(
            item for item in body
            if item["subName"] == self.TARGET_SUB_NAME and item["protocolName"] == self.TARGET_PROTOCOL
        )
        assert matched["status"] in {"REGISTERED", "UNREGISTERED"}

    @allure.title("RDAC 点位页面 HTML 包含当前站点和协议")
    def test_rdac_station_items_page_contains_context(self, auth_api, rdac_api, test_user):
        """校验站点点位页面能按站点和协议正常打开。"""
        login_response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert login_response.json()["status"] == 0

        response = rdac_api.get_station_items_page(self.TARGET_SUB_NAME, self.TARGET_PROTOCOL)
        assert response.status_code == 200
        assert "站点属性列表主页面" in response.text
        assert self.TARGET_SUB_NAME in response.text
        assert f"var protocol = '{self.TARGET_PROTOCOL}'" in response.text

    @allure.title("RDAC 点位列表接口返回标准结构")
    def test_rdac_station_item_list_returns_standard_keys(self, auth_api, rdac_api, test_user):
        """校验 RDAC 点位配置 JSON 结构完整。"""
        login_response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert login_response.json()["status"] == 0

        response = rdac_api.list_station_items(self.TARGET_SUB_NAME, self.TARGET_PROTOCOL)
        assert response.status_code == 200

        body = response.json()
        assert body["status"] == 0
        assert set(body["data"].keys()) == {
            "telemetryItems",
            "telesignalItems",
            "remoteControlItems",
            "remoteAdjustItems",
            "partialDischargeItems",
        }
