# -*- coding: utf-8 -*-
"""视频监控接口的损坏请求体和预检请求契约测试。"""
from __future__ import annotations

import allure


@allure.feature("视频监控")
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
