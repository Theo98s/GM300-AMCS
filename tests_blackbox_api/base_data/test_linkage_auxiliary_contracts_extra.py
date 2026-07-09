# -*- coding: utf-8 -*-
"""AMCS 联动辅助查询补充契约测试。"""
from __future__ import annotations

import re

import allure


@allure.feature("基础数据")
class TestLinkageAuxiliaryContractsExtra:
    """补充校验联动相关辅助查询接口契约。"""

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
    def _first_linkage_chain(database_api):
        """返回一组关联设备、摄像机与预置位链路，用于稳定性断言。"""
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

    @staticmethod
    def _assert_nullable_video_fields(entry: dict):
        """校验辅助查询结果里共用的可空视频字段契约。"""
        assert isinstance(entry["equipId"], str) and entry["equipId"]
        assert isinstance(entry["equipName"], str) and entry["equipName"]
        assert re.fullmatch(r"\d+-\d+", entry["valueField"])
        assert isinstance(entry["channelNo"], int)
        assert entry["channelNo"] >= 0
        assert isinstance(entry["moveable"], bool)
        assert entry["cameraName"] is None or isinstance(entry["cameraName"], str)
        assert entry["nvrSerialNum"] is None or isinstance(entry["nvrSerialNum"], str)
        assert entry["type"] is None or isinstance(entry["type"], str)

    @allure.title("联动关联设备行保留可空视频字段契约")
    def test_linkage_related_equip_rows_keep_expected_nullable_types(self, auth_api, database_api, test_user):
        """校验前几条关联设备记录保持稳定的可空类型和配对编码 valueField。"""
        self._login(auth_api, test_user)

        rows = database_api.query_related_equip_list().json()
        assert len(rows) > 0

        for row in rows[:5]:
            self._assert_nullable_video_fields(row)
            assert row["presetPointName"] is None or isinstance(row["presetPointName"], str)
            assert isinstance(row["presetPointIndex"], int)

    @allure.title("联动摄像机行保留标识与 valueField 对齐关系")
    def test_linkage_camera_row_keeps_identity_and_value_field_contract(self, auth_api, database_api, test_user):
        """校验联动摄像机记录仍保持当前自标识和按通道对齐的 valueField 结构。"""
        self._login(auth_api, test_user)

        related_equip, camera, _ = self._first_linkage_chain(database_api)
        camera_body = database_api.query_camera_list(related_equip["equipId"]).json()
        first_camera = camera_body["data"][0]

        self._assert_nullable_video_fields(first_camera)
        assert first_camera["id"] == camera["id"]
        assert first_camera["equipId"] == first_camera["id"]
        assert first_camera["valueField"] == f'{first_camera["channelNo"]}-0'
        assert first_camera["presetPointIndex"] == 0

    @allure.title("联动预置位行保留预置位索引与 valueField 对齐关系")
    def test_linkage_preset_row_keeps_preset_index_alignment(self, auth_api, database_api, test_user):
        """校验联动预置位记录仍把预置位索引编码在 valueField 中，供界面联动表单使用。"""
        self._login(auth_api, test_user)

        related_equip, camera, preset = self._first_linkage_chain(database_api)
        preset_list = database_api.query_preset_list(camera["id"], related_equip["equipId"]).json()
        first_preset = preset_list[0]

        self._assert_nullable_video_fields(first_preset)
        assert first_preset["equipId"] == camera["id"]
        assert first_preset["valueField"] == f'{first_preset["channelNo"]}-{first_preset["presetPointIndex"]}'
        assert isinstance(first_preset["presetPointName"], str)
        assert first_preset["presetPointName"]
        assert first_preset["presetPointIndex"] > 0

    @allure.title("联动辅助查询链路保留共享核心视频字段")
    def test_linkage_auxiliary_chain_keeps_core_video_fields_consistent(self, auth_api, database_api, test_user):
        """校验一组关联设备、摄像机和预置位链路保持一致的核心字段命名。"""
        self._login(auth_api, test_user)

        related_equip, camera, preset = self._first_linkage_chain(database_api)
        for entry in (related_equip, camera, preset):
            self._assert_nullable_video_fields(entry)

        # 预置位记录应回指所选摄像机，而摄像机记录自身则保持自引用标识。
        assert camera["equipId"] == camera["id"]
        assert preset["equipId"] == camera["id"]
        assert preset["valueField"].startswith(f'{preset["channelNo"]}-')
