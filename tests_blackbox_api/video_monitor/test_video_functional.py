# -*- coding: utf-8 -*-
"""视频监控跨接口功能流程测试。"""
from __future__ import annotations

import allure


class TestVideoFunctionalFlowsMore:
    """补充覆盖视频树和预置位摄像机列表之间的串联功能流。"""

    @staticmethod
    def _login(auth_api, test_user):
        """统一执行登录，保证两套视频接口复用同一会话。"""
        response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert response.status_code == 200
        assert response.json()["status"] == 0

    @staticmethod
    def _load_video_views(video_api):
        """同时加载视频树和预置位摄像机列表，并返回两边的原始数据。"""
        camera_tree = video_api.get_camera_tree().json()
        preset_body = video_api.get_preset_cameras().json()

        assert isinstance(camera_tree, list)
        assert len(camera_tree) > 0
        assert preset_body["status"] == 0
        assert isinstance(preset_body["data"], list)
        assert len(preset_body["data"]) > 0
        return camera_tree, preset_body["data"]

    @staticmethod
    def _pick_common_camera(camera_tree: list[dict], preset_rows: list[dict]) -> tuple[dict, dict]:
        """在视频树和预置位摄像机列表之间挑一条共同摄像机数据做对齐校验。"""
        tree_map = {node["id"]: node for node in camera_tree}
        preset_map = {row["id"]: row for row in preset_rows}
        common_ids = [camera_id for camera_id in preset_map if camera_id in tree_map]

        assert len(common_ids) > 0
        camera_id = common_ids[0]
        return tree_map[camera_id], preset_map[camera_id]

    @allure.title("同一登录会话可连续加载视频树和预置位摄像机列表")
    def test_single_login_session_can_load_camera_tree_and_preset_camera_list(
        self,
        auth_api,
        video_api,
        test_user,
    ):
        """登录一次后，连续访问视频树和预置位摄像机列表，并校验两边存在共同摄像机。"""
        self._login(auth_api, test_user)

        camera_tree, preset_rows = self._load_video_views(video_api)
        tree_node, preset_row = self._pick_common_camera(camera_tree, preset_rows)

        assert tree_node["id"] == preset_row["id"]
        assert tree_node["text"] == preset_row["equipName"]
        assert tree_node["model"]["name"] == preset_row["text"]

    @allure.title("共同摄像机在视频树和预置位列表中保持通道与 NVR 对齐")
    def test_common_camera_keeps_channel_and_nvr_alignment_across_video_views(
        self,
        auth_api,
        video_api,
        test_user,
    ):
        """校验共同摄像机在两套视频接口中返回的通道号和 NVR 序列号一致。"""
        self._login(auth_api, test_user)

        camera_tree, preset_rows = self._load_video_views(video_api)
        tree_node, preset_row = self._pick_common_camera(camera_tree, preset_rows)
        tree_model = tree_node["model"]

        assert preset_row["channelNo"] == str(tree_model["channelNum"])
        assert preset_row["nvrSerialNum"] == tree_model["nvrSerialNum"]
        assert tree_model["openClosed"] == "open"
        assert tree_node["state"] == "open"

    @allure.title("共同摄像机在两套视频视图中保持站点归属一致")
    def test_common_camera_keeps_same_station_identity_across_video_views(
        self,
        auth_api,
        video_api,
        test_user,
    ):
        """校验共同摄像机在视频树和预置位摄像机列表中的站点标识保持一致。"""
        self._login(auth_api, test_user)

        camera_tree, preset_rows = self._load_video_views(video_api)
        tree_node, preset_row = self._pick_common_camera(camera_tree, preset_rows)
        tree_model = tree_node["model"]

        assert tree_model["subId"] == preset_row["subId"]
        assert preset_row["subName"] is None or isinstance(preset_row["subName"], str)
        assert tree_model["text"] == tree_model["name"]
        assert preset_row["equipName"] == preset_row["text"]
