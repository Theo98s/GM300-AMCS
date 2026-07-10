# -*- coding: utf-8 -*-
"""巡检管理异常请求体、方法与参数兼容测试。"""
from __future__ import annotations

import allure
import pytest


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


class TestPatrolMethodAbnormalContractsMore:
    """补充巡检卡片和巡检计划接口在 OPTIONS 与无关参数下的响应。"""

    @staticmethod
    def _login(auth_api, test_user):
        """每条用例先登录，确保请求进入巡检业务接口。"""
        login_response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert login_response.status_code == 200
        assert login_response.json()["status"] == 0

    @staticmethod
    def _assert_empty_options_response(response):
        """统一校验 OPTIONS 探测返回空成功响应。"""
        assert response.status_code == 200
        assert response.content == b""

    @allure.title("巡检卡片接口使用 OPTIONS 方法时返回空成功响应")
    def test_patrol_card_options_method_returns_empty_success(self, auth_api, request_util, config, test_user):
        """记录巡检卡片接口当前 OPTIONS 探测行为。"""
        self._login(auth_api, test_user)

        response = request_util.send_request(
            "options",
            config["patrol"]["patrol_card_list_url"],
            allow_redirects=False,
        )

        self._assert_empty_options_response(response)

    @allure.title("巡检计划接口使用 OPTIONS 方法时返回空成功响应")
    def test_patrol_plan_options_method_returns_empty_success(self, auth_api, request_util, config, test_user):
        """记录巡检计划接口当前 OPTIONS 探测行为。"""
        self._login(auth_api, test_user)

        response = request_util.send_request(
            "options",
            config["patrol"]["patrol_plan_list_url"],
            allow_redirects=False,
        )

        self._assert_empty_options_response(response)

    @allure.title("巡检计划接口接收无关 GET 参数时仍返回列表")
    def test_patrol_plan_get_unknown_param_keeps_list_response(self, auth_api, request_util, config, test_user):
        """校验无关查询参数不会影响巡检计划列表基础结构。"""
        self._login(auth_api, test_user)

        response = request_util.send_request(
            "get",
            config["patrol"]["patrol_plan_list_url"],
            params={"unexpected": "NO_SUCH_VALUE"},
        )

        assert response.status_code == 200
        assert "application/json" in response.headers.get("Content-Type", "")
        assert isinstance(response.json(), list)


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
