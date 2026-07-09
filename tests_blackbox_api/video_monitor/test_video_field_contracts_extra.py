# -*- coding: utf-8 -*-
"""AMCS 视频字段补充契约测试。"""
from __future__ import annotations

import allure


@allure.feature("视频监控")
class TestVideoFieldContractsExtra:
    """补充校验视频接口中的跨字段对齐关系。"""

    @staticmethod
    def _login(auth_api, test_user):
        """每条用例先登录，并确认会话已建立。"""
        login_response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert login_response.status_code == 200
        assert login_response.json()["status"] == 0

    @allure.title("摄像机树前几条记录保持节点与模型图标一致")
    def test_camera_tree_first_rows_keep_icon_alignment_with_model(self, auth_api, video_api, test_user):
        """校验前几条摄像机树记录的节点图标与模型图标保持一致。"""
        self._login(auth_api, test_user)

        rows = video_api.get_camera_tree().json()[:5]
        for row in rows:
            assert row["iconCls"] == row["model"]["iconCls"]
            assert row["text"] == row["model"]["text"]
            assert row["url"] == row["model"]["url"]

    @allure.title("预置位摄像机前几条记录保持 customCode 与图标字段稳定")
    def test_preset_cameras_first_rows_keep_custom_code_and_icon_contract(self, auth_api, video_api, test_user):
        """校验前几条预置位摄像机记录保持非空 customCode 和图标样式字段。"""
        self._login(auth_api, test_user)

        rows = video_api.get_preset_cameras().json()["data"][:5]
        for row in rows:
            assert isinstance(row["customCode"], str)
            assert row["customCode"]
            assert isinstance(row["iconCls"], str)
            assert row["iconCls"]
            assert "iconfont" in row["iconCls"]

    @allure.title("摄像机树与预置位列表前几条记录保持 customCode 对齐")
    def test_video_views_first_rows_keep_custom_code_alignment(self, auth_api, video_api, test_user):
        """校验前几条摄像机树模型类型与预置位列表 customCode 保持对齐。"""
        self._login(auth_api, test_user)

        camera_rows = video_api.get_camera_tree().json()[:5]
        preset_rows = video_api.get_preset_cameras().json()["data"][:5]
        for camera_row, preset_row in zip(camera_rows, preset_rows):
            assert preset_row["id"] == camera_row["id"]
            assert preset_row["customCode"] == camera_row["model"]["type"]
