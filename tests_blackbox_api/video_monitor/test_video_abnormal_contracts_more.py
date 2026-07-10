# -*- coding: utf-8 -*-
"""视频监控接口异常请求契约测试。"""
from __future__ import annotations

import allure
import pytest


@allure.feature("视频监控")
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
