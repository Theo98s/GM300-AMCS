# -*- coding: utf-8 -*-
"""AMCS 登录页隐藏字段补充契约测试。"""
from __future__ import annotations

import re

import allure


@allure.feature("认证")
class TestAuthHiddenFieldContractsExtra:
    """补充校验登录页隐藏字段和页面控件标识。"""

    @allure.title("登录页保留 logo 和跳转相关隐藏字段")
    def test_login_page_keeps_logo_and_redirect_hidden_fields(self, auth_api):
        """校验登录页仍保留 logo 占位字段和登录后跳转字段。"""
        response = auth_api.get_login_page()

        assert 'id="sys_logo_a"' in response.text
        assert 'id="sys_logo_b"' in response.text
        assert 'id="toUrl"' in response.text
        assert 'id="alltran"' in response.text

    @allure.title("登录页关键控件 id 保持稳定子集")
    def test_login_page_keeps_expected_widget_id_subset(self, auth_api):
        """校验登录页关键控件 id 仍保持当前稳定集合。"""
        response = auth_api.get_login_page()

        input_ids = set(re.findall(r'id="([^"]+)"', response.text))
        assert {
            "loginForm",
            "account",
            "password",
            "toUrl",
            "cookie_rememberme",
            "btnLogin",
            "version",
            "versionWin",
        }.issubset(input_ids)
