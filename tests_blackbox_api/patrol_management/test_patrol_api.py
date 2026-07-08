# -*- coding: utf-8 -*-
"""AMCS 巡检管理接口测试。"""
from __future__ import annotations

import allure
import pytest


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

    @allure.title("巡检计划列表项包含计划基础字段")
    def test_patrol_plan_list_items_contain_plan_fields(self, auth_api, patrol_api, test_user):
        """有巡检计划数据时校验首条记录包含计划名称、所亭和时间字段。"""
        login_response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert login_response.json()["status"] == 0

        response = patrol_api.list_patrol_plans()
        body = response.json()
        if not body:
            pytest.skip("当前环境没有巡检计划，跳过计划字段校验")

        first_plan = body[0]
        assert set(first_plan.keys()) >= {"cardName", "subName", "beginTime", "canBeStarted", "details", "weeks"}
        assert isinstance(first_plan["beginTime"], int)
        assert isinstance(first_plan["canBeStarted"], bool)
        assert isinstance(first_plan["details"], list)

    @allure.title("巡检计划详情项包含点位与停留时长字段")
    def test_patrol_plan_details_contain_point_fields(self, auth_api, patrol_api, test_user):
        """有巡检计划数据时校验详情点位包含监控点名称、预置位和停留时长字段。"""
        login_response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert login_response.json()["status"] == 0

        response = patrol_api.list_patrol_plans()
        body = response.json()
        if not body or not body[0]["details"]:
            pytest.skip("当前环境没有巡检计划详情，跳过详情字段校验")

        first_detail = body[0]["details"][0]
        assert set(first_detail.keys()) >= {"monitorName", "presetName", "residenceTime", "pictureCount", "seq"}
        assert first_detail["monitorName"]
        assert first_detail["presetName"]
        assert first_detail["residenceTime"] >= 0
        assert first_detail["pictureCount"] >= 0

    @allure.title("巡检计划详情扩展字段保持字典结构")
    def test_patrol_plan_details_ext_field_is_dict(self, auth_api, patrol_api, test_user):
        """有巡检计划数据时校验详情 ext 字段仍是对象结构。"""
        login_response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert login_response.json()["status"] == 0

        response = patrol_api.list_patrol_plans()
        body = response.json()
        if not body or not body[0]["details"]:
            pytest.skip("当前环境没有巡检计划详情，跳过 ext 字段校验")

        first_detail = body[0]["details"][0]
        assert isinstance(first_detail["ext"], dict)
        assert isinstance(first_detail["seq"], str)

    @allure.title("巡检卡片列表主键唯一且名称非空")
    def test_patrol_card_ids_are_unique_and_names_non_empty(self, auth_api, patrol_api, test_user):
        """校验巡检卡片列表中的卡片主键唯一，且名称字段非空。"""
        login_response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert login_response.json()["status"] == 0

        response = patrol_api.list_patrol_cards()
        body = response.json()

        card_ids = [item["id"] for item in body]
        card_names = [item["text"] for item in body]
        assert len(card_ids) == len(set(card_ids))
        assert all(card_names)
