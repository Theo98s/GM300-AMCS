# -*- coding: utf-8 -*-
"""Additional AMCS unauthenticated access-control contract tests."""
from __future__ import annotations

import allure


@allure.feature("系统管理")
class TestAccessControlContractsExtra:
    """Extra checks for anonymous requests that resolve to the login page."""

    @allure.title("匿名菜单树请求落地登录页标题")
    def test_anonymous_menu_tree_request_resolves_to_login_page_title(self, request_util, config):
        """Verify anonymous menu-tree requests resolve to the login page HTML with a title tag."""
        response = request_util.send_request(
            "get",
            config["menu"]["user_menu_tree_url"],
        )

        assert response.status_code == 200
        assert "<title>" in response.text.lower()
        assert "/sso/ajaxcheck" in response.text

    @allure.title("匿名字典请求返回登录页表单字段")
    def test_anonymous_dict_request_resolves_to_login_form_fields(self, request_util, config):
        """Verify anonymous dictionary requests resolve to login HTML that still contains account/password fields."""
        response = request_util.send_request(
            "get",
            f"{config['home']['dict_list_url_prefix']}/EQUIP_AREA",
        )

        assert response.status_code == 200
        assert 'name="account"' in response.text
        assert 'name="password"' in response.text

