# -*- coding: utf-8 -*-
"""巡检点位管理跨接口功能流程测试。"""
from __future__ import annotations

import allure
import pytest


@allure.feature("巡检点位管理")
class TestPatrolPointFunctionalFlowsMore:
    """覆盖列表、查看、预置位、删除校验和导出的完整只读链路。"""

    @staticmethod
    def _login(auth_api, test_user):
        """先建立登录会话，确保功能链路使用同一用户权限。"""
        response = auth_api.login(test_user["username"], test_user["password"])
        assert response.status_code == 200
        assert response.json()["status"] == 0

    @staticmethod
    def _first_point(patrol_point_api):
        """获取首条巡检点位作为只读链路样本。"""
        rows = patrol_point_api.list_points(rows=1).json()["rows"]
        if not rows:
            pytest.skip("当前环境没有巡检点位，跳过已有数据链路校验。")
        return rows[0]

    @allure.title("巡检点位可从列表进入只读查看页面")
    def test_patrol_point_list_to_readonly_page(
        self,
        auth_api,
        patrol_point_api,
        test_user,
    ):
        """校验列表标识可打开查看页，并保留巡检点位核心表单。"""
        self._login(auth_api, test_user)
        point = self._first_point(patrol_point_api)

        response = patrol_point_api.get_edit_page(point["id"], readonly=1)

        assert response.status_code == 200
        assert point["id"] in response.text
        assert point["presetName"] in response.text
        assert 'id="editForm"' in response.text

    @allure.title("巡检点位关联摄像机可查询已使用预置位")
    def test_patrol_point_camera_to_existing_preset_chain(
        self,
        auth_api,
        patrol_point_api,
        test_user,
    ):
        """校验列表中的摄像机能够反查到当前巡检点位的预置位。"""
        self._login(auth_api, test_user)
        point = self._first_point(patrol_point_api)

        body = patrol_point_api.list_existing_presets(point["monitorequipId"]).json()

        assert body["status"] == 0
        assert isinstance(body["data"], list)
        matched = next(item for item in body["data"] if item["id"] == point["id"])
        assert matched["monitorequipId"] == point["monitorequipId"]
        assert matched["presetNum"] == point["presetNum"]
        assert matched["presetName"] == point["presetName"]

    @allure.title("巡检点位删除前校验返回可识别依赖结果")
    def test_patrol_point_existing_row_can_delete_contract(
        self,
        auth_api,
        patrol_point_api,
        test_user,
    ):
        """校验已有点位删除校验返回代码和文字说明，但不执行实际删除。"""
        self._login(auth_api, test_user)
        point = self._first_point(patrol_point_api)

        body = patrol_point_api.can_delete([point]).json()

        assert body["status"] == 0
        assert body["message"] == "操作成功！"
        assert body["data"]["code"] in {0, 1}
        assert body["data"]["msg"] in {"可以删除", "不能删"}
        if body["data"]["code"] == 1:
            assert isinstance(body["data"]["reason"], list)
            assert body["data"]["reason"]

    @allure.title("不存在的巡检点位删除前校验允许幂等清理")
    def test_patrol_point_unknown_row_is_safe_to_delete(
        self,
        auth_api,
        patrol_point_api,
        test_user,
    ):
        """校验不存在标识不会产生虚假的巡检卡片或计划依赖。"""
        self._login(auth_api, test_user)

        body = patrol_point_api.can_delete([{"id": "NO_SUCH_POINT_ID"}]).json()

        assert body == {
            "status": 0,
            "message": "操作成功！",
            "data": {"msg": "可以删除", "code": 0},
        }

    @allure.title("巡检点位导出返回可识别的 Excel 文件")
    def test_patrol_point_export_returns_excel_file(
        self,
        auth_api,
        patrol_point_api,
        test_user,
    ):
        """校验空筛选导出具有 Excel 类型、附件头和旧版 XLS 文件头。"""
        self._login(auth_api, test_user)

        response = patrol_point_api.export_points(
            {"keyword": "", "cameraName": "", "equipName": ""}
        )

        assert response.status_code == 200
        assert "application/vnd.ms-excel" in response.headers.get("Content-Type", "")
        assert "attachment" in response.headers.get("Content-Disposition", "")
        assert response.content.startswith(bytes.fromhex("D0CF11E0A1B11AE1"))
        assert len(response.content) > 1024
