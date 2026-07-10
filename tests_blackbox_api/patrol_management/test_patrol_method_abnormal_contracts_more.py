# -*- coding: utf-8 -*-
"""巡检管理接口异常请求方法契约测试。"""
from __future__ import annotations

import allure


@allure.feature("巡检管理")
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
