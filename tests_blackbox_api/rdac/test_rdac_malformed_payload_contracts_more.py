# -*- coding: utf-8 -*-
"""RDAC 接口的损坏 JSON 请求体异常契约测试。"""
from __future__ import annotations

import allure


@allure.feature("RDAC")
class TestRdacMalformedPayloadContractsMore:
    """校验遥信点查询接口对无法解析 JSON 的错误响应。"""

    @staticmethod
    def _login(auth_api, test_user):
        """先建立登录会话，排除权限跳转对异常响应的干扰。"""
        response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert response.status_code == 200
        assert response.json()["status"] == 0

    @allure.title("RDAC 点表接口收到损坏 JSON 时返回解析错误")
    def test_rdac_item_list_malformed_json_returns_parse_error(
        self,
        auth_api,
        request_util,
        config,
        test_user,
    ):
        """校验损坏 JSON 被明确拒绝，并保留可定位问题的解析错误信息。"""
        self._login(auth_api, test_user)

        response = request_util.send_request(
            "post",
            config["rdac"]["station_item_list_url"],
            data="{bad-json",
            headers={"Content-Type": "application/json"},
        )

        assert response.status_code == 400
        assert "JSON parse error" in response.text
        assert "JsonParseException" in response.text
