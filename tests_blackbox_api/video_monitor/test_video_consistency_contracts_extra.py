# -*- coding: utf-8 -*-
"""AMCS 视频跨接口一致性补充测试。"""
from __future__ import annotations

import allure


@allure.feature("Video Monitor")
class TestVideoConsistencyContractsExtra:
    """补充校验摄像机树接口与预置位摄像机接口的一致性。"""

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
    def _load_video_views(video_api):
        """统一返回摄像机树列表和预置位摄像机列表。"""
        camera_nodes = video_api.get_camera_tree().json()
        preset_rows = video_api.get_preset_cameras().json()["data"]
        assert len(camera_nodes) > 0
        assert len(preset_rows) > 0
        return camera_nodes, preset_rows

    @allure.title("摄像机树与预置位列表保持记录数量一致")
    def test_video_camera_tree_and_preset_list_keep_matching_counts(self, auth_api, video_api, test_user):
        """校验摄像机树页面和预置位页面仍暴露相同数量的摄像机。"""
        self._login(auth_api, test_user)

        camera_nodes, preset_rows = self._load_video_views(video_api)
        assert len(camera_nodes) == len(preset_rows)

    @allure.title("摄像机树与预置位列表保持标识顺序对齐")
    def test_video_camera_tree_and_preset_list_keep_aligned_identity_order(
        self,
        auth_api,
        video_api,
        test_user,
    ):
        """校验两个接口在摄像机 id、展示名称、通道号和 NVR 顺序上保持对齐。"""
        self._login(auth_api, test_user)

        camera_nodes, preset_rows = self._load_video_views(video_api)
        for node, preset in zip(camera_nodes, preset_rows):
            model = node["model"]
            assert preset["id"] == node["id"]
            assert preset["equipName"] == node["text"]
            assert preset["text"] == model["name"]
            assert preset["channelNo"] == str(model["channelNum"])
            assert preset["nvrSerialNum"] == model["nvrSerialNum"]
