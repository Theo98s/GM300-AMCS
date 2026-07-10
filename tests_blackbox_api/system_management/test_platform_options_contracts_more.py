# -*- coding: utf-8 -*-
"""平台初始化及导航接口的 OPTIONS 方法契约测试。"""
from __future__ import annotations

import allure
import pytest


@allure.feature("系统管理")
class TestPlatformOptionsContractsMore:
    """校验首页、字典、菜单和插件接口的浏览器预检响应。"""

    @staticmethod
    def _login(auth_api, test_user):
        """先建立登录会话，使预检请求进入平台业务路由。"""
        response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert response.status_code == 200
        assert response.json()["status"] == 0

    @pytest.mark.parametrize(
        ("url_factory", "case_name"),
        [
            pytest.param(lambda config: config["home"]["init_menu_url"], "首页初始化", id="home"),
            pytest.param(
                lambda config: f'{config["home"]["dict_list_url_prefix"]}/equipArea',
                "设备区域字典",
                id="dict",
            ),
            pytest.param(lambda config: config["menu"]["user_menu_tree_url"], "用户菜单树", id="menu"),
            pytest.param(lambda config: config["plugin"]["find_plugin_url"], "插件查询", id="plugin"),
        ],
    )
    @allure.title("平台查询接口使用 OPTIONS 时返回空成功响应")
    def test_platform_endpoint_options_returns_empty_success(
        self,
        auth_api,
        request_util,
        config,
        test_user,
        url_factory,
        case_name,
    ):
        """逐项校验平台查询预检请求不会返回菜单或字典业务数据。"""
        self._login(auth_api, test_user)
        allure.dynamic.parameter("接口名称", case_name)

        response = request_util.send_request("options", url_factory(config))

        assert response.status_code == 200
        assert response.content == b""
