# -*- coding: utf-8 -*-
"""AMCS 未登录访问控制契约测试。"""
from __future__ import annotations

import allure


@allure.feature("系统管理")
class TestAccessControlContracts:
    """校验匿名用户应被重定向的接口契约。"""

    @staticmethod
    def _assert_redirects_to_login(response):
        """断言受保护接口会把匿名用户重定向到登录页。"""
        assert response.status_code == 302
        assert response.headers["Location"].startswith("/amcs/login")

    @allure.title("首页菜单初始化接口未登录时跳转登录页")
    def test_init_menu_requires_login(self, request_util, config):
        """校验首页菜单初始化接口受登录保护。"""
        response = request_util.send_request(
            "post",
            config["home"]["init_menu_url"],
            data={},
            allow_redirects=False,
        )

        self._assert_redirects_to_login(response)

    @allure.title("用户菜单树接口未登录时跳转登录页")
    def test_user_menu_tree_requires_login(self, request_util, config):
        """校验用户菜单树接口受登录保护。"""
        response = request_util.send_request(
            "get",
            config["menu"]["user_menu_tree_url"],
            allow_redirects=False,
        )

        self._assert_redirects_to_login(response)

    @allure.title("通用字典接口未登录时跳转登录页")
    def test_dict_list_requires_login(self, request_util, config):
        """校验字典接口在未登录前受保护。"""
        response = request_util.send_request(
            "get",
            f"{config['home']['dict_list_url_prefix']}/EQUIP_AREA",
            allow_redirects=False,
        )

        self._assert_redirects_to_login(response)

    @allure.title("首页菜单初始化接口默认行为会落到登录页 HTML")
    def test_init_menu_default_request_returns_login_html(self, request_util, config):
        """校验未控制 allow_redirects 时，initMenu 最终会落到登录页 HTML。"""
        response = request_util.send_request(
            "post",
            config["home"]["init_menu_url"],
            data={},
        )

        assert response.status_code == 200
        assert "text/html" in response.headers.get("Content-Type", "")
        assert "window.top" in response.text

    @allure.title("匿名访问受保护接口时仍暴露登录提交地址")
    def test_default_anonymous_request_login_html_contains_submit_route(self, request_util, config):
        """校验解析后的登录页 HTML 仍包含 ajax 登录提交地址，便于用户恢复登录。"""
        response = request_util.send_request(
            "get",
            config["menu"]["user_menu_tree_url"],
        )

        assert response.status_code == 200
        assert "/sso/ajaxcheck" in response.text
        assert 'name="password"' in response.text

    @allure.title("用户菜单树接口默认行为会落到登录页 HTML")
    def test_user_menu_tree_default_request_returns_login_html(self, request_util, config):
        """校验未登录访问 getUserMenuTree 时会落到登录页 HTML。"""
        response = request_util.send_request(
            "get",
            config["menu"]["user_menu_tree_url"],
        )

        assert response.status_code == 200
        assert "text/html" in response.headers.get("Content-Type", "")
        assert "window.top" in response.text

    @allure.title("设备区域字典接口默认行为会落到登录页 HTML")
    def test_dict_list_default_request_returns_login_html(self, request_util, config):
        """校验未登录访问字典接口时会落到登录页 HTML。"""
        response = request_util.send_request(
            "get",
            f"{config['home']['dict_list_url_prefix']}/EQUIP_AREA",
        )

        assert response.status_code == 200
        assert "text/html" in response.headers.get("Content-Type", "")
        assert "window.top" in response.text
