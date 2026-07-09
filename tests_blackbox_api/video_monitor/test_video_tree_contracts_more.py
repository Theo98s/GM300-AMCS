# -*- coding: utf-8 -*-
"""AMCS 视频树更多契约测试。"""
from __future__ import annotations

import allure


@allure.feature("视频监控")
class TestVideoTreeContractsMore:
    """补充校验摄像机树与预置位摄像机的一致性。"""

    @allure.title("视频树前几项模型类型保持非空并带模块前缀")
    def test_camera_tree_first_models_keep_expected_type_prefix(self, auth_api, video_api, test_user):
        """校验前几条摄像机模型的 type 字段保持非空并带有预期模块前缀。"""
        login_response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert login_response.json()["status"] == 0

        body = video_api.get_camera_tree().json()
        for node in body[:3]:
            assert node["model"]["type"].startswith("GM300_CAMS_SP_")

    @allure.title("预置位摄像机前几项轨道机字段保持布尔类型")
    def test_preset_camera_first_rows_keep_boolean_rail_machine_field(self, auth_api, video_api, test_user):
        """校验前几条预置位摄像机记录的 railMachine 字段保持布尔值。"""
        login_response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert login_response.json()["status"] == 0

        body = video_api.get_preset_cameras().json()["data"]
        for item in body[:5]:
            assert isinstance(item["railMachine"], bool)
