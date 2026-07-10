# -*- coding: utf-8 -*-
"""历史趋势接口异常参数与方法边界测试。"""
from __future__ import annotations

import allure


@allure.feature("历史趋势")
class TestHistoryTrendAbnormal:
    """覆盖错误方法、无效设备、空条件和损坏 JSON 场景。"""

    @staticmethod
    def _login(auth_api, test_user):
        """先建立登录会话，排除权限跳转影响。"""
        response = auth_api.login(test_user["username"], test_user["password"])
        assert response.status_code == 200
        assert response.json()["status"] == 0

    @allure.title("历史趋势设备树使用 POST 时返回方法不支持")
    def test_history_trend_tree_post_returns_405(self, auth_api, request_util, config, test_user):
        """校验设备树严格使用 GET 方法。"""
        self._login(auth_api, test_user)

        response = request_util.send_request("post", config["history_trend"]["tree_url"])

        assert response.status_code == 405
        assert "Request method 'POST' not supported" in response.text

    @allure.title("不存在的设备趋势页面仍返回标准页面骨架")
    def test_history_trend_unknown_equipment_keeps_page_shell(
        self,
        auth_api,
        history_trend_api,
        test_user,
    ):
        """校验无效设备标识不会导致趋势页面服务端异常。"""
        self._login(auth_api, test_user)

        response = history_trend_api.get_trend_page("NO_SUCH_EQUIPMENT_ID", "NO_SUCH")

        assert response.status_code == 200
        assert "<title>历史趋势</title>" in response.text
        assert "NO_SUCH_EQUIPMENT_ID" in response.text

    @allure.title("不存在的设备返回空趋势属性列表")
    def test_history_trend_unknown_equipment_returns_empty_attributes(
        self,
        auth_api,
        history_trend_api,
        test_user,
    ):
        """校验无效设备不会返回其他设备的监控属性。"""
        self._login(auth_api, test_user)

        body = history_trend_api.list_attributes("NO_SUCH_EQUIPMENT_ID").json()

        assert body == {"status": 0, "message": "操作成功!", "data": []}

    @allure.title("趋势数据接口收到损坏 JSON 时返回解析错误")
    def test_history_trend_data_rejects_malformed_json(
        self,
        auth_api,
        request_util,
        config,
        test_user,
    ):
        """校验无法解析的趋势查询请求体被明确拒绝。"""
        self._login(auth_api, test_user)

        response = request_util.send_request(
            "post",
            config["history_trend"]["condition_data_url"],
            data="{bad-json",
            headers={"Content-Type": "application/json"},
        )

        assert response.status_code == 400
        assert "JSON parse error" in response.text
        assert "JsonParseException" in response.text

    @allure.title("趋势数据接口空条件返回可识别查询异常")
    def test_history_trend_empty_condition_returns_query_error(
        self,
        auth_api,
        history_trend_api,
        test_user,
    ):
        """记录空监控点条件当前返回多结果查询异常的服务行为。"""
        self._login(auth_api, test_user)

        response = history_trend_api.query_condition_data({})

        assert response.status_code == 200
        assert "TooManyResultsException" in response.text

    @allure.title("历史趋势设备树使用 OPTIONS 时返回空成功响应")
    def test_history_trend_tree_options_returns_empty_success(
        self,
        auth_api,
        request_util,
        config,
        test_user,
    ):
        """校验设备树预检请求不会返回业务节点。"""
        self._login(auth_api, test_user)

        response = request_util.send_request("options", config["history_trend"]["tree_url"])

        assert response.status_code == 200
        assert response.content == b""

    @allure.title("趋势数据接口使用 GET 时返回方法不支持")
    def test_history_trend_data_get_returns_405(
        self,
        auth_api,
        request_util,
        config,
        test_user,
    ):
        """校验时序数据查询严格要求 POST 请求体。"""
        self._login(auth_api, test_user)

        response = request_util.send_request(
            "get",
            config["history_trend"]["condition_data_url"],
        )

        assert response.status_code == 405
        assert "Request method 'GET' not supported" in response.text
