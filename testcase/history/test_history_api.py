# -*- coding: utf-8 -*-
"""AMCS 历史记录接口测试。"""
from __future__ import annotations

import allure


@allure.feature("历史记录")
class TestHistoryApi:
    """联动历史查询 smoke 用例。"""

    @allure.title("联动历史分页接口返回总数与列表")
    def test_monitor_link_history_returns_total_and_rows(self, auth_api, history_api, test_user):
        """校验联动历史分页结构完整。"""
        login_response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert login_response.json()["status"] == 0

        response = history_api.find_monitor_link_history()
        assert response.status_code == 200

        body = response.json()
        assert isinstance(body["total"], int)
        assert isinstance(body["rows"], list)
        assert body["total"] >= len(body["rows"])

    @allure.title("联动历史首条记录包含关键业务字段")
    def test_monitor_link_history_first_row_contains_expected_fields(self, auth_api, history_api, test_user):
        """校验联动历史记录包含站点、联动描述和状态等关键字段。"""
        login_response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert login_response.json()["status"] == 0

        response = history_api.find_monitor_link_history()
        body = response.json()
        assert len(body["rows"]) > 0

        first_row = body["rows"][0]
        assert set(first_row.keys()) >= {
            "subId",
            "equipName",
            "alarmType",
            "linkage",
            "description",
            "status",
        }
        assert first_row["subId"] == "青花牵引变电所"
