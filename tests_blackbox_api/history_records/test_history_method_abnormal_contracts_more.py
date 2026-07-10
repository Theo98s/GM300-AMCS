# -*- coding: utf-8 -*-
"""历史记录接口异常请求方法契约测试。"""
from __future__ import annotations

import allure


@allure.feature("历史记录")
class TestHistoryMethodAbnormalContractsMore:
    """补充历史分页接口在错误方法、错误请求体和浮点分页参数下的响应。"""

    @staticmethod
    def _login(auth_api, test_user):
        """每条用例先登录，保证历史记录接口拥有有效会话。"""
        login_response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert login_response.status_code == 200
        assert login_response.json()["status"] == 0

    @staticmethod
    def _assert_history_page_response(response):
        """统一校验历史记录分页接口返回分页结构。"""
        assert response.status_code == 200
        assert "application/json" in response.headers.get("Content-Type", "")
        body = response.json()
        assert set(body.keys()) == {"total", "rows"}
        assert isinstance(body["total"], int)
        assert isinstance(body["rows"], list)

    @staticmethod
    def _assert_number_format_error(response, value: str):
        """统一校验分页参数转换失败的 400 错误。"""
        assert response.status_code == 400
        assert "NumberFormatException" in response.text
        assert f'For input string: "{value}"' in response.text

    @allure.title("历史分页接口使用 GET 方法时仍返回默认分页")
    def test_history_get_method_keeps_default_page_response(self, auth_api, request_util, config, test_user):
        """校验历史分页接口兼容 GET 方法，仍按默认条件返回分页数据。"""
        self._login(auth_api, test_user)

        response = request_util.send_request("get", config["history"]["monitor_link_history_url"])

        self._assert_history_page_response(response)

    @allure.title("历史分页接口接收文本请求体时仍返回默认分页")
    def test_history_plain_text_body_keeps_default_page_response(self, auth_api, request_util, config, test_user):
        """校验错误文本请求体不会导致历史分页接口返回服务端错误。"""
        self._login(auth_api, test_user)

        response = request_util.send_request(
            "post",
            config["history"]["monitor_link_history_url"],
            data="not-form",
            headers={"Content-Type": "text/plain"},
        )

        self._assert_history_page_response(response)

    @allure.title("历史分页接口接收 JSON 请求体时仍按默认分页处理")
    def test_history_json_body_is_ignored_and_keeps_default_page_response(
        self,
        auth_api,
        request_util,
        config,
        test_user,
    ):
        """校验历史分页接口当前读取表单参数，JSON 请求体不会改变默认分页结果。"""
        self._login(auth_api, test_user)

        default_body = request_util.send_request("post", config["history"]["monitor_link_history_url"]).json()
        json_body = request_util.send_request(
            "post",
            config["history"]["monitor_link_history_url"],
            json={"rows": 2},
        ).json()

        assert json_body["total"] == default_body["total"]
        assert len(json_body["rows"]) == len(default_body["rows"]) == 10
        assert json_body["rows"][0]["id"] == default_body["rows"][0]["id"]

    @allure.title("历史分页 rows 传入浮点文本时返回 400")
    def test_history_rows_float_text_returns_number_format_error(self, auth_api, history_api, test_user):
        """校验 rows=1.5 这类非整数文本会触发参数转换错误。"""
        self._login(auth_api, test_user)

        response = history_api.find_monitor_link_history({"rows": "1.5"})

        self._assert_number_format_error(response, "1.5")

    @allure.title("历史分页 page 传入浮点文本时返回 400")
    def test_history_page_float_text_returns_number_format_error(self, auth_api, history_api, test_user):
        """校验 page=1.5 这类非整数文本会触发参数转换错误。"""
        self._login(auth_api, test_user)

        response = history_api.find_monitor_link_history({"rows": 2, "page": "1.5"})

        self._assert_number_format_error(response, "1.5")
