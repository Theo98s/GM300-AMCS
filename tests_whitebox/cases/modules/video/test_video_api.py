# -*- coding: utf-8 -*-
"""AMCS 视频监控接口测试。"""
from __future__ import annotations

import allure


@allure.feature("视频监控")
class TestVideoApi:
    """摄像机树和预置位摄像机列表查询用例。"""

    @allure.title("视频树接口返回摄像机节点")
    def test_camera_tree_returns_nodes(self, auth_api, video_api, test_user):
        """校验视频树至少返回一条摄像机节点数据。"""
        login_response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert login_response.json()["status"] == 0

        response = video_api.get_camera_tree()
        assert response.status_code == 200

        body = response.json()
        assert isinstance(body, list)
        assert len(body) > 0
        first_node = body[0]
        assert set(first_node.keys()) >= {"id", "text", "state", "model"}

    @allure.title("视频树节点包含通道号和 NVR 序列号")
    def test_camera_tree_model_contains_channel_and_nvr(self, auth_api, video_api, test_user):
        """校验视频树模型里包含播放所需关键字段。"""
        login_response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert login_response.json()["status"] == 0

        response = video_api.get_camera_tree()
        first_model = response.json()[0]["model"]

        assert "channelNum" in first_model
        assert "nvrSerialNum" in first_model
        assert first_model["channelNum"] >= 1
        assert first_model["nvrSerialNum"]

    @allure.title("预置位摄像机列表返回设备名称")
    def test_preset_cameras_returns_camera_names(self, auth_api, video_api, test_user):
        """校验预置位摄像机列表可正常返回。"""
        login_response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert login_response.json()["status"] == 0

        response = video_api.get_preset_cameras()
        assert response.status_code == 200

        body = response.json()
        assert body["status"] == 0
        assert isinstance(body["data"], list)
        assert len(body["data"]) > 0
        assert "equipName" in body["data"][0]
