# -*- coding: utf-8 -*-
"""图像识别配置导入导出功能测试。"""
from __future__ import annotations

import tempfile
from pathlib import Path
import allure


class TestImageRecognitionImportExportMore:
    """覆盖模板下载、数据导出和导出文件回灌导入。"""

    @staticmethod
    def _login(auth_api, test_user):
        """先建立登录会话，确保文件接口具备当前用户权限。"""
        response = auth_api.login(test_user["username"], test_user["password"])
        assert response.status_code == 200
        assert response.json()["status"] == 0

    @staticmethod
    def _assert_xls_response(response):
        """统一校验响应为可识别的旧版 Excel 文件。"""
        assert response.status_code == 200
        assert "application/vnd.ms-excel" in response.headers.get("Content-Type", "")
        assert "attachment" in response.headers.get("Content-Disposition", "")
        assert response.content.startswith(bytes.fromhex("D0CF11E0A1B11AE1"))
        assert len(response.content) > 1024

    @staticmethod
    def _snapshot(image_recognition_api):
        """记录当前图像识别配置总数和标识集合。"""
        body = image_recognition_api.list_configs(rows=200).json()
        return body["total"], sorted(row["id"] for row in body["rows"])

    @allure.title("图像识别配置导入模板可正常下载")
    def test_image_recognition_import_template_download(
        self,
        auth_api,
        image_recognition_api,
        test_user,
    ):
        """校验模板下载返回带附件头的有效 XLS 文件。"""
        self._login(auth_api, test_user)

        response = image_recognition_api.download_import_template()

        self._assert_xls_response(response)

    @allure.title("图像识别配置现有数据可正常导出")
    def test_image_recognition_config_export(
        self,
        auth_api,
        image_recognition_api,
        test_user,
    ):
        """校验当前配置导出为可供回灌使用的 XLS 文件。"""
        self._login(auth_api, test_user)

        response = image_recognition_api.export_configs()

        self._assert_xls_response(response)

    @allure.title("图像识别配置导出文件可回灌且不产生重复数据")
    def test_image_recognition_export_then_import_keeps_ids(
        self,
        auth_api,
        image_recognition_api,
        test_user,
    ):
        """导出当前配置后直接导入，并校验总数和配置标识集合保持不变。"""
        self._login(auth_api, test_user)
        before_total, before_ids = self._snapshot(image_recognition_api)
        export_response = image_recognition_api.export_configs()
        self._assert_xls_response(export_response)

        temp_path = None
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".xls") as temp_file:
                temp_file.write(export_response.content)
                temp_path = temp_file.name

            import_response = image_recognition_api.import_configs(temp_path)
            assert import_response.status_code == 200
            body = import_response.json()
            assert body["status"] == 0
            assert body["message"] == "导入完成！"
            assert isinstance(body["data"], list)

            after_total, after_ids = self._snapshot(image_recognition_api)
            assert after_total == before_total
            assert after_ids == before_ids
        finally:
            if temp_path:
                Path(temp_path).unlink(missing_ok=True)
