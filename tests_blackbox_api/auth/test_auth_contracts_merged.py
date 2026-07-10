# -*- coding: utf-8 -*-
"""登录页面、脚本、隐藏字段与运行时响应契约测试。"""
from __future__ import annotations

import re
import allure


class TestAuthContracts:
    """校验公共登录页面的契约。"""

    @allure.title("登录页返回 HTML 内容")
    def test_login_page_returns_html(self, auth_api):
        """校验公共登录页返回的是 HTML，而不是重定向或 JSON。"""
        response = auth_api.get_login_page()

        assert response.status_code == 200
        assert "text/html" in response.headers.get("Content-Type", "")
        assert "<html" in response.text.lower()
        assert "</html>" in response.text.lower()

    @allure.title("登录页 CSRFToken 使用 UUID 格式")
    def test_login_page_csrf_token_uses_uuid_format(self, auth_api):
        """校验登录页中的 CSRFToken 保持登录流程需要的 UUID 样式。"""
        response = auth_api.get_login_page()

        csrf_token = auth_api.extract_csrf_token(response.text)
        assert re.fullmatch(
            r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}",
            csrf_token,
        )

    @allure.title("登录页包含顶层窗口保护脚本")
    def test_login_page_contains_top_window_guard(self, auth_api):
        """校验登录页仍保留跳出嵌套框架的脚本。"""
        response = auth_api.get_login_page()

        assert "window.top" in response.text
        assert "window.self" in response.text
        assert "window.top.location=window.location.href" in response.text

    @allure.title("登录页暴露项目版本变量")
    def test_login_page_contains_project_version(self, auth_api):
        """校验登录页仍暴露 projectVersion，便于静态资源版本控制。"""
        response = auth_api.get_login_page()

        assert re.search(r'var projectVersion="[^"]+";', response.text)

    @allure.title("登录页标题包含系统名和登录字样")
    def test_login_page_title_contains_system_name_and_login_text(self, auth_api):
        """校验登录页标题仍包含系统名称和“登录”关键字。"""
        response = auth_api.get_login_page()

        title_match = re.search(r"<title>(.*?)</title>", response.text, re.IGNORECASE | re.DOTALL)
        assert title_match
        assert "牵引变电所辅助监控被控站系统" in title_match.group(1)
        assert "登录" in title_match.group(1)

    @allure.title("登录页包含密码输入框和登录提交地址")
    def test_login_page_contains_password_field_and_submit_route(self, auth_api):
        """校验登录页仍保留密码输入框和 Ajax 登录提交地址。"""
        response = auth_api.get_login_page()

        assert 'name="password"' in response.text
        assert "/sso/ajaxcheck" in response.text

    @allure.title("登录页保留账号输入框 id 和 name 标记")
    def test_login_page_contains_account_field_markers(self, auth_api):
        """校验登录页仍保留自动化和前端脚本依赖的账号输入框标记。"""
        response = auth_api.get_login_page()

        assert 'name="account"' in response.text
        assert 'id="password"' in response.text


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


class TestAuthRuntimeContractsMore:
    """补充校验登录成功、失败和登录页响应的运行时契约。"""

    @allure.title("登录成功返回固定三段式结果")
    def test_login_success_keeps_exact_result_contract(self, auth_api, test_user):
        """校验登录成功时仍返回 status、message、data 三段式结果。"""
        response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )

        assert response.status_code == 200
        body = response.json()
        assert set(body.keys()) == {"status", "message", "data"}
        assert body["status"] == 0
        assert body["message"] == "登录成功"
        assert body["data"] == "/"

    @allure.title("错误用户名与错误密码保持相同失败契约")
    def test_login_fail_variants_keep_same_contract(self, auth_api, test_user):
        """校验错误用户名与错误密码仍保持相同失败返回结构。"""
        wrong_password_body = auth_api.login(
            account=test_user["username"],
            password=f"{test_user['password']}_bad",
        ).json()
        wrong_username_body = auth_api.login(
            account=f"{test_user['username']}_bad",
            password=test_user["password"],
        ).json()

        for body in (wrong_password_body, wrong_username_body):
            assert set(body.keys()) == {"status", "message", "data"}
            assert body["status"] == 1
            assert isinstance(body["message"], str)
            assert body["message"] in {
                "用户名/密码错误",
                "你已连续多次输入错误！请联系管理员或30分钟后重试！",
            }
            assert body["data"] is None

    @allure.title("登录页响应保持 HTML 内容类型与关键表单标记")
    def test_login_page_keeps_html_content_type_and_form_markers(self, auth_api):
        """校验登录页响应仍保持 HTML 内容类型和关键表单标记。"""
        response = auth_api.get_login_page()

        assert response.status_code == 200
        assert "text/html" in response.headers.get("Content-Type", "")
        assert '<form id="loginForm"' in response.text
        assert 'id="account"' in response.text
        assert 'id="password"' in response.text
