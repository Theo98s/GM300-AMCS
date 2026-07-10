# -*- coding: utf-8 -*-
"""视频监控接口异常请求方法契约测试。"""
from __future__ import annotations

import allure


@allure.feature("视频监控")
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
