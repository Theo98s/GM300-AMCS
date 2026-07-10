# -*- coding: utf-8 -*-
"""报警事件异常参数、损坏请求体与方法边界测试。"""
from __future__ import annotations

import allure
import pytest


class TestAlarmAbnormalContractsMore:
    """补充报警记录查询在异常请求体下的兼容行为。"""

    @staticmethod
    def _login(auth_api, test_user):
        """每条用例先登录，避免把权限跳转误判为接口异常。"""
        login_response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert login_response.status_code == 200
        assert login_response.json()["status"] == 0

    @staticmethod
    def _assert_alarm_rows_response(response):
        """统一校验报警记录接口仍返回列表结构。"""
        assert response.status_code == 200
        assert "application/json" in response.headers.get("Content-Type", "")
        assert isinstance(response.json(), list)

    @allure.title("报警记录接口接收空 JSON 请求体时仍返回列表")
    def test_alarm_record_accepts_null_json_body(self, auth_api, request_util, config, test_user):
        """校验空 JSON 请求体不会导致接口报错，服务端会按默认条件查询。"""
        self._login(auth_api, test_user)

        response = request_util.send_request(
            "post",
            config["alarm"]["alarm_record_page_url"],
            json=None,
        )

        self._assert_alarm_rows_response(response)

    @allure.title("报警记录接口接收文本请求体时仍按默认条件返回")
    def test_alarm_record_ignores_plain_text_body(self, auth_api, request_util, config, test_user):
        """校验错误的文本请求体不会破坏报警记录默认查询能力。"""
        self._login(auth_api, test_user)

        response = request_util.send_request(
            "post",
            config["alarm"]["alarm_record_page_url"],
            data="not-json",
            headers={"Content-Type": "text/plain"},
        )

        self._assert_alarm_rows_response(response)

    @allure.title("报警记录接口接收非法分页参数时保持列表响应")
    def test_alarm_record_invalid_paging_params_keep_list_response(self, auth_api, alarm_api, test_user):
        """校验非法分页参数不会返回 500，接口仍保持列表结果契约。"""
        self._login(auth_api, test_user)

        response = alarm_api.get_alarm_record_page({"page": "bad", "rows": "bad"})

        self._assert_alarm_rows_response(response)

    @allure.title("报警记录接口接收无关筛选条件时不改变响应结构")
    def test_alarm_record_unknown_filter_keeps_row_shape(self, auth_api, alarm_api, test_user):
        """校验无关筛选字段会被兼容处理，已有数据行仍保持核心字段。"""
        self._login(auth_api, test_user)

        body = alarm_api.get_alarm_record_page({"unknownFilter": "NO_SUCH_VALUE"}).json()
        if not body:
            pytest.skip("当前环境没有报警记录，跳过行结构校验。")

        first_row = body[0]
        assert set(first_row.keys()) >= {"id", "alarmDt", "warnContent", "status", "equipId"}


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
