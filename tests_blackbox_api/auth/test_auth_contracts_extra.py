# -*- coding: utf-8 -*-
"""AMCS 登录页面补充契约测试。"""
from __future__ import annotations

import re

import allure


@allure.feature("认证")
class TestAuthContractsExtra:
    """补充校验登录页面的稳定标记结构。"""

    @allure.title("登录页同时保留账号密码输入框 id 标记")
    def test_login_page_contains_account_and_password_ids(self, auth_api):
        """校验登录页仍保留自动化脚本使用的账号和密码输入框 id。"""
        response = auth_api.get_login_page()

        assert 'id="account"' in response.text
        assert 'id="password"' in response.text

    @allure.title("登录页标题标签保持完整")
    def test_login_page_contains_single_title_block(self, auth_api):
        """校验登录页仍保留可解析的标题标签。"""
        response = auth_api.get_login_page()

        title_matches = re.findall(r"<title>.*?</title>", response.text, re.IGNORECASE | re.DOTALL)
        assert len(title_matches) == 1
