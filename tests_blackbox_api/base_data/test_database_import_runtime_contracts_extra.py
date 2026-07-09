# -*- coding: utf-8 -*-
"""AMCS 基础数据导入页运行时补充契约测试。"""
from __future__ import annotations

import re

import allure


@allure.feature("基础数据")
class TestDatabaseImportRuntimeContractsExtra:
    """补充校验基础数据导入页中的脚本函数和容器标识。"""

    @staticmethod
    def _login(auth_api, test_user):
        """每条用例先登录，并确认会话已建立。"""
        login_response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert login_response.status_code == 200
        assert login_response.json()["status"] == 0

    @allure.title("基础数据导入页保留核心下载导入函数")
    def test_monitor_import_page_keeps_core_function_set(self, auth_api, database_api, test_user):
        """校验导入页仍保留下载模板、导入 Excel 和导出相关函数。"""
        self._login(auth_api, test_user)

        response = database_api.get_monitor_import_page()
        assert response.status_code == 200

        function_names = set(re.findall(r"function\s+([A-Za-z0-9_]+)\s*\(", response.text))
        assert {"down", "importExcel", "downExcel", "getParams", "downXml"} <= function_names

    @allure.title("基础数据导入页保留页签容器和模板参数字段")
    def test_monitor_import_page_keeps_tab_ids_and_template_params(self, auth_api, database_api, test_user):
        """校验导入页仍保留页签容器标识以及模板参数名。"""
        self._login(auth_api, test_user)

        response = database_api.get_monitor_import_page()
        assert response.status_code == 200

        assert 'id="cc"' in response.text
        assert 'id="tt"' in response.text
        assert "templateName" in response.text
        assert "downloadName" in response.text
        assert "monitorImport.xls" in response.text
        assert "alarmImport.xls" in response.text
        assert "linkageImport.xls" in response.text
