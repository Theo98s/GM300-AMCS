# -*- coding: utf-8 -*-
"""历史记录异常分页、损坏请求体与方法边界测试。"""
from __future__ import annotations

import allure


class TestHistoryAbnormalContractsMore:
    """补充校验历史分页接口对异常 rows 和 page 参数的保护行为。"""

    @staticmethod
    def _login(auth_api, test_user):
        """统一执行登录，保证后续异常分页请求使用有效会话。"""
        response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert response.status_code == 200
        assert response.json()["status"] == 0

    @allure.title("历史分页 rows 传入文本时返回 400 转换错误")
    def test_history_rows_text_value_returns_http_400_with_conversion_error(self, auth_api, history_api, test_user):
        """校验 rows 传入非整数字符串时，后端返回 400 而不是成功 JSON。"""
        self._login(auth_api, test_user)

        response = history_api.find_monitor_link_history({"rows": "bad"})
        assert response.status_code == 400
        assert "NumberFormatException" in response.text
        assert 'input string: "bad"' in response.text.lower()

    @allure.title("历史分页 rows 为 0 时回退到默认首页")
    def test_history_rows_zero_falls_back_to_default_first_page(self, auth_api, history_api, test_user):
        """校验 rows=0 不会报错，而是回退到默认分页大小和默认首页结果。"""
        self._login(auth_api, test_user)

        default_body = history_api.find_monitor_link_history().json()
        zero_body = history_api.find_monitor_link_history({"rows": 0}).json()

        assert zero_body["total"] == default_body["total"]
        assert len(zero_body["rows"]) == len(default_body["rows"]) == 10
        assert zero_body["rows"][0]["id"] == default_body["rows"][0]["id"]

    @allure.title("历史分页 rows 为负数时回退到默认首页")
    def test_history_negative_rows_falls_back_to_default_first_page(self, auth_api, history_api, test_user):
        """校验 rows=-1 不会报错，而是回退到默认分页大小和默认首页结果。"""
        self._login(auth_api, test_user)

        default_body = history_api.find_monitor_link_history().json()
        negative_body = history_api.find_monitor_link_history({"rows": -1}).json()

        assert negative_body["total"] == default_body["total"]
        assert len(negative_body["rows"]) == len(default_body["rows"]) == 10
        assert negative_body["rows"][0]["id"] == default_body["rows"][0]["id"]

    @allure.title("历史分页 page 传入文本时返回 400 转换错误")
    def test_history_page_text_value_returns_http_400_with_conversion_error(self, auth_api, history_api, test_user):
        """校验 page 传入非整数字符串时，后端返回 400 而不是成功 JSON。"""
        self._login(auth_api, test_user)

        response = history_api.find_monitor_link_history({"rows": 2, "page": "bad"})
        assert response.status_code == 400
        assert "NumberFormatException" in response.text
        assert 'input string: "bad"' in response.text.lower()

    @allure.title("历史分页 page 超出范围时返回空列表")
    def test_history_page_out_of_range_returns_empty_rows(self, auth_api, history_api, test_user):
        """校验 page 远超总页数时，接口返回空 rows 而不是报错。"""
        self._login(auth_api, test_user)

        body = history_api.find_monitor_link_history({"rows": 1, "page": 99999}).json()
        assert body["total"] >= 0
        assert body["rows"] == []

    @allure.title("历史分页 page 为负数时回退到首页")
    def test_history_negative_page_falls_back_to_first_page(self, auth_api, history_api, test_user):
        """校验 page=-1 时接口回退到首页，并按 rows 参数返回指定条数。"""
        self._login(auth_api, test_user)

        first_page_body = history_api.find_monitor_link_history({"rows": 2, "page": 1}).json()
        negative_page_body = history_api.find_monitor_link_history({"rows": 2, "page": -1}).json()

        assert negative_page_body["total"] == first_page_body["total"]
        assert len(negative_page_body["rows"]) == 2
        assert negative_page_body["rows"][0]["id"] == first_page_body["rows"][0]["id"]


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
