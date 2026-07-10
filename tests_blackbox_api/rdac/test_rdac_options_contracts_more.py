# -*- coding: utf-8 -*-
"""RDAC 查询接口的 OPTIONS 方法契约测试。"""
from __future__ import annotations

import allure
import pytest


@allure.feature("RDAC")
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
