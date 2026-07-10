# -*- coding: utf-8 -*-
"""基础数据设备管理新增、修改和删除功能测试。"""
from __future__ import annotations

import uuid

import allure
import pytest


@allure.feature("设备管理")
class TestEquipmentCrudMore:
    """基于现有设备类型创建唯一测试设备，并在用例结束时清理。"""

    @staticmethod
    def _login(auth_api, test_user):
        """先建立登录会话，确保写操作使用明确测试账号。"""
        response = auth_api.login(test_user["username"], test_user["password"])
        assert response.status_code == 200
        assert response.json()["status"] == 0

    @staticmethod
    def _unique_name(prefix: str) -> str:
        """生成不会与现场设备重名的 ASCII 测试名称。"""
        return f"{prefix}-{uuid.uuid4().hex[:10]}"

    @staticmethod
    def _all_equipment(equipment_api):
        """查询完整设备分页，供测试数据回查和清理使用。"""
        return equipment_api.list_equipment(rows=1000).json()

    @classmethod
    def _build_payload(cls, equipment_api, name: str):
        """复用现有设备类型和区域构造最小可保存数据。"""
        rows = cls._all_equipment(equipment_api)["rows"]
        if not rows:
            pytest.skip("当前环境没有可复用的设备类型与区域数据。")
        source = rows[0]
        return {
            "action": "",
            "equipVersionType": "SB",
            "operationType": "1",
            "equipTypeId": source["equipTypeId"],
            "equipName": name,
            "c10": source.get("areacode") or "00",
            "equipCode": "",
            "c12": "",
            "hwxj": "0",
            "c4": "",
            "c5": "",
            "c6": "",
            "c7": "",
            "c8": "",
            "c9": "",
            "remark": "automation-test-equipment",
        }

    @classmethod
    def _find_by_name(cls, equipment_api, name: str):
        """按唯一名称回查测试设备。"""
        return next(
            (row for row in cls._all_equipment(equipment_api)["rows"] if row["equipName"] == name),
            None,
        )

    @staticmethod
    def _cleanup(equipment_api, equipment_ids: list[str]):
        """删除本用例创建的设备，避免污染测试环境。"""
        if equipment_ids:
            equipment_api.delete_by_ids(equipment_ids)

    @allure.title("设备管理接口可新增并删除测试设备")
    def test_equipment_add_and_delete(self, auth_api, equipment_api, test_user):
        """新增唯一设备，回查核心字段后删除并确认数据消失。"""
        self._login(auth_api, test_user)
        name = self._unique_name("AUTO-EQUIPMENT-ADD")
        payload = self._build_payload(equipment_api, name)
        created_id = None

        try:
            response = equipment_api.save_equipment(payload)
            body = response.json()
            assert response.status_code == 200
            assert body["status"] == 0
            assert body["message"] == "保存成功"
            created_id = body["data"]["id"]

            row = self._find_by_name(equipment_api, name)
            assert row is not None
            assert row["id"] == created_id
            assert row["equipTypeId"] == payload["equipTypeId"]
            assert row["areacode"] == payload["c10"]
            assert row["remark"] == payload["remark"]
        finally:
            self._cleanup(equipment_api, [created_id] if created_id else [])

        assert self._find_by_name(equipment_api, name) is None

    @allure.title("设备管理接口可修改名称并保持原标识")
    def test_equipment_update_keeps_id(self, auth_api, equipment_api, test_user):
        """先新增测试设备，再修改名称并确认仍为同一设备标识。"""
        self._login(auth_api, test_user)
        original_name = self._unique_name("AUTO-EQUIPMENT-BEFORE")
        updated_name = self._unique_name("AUTO-EQUIPMENT-AFTER")
        payload = self._build_payload(equipment_api, original_name)
        created_id = None

        try:
            create_body = equipment_api.save_equipment(payload).json()
            assert create_body["status"] == 0
            created_id = create_body["data"]["id"]

            payload["equipName"] = updated_name
            update_body = equipment_api.save_equipment(payload, created_id).json()
            assert update_body["status"] == 0
            assert update_body["data"]["id"] == created_id

            assert self._find_by_name(equipment_api, original_name) is None
            updated_row = self._find_by_name(equipment_api, updated_name)
            assert updated_row is not None
            assert updated_row["id"] == created_id
        finally:
            self._cleanup(equipment_api, [created_id] if created_id else [])

    @allure.title("设备管理接口拒绝重复设备名称")
    def test_equipment_rejects_duplicate_name(self, auth_api, equipment_api, test_user):
        """保存同名第二条设备时校验业务失败，且列表仅保留首条。"""
        self._login(auth_api, test_user)
        name = self._unique_name("AUTO-EQUIPMENT-DUP")
        payload = self._build_payload(equipment_api, name)
        created_id = None

        try:
            first_body = equipment_api.save_equipment(payload).json()
            assert first_body["status"] == 0
            created_id = first_body["data"]["id"]

            duplicate_body = equipment_api.save_equipment(payload).json()
            assert duplicate_body == {
                "status": 1,
                "message": "设备名称已被使用",
                "data": None,
            }

            matches = [
                row for row in self._all_equipment(equipment_api)["rows"]
                if row["equipName"] == name
            ]
            assert len(matches) == 1
            assert matches[0]["id"] == created_id
        finally:
            self._cleanup(equipment_api, [created_id] if created_id else [])
