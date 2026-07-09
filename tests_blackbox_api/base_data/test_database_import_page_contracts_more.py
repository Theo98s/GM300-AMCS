# -*- coding: utf-8 -*-
"""AMCS 基础数据导入页更多契约测试。"""
from __future__ import annotations

import re

import allure


@allure.feature("基础数据")
class TestDatabaseImportPageContractsMore:
    """补充校验基础数据导入页中的脚本变量与操作入口。"""

    @staticmethod
    def _login(auth_api, test_user):
        """每条用例先登录，并确认会话已建立。"""
        login_response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert login_response.status_code == 200
        assert login_response.json()["status"] == 0

    @allure.title("基础数据导入页保留核心脚本变量名")
    def test_monitor_import_page_keeps_core_script_variable_names(self, auth_api, database_api, test_user):
        """校验基础数据导入页仍暴露核心脚本变量。"""
        self._login(auth_api, test_user)

        response = database_api.get_monitor_import_page()
        variable_names = re.findall(r"var\s+(\w+)\s*=", response.text)
        assert "csrftoken" in variable_names
        assert "projectVersion" in variable_names
        assert "templateName" in variable_names
        assert "downloadName" in variable_names

    @allure.title("基础数据导入页保留下载和导入脚本函数")
    def test_monitor_import_page_keeps_download_and_import_functions(self, auth_api, database_api, test_user):
        """校验基础数据导入页仍保留模板下载、Excel 导入和 XML 导出函数。"""
        self._login(auth_api, test_user)

        response = database_api.get_monitor_import_page()
        function_names = re.findall(r"function\s+(\w+)\(", response.text)
        assert "appendToken" in function_names
        assert "importExcel" in function_names
        assert "downExcel" in function_names
        assert "downXml" in function_names
        assert "getParams" in function_names
