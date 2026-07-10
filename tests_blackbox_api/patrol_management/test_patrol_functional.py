# -*- coding: utf-8 -*-
"""巡检卡片与计划跨接口功能流程测试。"""
from __future__ import annotations

import pytest
import allure


class TestPatrolFunctionalFlowsMore:
    """补充覆盖巡检卡片、计划和详情之间的串联功能流。"""

    @staticmethod
    def _login(auth_api, test_user):
        """统一执行登录，保证巡检卡片和计划查询复用同一会话。"""
        response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert response.status_code == 200
        assert response.json()["status"] == 0

    @staticmethod
    def _plans_or_skip(patrol_api) -> list[dict]:
        """返回巡检计划；如果当前环境没有计划，则跳过计划相关功能流。"""
        plans = patrol_api.list_patrol_plans().json()
        if not plans:
            pytest.skip("当前环境没有巡检计划，跳过巡检计划功能流校验。")
        return plans

    @staticmethod
    def _first_detail_or_skip(plan: dict) -> dict:
        """返回首个巡检点位详情；如果当前计划没有详情，则跳过明细相关校验。"""
        details = plan["details"]
        if not details:
            pytest.skip("当前巡检计划没有点位详情，跳过详情功能流校验。")
        return details[0]

    @allure.title("同一登录会话可连续加载巡检卡片和巡检计划")
    def test_single_login_session_can_load_patrol_cards_and_plans(
        self,
        auth_api,
        patrol_api,
        test_user,
    ):
        """登录一次后，连续访问巡检卡片列表和巡检计划列表。"""
        self._login(auth_api, test_user)

        card_rows = patrol_api.list_patrol_cards().json()
        plan_rows = patrol_api.list_patrol_plans().json()

        assert isinstance(card_rows, list)
        assert len(card_rows) > 0
        assert isinstance(plan_rows, list)

    @allure.title("巡检计划中的卡片名称可在巡检卡片列表中回查到")
    def test_patrol_plan_card_name_can_be_resolved_from_patrol_card_list(
        self,
        auth_api,
        patrol_api,
        test_user,
    ):
        """如果当前环境存在巡检计划，则校验计划关联的卡片名称能在卡片列表中找到。"""
        self._login(auth_api, test_user)

        card_rows = patrol_api.list_patrol_cards().json()
        plan_rows = self._plans_or_skip(patrol_api)
        card_names = {row["text"] for row in card_rows}
        first_plan = plan_rows[0]

        assert first_plan["cardName"] in card_names
        assert first_plan["subName"]
        assert isinstance(first_plan["canBeStarted"], bool)

    @allure.title("巡检计划详情可在同一会话内完成明细初始化")
    def test_patrol_plan_detail_can_bootstrap_in_same_session(
        self,
        auth_api,
        patrol_api,
        test_user,
    ):
        """如果当前环境存在巡检详情，则校验首个点位详情可直接用于页面初始化。"""
        self._login(auth_api, test_user)

        first_plan = self._plans_or_skip(patrol_api)[0]
        first_detail = self._first_detail_or_skip(first_plan)

        assert first_plan["cardName"]
        assert isinstance(first_plan["details"], list)
        assert first_detail["monitorName"]
        assert isinstance(first_detail["residenceTime"], int)
        assert isinstance(first_detail["pictureCount"], int)
        assert isinstance(first_detail["seq"], str)
        assert isinstance(first_detail["ext"], dict)
