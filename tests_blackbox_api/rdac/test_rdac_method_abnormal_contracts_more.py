# -*- coding: utf-8 -*-
"""RDAC 接口异常请求方法契约测试。"""
from __future__ import annotations

import allure


@allure.feature("基础数据-RDAC")
class TestRdacMethodAbnormalContractsMore:
    """补充 RDAC 站点和点位接口在错误方法、缺参、错误请求体下的响应。"""

    @staticmethod
    def _login(auth_api, test_user):
        """每条用例先登录，保证后续请求进入 RDAC 业务接口。"""
        login_response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert login_response.status_code == 200
        assert login_response.json()["status"] == 0

    @staticmethod
    def _assert_method_not_supported(response, method: str):
        """统一校验错误 HTTP 方法返回方法不支持。"""
        assert response.status_code == 405
        assert f"Request method '{method}' not supported" in response.text

    @allure.title("RDAC 站点列表接口使用 GET 方法时返回 405")
    def test_rdac_station_list_get_method_returns_405(self, auth_api, request_util, config, test_user):
        """校验 RDAC 站点列表只接受 POST 查询。"""
        self._login(auth_api, test_user)

        response = request_util.send_request(
            "get",
            config["rdac"]["station_list_url"],
            allow_redirects=False,
        )

        self._assert_method_not_supported(response, "GET")

    @allure.title("RDAC 站点列表接口接收文本请求体时仍返回站点列表")
    def test_rdac_station_list_plain_text_body_keeps_list_response(
        self,
        auth_api,
        request_util,
        config,
        test_user,
    ):
        """校验站点列表接口对文本请求体保持兼容，不影响列表返回。"""
        self._login(auth_api, test_user)

        response = request_util.send_request(
            "post",
            config["rdac"]["station_list_url"],
            data="not-json",
            headers={"Content-Type": "text/plain"},
        )

        assert response.status_code == 200
        assert isinstance(response.json(), list)

    @allure.title("RDAC 点位页面缺少参数时仍返回标准 HTML 页面")
    def test_rdac_items_page_missing_params_returns_standard_html(self, auth_api, request_util, config, test_user):
        """校验点位页面缺少站点和协议参数时不会返回 500。"""
        self._login(auth_api, test_user)

        response = request_util.send_request("get", config["rdac"]["station_items_page_url"])

        assert response.status_code == 200
        assert "text/html" in response.headers.get("Content-Type", "")
        assert "<title>站点属性列表主页面</title>" in response.text
        assert "function appendToken()" in response.text

    @allure.title("RDAC 点位列表接口使用 GET 方法时返回 405")
    def test_rdac_item_list_get_method_returns_405(self, auth_api, request_util, config, test_user):
        """校验 RDAC 点位列表 JSON 接口只接受 POST 查询。"""
        self._login(auth_api, test_user)

        response = request_util.send_request(
            "get",
            config["rdac"]["station_item_list_url"],
            allow_redirects=False,
        )

        self._assert_method_not_supported(response, "GET")

    @allure.title("RDAC 点位列表接口空 JSON 时返回参数错误")
    def test_rdac_item_list_empty_json_returns_parameter_error(self, auth_api, request_util, config, test_user):
        """校验缺少站点名称和协议时返回结构化业务错误。"""
        self._login(auth_api, test_user)

        response = request_util.send_request(
            "post",
            config["rdac"]["station_item_list_url"],
            json={},
        )

        assert response.status_code == 200
        body = response.json()
        assert body["status"] == 1
        # 服务端参数校验消息的拼接顺序可能随校验器遍历顺序变化，这里只锁定两项错误都出现。
        message_parts = set(body["message"].split(","))
        assert message_parts == {"协议不允许为空", "站点名称不允许为空"}
        assert body["data"] is None

    @allure.title("RDAC 点位列表接口文本请求体时返回 JSON 解析错误")
    def test_rdac_item_list_plain_text_body_returns_json_parse_error(
        self,
        auth_api,
        request_util,
        config,
        test_user,
    ):
        """校验错误文本请求体会被框架层拦截为 JSON 解析错误。"""
        self._login(auth_api, test_user)

        response = request_util.send_request(
            "post",
            config["rdac"]["station_item_list_url"],
            data="not-json",
            headers={"Content-Type": "text/plain"},
            allow_redirects=False,
        )

        assert response.status_code == 400
        assert "JSON parse error" in response.text
        assert "Unrecognized token 'not'" in response.text
