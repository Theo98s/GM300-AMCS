# -*- coding: utf-8 -*-
"""Additional AMCS base-data import/export contract tests."""
from __future__ import annotations

import xml.etree.ElementTree as element_tree

import allure


@allure.feature("Base Data")
class TestDatabaseTemplateContractsExtra:
    """Extra contract checks for base-data templates and export pages."""

    @staticmethod
    def _login(auth_api, test_user):
        """Log in once per test and assert the session is ready."""
        login_response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert login_response.status_code == 200
        assert login_response.json()["status"] == 0

    @staticmethod
    def _template_cases():
        """Return the three template kinds supported by the import/export page."""
        return [
            ("monitorImport.xls", "monitor"),
            ("alarmImport.xls", "alarm"),
            ("linkageImport.xls", "linkage"),
        ]

    @allure.title("Base-data template downloads keep Excel attachment headers")
    def test_database_template_downloads_keep_excel_attachment_contract(
        self,
        auth_api,
        database_api,
        test_user,
    ):
        """Verify monitor, alarm, and linkage templates stay downloadable Excel files."""
        self._login(auth_api, test_user)

        for template_name, download_name in self._template_cases():
            response = database_api.download_template(template_name, download_name)
            assert response.status_code == 200
            assert "application/vnd.ms-excel" in response.headers.get("Content-Type", "")
            assert "attachment" in response.headers.get("Content-Disposition", "").lower()
            assert len(response.content) > 10_000

    @allure.title("Base-data exports keep template-prefixed attachment names")
    def test_database_export_files_keep_expected_name_prefixes(self, auth_api, database_api, test_user):
        """Verify exported files still use the monitor/alarm/linkage filename prefixes."""
        self._login(auth_api, test_user)

        for template_name, download_name in self._template_cases():
            expected_prefix = template_name.replace("Import.xls", "")
            response = database_api.export_excel(template_name, download_name)
            assert response.status_code == 200

            content_disposition = response.headers.get("Content-Disposition", "").lower()
            assert "attachment" in content_disposition
            assert f"filename={expected_prefix}" in content_disposition
            assert content_disposition.endswith(".xls")

    @allure.title("Monitor XML export remains parseable UTF-8 config data")
    def test_monitor_xml_export_is_parseable_utf8_xml(self, auth_api, database_api, test_user):
        """Verify the XML point-table export remains a valid UTF-8 document with RTU and Item nodes."""
        self._login(auth_api, test_user)

        response = database_api.export_monitor_xml()
        assert response.status_code == 200
        assert "attachment" in response.headers.get("Content-Disposition", "").lower()
        assert ".xml" in response.headers.get("Content-Disposition", "").lower()

        # The endpoint declares a GB2312 content-type header, but the payload itself is UTF-8 XML.
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

    @allure.title("Base-data import page keeps stable template hooks")
    def test_monitor_import_page_exposes_stable_javascript_hooks(self, auth_api, database_api, test_user):
        """Verify the import page still exposes the template names and JS entry points used by operators."""
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
