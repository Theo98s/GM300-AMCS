# -*- coding: utf-8 -*-
"""视频监控异常请求体、方法与兼容边界测试。"""
from __future__ import annotations

import allure
import pytest


class TestVideoAbnormalContractsMore:
    """补充视频树和预置位摄像机接口的异常请求行为。"""

    @staticmethod
    def _login(auth_api, test_user):
        """每条用例先登录，保证后续请求拥有业务访问会话。"""
        login_response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert login_response.status_code == 200
        assert login_response.json()["status"] == 0

    @staticmethod
    def _assert_camera_tree_response(response):
        """统一校验视频树接口仍返回节点列表。"""
        assert response.status_code == 200
        assert "application/json" in response.headers.get("Content-Type", "")
        assert isinstance(response.json(), list)

    @allure.title("视频树接口接收文本请求体时仍返回节点列表")
    def test_camera_tree_plain_text_body_keeps_tree_contract(self, auth_api, request_util, config, test_user):
        """校验错误文本请求体不会破坏视频树默认加载能力。"""
        self._login(auth_api, test_user)

        response = request_util.send_request(
            "post",
            config["video"]["camera_tree_url"],
            data="not-json",
            headers={"Content-Type": "text/plain"},
        )

        self._assert_camera_tree_response(response)

    @allure.title("视频树接口接收不存在所亭参数时仍返回默认节点列表")
    def test_camera_tree_unknown_station_param_keeps_tree_contract(self, auth_api, request_util, config, test_user):
        """校验不存在的所亭筛选参数会被兼容处理，接口仍返回列表结构。"""
        self._login(auth_api, test_user)

        response = request_util.send_request(
            "post",
            config["video"]["camera_tree_url"],
            json={"subId": "NO_SUCH_SUB_001"},
        )

        self._assert_camera_tree_response(response)

    @allure.title("视频树接口接收无关字段时节点核心字段不丢失")
    def test_camera_tree_unknown_field_keeps_node_shape(self, auth_api, request_util, config, test_user):
        """校验无关字段不会导致视频树节点缺失核心展示字段。"""
        self._login(auth_api, test_user)

        body = request_util.send_request(
            "post",
            config["video"]["camera_tree_url"],
            json={"unexpected": "NO_SUCH_VALUE"},
        ).json()
        if not body:
            pytest.skip("当前环境没有视频树节点，跳过节点结构校验。")

        first_node = body[0]
        assert set(first_node.keys()) >= {"id", "text", "state", "iconCls", "model"}
        assert set(first_node["model"].keys()) >= {"id", "text", "name", "type"}

    @allure.title("预置位摄像机接口使用错误 POST 方法时返回方法不支持")
    def test_preset_cameras_post_method_returns_method_not_supported(
        self,
        auth_api,
        request_util,
        config,
        test_user,
    ):
        """校验预置位摄像机列表的 HTTP 方法契约，错误 POST 应明确返回 405。"""
        self._login(auth_api, test_user)

        response = request_util.send_request(
            "post",
            config["video"]["preset_cameras_url"],
            json={"unexpected": "NO_SUCH_VALUE"},
        )

        assert response.status_code == 405
        assert "Request method 'POST' not supported" in response.text


class TestVideoMalformedAndOptionsMore:
    """校验摄像机树异常请求体和预置位预检请求的稳定响应。"""

    @staticmethod
    def _login(auth_api, test_user):
        """先建立登录会话，避免视频接口跳转到登录页面。"""
        response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert response.status_code == 200
        assert response.json()["status"] == 0

    @allure.title("摄像机树接口收到损坏 JSON 时仍返回节点列表")
    def test_camera_tree_malformed_json_keeps_tree_contract(
        self,
        auth_api,
        request_util,
        config,
        test_user,
    ):
        """校验摄像机树忽略无法解析的请求体并按默认条件查询。"""
        self._login(auth_api, test_user)

        response = request_util.send_request(
            "post",
            config["video"]["camera_tree_url"],
            data="{bad-json",
            headers={"Content-Type": "application/json"},
        )

        assert response.status_code == 200
        assert "application/json" in response.headers.get("Content-Type", "")
        assert isinstance(response.json(), list)

    @allure.title("预置位摄像机接口使用 OPTIONS 时返回空成功响应")
    def test_preset_cameras_options_method_returns_empty_success(
        self,
        auth_api,
        request_util,
        config,
        test_user,
    ):
        """校验预置位摄像机接口的浏览器预检请求不会返回业务数据。"""
        self._login(auth_api, test_user)

        response = request_util.send_request(
            "options",
            config["video"]["preset_cameras_url"],
        )

        assert response.status_code == 200
        assert response.content == b""


class TestVideoMethodAbnormalContractsMore:
    """补充视频树和预置位摄像机接口在边界请求方法下的响应。"""

    @staticmethod
    def _login(auth_api, test_user):
        """每条用例先登录，确保访问的是业务接口本身。"""
        login_response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert login_response.status_code == 200
        assert login_response.json()["status"] == 0

    @staticmethod
    def _assert_camera_tree_list(response):
        """统一校验视频树接口返回节点列表。"""
        assert response.status_code == 200
        assert "application/json" in response.headers.get("Content-Type", "")
        assert isinstance(response.json(), list)

    @staticmethod
    def _assert_preset_camera_body(response):
        """统一校验预置位摄像机接口返回标准三段式列表。"""
        assert response.status_code == 200
        assert "application/json" in response.headers.get("Content-Type", "")
        body = response.json()
        assert set(body.keys()) == {"status", "message", "data"}
        assert body["status"] == 0
        assert body["message"] == ""
        assert isinstance(body["data"], list)

    @allure.title("视频树接口使用 GET 方法时仍返回节点列表")
    def test_camera_tree_get_method_keeps_tree_response(self, auth_api, request_util, config, test_user):
        """校验视频树接口兼容 GET 访问，仍返回默认树节点。"""
        self._login(auth_api, test_user)

        response = request_util.send_request("get", config["video"]["camera_tree_url"])

        self._assert_camera_tree_list(response)

    @allure.title("视频树接口使用 OPTIONS 方法时返回空成功响应")
    def test_camera_tree_options_method_returns_empty_success(self, auth_api, request_util, config, test_user):
        """记录视频树接口当前 OPTIONS 探测行为，便于发现网关方法策略变化。"""
        self._login(auth_api, test_user)

        response = request_util.send_request(
            "options",
            config["video"]["camera_tree_url"],
            allow_redirects=False,
        )

        assert response.status_code == 200
        assert response.content == b""

    @allure.title("预置位摄像机接口接收未知参数时仍返回列表结构")
    def test_preset_cameras_unknown_param_keeps_list_response(self, auth_api, request_util, config, test_user):
        """校验未知查询参数不会影响预置位摄像机列表结构。"""
        self._login(auth_api, test_user)

        response = request_util.send_request(
            "get",
            config["video"]["preset_cameras_url"],
            params={"equipId": "NO_SUCH_EQUIP_001"},
        )

        self._assert_preset_camera_body(response)

    @allure.title("预置位摄像机接口携带文本请求体时仍返回列表结构")
    def test_preset_cameras_get_with_plain_text_body_keeps_list_response(
        self,
        auth_api,
        request_util,
        config,
        test_user,
    ):
        """校验 GET 请求携带无意义文本体时不会破坏预置位列表返回。"""
        self._login(auth_api, test_user)

        response = request_util.send_request(
            "get",
            config["video"]["preset_cameras_url"],
            data="not-form",
            headers={"Content-Type": "text/plain"},
        )

        self._assert_preset_camera_body(response)


class TestVideoPutMethodContractMore:
    """校验摄像机树接口使用 PUT 时仍保持默认列表响应。"""

    @staticmethod
    def _login(auth_api, test_user):
        """先建立登录会话，确保请求命中摄像机树接口。"""
        response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert response.status_code == 200
        assert response.json()["status"] == 0

    @allure.title("摄像机树接口使用 PUT 时仍返回节点列表")
    def test_camera_tree_put_method_keeps_tree_contract(
        self,
        auth_api,
        request_util,
        config,
        test_user,
    ):
        """记录接口当前兼容 PUT 的行为，防止方法策略变化造成调用回归。"""
        self._login(auth_api, test_user)

        response = request_util.send_request(
            "put",
            config["video"]["camera_tree_url"],
            json={},
        )

        assert response.status_code == 200
        assert "application/json" in response.headers.get("Content-Type", "")
        assert isinstance(response.json(), list)
