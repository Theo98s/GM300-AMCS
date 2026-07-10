# -*- coding: utf-8 -*-
"""巡检管理接口异常访问契约测试。"""
from __future__ import annotations

import allure
import pytest


@allure.feature("巡检管理")
class TestPatrolAbnormalContractsMore:
    """补充巡检卡片和巡检计划在异常请求方式下的稳定性校验。"""

    @staticmethod
    def _login(auth_api, test_user):
        """每条用例先登录，确保校验的是业务接口本身。"""
        login_response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert login_response.status_code == 200
        assert login_response.json()["status"] == 0

    @staticmethod
    def _assert_json_list(response):
        """统一校验接口返回 JSON 列表。"""
        assert response.status_code == 200
        assert "application/json" in response.headers.get("Content-Type", "")
        assert isinstance(response.json(), list)

    @allure.title("巡检卡片接口使用 GET 访问时仍返回列表")
    def test_patrol_card_list_get_method_keeps_list_contract(self, auth_api, request_util, config, test_user):
        """校验巡检卡片接口对 GET 方式保持兼容，不因请求方式变化失败。"""
        self._login(auth_api, test_user)

        response = request_util.send_request("get", config["patrol"]["patrol_card_list_url"])

        self._assert_json_list(response)

    @allure.title("巡检卡片接口接收无关表单字段时仍返回原列表结构")
    def test_patrol_card_list_ignores_unknown_form_fields(self, auth_api, request_util, config, test_user):
        """校验无关表单字段不会影响巡检卡片列表基础契约。"""
        self._login(auth_api, test_user)

        response = request_util.send_request(
            "post",
            config["patrol"]["patrol_card_list_url"],
            data={"unexpected": "NO_SUCH_VALUE"},
        )

        self._assert_json_list(response)
        if not response.json():
            pytest.skip("当前环境没有巡检卡片，跳过字段结构校验。")
        assert set(response.json()[0].keys()) >= {"id", "text", "equipamount", "pointamount"}

    @allure.title("巡检计划接口使用 POST 附带无关 JSON 时仍返回计划列表")
    def test_patrol_plan_list_post_unknown_json_keeps_list_contract(
        self,
        auth_api,
        request_util,
        config,
        test_user,
    ):
        """校验巡检计划接口能兼容额外 JSON 参数，避免前端扩展字段导致接口失败。"""
        self._login(auth_api, test_user)

        response = request_util.send_request(
            "post",
            config["patrol"]["patrol_plan_list_url"],
            json={"unexpected": "NO_SUCH_VALUE"},
        )

        self._assert_json_list(response)

    @allure.title("巡检计划接口接收错误文本请求体时仍保持列表响应")
    def test_patrol_plan_list_plain_text_body_keeps_list_response(
        self,
        auth_api,
        request_util,
        config,
        test_user,
    ):
        """校验错误文本请求体不会让巡检计划列表接口返回服务端错误。"""
        self._login(auth_api, test_user)

        response = request_util.send_request(
            "post",
            config["patrol"]["patrol_plan_list_url"],
            data="not-json",
            headers={"Content-Type": "text/plain"},
        )

        self._assert_json_list(response)
