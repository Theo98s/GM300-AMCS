# -*- coding: utf-8 -*-
"""监控点校验、保存和删除接口异常契约测试。"""
from __future__ import annotations

import allure


@allure.feature("基础数据")
class TestMonitorMutationAbnormalContractsMore:
    """补充监控点写入类接口在空请求、错误方法和错误请求体下的响应。"""

    @staticmethod
    def _login(auth_api, test_user):
        """每条用例先登录，保证异常请求进入监控点业务接口。"""
        login_response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert login_response.status_code == 200
        assert login_response.json()["status"] == 0

    @staticmethod
    def _assert_json_parse_error(response):
        """统一校验错误文本请求体触发 JSON 解析失败。"""
        assert response.status_code == 400
        assert "JSON parse error" in response.text
        assert "Unrecognized token 'not'" in response.text

    @staticmethod
    def _assert_method_not_supported(response, method: str):
        """统一校验错误 HTTP 方法返回 405。"""
        assert response.status_code == 405
        assert f"Request method '{method}' not supported" in response.text

    @allure.title("监控点保存前校验接口空 JSON 返回成功空消息")
    def test_monitor_validate_empty_json_returns_success(self, auth_api, database_api, test_user):
        """校验空对象只做格式校验时不会失败，返回成功但不携带数据。"""
        self._login(auth_api, test_user)

        response = database_api.validate_monitor({})

        assert response.status_code == 200
        body = response.json()
        assert body["status"] == 0
        assert body["message"] == ""
        assert body["data"] is None

    @allure.title("监控点保存前校验接口无请求体时返回 400")
    def test_monitor_validate_missing_body_returns_400(self, auth_api, request_util, config, test_user):
        """校验校验接口缺少 JSON 请求体时明确返回缺失请求体错误。"""
        self._login(auth_api, test_user)

        response = request_util.send_request(
            "post",
            config["database"]["monitor_validate_url"],
            json=None,
            allow_redirects=False,
        )

        assert response.status_code == 400
        assert "Required request body is missing" in response.text
        assert "validateMonitor" in response.text

    @allure.title("监控点保存前校验接口文本请求体时返回 JSON 解析错误")
    def test_monitor_validate_plain_text_body_returns_json_parse_error(
        self,
        auth_api,
        request_util,
        config,
        test_user,
    ):
        """校验校验接口接收非 JSON 文本时由框架层返回解析错误。"""
        self._login(auth_api, test_user)

        response = request_util.send_request(
            "post",
            config["database"]["monitor_validate_url"],
            data="not-json",
            headers={"Content-Type": "text/plain"},
            allow_redirects=False,
        )

        self._assert_json_parse_error(response)

    @allure.title("监控点保存前校验接口使用 GET 方法时返回 405")
    def test_monitor_validate_get_method_returns_405(self, auth_api, request_util, config, test_user):
        """校验监控点保存前校验只接受 POST 方法。"""
        self._login(auth_api, test_user)

        response = request_util.send_request(
            "get",
            config["database"]["monitor_validate_url"],
            allow_redirects=False,
        )

        self._assert_method_not_supported(response, "GET")

    @allure.title("监控点保存接口空 JSON 返回保存失败")
    def test_monitor_save_empty_json_returns_business_failure(self, auth_api, database_api, test_user):
        """校验空对象保存不会创建脏数据，而是返回保存失败。"""
        self._login(auth_api, test_user)

        response = database_api.save_or_update_monitor({})

        assert response.status_code == 200
        body = response.json()
        assert body["status"] == 1
        assert body["message"] == "保存监控点失败！"
        assert body["data"] is None

    @allure.title("监控点保存接口文本请求体时返回 JSON 解析错误")
    def test_monitor_save_plain_text_body_returns_json_parse_error(self, auth_api, request_util, config, test_user):
        """校验保存接口接收非 JSON 文本时不会进入业务保存流程。"""
        self._login(auth_api, test_user)

        response = request_util.send_request(
            "post",
            config["database"]["monitor_save_url"],
            data="not-json",
            headers={"Content-Type": "text/plain"},
            allow_redirects=False,
        )

        self._assert_json_parse_error(response)

    @allure.title("监控点保存接口使用 GET 方法时返回 405")
    def test_monitor_save_get_method_returns_405(self, auth_api, request_util, config, test_user):
        """校验监控点保存接口只接受 POST 方法。"""
        self._login(auth_api, test_user)

        response = request_util.send_request(
            "get",
            config["database"]["monitor_save_url"],
            allow_redirects=False,
        )

        self._assert_method_not_supported(response, "GET")

    @allure.title("监控点删除接口使用 GET 方法时返回 405")
    def test_monitor_delete_get_method_returns_405(self, auth_api, request_util, config, test_user):
        """校验监控点批量删除接口只接受 POST 方法。"""
        self._login(auth_api, test_user)

        response = request_util.send_request(
            "get",
            config["database"]["monitor_delete_url"],
            allow_redirects=False,
        )

        self._assert_method_not_supported(response, "GET")

    @allure.title("监控点删除接口文本请求体时返回 JSON 解析错误")
    def test_monitor_delete_plain_text_body_returns_json_parse_error(self, auth_api, request_util, config, test_user):
        """校验删除接口接收非 JSON 文本时不会进入删除流程。"""
        self._login(auth_api, test_user)

        response = request_util.send_request(
            "post",
            config["database"]["monitor_delete_url"],
            data="not-json",
            headers={"Content-Type": "text/plain"},
            allow_redirects=False,
        )

        self._assert_json_parse_error(response)
