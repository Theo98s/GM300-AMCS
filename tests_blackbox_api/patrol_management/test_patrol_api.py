# -*- coding: utf-8 -*-
"""AMCS 巡检管理接口测试。"""
from __future__ import annotations

import allure


@allure.feature("巡检管理")
class TestPatrolApi:
    """巡检卡片和巡检计划查询用例。"""

    @allure.title("巡检卡片列表可正常返回")
    def test_patrol_card_list_returns_cards(self, auth_api, patrol_api, test_user):
        """校验巡检卡片列表至少能返回一条卡片数据。"""
        login_response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert login_response.json()["status"] == 0

        response = patrol_api.list_patrol_cards()
        assert response.status_code == 200

        body = response.json()
        assert isinstance(body, list)
        assert len(body) > 0
        first_item = body[0]
        assert set(first_item.keys()) >= {"id", "text", "equipamount", "pointamount"}

    @allure.title("巡检卡片列表数量字段为非负整数")
    def test_patrol_card_list_count_fields_are_non_negative(self, auth_api, patrol_api, test_user):
        """校验巡检卡片中的设备数和点位数格式正确。"""
        login_response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert login_response.json()["status"] == 0

        response = patrol_api.list_patrol_cards()
        body = response.json()

        for item in body:
            assert isinstance(item["equipamount"], int)
            assert isinstance(item["pointamount"], int)
            assert item["equipamount"] >= 0
            assert item["pointamount"] >= 0

    @allure.title("巡检计划列表接口可访问")
    def test_patrol_plan_list_accessible(self, auth_api, patrol_api, test_user):
        """校验巡检计划列表接口可正常访问，即使当前没有计划数据。"""
        login_response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert login_response.json()["status"] == 0

        response = patrol_api.list_patrol_plans()
        assert response.status_code == 200

        body = response.json()
        assert isinstance(body, list)
