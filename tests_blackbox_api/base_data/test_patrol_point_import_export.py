# -*- coding: utf-8 -*-
"""巡检点位导入导出功能测试。"""
from __future__ import annotations

import tempfile
from pathlib import Path
import allure


class TestPatrolPointImportRoundtripMore:
    """校验现有巡检点位导出文件可导入且不会生成重复标识。"""

    @staticmethod
    def _login(auth_api, test_user):
        """先建立登录会话，确保导入导出使用同一账号。"""
        response = auth_api.login(test_user["username"], test_user["password"])
        assert response.status_code == 200
        assert response.json()["status"] == 0

    @staticmethod
    def _snapshot(patrol_point_api):
        """记录巡检点位总数和标识集合，供回灌前后比较。"""
        body = patrol_point_api.list_points(rows=500).json()
        return body["total"], sorted(row["id"] for row in body["rows"])

    @allure.title("巡检点位导出文件可回灌且不产生重复数据")
    def test_patrol_point_export_then_import_keeps_ids(
        self,
        auth_api,
        patrol_point_api,
        test_user,
    ):
        """导出所有巡检点位后直接导入，并确认总数和标识集合保持不变。"""
        self._login(auth_api, test_user)
        before_total, before_ids = self._snapshot(patrol_point_api)
        export_response = patrol_point_api.export_points(
            {"keyword": "", "cameraName": "", "equipName": ""}
        )
        assert export_response.status_code == 200
        assert export_response.content.startswith(bytes.fromhex("D0CF11E0A1B11AE1"))

        temp_path = None
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".xls") as temp_file:
                temp_file.write(export_response.content)
                temp_path = temp_file.name

            import_response = patrol_point_api.import_points(temp_path)
            body = import_response.json()
            assert import_response.status_code == 200
            assert body["status"] == 0
            assert body["message"] == "导入完成"
            assert isinstance(body["data"], list)

            after_total, after_ids = self._snapshot(patrol_point_api)
            assert after_total == before_total
            assert after_ids == before_ids
        finally:
            if temp_path:
                Path(temp_path).unlink(missing_ok=True)
