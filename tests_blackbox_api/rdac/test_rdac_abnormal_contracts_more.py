# -*- coding: utf-8 -*-
"""AMCS RDAC 异常场景补充测试。"""
from __future__ import annotations

import allure


@allure.feature("基础数据-RDAC")
class TestRdacAbnormalContractsMore:
    """补充校验 RDAC 对非法站点参数的兜底行为。"""

    @staticmethod
    def _login(auth_api, test_user):
        """统一执行登录，保证异常站点查询在已登录状态下进行。"""
        response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert response.status_code == 200
        assert response.json()["status"] == 0

    @allure.title("RDAC 非法站点点位 JSON 返回空桶而不是报错")
    def test_rdac_invalid_station_item_query_returns_null_buckets(self, auth_api, rdac_api, test_user):
        """校验非法站点名查询点位 JSON 时，后端返回成功包裹但各类点位桶为空。"""
        self._login(auth_api, test_user)

        response = rdac_api.list_station_items("NO_SUCH_SUB_001", "104")
        assert response.status_code == 200

        body = response.json()
        assert body["status"] == 0
        assert body["message"] is None
        assert body["data"] == {
            "telemetryItems": None,
            "telesignalItems": None,
            "remoteControlItems": None,
            "remoteAdjustItems": None,
            "partialDischargeItems": None,
        }

    @allure.title("RDAC 非法站点点位页仍返回标准 HTML 壳")
    def test_rdac_invalid_station_page_still_returns_standard_html_shell(self, auth_api, rdac_api, test_user):
        """校验非法站点名打开点位页时，页面仍能返回标准 HTML 壳而不是 500。"""
        self._login(auth_api, test_user)

        response = rdac_api.get_station_items_page("NO_SUCH_SUB_001", "104")
        assert response.status_code == 200
        assert "text/html" in response.headers.get("Content-Type", "")
        assert "站点属性列表主页面" in response.text
        assert "var protocol = '104'" in response.text
