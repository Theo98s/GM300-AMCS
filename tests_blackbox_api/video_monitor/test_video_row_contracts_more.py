# -*- coding: utf-8 -*-
"""More AMCS video row-level contract tests."""
from __future__ import annotations

import allure


@allure.feature("视频监控")
class TestVideoRowContractsMore:
    """Extra row-level checks for camera tree and preset lists."""

    @allure.title("视频树前五项 id 唯一且默认展开未勾选")
    def test_camera_tree_first_rows_keep_unique_open_unchecked_contract(self, auth_api, video_api, test_user):
        """Verify the first five camera-tree rows keep unique ids and the default open/unchecked state."""
        login_response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert login_response.json()["status"] == 0

        body = video_api.get_camera_tree().json()[:5]
        ids = [item["id"] for item in body]
        assert len(ids) == len(set(ids))
        for item in body:
            assert item["checked"] is False
            assert item["state"] == "open"

    @allure.title("预置位前五项通道号与视频树模型通道号保持一致")
    def test_first_preset_rows_keep_channel_alignment_with_camera_tree(self, auth_api, video_api, test_user):
        """Verify the first preset rows align with the first camera-tree models on channel numbers."""
        login_response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert login_response.json()["status"] == 0

        camera_rows = video_api.get_camera_tree().json()[:5]
        preset_rows = video_api.get_preset_cameras().json()["data"][:5]
        for camera_row, preset_row in zip(camera_rows, preset_rows):
            assert preset_row["channelNo"] == str(camera_row["model"]["channelNum"])
            assert preset_row["channelNo"].isdigit()

