# -*- coding: utf-8 -*-
"""AMCS 登录页面契约测试。"""
from __future__ import annotations

import re

import allure


@allure.feature("认证")
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
