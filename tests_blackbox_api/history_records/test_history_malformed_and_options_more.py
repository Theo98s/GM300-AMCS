# -*- coding: utf-8 -*-
"""历史记录接口的损坏请求体和预检请求契约测试。"""
from __future__ import annotations

import allure


@allure.feature("历史记录")
class TestHistoryMalformedAndOptionsMore:
    """校验历史记录查询收到损坏 JSON 和 OPTIONS 请求时的响应。"""

    @staticmethod
    def _login(auth_api, test_user):
        """先建立登录会话，确保请求命中历史记录接口。"""
        response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert response.status_code == 200
        assert response.json()["status"] == 0

    @allure.title("历史记录接口收到损坏 JSON 时仍返回默认分页")
    def test_history_malformed_json_keeps_default_page_contract(
        self,
        auth_api,
        request_util,
        config,
        test_user,
    ):
        """校验损坏 JSON 被忽略后，历史查询仍保持标准分页结构。"""
        self._login(auth_api, test_user)

        response = request_util.send_request(
            "post",
            config["history"]["monitor_link_history_url"],
            data="{bad-json",
            headers={"Content-Type": "application/json"},
        )

        assert response.status_code == 200
        assert "application/json" in response.headers.get("Content-Type", "")
        body = response.json()
        assert isinstance(body["total"], int)
        assert isinstance(body["rows"], list)

    @allure.title("历史记录接口使用 OPTIONS 时返回空成功响应")
    def test_history_options_method_returns_empty_success(
        self,
        auth_api,
        request_util,
        config,
        test_user,
    ):
        """校验历史查询预检请求不会执行分页查询或返回历史数据。"""
        self._login(auth_api, test_user)

        response = request_util.send_request(
            "options",
            config["history"]["monitor_link_history_url"],
        )

        assert response.status_code == 200
        assert response.content == b""
