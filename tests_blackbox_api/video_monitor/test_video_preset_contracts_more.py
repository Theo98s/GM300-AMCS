# -*- coding: utf-8 -*-
"""Additional AMCS preset-camera contract tests."""
from __future__ import annotations

import allure


@allure.feature("视频监控")
class TestVideoPresetContractsMore:
    """Extra checks for preset-camera row formatting."""

    @allure.title("预置位前五项展示文本与设备名保持一致")
    def test_preset_camera_first_rows_keep_text_and_name_alignment(self, auth_api, video_api, test_user):
        """Verify the first few preset rows keep text aligned with equipName."""
        login_response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert login_response.json()["status"] == 0

        rows = video_api.get_preset_cameras().json()["data"][:5]
        for row in rows:
            assert row["text"] == row["equipName"]

    @allure.title("预置位前五项通道号保持数字字符串")
    def test_preset_camera_first_rows_keep_digit_channel_numbers(self, auth_api, video_api, test_user):
        """Verify the first few preset rows keep channel numbers as digit strings."""
        login_response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert login_response.json()["status"] == 0

        rows = video_api.get_preset_cameras().json()["data"][:5]
        for row in rows:
            assert isinstance(row["channelNo"], str)
            assert row["channelNo"].isdigit()

