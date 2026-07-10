# -*- coding: utf-8 -*-
"""监控点写操作接口的 OPTIONS 预检契约测试。"""
from __future__ import annotations

import allure
import pytest


@allure.feature("基础数据")
class TestMonitorMutationOptionsMore:
    """校验校验、保存、删除校验及删除接口的预检请求不会写入数据。"""

    @staticmethod
    def _login(auth_api, test_user):
        """先建立登录会话，确保受保护写接口正常接收预检请求。"""
        response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert response.status_code == 200
        assert response.json()["status"] == 0

    @pytest.mark.parametrize(
        ("config_key", "case_name"),
        [
            pytest.param("monitor_validate_url", "保存前校验", id="validate"),
            pytest.param("monitor_save_url", "保存或修改", id="save"),
            pytest.param("monitor_can_delete_url", "删除前校验", id="can-delete"),
            pytest.param("monitor_delete_url", "批量删除", id="delete"),
        ],
    )
    @allure.title("监控点写接口使用 OPTIONS 时返回空成功响应")
    def test_monitor_mutation_endpoint_options_returns_empty_success(
        self,
        auth_api,
        request_util,
        config,
        test_user,
        config_key,
        case_name,
    ):
        """逐项校验预检请求只返回空响应，不执行任何数据写操作。"""
        self._login(auth_api, test_user)
        allure.dynamic.parameter("接口名称", case_name)

        response = request_util.send_request(
            "options",
            config["database"][config_key],
        )

        assert response.status_code == 200
        assert response.content == b""
