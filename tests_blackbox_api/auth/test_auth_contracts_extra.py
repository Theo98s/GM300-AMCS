# -*- coding: utf-8 -*-
"""Additional AMCS login-page contract tests."""
from __future__ import annotations

import re

import allure


@allure.feature("认证")
class TestAuthContractsExtra:
    """Extra checks for stable login-page markup."""

    @allure.title("登录页同时保留账号密码输入框 id 标记")
    def test_login_page_contains_account_and_password_ids(self, auth_api):
        """Verify the login page keeps the account and password input ids used by automation scripts."""
        response = auth_api.get_login_page()

        assert 'id="account"' in response.text
        assert 'id="password"' in response.text

    @allure.title("登录页标题标签保持完整")
    def test_login_page_contains_single_title_block(self, auth_api):
        """Verify the login page still contains a parseable title block."""
        response = auth_api.get_login_page()

        title_matches = re.findall(r"<title>.*?</title>", response.text, re.IGNORECASE | re.DOTALL)
        assert len(title_matches) == 1

