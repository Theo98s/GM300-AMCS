# -*- coding: utf-8 -*-
"""AMCS 预置位摄像机补充契约测试。"""
from __future__ import annotations

import allure


@allure.feature("视频监控")
class TestVideoPresetContractsMore:
    """补充校验预置位摄像机行级格式。"""

    @allure.title("预置位前五项展示文本与设备名保持一致")
    def test_preset_camera_first_rows_keep_text_and_name_alignment(self, auth_api, video_api, test_user):
        """校验前几条预置位记录的 text 与 equipName 保持一致。"""
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
        """校验前几条预置位记录的通道号保持数字字符串格式。"""
        login_response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert login_response.json()["status"] == 0

        rows = video_api.get_preset_cameras().json()["data"][:5]
        for row in rows:
            assert isinstance(row["channelNo"], str)
            assert row["channelNo"].isdigit()
