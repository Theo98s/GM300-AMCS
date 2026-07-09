# -*- coding: utf-8 -*-
"""AMCS 未登录访问控制补充契约测试。"""
from __future__ import annotations

import allure


@allure.feature("系统管理")
class TestAccessControlContractsExtra:
    """补充校验匿名请求落到登录页时的契约。"""

    @allure.title("匿名菜单树请求落地登录页标题")
    def test_anonymous_menu_tree_request_resolves_to_login_page_title(self, request_util, config):
        """校验匿名菜单树请求会落到带标题标签的登录页 HTML。"""
        response = request_util.send_request(
            "get",
            config["menu"]["user_menu_tree_url"],
        )

        assert response.status_code == 200
        assert "<title>" in response.text.lower()
        assert "/sso/ajaxcheck" in response.text

    @allure.title("匿名字典请求返回登录页表单字段")
    def test_anonymous_dict_request_resolves_to_login_form_fields(self, request_util, config):
        """校验匿名字典请求会落到仍包含账号和密码输入框的登录页 HTML。"""
        response = request_util.send_request(
            "get",
            f"{config['home']['dict_list_url_prefix']}/EQUIP_AREA",
        )

        assert response.status_code == 200
        assert 'name="account"' in response.text
        assert 'name="password"' in response.text
