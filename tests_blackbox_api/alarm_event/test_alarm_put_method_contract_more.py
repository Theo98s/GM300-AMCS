# -*- coding: utf-8 -*-
"""报警记录接口的 PUT 方法异常契约测试。"""
from __future__ import annotations

import allure


@allure.feature("报警事件")
class TestAlarmPutMethodContractMore:
    """校验报警记录查询接口拒绝未约定的 PUT 方法。"""

    @staticmethod
    def _login(auth_api, test_user):
        """先建立登录会话，排除权限跳转对方法断言的干扰。"""
        response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert response.status_code == 200
        assert response.json()["status"] == 0

    @allure.title("报警记录接口使用 PUT 时返回方法不支持")
    def test_alarm_record_put_method_returns_405(
        self,
        auth_api,
        request_util,
        config,
        test_user,
    ):
        """校验错误方法不会执行报警记录查询，并返回明确的 405 响应。"""
        self._login(auth_api, test_user)

        response = request_util.send_request(
            "put",
            config["alarm"]["alarm_record_page_url"],
            json={},
        )

        assert response.status_code == 405
        assert "Request method 'PUT' not supported" in response.text
