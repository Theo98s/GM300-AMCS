# -*- coding: utf-8 -*-
"""More AMCS video-tree contract tests."""
from __future__ import annotations

import allure


@allure.feature("视频监控")
class TestVideoTreeContractsMore:
    """Extra checks for camera-tree and preset-camera consistency."""

    @allure.title("视频树前几项模型类型保持非空并带模块前缀")
    def test_camera_tree_first_models_keep_expected_type_prefix(self, auth_api, video_api, test_user):
        """Verify the first few camera models keep non-empty type values with the expected module prefix."""
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
        """Verify the first few preset camera rows keep the railMachine field as a boolean."""
        login_response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert login_response.json()["status"] == 0

        body = video_api.get_preset_cameras().json()["data"]
        for item in body[:5]:
            assert isinstance(item["railMachine"], bool)

