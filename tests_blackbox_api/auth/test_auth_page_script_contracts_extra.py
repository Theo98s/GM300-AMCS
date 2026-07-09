# -*- coding: utf-8 -*-
"""AMCS 登录页脚本变量补充契约测试。"""
from __future__ import annotations

import re

import allure


@allure.feature("认证")
class TestAuthPageScriptContractsExtra:
    """补充校验登录页中的脚本变量和记住账号控件。"""

    @allure.title("登录页保留核心脚本变量名")
    def test_login_page_keeps_core_script_variable_names(self, auth_api):
        """校验登录页仍暴露登录流程依赖的核心脚本变量。"""
        response = auth_api.get_login_page()

        variable_names = re.findall(r"var\s+(\w+)\s*=", response.text)
        assert "csrftoken" in variable_names
        assert "projectVersion" in variable_names
        assert "userinfo" in variable_names
        assert "account" in variable_names
        assert "password" in variable_names
        assert "rememberMe" in variable_names

    @allure.title("登录页保留记住账号复选框和版本展示控件")
    def test_login_page_keeps_remember_me_and_version_widgets(self, auth_api):
        """校验登录页仍保留记住账号复选框和版本信息展示控件。"""
        response = auth_api.get_login_page()

        assert 'id="cookie_rememberme"' in response.text
        assert 'id="version"' in response.text
        assert 'id="versionWin"' in response.text
        assert "downloadSoftware" in response.text
