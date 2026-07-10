# -*- coding: utf-8 -*-
"""巡检点位 CRUD 与跨接口功能流程测试。"""
from __future__ import annotations

import allure
import pytest
import time
import uuid


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


class TestPatrolPointCrudMore:
    """使用现有设备构造唯一巡检点位，并在用例结束时清理。"""

    @staticmethod
    def _login(auth_api, test_user):
        """先建立登录会话，确保写操作使用明确测试账号。"""
        response = auth_api.login(test_user["username"], test_user["password"])
        assert response.status_code == 200
        assert response.json()["status"] == 0

    @staticmethod
    def _unique_name(prefix: str) -> str:
        """生成可追踪且不会与现场配置重名的巡检点位名称。"""
        return f"{prefix}-{time.strftime('%H%M%S')}-{uuid.uuid4().hex[:6]}"

    @staticmethod
    def _all_points(patrol_point_api):
        """查询足够大的分页，供测试数据回查和清理使用。"""
        return patrol_point_api.list_points(rows=500).json()

    @classmethod
    def _build_payload(cls, patrol_point_api, name: str, reserved: set[int] | None = None):
        """基于现有巡检点位选择同摄像机下未占用的预置位编号。"""
        body = cls._all_points(patrol_point_api)
        if not body["rows"]:
            pytest.skip("当前环境没有可复用的巡检点位设备数据。")
        source = body["rows"][0]
        used = {
            int(row["presetNum"])
            for row in body["rows"]
            if row.get("monitorequipId") == source["monitorequipId"]
            and str(row.get("presetNum", "")).isdigit()
        }
        used.update(reserved or set())
        preset_num = next(value for value in range(300, 0, -1) if value not in used)
        return {
            "equipId": source["equipId"],
            "monitorequipId": source["monitorequipId"],
            "presetNum": str(preset_num),
            "presetName": name,
            "thermalparam": "",
            "refCameraId": "",
            "refPresetName": "",
            "refPresetNum": "",
            "refRuleId": "",
            "setPresetToNvr": "false",
        }

    @classmethod
    def _find_by_name(cls, patrol_point_api, name: str):
        """按测试生成的唯一名称回查巡检点位。"""
        return next(
            (row for row in cls._all_points(patrol_point_api)["rows"] if row["presetName"] == name),
            None,
        )

    @staticmethod
    def _cleanup(patrol_point_api, point_ids: list[str]):
        """删除本用例创建的巡检点位，避免污染测试环境。"""
        if point_ids:
            patrol_point_api.delete_by_ids(point_ids)

    @allure.title("巡检点位接口可新增并删除测试数据")
    def test_patrol_point_add_and_delete(self, auth_api, patrol_point_api, test_user):
        """新增唯一巡检点位，回查字段后删除并确认数据消失。"""
        self._login(auth_api, test_user)
        name = self._unique_name("AUTO-巡检点位新增")
        payload = self._build_payload(patrol_point_api, name)
        created_id = None

        try:
            response = patrol_point_api.save_point(payload)
            body = response.json()
            assert response.status_code == 200
            assert body["status"] == 0
            assert body["message"] == "保存成功。"
            created_id = body["data"]

            row = self._find_by_name(patrol_point_api, name)
            assert row is not None
            assert row["id"] == created_id
            assert row["equipId"] == payload["equipId"]
            assert row["monitorequipId"] == payload["monitorequipId"]
            assert row["presetNum"] == payload["presetNum"]
        finally:
            self._cleanup(patrol_point_api, [created_id] if created_id else [])

        assert self._find_by_name(patrol_point_api, name) is None

    @allure.title("巡检点位接口可修改名称并保持原标识")
    def test_patrol_point_update_keeps_id(self, auth_api, patrol_point_api, test_user):
        """先新增测试点位，再修改名称并确认列表中仅保留同一标识。"""
        self._login(auth_api, test_user)
        original_name = self._unique_name("AUTO-巡检点位修改前")
        updated_name = self._unique_name("AUTO-巡检点位修改后")
        payload = self._build_payload(patrol_point_api, original_name)
        created_id = None

        try:
            create_body = patrol_point_api.save_point(payload).json()
            assert create_body["status"] == 0
            created_id = create_body["data"]

            payload["presetName"] = updated_name
            update_body = patrol_point_api.save_point(payload, created_id).json()
            assert update_body["status"] == 0
            assert update_body["data"] == created_id

            assert self._find_by_name(patrol_point_api, original_name) is None
            updated_row = self._find_by_name(patrol_point_api, updated_name)
            assert updated_row is not None
            assert updated_row["id"] == created_id
        finally:
            self._cleanup(patrol_point_api, [created_id] if created_id else [])

    @allure.title("巡检点位接口支持批量删除测试数据")
    def test_patrol_point_batch_delete(self, auth_api, patrol_point_api, test_user):
        """新增两个不同预置位的测试点位，再通过逗号分隔标识一次清理。"""
        self._login(auth_api, test_user)
        first_name = self._unique_name("AUTO-巡检点位批量一")
        second_name = self._unique_name("AUTO-巡检点位批量二")
        first_payload = self._build_payload(patrol_point_api, first_name)
        second_payload = self._build_payload(
            patrol_point_api,
            second_name,
            reserved={int(first_payload["presetNum"])},
        )
        created_ids = []

        try:
            for payload in (first_payload, second_payload):
                body = patrol_point_api.save_point(payload).json()
                assert body["status"] == 0
                created_ids.append(body["data"])

            delete_response = patrol_point_api.delete_by_ids(created_ids)
            assert delete_response.status_code == 200
            assert delete_response.json() == {"status": 0, "message": "", "data": None}
            created_ids.clear()

            assert self._find_by_name(patrol_point_api, first_name) is None
            assert self._find_by_name(patrol_point_api, second_name) is None
        finally:
            self._cleanup(patrol_point_api, created_ids)

    @allure.title("巡检点位接口拒绝重复摄像机预置位编号")
    def test_patrol_point_rejects_duplicate_camera_preset(
        self,
        auth_api,
        patrol_point_api,
        test_user,
    ):
        """先新增点位，再用相同摄像机和编号保存另一名称并确认被拒绝。"""
        self._login(auth_api, test_user)
        first_name = self._unique_name("AUTO-巡检点位唯一一")
        duplicate_name = self._unique_name("AUTO-巡检点位唯一二")
        payload = self._build_payload(patrol_point_api, first_name)
        created_id = None

        try:
            first_body = patrol_point_api.save_point(payload).json()
            assert first_body["status"] == 0
            created_id = first_body["data"]

            duplicate_payload = dict(payload, presetName=duplicate_name)
            duplicate_body = patrol_point_api.save_point(duplicate_payload).json()
            assert duplicate_body == {
                "status": 1,
                "message": "操作失败",
                "data": "相机预置位已存在",
            }

            assert self._find_by_name(patrol_point_api, first_name) is not None
            assert self._find_by_name(patrol_point_api, duplicate_name) is None
        finally:
            self._cleanup(patrol_point_api, [created_id] if created_id else [])
