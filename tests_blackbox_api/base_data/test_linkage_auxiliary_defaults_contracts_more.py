# -*- coding: utf-8 -*-
"""AMCS 联动辅助查询默认值补充契约测试。"""
from __future__ import annotations

import allure


@allure.feature("基础数据")
class TestLinkageAuxiliaryDefaultsContractsMore:
    """补充校验联动辅助查询中的默认值、空值和对齐关系。"""

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
    def _first_linkage_chain(database_api) -> tuple[dict, dict, dict]:
        """返回一组关联设备、摄像机与预置位链路，供稳定断言使用。"""
        related_equip_list = database_api.query_related_equip_list().json()
        assert len(related_equip_list) > 0
        related_equip = related_equip_list[0]

        camera_body = database_api.query_camera_list(related_equip["equipId"]).json()
        assert camera_body["status"] == 0
        assert len(camera_body["data"]) > 0
        camera = camera_body["data"][0]

        preset_list = database_api.query_preset_list(camera["id"], related_equip["equipId"]).json()
        assert len(preset_list) > 0
        preset = preset_list[0]
        return related_equip, camera, preset

    @allure.title("联动关联设备与摄像机首条记录保持默认预置位索引")
    def test_linkage_related_and_camera_rows_keep_zero_preset_defaults(self, auth_api, database_api, test_user):
        """校验关联设备和摄像机首条记录仍保持默认预置位索引和不可移动标记。"""
        self._login(auth_api, test_user)

        related_equip, camera, _ = self._first_linkage_chain(database_api)
        for entry in (related_equip, camera):
            assert entry["presetPointIndex"] == 0
            assert entry["valueField"].endswith("-0")
            assert entry["moveable"] is False
            assert entry["presetPointName"] is None

    @allure.title("联动预置位首条记录保持可回查的索引与标识字段")
    def test_linkage_preset_row_keeps_lookup_fields(self, auth_api, database_api, test_user):
        """校验预置位首条记录仍保留 cameraIndexCode、maId 和非零预置位索引。"""
        self._login(auth_api, test_user)

        related_equip, camera, preset = self._first_linkage_chain(database_api)
        assert preset["equipId"] == camera["id"]
        assert preset["equipName"] == camera["equipName"]
        assert preset["id"] is None
        assert isinstance(preset["cameraIndexCode"], str) and preset["cameraIndexCode"]
        assert isinstance(preset["maId"], str) and preset["maId"]
        assert preset["presetPointIndex"] > 0
        assert preset["valueField"].endswith(f'-{preset["presetPointIndex"]}')

    @allure.title("联动首条链路保持空摄像机名称与自引用摄像机标识")
    def test_linkage_first_chain_keeps_nullable_name_and_identity_alignment(self, auth_api, database_api, test_user):
        """校验首条联动链路中的摄像机名称空值和设备标识对齐关系。"""
        self._login(auth_api, test_user)

        related_equip, camera, preset = self._first_linkage_chain(database_api)
        assert related_equip["id"] is None
        assert related_equip["cameraName"] is None
        assert camera["id"] == camera["equipId"]
        assert camera["cameraName"] is None
        assert preset["cameraName"] is None
        assert preset["nvrSerialNum"] is None
