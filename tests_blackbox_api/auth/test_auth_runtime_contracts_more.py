# -*- coding: utf-8 -*-
"""AMCS 认证运行时补充契约测试。"""
from __future__ import annotations

import allure


@allure.feature("认证")
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
