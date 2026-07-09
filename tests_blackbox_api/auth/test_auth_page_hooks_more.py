# -*- coding: utf-8 -*-
"""AMCS 登录页面钩子更多契约测试。"""
from __future__ import annotations

import re

import allure


@allure.feature("认证")
class TestAuthPageHooksMore:
    """补充校验登录页面表单与脚本钩子的稳定性。"""

    @allure.title("登录页保留唯一的 Ajax 登录表单提交地址")
    def test_login_page_keeps_single_ajax_login_form_action(self, auth_api):
        """校验登录页仍通过唯一的 ajaxcheck 表单地址提交。"""
        response = auth_api.get_login_page()

        form_actions = re.findall(r'<form[^>]*action="([^"]*)"', response.text)
        assert form_actions == ["/sso/ajaxcheck"]

    @allure.title("登录页保留核心脚本辅助函数名")
    def test_login_page_keeps_core_script_helper_function_names(self, auth_api):
        """校验当前登录页仍暴露表单提交流程依赖的辅助函数。"""
        response = auth_api.get_login_page()

        function_names = re.findall(r"function\s+(\w+)\(", response.text)
        assert "appendToken" in function_names
        assert "updateForms" in function_names
        assert "checkForm" in function_names
        assert "storeAccountData" in function_names
        assert "getAccountInfo" in function_names

    @allure.title("登录页保留稳定的输入框和按钮 id")
    def test_login_page_keeps_stable_input_and_button_ids(self, auth_api):
        """校验登录页仍暴露自动化和前端依赖的当前控件 id。"""
        response = auth_api.get_login_page()

        input_ids = set(re.findall(r'id="([^"]+)"', response.text))
        assert {"loginForm", "account", "password", "btnLogin", "version"}.issubset(input_ids)
        assert "cookie_rememberme" in input_ids
