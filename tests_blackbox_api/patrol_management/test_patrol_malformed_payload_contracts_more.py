# -*- coding: utf-8 -*-
"""巡检管理接口的损坏 JSON 请求体契约测试。"""
from __future__ import annotations

import allure


@allure.feature("巡检管理")
class TestPatrolMalformedPayloadContractsMore:
    """校验巡检列表接口对无法解析的 JSON 请求体保持兼容。"""

    @staticmethod
    def _login(auth_api, test_user):
        """先完成登录，避免鉴权页面影响响应格式断言。"""
        response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert response.status_code == 200
        assert response.json()["status"] == 0

    @staticmethod
    def _assert_json_list(response):
        """统一校验巡检查询仍返回正常 JSON 列表。"""
        assert response.status_code == 200
        assert "application/json" in response.headers.get("Content-Type", "")
        assert isinstance(response.json(), list)

    @allure.title("巡检卡片接口收到损坏 JSON 时仍返回卡片列表")
    def test_patrol_card_list_malformed_json_keeps_list_contract(
        self,
        auth_api,
        request_util,
        config,
        test_user,
    ):
        """校验损坏 JSON 不会破坏巡检卡片的默认查询行为。"""
        self._login(auth_api, test_user)

        response = request_util.send_request(
            "post",
            config["patrol"]["patrol_card_list_url"],
            data="{bad-json",
            headers={"Content-Type": "application/json"},
        )

        self._assert_json_list(response)

    @allure.title("巡检计划接口收到损坏 JSON 时仍返回计划列表")
    def test_patrol_plan_list_malformed_json_keeps_list_contract(
        self,
        auth_api,
        request_util,
        config,
        test_user,
    ):
        """校验损坏 JSON 被兼容处理后，计划列表响应结构不变。"""
        self._login(auth_api, test_user)

        response = request_util.send_request(
            "post",
            config["patrol"]["patrol_plan_list_url"],
            data="{bad-json",
            headers={"Content-Type": "application/json"},
        )

        self._assert_json_list(response)
