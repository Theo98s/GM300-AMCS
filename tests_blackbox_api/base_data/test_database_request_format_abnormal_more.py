# -*- coding: utf-8 -*-
"""基础数据库接口的请求格式异常契约测试。"""
from __future__ import annotations

import allure


@allure.feature("基础数据")
class TestDatabaseRequestFormatAbnormalMore:
    """校验列表、删除校验和导入接口收到错误请求格式时的响应。"""

    @staticmethod
    def _login(auth_api, test_user):
        """先完成登录，确保验证的是基础数据库接口本身。"""
        response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert response.status_code == 200
        assert response.json()["status"] == 0

    @allure.title("监控点列表收到损坏 JSON 时仍返回默认分页数据")
    def test_monitor_page_malformed_json_keeps_default_page_contract(
        self,
        auth_api,
        request_util,
        config,
        test_user,
    ):
        """校验列表接口忽略无法解析的 JSON，并保持分页响应结构。"""
        self._login(auth_api, test_user)

        response = request_util.send_request(
            "post",
            config["database"]["monitor_page_url"],
            data="{bad-json",
            headers={"Content-Type": "application/json"},
        )

        assert response.status_code == 200
        assert "application/json" in response.headers.get("Content-Type", "")
        body = response.json()
        assert isinstance(body["total"], int)
        assert isinstance(body["rows"], list)

    @allure.title("监控点删除前校验接口使用 GET 时返回方法不支持")
    def test_monitor_can_delete_get_method_returns_405(
        self,
        auth_api,
        request_util,
        config,
        test_user,
    ):
        """校验删除前校验只接受约定方法，错误方法不会触发业务处理。"""
        self._login(auth_api, test_user)

        response = request_util.send_request(
            "get",
            config["database"]["monitor_can_delete_url"],
        )

        assert response.status_code == 405
        assert "Request method 'GET' not supported" in response.text

    @allure.title("监控点删除前校验接收不存在标识时返回空依赖")
    def test_monitor_can_delete_plain_text_unknown_id_returns_empty_dependencies(
        self,
        auth_api,
        request_util,
        config,
        test_user,
    ):
        """校验不存在的监控点标识不会产生依赖数据，也不会修改任何记录。"""
        self._login(auth_api, test_user)

        response = request_util.send_request(
            "post",
            config["database"]["monitor_can_delete_url"],
            data="NO_SUCH_MONITOR_ID",
            headers={"Content-Type": "text/plain"},
        )

        assert response.status_code == 200
        assert response.json() == {
            "status": 0,
            "message": "数据查询成功!",
            "data": {"image": []},
        }

    @allure.title("Excel 导入接口缺少 multipart 文件时返回格式错误")
    def test_excel_import_without_multipart_file_returns_format_error(
        self,
        auth_api,
        request_util,
        config,
        test_user,
    ):
        """校验只传模板名但不上传文件时，接口返回明确的 multipart 错误。"""
        self._login(auth_api, test_user)

        response = request_util.send_request(
            "post",
            config["database"]["monitor_excel_import_url"],
            params={"templateName": "monitor"},
        )

        assert response.status_code == 200
        assert response.text == "Current request is not a multipart request"

    @allure.title("Excel 导入接口使用 GET 时返回 multipart 格式错误")
    def test_excel_import_get_method_returns_format_error(
        self,
        auth_api,
        request_util,
        config,
        test_user,
    ):
        """校验错误请求方法不会触发导入，并返回稳定的格式错误信息。"""
        self._login(auth_api, test_user)

        response = request_util.send_request(
            "get",
            config["database"]["monitor_excel_import_url"],
            params={"templateName": "monitor"},
        )

        assert response.status_code == 200
        assert response.text == "Current request is not a multipart request"
