# -*- coding: utf-8 -*-
"""巡检管理接口的异常请求体兼容性测试。"""
from __future__ import annotations

import allure


@allure.feature("巡检管理")
class TestPatrolPayloadAbnormalContractsMore:
    """校验巡检卡片和计划接口对非预期请求体的稳定响应。"""

    @staticmethod
    def _login(auth_api, test_user):
        """每条用例先建立登录会话，排除鉴权跳转的干扰。"""
        response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert response.status_code == 200
        assert response.json()["status"] == 0

    @staticmethod
    def _assert_json_list(response):
        """统一校验接口正常退化后仍返回 JSON 列表。"""
        assert response.status_code == 200
        assert "application/json" in response.headers.get("Content-Type", "")
        assert isinstance(response.json(), list)

    @allure.title("巡检卡片接口接收无关 JSON 请求体时仍返回列表")
    def test_patrol_card_list_ignores_unknown_json_body(
        self,
        auth_api,
        request_util,
        config,
        test_user,
    ):
        """校验巡检卡片列表不会因前端额外 JSON 字段而报错。"""
        self._login(auth_api, test_user)

        response = request_util.send_request(
            "post",
            config["patrol"]["patrol_card_list_url"],
            json={"unexpected": "NO_SUCH_VALUE"},
        )

        self._assert_json_list(response)

    @allure.title("巡检计划接口使用 GET 并附带文本请求体时仍返回列表")
    def test_patrol_plan_get_with_plain_text_body_keeps_list_contract(
        self,
        auth_api,
        request_util,
        config,
        test_user,
    ):
        """记录计划列表对 GET 文本请求体的兼容行为，防止改造后出现 500 错误。"""
        self._login(auth_api, test_user)

        response = request_util.send_request(
            "get",
            config["patrol"]["patrol_plan_list_url"],
            data="not-json",
            headers={"Content-Type": "text/plain"},
        )

        self._assert_json_list(response)
