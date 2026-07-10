# -*- coding: utf-8 -*-
"""GIS 接口的损坏请求体异常契约测试。"""
from __future__ import annotations

import allure


@allure.feature("GIS 地图")
class TestGisMalformedPayloadContractsMore:
    """校验二维地图路径接口收到损坏 JSON 时的参数保护行为。"""

    @staticmethod
    def _login(auth_api, test_user):
        """先建立登录会话，确保请求进入 GIS 业务处理。"""
        response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert response.status_code == 200
        assert response.json()["status"] == 0

    @allure.title("二维地图路径接口收到损坏 JSON 时返回缺少地图类型提示")
    def test_d2_data_path_malformed_json_returns_missing_type_prompt(
        self,
        auth_api,
        request_util,
        config,
        test_user,
    ):
        """校验损坏 JSON 被视为缺少参数，接口返回可识别的业务提示。"""
        self._login(auth_api, test_user)

        response = request_util.send_request(
            "post",
            config["gis"]["d2_data_path_url"],
            data="{bad-json",
            headers={"Content-Type": "application/json"},
        )

        assert response.status_code == 200
        assert "application/json" in response.headers.get("Content-Type", "")
        assert response.json() == {
            "status": 0,
            "message": "请传地图类型参数！",
            "data": None,
        }
