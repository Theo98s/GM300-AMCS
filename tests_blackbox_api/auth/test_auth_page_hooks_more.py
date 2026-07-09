# -*- coding: utf-8 -*-
"""More AMCS login-page hook contract tests."""
from __future__ import annotations

import re

import allure


@allure.feature("Auth")
class TestAuthPageHooksMore:
    """Extra checks for stable login-page forms and script hooks."""

    @allure.title("Login page keeps single ajax login form action")
    def test_login_page_keeps_single_ajax_login_form_action(self, auth_api):
        """Verify the login page still posts through the single ajaxcheck form route."""
        response = auth_api.get_login_page()

        form_actions = re.findall(r'<form[^>]*action="([^"]*)"', response.text)
        assert form_actions == ["/sso/ajaxcheck"]

    @allure.title("Login page keeps core script helper function names")
    def test_login_page_keeps_core_script_helper_function_names(self, auth_api):
        """Verify the current login page still exposes the helper functions used around form submission."""
        response = auth_api.get_login_page()

        function_names = re.findall(r"function\s+(\w+)\(", response.text)
        assert "appendToken" in function_names
        assert "updateForms" in function_names
        assert "checkForm" in function_names
        assert "storeAccountData" in function_names
        assert "getAccountInfo" in function_names

    @allure.title("Login page keeps stable input and button ids")
    def test_login_page_keeps_stable_input_and_button_ids(self, auth_api):
        """Verify the login page still exposes the current ids used by automation and the frontend."""
        response = auth_api.get_login_page()

        input_ids = set(re.findall(r'id="([^"]+)"', response.text))
        assert {"loginForm", "account", "password", "btnLogin", "version"}.issubset(input_ids)
        assert "cookie_rememberme" in input_ids
