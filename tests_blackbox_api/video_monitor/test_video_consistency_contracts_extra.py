# -*- coding: utf-8 -*-
"""Additional AMCS video cross-endpoint consistency tests."""
from __future__ import annotations

import allure


@allure.feature("Video Monitor")
class TestVideoConsistencyContractsExtra:
    """Extra consistency checks between camera-tree and preset-camera endpoints."""

    @staticmethod
    def _login(auth_api, test_user):
        """Log in once per test and assert the session is ready."""
        login_response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert login_response.status_code == 200
        assert login_response.json()["status"] == 0

    @staticmethod
    def _load_video_views(video_api):
        """Return the camera-tree list and preset-camera list in one place."""
        camera_nodes = video_api.get_camera_tree().json()
        preset_rows = video_api.get_preset_cameras().json()["data"]
        assert len(camera_nodes) > 0
        assert len(preset_rows) > 0
        return camera_nodes, preset_rows

    @allure.title("Camera tree and preset list keep matching record counts")
    def test_video_camera_tree_and_preset_list_keep_matching_counts(self, auth_api, video_api, test_user):
        """Verify the tree page and preset page still expose the same number of cameras."""
        self._login(auth_api, test_user)

        camera_nodes, preset_rows = self._load_video_views(video_api)
        assert len(camera_nodes) == len(preset_rows)

    @allure.title("Camera tree and preset list keep aligned identity ordering")
    def test_video_camera_tree_and_preset_list_keep_aligned_identity_order(
        self,
        auth_api,
        video_api,
        test_user,
    ):
        """Verify both endpoints stay aligned on camera id, display name, channel number, and NVR order."""
        self._login(auth_api, test_user)

        camera_nodes, preset_rows = self._load_video_views(video_api)
        for node, preset in zip(camera_nodes, preset_rows):
            model = node["model"]
            assert preset["id"] == node["id"]
            assert preset["equipName"] == node["text"]
            assert preset["text"] == model["name"]
            assert preset["channelNo"] == str(model["channelNum"])
            assert preset["nvrSerialNum"] == model["nvrSerialNum"]
