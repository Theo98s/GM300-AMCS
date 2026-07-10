# -*- coding: utf-8 -*-
"""报警记录接口异常请求方法契约测试。"""
from __future__ import annotations

import allure


@allure.feature("报警事件")
class TestAlarmMethodAbnormalContractsMore:
    """补充报警记录接口在错误 HTTP 方法下的响应。"""

    @staticmethod
    def _login(auth_api, test_user):
        """每条用例先登录，避免未认证跳转影响方法断言。"""
        login_response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert login_response.status_code == 200
        assert login_response.json()["status"] == 0

    @allure.title("报警记录接口使用 GET 方法时返回 405")
    def test_alarm_record_get_method_returns_405(self, auth_api, request_util, config, test_user):
        """校验报警记录查询接口只支持 POST 业务查询。"""
        self._login(auth_api, test_user)

        response = request_util.send_request(
            "get",
            config["alarm"]["alarm_record_page_url"],
            allow_redirects=False,
        )

        assert response.status_code == 405
        assert "Request method 'GET' not supported" in response.text

    @allure.title("报警记录接口使用 OPTIONS 方法时返回空成功响应")
    def test_alarm_record_options_method_returns_empty_success(self, auth_api, request_util, config, test_user):
        """记录当前 OPTIONS 探测行为，便于发现跨域或方法探测响应变化。"""
        self._login(auth_api, test_user)

        response = request_util.send_request(
            "options",
            config["alarm"]["alarm_record_page_url"],
            allow_redirects=False,
        )

        assert response.status_code == 200
        assert response.content == b""
