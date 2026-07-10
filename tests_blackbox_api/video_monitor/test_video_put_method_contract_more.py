# -*- coding: utf-8 -*-
"""摄像机树接口的 PUT 方法兼容契约测试。"""
from __future__ import annotations

import allure


@allure.feature("视频监控")
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
