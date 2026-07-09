# -*- coding: utf-8 -*-
"""AMCS 访问控制例外场景补充测试。"""
from __future__ import annotations

import allure


@allure.feature("系统管理")
class TestAccessExceptionContractsMore:
    """补充校验需要登录和无需登录接口之间的当前差异化行为。"""

    @allure.title("匿名访问报警记录接口会跳转登录页")
    def test_anonymous_alarm_record_request_redirects_to_login(self, request_util, config):
        """校验报警记录接口仍受登录态保护。"""
        response = request_util.send_request(
            "post",
            config["alarm"]["alarm_record_page_url"],
            json={},
            allow_redirects=False,
        )

        assert response.status_code == 302
        assert response.headers["Location"] == "/amcs/login"

    @allure.title("匿名访问监控点列表接口仍可返回公开 JSON")
    def test_anonymous_monitor_page_request_still_returns_public_json(self, request_util, config):
        """校验监控点列表接口当前仍允许匿名访问，并返回标准分页 JSON。"""
        response = request_util.send_request(
            "post",
            config["database"]["monitor_page_url"],
            data={"page": 1, "rows": 5},
            allow_redirects=False,
        )

        assert response.status_code == 200
        assert "application/json" in response.headers.get("Content-Type", "")

        body = response.json()
        assert isinstance(body["rows"], list)
        assert body["total"] >= len(body["rows"])
        assert len(body["rows"]) > 0

    @allure.title("匿名访问监控点导入页仍可返回公开 HTML")
    def test_anonymous_monitor_import_page_still_returns_public_html(self, request_util, config):
        """校验监控点导入页当前仍允许匿名访问，并返回标准导入页 HTML。"""
        response = request_util.send_request(
            "get",
            config["database"]["monitor_import_page_url"],
            allow_redirects=False,
        )

        assert response.status_code == 200
        assert "text/html" in response.headers.get("Content-Type", "")
        assert "<title>导入页面</title>" in response.text
        assert "monitorImport.xls" in response.text

    @allure.title("匿名访问非法监控点编辑页仍可返回公开 HTML 壳")
    def test_anonymous_monitor_edit_page_with_invalid_id_still_returns_public_html_shell(self, request_util, config):
        """校验监控点编辑页在匿名且非法 ID 下当前仍返回标准编辑页 HTML 壳。"""
        response = request_util.send_request(
            "get",
            config["database"]["monitor_edit_page_url"],
            params={"id": "bad-id"},
            allow_redirects=False,
        )

        assert response.status_code == 200
        assert "text/html" in response.headers.get("Content-Type", "")
        assert "<title>监控点编辑</title>" in response.text
        assert 'function appendToken()' in response.text
