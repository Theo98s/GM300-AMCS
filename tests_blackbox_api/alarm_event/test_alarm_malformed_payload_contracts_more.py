# -*- coding: utf-8 -*-
"""报警记录接口的损坏请求体异常契约测试。"""
from __future__ import annotations

import allure


@allure.feature("报警事件")
class TestAlarmMalformedPayloadContractsMore:
    """校验报警查询在收到无法解析的 JSON 时仍保持默认查询能力。"""

    @staticmethod
    def _login(auth_api, test_user):
        """先建立登录会话，确保断言针对报警业务接口。"""
        response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert response.status_code == 200
        assert response.json()["status"] == 0

    @allure.title("报警记录接口收到损坏 JSON 时仍返回默认记录列表")
    def test_alarm_record_malformed_json_keeps_list_contract(
        self,
        auth_api,
        request_util,
        config,
        test_user,
    ):
        """校验请求声明为 JSON 但内容损坏时，接口不会产生服务端异常。"""
        self._login(auth_api, test_user)

        response = request_util.send_request(
            "post",
            config["alarm"]["alarm_record_page_url"],
            data="{bad-json",
            headers={"Content-Type": "application/json"},
        )

        assert response.status_code == 200
        assert "application/json" in response.headers.get("Content-Type", "")
        assert isinstance(response.json(), list)
