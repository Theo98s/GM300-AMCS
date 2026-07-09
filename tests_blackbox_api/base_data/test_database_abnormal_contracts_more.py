# -*- coding: utf-8 -*-
"""AMCS 基础数据库异常场景补充测试。"""
from __future__ import annotations

from pathlib import Path
import tempfile

import allure


@allure.feature("基础数据")
class TestDatabaseAbnormalContractsMore:
    """补充校验基础数据库对空参数、非法 ID 和错误文件的兜底行为。"""

    @staticmethod
    def _login(auth_api, test_user):
        """统一执行登录，保证异常请求运行在已认证会话下。"""
        response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert response.status_code == 200
        assert response.json()["status"] == 0

    @allure.title("监控点删除前校验在空请求体下返回 400")
    def test_monitor_can_delete_empty_body_returns_http_400(self, auth_api, database_api, test_user):
        """校验删除前校验接口在空 ID 集合下不会伪成功，而是明确返回缺少请求体。"""
        self._login(auth_api, test_user)

        response = database_api.can_delete_monitor([])
        assert response.status_code == 400
        assert "Required request body is missing" in response.text
        assert "checkCanDeleteMonitor" in response.text

    @allure.title("监控点删除接口在空数组下保持幂等成功")
    def test_monitor_delete_empty_id_list_keeps_idempotent_success(self, auth_api, database_api, test_user):
        """校验批量删除接口在空数组下仍返回成功结果，便于前端直接透传空选择。"""
        self._login(auth_api, test_user)

        response = database_api.delete_monitor_by_ids([])
        assert response.status_code == 200

        body = response.json()
        assert body["status"] == 0
        assert body["message"] == "操作成功!"
        assert body["data"] is None

    @allure.title("监控点导入接口在上传非 Excel 文件时返回结构化校验错误")
    def test_monitor_import_rejects_non_excel_file_with_validation_message(self, auth_api, database_api, test_user):
        """校验导入接口在上传文本文件时不会 500，而是返回结构化导入失败提示。"""
        self._login(auth_api, test_user)

        with tempfile.NamedTemporaryFile(delete=False, suffix=".txt", mode="w", encoding="utf-8") as temp_file:
            temp_file.write("not excel")
            temp_path = temp_file.name

        try:
            response = database_api.import_excel("monitorImport.xls", temp_path)
            assert response.status_code == 200

            body = response.json()
            assert body["status"] == 0
            assert body["message"] == "导入出错:数据验证失败"
            assert isinstance(body["data"], list)
            assert len(body["data"]) > 0
            assert "InputStream" in body["data"][0]
        finally:
            Path(temp_path).unlink(missing_ok=True)

    @allure.title("监控点编辑页在非法 ID 下仍返回标准页面壳")
    def test_monitor_edit_page_invalid_id_still_returns_standard_html_shell(self, auth_api, database_api, test_user):
        """校验编辑页在非法监控点 ID 下仍能返回标准编辑页 HTML，而不是 500 错页。"""
        self._login(auth_api, test_user)

        response = database_api.get_monitor_edit_page("bad-id")
        assert response.status_code == 200
        assert "text/html" in response.headers.get("Content-Type", "")
        assert "<title>监控点编辑</title>" in response.text
        assert 'function appendToken()' in response.text
