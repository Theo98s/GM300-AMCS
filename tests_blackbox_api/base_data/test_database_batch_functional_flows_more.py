# -*- coding: utf-8 -*-
"""AMCS 基础数据库批量功能流补充测试。"""
from __future__ import annotations

from pathlib import Path

from .test_database_api import TestDatabaseApi as DatabaseApiHelper

import allure


@allure.feature("基础数据")
class TestDatabaseBatchFunctionalFlowsMore:
    """补充覆盖导入页、模板下载、导出回灌导入等批量操作场景。"""

    @staticmethod
    def _roundtrip_cases() -> list[tuple[str, str, str]]:
        """返回三类基础数据库导出再导入的测试参数。"""
        return [
            ("monitorImport.xls", "监控点", "成功新增"),
            ("alarmImport.xls", "报警配置", "成功新增"),
            ("linkageImport.xls", "联动配置", "成功保存"),
        ]

    @staticmethod
    def _template_cases() -> list[tuple[str, str]]:
        """返回三类基础数据库模板下载参数。"""
        return [
            ("monitorTemplate.xls", "监控点模板"),
            ("alarmTemplate.xls", "报警配置模板"),
            ("linkageTemplate.xls", "联动配置模板"),
        ]

    @allure.title("基础数据库导入页可驱动三类模板入口初始化")
    def test_database_import_page_can_bootstrap_three_template_entry_points(
        self,
        auth_api,
        database_api,
        test_user,
    ):
        """登录后打开基础数据导入页，校验三类模板和三类导入参数都已暴露。"""
        DatabaseApiHelper._login(auth_api, test_user)

        response = database_api.get_monitor_import_page()
        assert response.status_code == 200

        page_text = response.text
        for template_name, _ in self._template_cases():
            assert template_name in page_text
        for import_name, _, _ in self._roundtrip_cases():
            assert import_name in page_text

    @allure.title("基础数据库三类模板可在同一会话内连续下载")
    def test_database_operator_can_download_three_templates_in_single_session(
        self,
        auth_api,
        database_api,
        test_user,
    ):
        """登录一次后，连续下载监控点、报警配置和联动配置模板。"""
        DatabaseApiHelper._login(auth_api, test_user)

        for template_name, download_name in self._template_cases():
            response = database_api.download_template(template_name, download_name)
            assert response.status_code == 200
            assert len(response.content) > 0
            assert "attachment" in response.headers.get("Content-Disposition", "").lower()

    @allure.title("基础数据库三类导出文件可在同一会话内连续回灌导入")
    def test_database_operator_can_roundtrip_three_exported_datasets_in_single_session(
        self,
        auth_api,
        database_api,
        test_user,
    ):
        """依次导出监控点、报警配置和联动配置，再立即把导出文件回灌导入。"""
        DatabaseApiHelper._login(auth_api, test_user)

        temp_paths: list[str] = []
        try:
            for template_name, download_name, success_fragment in self._roundtrip_cases():
                temp_path = DatabaseApiHelper._export_excel_to_tempfile(
                    database_api,
                    template_name=template_name,
                    download_name=download_name,
                )
                temp_paths.append(temp_path)

                response = database_api.import_excel(template_name, temp_path)
                assert response.status_code == 200

                body = response.json()
                assert body["status"] == 0
                assert body["message"] == "导入完成！"
                assert isinstance(body["data"], list)
                assert len(body["data"]) > 0
                assert success_fragment in body["data"][0]
        finally:
            for temp_path in temp_paths:
                Path(temp_path).unlink(missing_ok=True)
