# -*- coding: utf-8 -*-
"""AMCS 基础数据库导入导出补充契约测试。"""
from __future__ import annotations

import xml.etree.ElementTree as element_tree

import allure


@allure.feature("基础数据")
class TestDatabaseTemplateContractsExtra:
    """补充校验基础数据库模板与导出页面契约。"""

    @staticmethod
    def _login(auth_api, test_user):
        """每条用例先登录，并确认会话已建立。"""
        login_response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert login_response.status_code == 200
        assert login_response.json()["status"] == 0

    @staticmethod
    def _template_cases():
        """返回导入导出页面支持的三类模板。"""
        return [
            ("monitorImport.xls", "monitor"),
            ("alarmImport.xls", "alarm"),
            ("linkageImport.xls", "linkage"),
        ]

    @allure.title("基础数据模板下载保留 Excel 附件响应头")
    def test_database_template_downloads_keep_excel_attachment_contract(
        self,
        auth_api,
        database_api,
        test_user,
    ):
        """校验监控点、报警配置和联动配置模板仍可作为 Excel 文件下载。"""
        self._login(auth_api, test_user)

        for template_name, download_name in self._template_cases():
            response = database_api.download_template(template_name, download_name)
            assert response.status_code == 200
            assert "application/vnd.ms-excel" in response.headers.get("Content-Type", "")
            assert "attachment" in response.headers.get("Content-Disposition", "").lower()
            assert len(response.content) > 10_000

    @allure.title("基础数据导出文件保留模板前缀命名")
    def test_database_export_files_keep_expected_name_prefixes(self, auth_api, database_api, test_user):
        """校验导出文件仍使用 monitor、alarm、linkage 作为文件名前缀。"""
        self._login(auth_api, test_user)

        for template_name, download_name in self._template_cases():
            expected_prefix = template_name.replace("Import.xls", "")
            response = database_api.export_excel(template_name, download_name)
            assert response.status_code == 200

            content_disposition = response.headers.get("Content-Disposition", "").lower()
            assert "attachment" in content_disposition
            assert f"filename={expected_prefix}" in content_disposition
            assert content_disposition.endswith(".xls")

    @allure.title("监控点 XML 导出保持可解析的 UTF-8 配置数据")
    def test_monitor_xml_export_is_parseable_utf8_xml(self, auth_api, database_api, test_user):
        """校验 XML 点表导出仍是包含 RTU 和 Item 节点的合法 UTF-8 文档。"""
        self._login(auth_api, test_user)

        response = database_api.export_monitor_xml()
        assert response.status_code == 200
        assert "attachment" in response.headers.get("Content-Disposition", "").lower()
        assert ".xml" in response.headers.get("Content-Disposition", "").lower()

        # 接口响应头声明的是 GB2312，但实际 XML 载荷内容为 UTF-8 编码。
        root = element_tree.fromstring(response.content.decode("utf-8"))
        assert root.tag == "CONFIG"

        rtu_nodes = root.findall("./RTU")
        item_nodes = root.findall(".//Item")
        assert len(rtu_nodes) >= 1
        assert len(item_nodes) >= 1
        assert rtu_nodes[0].attrib["ADDR"]
        assert rtu_nodes[0].attrib["ProtocolName"]
        assert item_nodes[0].attrib["Name"]
        assert item_nodes[0].attrib["Reference"]

    @allure.title("基础数据导入页保留稳定的模板钩子")
    def test_monitor_import_page_exposes_stable_javascript_hooks(self, auth_api, database_api, test_user):
        """校验导入页仍暴露模板名称和操作页面依赖的脚本入口。"""
        self._login(auth_api, test_user)

        response = database_api.get_monitor_import_page()
        assert response.status_code == 200

        page_text = response.text
        assert "<title>导入页面</title>" in page_text
        assert "function importExcel(" in page_text
        assert "function downExcel(" in page_text
        assert "function downXml(" in page_text
        assert "monitorImport.xls" in page_text
        assert "alarmImport.xls" in page_text
        assert "linkageImport.xls" in page_text
