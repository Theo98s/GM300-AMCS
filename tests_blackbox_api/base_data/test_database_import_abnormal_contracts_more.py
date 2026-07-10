# -*- coding: utf-8 -*-
"""AMCS 基础数据库导入异常场景补充测试。"""
from __future__ import annotations

from pathlib import Path
import tempfile

import allure


@allure.feature("基础数据")
class TestDatabaseImportAbnormalContractsMore:
    """补充校验三类基础数据导入接口对错误文件的统一兜底行为。"""

    @staticmethod
    def _login(auth_api, test_user):
        """统一执行登录，保证导入异常请求使用有效会话。"""
        response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert response.status_code == 200
        assert response.json()["status"] == 0

    @staticmethod
    def _create_text_file() -> str:
        """创建一个非 Excel 临时文件，用于触发导入文件格式校验。"""
        with tempfile.NamedTemporaryFile(delete=False, suffix=".txt", mode="w", encoding="utf-8") as temp_file:
            temp_file.write("not excel")
            return temp_file.name

    @staticmethod
    def _assert_import_validation_error(response):
        """断言错误文件导入返回结构化校验失败结果。"""
        assert response.status_code == 200

        body = response.json()
        assert body["status"] == 0
        assert body["message"] == "导入出错:数据验证失败"
        assert isinstance(body["data"], list)
        assert len(body["data"]) > 0
        assert "InputStream" in body["data"][0]

    @allure.title("报警配置导入接口拒绝非 Excel 文件")
    def test_alarm_config_import_rejects_non_excel_file(self, auth_api, database_api, test_user):
        """校验报警配置导入接口上传文本文件时返回导入校验失败，而不是 500。"""
        self._login(auth_api, test_user)
        temp_path = self._create_text_file()

        try:
            response = database_api.import_excel("alarmImport.xls", temp_path)
            self._assert_import_validation_error(response)
        finally:
            Path(temp_path).unlink(missing_ok=True)

    @allure.title("联动配置导入接口拒绝非 Excel 文件")
    def test_linkage_config_import_rejects_non_excel_file(self, auth_api, database_api, test_user):
        """校验联动配置导入接口上传文本文件时返回导入校验失败，而不是 500。"""
        self._login(auth_api, test_user)
        temp_path = self._create_text_file()

        try:
            response = database_api.import_excel("linkageImport.xls", temp_path)
            self._assert_import_validation_error(response)
        finally:
            Path(temp_path).unlink(missing_ok=True)

    @allure.title("未知导入模板上传非 Excel 文件时仍返回结构化校验错误")
    def test_unknown_template_import_rejects_non_excel_file_with_structured_error(
        self,
        auth_api,
        database_api,
        test_user,
    ):
        """校验未知模板名配合错误文件时，接口仍返回统一的结构化导入失败结果。"""
        self._login(auth_api, test_user)
        temp_path = self._create_text_file()

        try:
            response = database_api.import_excel("unknownImport.xls", temp_path)
            self._assert_import_validation_error(response)
        finally:
            Path(temp_path).unlink(missing_ok=True)
