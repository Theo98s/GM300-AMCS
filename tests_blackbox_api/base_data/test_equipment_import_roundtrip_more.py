# -*- coding: utf-8 -*-
"""设备管理导出文件回灌与异常导入测试。"""
from __future__ import annotations

import tempfile
from pathlib import Path

import allure


@allure.feature("设备管理")
class TestEquipmentImportRoundtripMore:
    """校验设备导出文件可回灌，并拒绝伪造 Excel 内容。"""

    @staticmethod
    def _login(auth_api, test_user):
        """先建立登录会话，确保导入导出使用同一账号。"""
        response = auth_api.login(test_user["username"], test_user["password"])
        assert response.status_code == 200
        assert response.json()["status"] == 0

    @staticmethod
    def _snapshot(equipment_api):
        """记录设备总数和标识集合，供导入前后比较。"""
        body = equipment_api.list_equipment(rows=1000).json()
        return body["total"], sorted(row["id"] for row in body["rows"])

    @allure.title("设备导出文件可回灌且不产生重复设备")
    def test_equipment_export_then_import_keeps_ids(
        self,
        auth_api,
        equipment_api,
        test_user,
    ):
        """导出全部设备后直接导入，并确认总数和标识集合保持不变。"""
        self._login(auth_api, test_user)
        before_total, before_ids = self._snapshot(equipment_api)
        export_response = equipment_api.export_equipment()
        assert export_response.status_code == 200
        assert export_response.content.startswith(bytes.fromhex("D0CF11E0A1B11AE1"))

        temp_path = None
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".xls") as temp_file:
                temp_file.write(export_response.content)
                temp_path = temp_file.name

            import_response = equipment_api.import_equipment(temp_path)
            body = import_response.json()
            assert import_response.status_code == 200
            assert body["status"] == 0
            assert body["message"] == "导入完成！"
            assert isinstance(body["data"], list)

            after_total, after_ids = self._snapshot(equipment_api)
            assert after_total == before_total
            assert after_ids == before_ids
        finally:
            if temp_path:
                Path(temp_path).unlink(missing_ok=True)

    @allure.title("设备导入拒绝伪造 Excel 文件")
    def test_equipment_import_rejects_invalid_excel(
        self,
        auth_api,
        equipment_api,
        test_user,
    ):
        """上传文本内容伪装的 Excel，并校验接口返回数据验证失败。"""
        self._login(auth_api, test_user)
        temp_path = None
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".xls") as temp_file:
                temp_file.write(b"not-an-excel-file")
                temp_path = temp_file.name

            response = equipment_api.import_equipment(temp_path)
            body = response.json()
            assert response.status_code == 200
            assert body["status"] == 0
            assert body["message"] == "导入出错:数据验证失败！"
            assert body["data"] == ["上传的excel不符合规范"]
        finally:
            if temp_path:
                Path(temp_path).unlink(missing_ok=True)
