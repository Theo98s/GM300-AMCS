# -*- coding: utf-8 -*-
"""RDAC 异常参数、损坏请求体与方法边界测试。"""
from __future__ import annotations

import allure
import pytest


class TestRdacAbnormalContractsMore:
    """补充校验 RDAC 对非法站点参数的兜底行为。"""

    @staticmethod
    def _login(auth_api, test_user):
        """统一执行登录，保证异常站点查询在已登录状态下进行。"""
        response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert response.status_code == 200
        assert response.json()["status"] == 0

    @allure.title("RDAC 非法站点点位 JSON 返回空桶而不是报错")
    def test_rdac_invalid_station_item_query_returns_null_buckets(self, auth_api, rdac_api, test_user):
        """校验非法站点名查询点位 JSON 时，后端返回成功包裹但各类点位桶为空。"""
        self._login(auth_api, test_user)

        response = rdac_api.list_station_items("NO_SUCH_SUB_001", "104")
        assert response.status_code == 200

        body = response.json()
        assert body["status"] == 0
        assert body["message"] is None
        assert body["data"] == {
            "telemetryItems": None,
            "telesignalItems": None,
            "remoteControlItems": None,
            "remoteAdjustItems": None,
            "partialDischargeItems": None,
        }

    @allure.title("RDAC 非法站点点位页仍返回标准 HTML 壳")
    def test_rdac_invalid_station_page_still_returns_standard_html_shell(self, auth_api, rdac_api, test_user):
        """校验非法站点名打开点位页时，页面仍能返回标准 HTML 壳而不是 500。"""
        self._login(auth_api, test_user)

        response = rdac_api.get_station_items_page("NO_SUCH_SUB_001", "104")
        assert response.status_code == 200
        assert "text/html" in response.headers.get("Content-Type", "")
        assert "站点属性列表主页面" in response.text
        assert "var protocol = '104'" in response.text


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


class TestRdacOptionsContractsMore:
    """校验站点列表和点表查询接口的浏览器预检响应。"""

    @staticmethod
    def _login(auth_api, test_user):
        """先建立登录会话，使预检请求进入 RDAC 路由。"""
        response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert response.status_code == 200
        assert response.json()["status"] == 0

    @pytest.mark.parametrize(
        ("config_key", "case_name"),
        [
            pytest.param("station_list_url", "站点列表", id="station-list"),
            pytest.param("station_item_list_url", "站点点表", id="station-item-list"),
        ],
    )
    @allure.title("RDAC 查询接口使用 OPTIONS 时返回空成功响应")
    def test_rdac_endpoint_options_method_returns_empty_success(
        self,
        auth_api,
        request_util,
        config,
        test_user,
        config_key,
        case_name,
    ):
        """逐项校验 RDAC 查询预检不会执行数据查询或返回业务内容。"""
        self._login(auth_api, test_user)
        allure.dynamic.parameter("接口名称", case_name)

        response = request_util.send_request(
            "options",
            config["rdac"][config_key],
        )

        assert response.status_code == 200
        assert response.content == b""
