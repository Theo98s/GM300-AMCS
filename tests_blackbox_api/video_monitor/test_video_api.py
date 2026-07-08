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

    @allure.title("视频树节点包含图标地址与访问路径")
    def test_camera_tree_nodes_include_icon_and_url_fields(self, auth_api, video_api, test_user):
        """校验视频树首节点保留图标样式、访问路径和子节点字段。"""
        login_response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert login_response.json()["status"] == 0

        response = video_api.get_camera_tree()
        first_node = response.json()[0]

        assert "iconCls" in first_node
        assert "url" in first_node
        assert "children" in first_node
        assert isinstance(first_node["children"], list)

    @allure.title("视频树模型包含摄像机标识与类型字段")
    def test_camera_tree_model_contains_identity_fields(self, auth_api, video_api, test_user):
        """校验视频树模型保留摄像机 ID、名称、类型和父节点信息。"""
        login_response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert login_response.json()["status"] == 0

        response = video_api.get_camera_tree()
        first_model = response.json()[0]["model"]

        assert first_model["id"]
        assert first_model["name"]
        assert first_model["type"] is not None
        assert "pid" in first_model

    @allure.title("预置位摄像机列表包含站点与通道字段")
    def test_preset_cameras_contain_station_and_channel_fields(self, auth_api, video_api, test_user):
        """校验预置位摄像机列表保留站点、通道号和 NVR 序列号字段。"""
        login_response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert login_response.json()["status"] == 0

        response = video_api.get_preset_cameras()
        body = response.json()
        first_item = body["data"][0]

        assert "subId" in first_item
        assert "subName" in first_item
        assert "channelNo" in first_item
        assert "nvrSerialNum" in first_item
        assert first_item["channelNo"]

    @allure.title("视频树节点默认展开且模型类型非空")
    def test_camera_tree_nodes_are_open_and_model_type_present(self, auth_api, video_api, test_user):
        """校验视频树前几个节点默认展开，且模型类型字段非空。"""
        login_response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert login_response.json()["status"] == 0

        response = video_api.get_camera_tree()
        body = response.json()

        for node in body[:3]:
            assert node["state"] == "open"
            assert node["model"]["type"]

    @allure.title("预置位摄像机列表通道号使用字符串且轨道机标记为布尔值")
    def test_preset_cameras_channel_and_rail_machine_types_are_stable(self, auth_api, video_api, test_user):
        """校验预置位摄像机列表中的通道号和轨道机标记字段类型稳定。"""
        login_response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert login_response.json()["status"] == 0

        response = video_api.get_preset_cameras()
        first_item = response.json()["data"][0]

        assert isinstance(first_item["channelNo"], str)
        assert first_item["channelNo"].isdigit()
        assert isinstance(first_item["railMachine"], bool)

    @allure.title("视频树节点 ID 与模型 ID 保持一致")
    def test_camera_tree_node_id_matches_model_id(self, auth_api, video_api, test_user):
        """校验视频树节点的显示 ID 与模型内部 ID 保持一致。"""
        login_response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert login_response.json()["status"] == 0

        response = video_api.get_camera_tree()
        first_node = response.json()[0]

        assert first_node["id"] == first_node["model"]["id"]
        assert first_node["text"] == first_node["model"]["name"]

    @allure.title("预置位摄像机列表文本与设备名称保持一致")
    def test_preset_cameras_text_matches_equipment_name(self, auth_api, video_api, test_user):
        """校验预置位摄像机列表里的展示文本与设备名称一致。"""
        login_response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert login_response.json()["status"] == 0

        response = video_api.get_preset_cameras()
        first_item = response.json()["data"][0]

        assert first_item["id"]
        assert first_item["text"] == first_item["equipName"]

    @allure.title("First camera tree node keeps checked flag and open state")
    def test_camera_tree_first_node_checked_flag_and_state_are_stable(self, auth_api, video_api, test_user):
        """Verify the first camera-tree node remains unchecked, open, and without a direct page route."""
        login_response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert login_response.json()["status"] == 0

        response = video_api.get_camera_tree()
        first_node = response.json()[0]

        assert first_node["checked"] is False
        assert first_node["state"] == "open"
        assert first_node["url"] == ""

    @allure.title("First camera tree model keeps checked flag and open state")
    def test_camera_tree_first_model_checked_flag_and_state_are_stable(self, auth_api, video_api, test_user):
        """Verify the embedded camera model remains unchecked and open for tree rendering."""
        login_response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert login_response.json()["status"] == 0

        response = video_api.get_camera_tree()
        first_model = response.json()[0]["model"]

        assert first_model["checked"] is False
        assert first_model["state"] == "open"
        assert first_model["channelNum"] >= 1
