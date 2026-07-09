# -*- coding: utf-8 -*-
"""AMCS 视频运行时补充契约测试。"""
from __future__ import annotations

import re

import allure


@allure.feature("视频监控")
class TestVideoRuntimeContractsExtra:
    """补充校验视频树和预置位列表中的运行时默认值。"""

    @staticmethod
    def _login(auth_api, test_user):
        """每条用例先登录，并确认会话已建立。"""
        login_response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert login_response.status_code == 200
        assert login_response.json()["status"] == 0

    @allure.title("视频树前几条模型保持空父节点和空扩展编码字段")
    def test_camera_tree_first_models_keep_null_parent_and_extension_fields(self, auth_api, video_api, test_user):
        """校验前几条视频树模型仍保持空父节点、空扩展编码和可空备注字段。"""
        self._login(auth_api, test_user)

        rows = video_api.get_camera_tree().json()[:5]
        for row in rows:
            model = row["model"]
            assert model["pid"] is None
            assert model["subId"] is None
            assert model.get("customCode") is None
            assert model.get("remark") is None or isinstance(model.get("remark"), str)

    @allure.title("视频树前几条节点保持图标样式后缀和未勾选状态")
    def test_camera_tree_first_rows_keep_icon_style_suffix_and_unchecked_flag(self, auth_api, video_api, test_user):
        """校验前几条视频树节点仍保持图标样式后缀和未勾选状态。"""
        self._login(auth_api, test_user)

        rows = video_api.get_camera_tree().json()[:5]
        for row in rows:
            assert row["checked"] is False
            assert row["state"] == "open"
            assert row["iconCls"].startswith("iconfont ")
            assert row["iconCls"].endswith(" display")

    @allure.title("预置位前几条记录保持空状态字段和 NVR 序列号格式")
    def test_preset_cameras_first_rows_keep_null_state_fields_and_nvr_format(self, auth_api, video_api, test_user):
        """校验前几条预置位记录仍保持空状态字段和稳定 NVR 序列号格式。"""
        self._login(auth_api, test_user)

        rows = video_api.get_preset_cameras().json()["data"][:5]
        for row in rows:
            assert row.get("state") is None
            assert row.get("checked") is None
            assert row["moveable"] is False
            assert row["railMachine"] is False
            assert re.fullmatch(r"[A-Za-z0-9-]+", row["nvrSerialNum"])
