# -*- coding: utf-8 -*-
"""AMCS unauthenticated access-control contract tests."""
from __future__ import annotations

import allure


@allure.feature("系统管理")
class TestAccessControlContracts:
    """Contract checks for endpoints that should redirect anonymous users."""

    @staticmethod
    def _assert_redirects_to_login(response):
        """Assert a protected endpoint redirects anonymous users to the login page."""
        assert response.status_code == 302
        assert response.headers["Location"].startswith("/amcs/login")

    @allure.title("首页菜单初始化接口未登录时跳转登录页")
    def test_init_menu_requires_login(self, request_util, config):
        """Verify the home menu initialization endpoint is protected."""
        response = request_util.send_request(
            "post",
            config["home"]["init_menu_url"],
            data={},
            allow_redirects=False,
        )

        self._assert_redirects_to_login(response)

    @allure.title("用户菜单树接口未登录时跳转登录页")
    def test_user_menu_tree_requires_login(self, request_util, config):
        """Verify the user menu tree endpoint is protected."""
        response = request_util.send_request(
            "get",
            config["menu"]["user_menu_tree_url"],
            allow_redirects=False,
        )

        self._assert_redirects_to_login(response)

    @allure.title("通用字典接口未登录时跳转登录页")
    def test_dict_list_requires_login(self, request_util, config):
        """Verify dictionary endpoints are protected before login."""
        response = request_util.send_request(
            "get",
            f"{config['home']['dict_list_url_prefix']}/EQUIP_AREA",
            allow_redirects=False,
        )

        self._assert_redirects_to_login(response)
