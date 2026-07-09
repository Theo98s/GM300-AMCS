# -*- coding: utf-8 -*-
"""AMCS 视频可空字段更多契约测试。"""
from __future__ import annotations

import allure


@allure.feature("视频监控")
class TestVideoNullableContractsMore:
    """补充校验视频接口中的可空字段和默认值模式。"""

    @staticmethod
    def _login(auth_api, test_user):
        """每条用例先登录，并确认会话已建立。"""
        login_response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert login_response.status_code == 200
        assert login_response.json()["status"] == 0

    @allure.title("摄像机树前几条记录保持空子节点和空站点标识")
    def test_camera_tree_first_rows_keep_empty_children_and_null_subid(self, auth_api, video_api, test_user):
        """校验前几条摄像机树记录保持空 children 和空 subId 模式。"""
        self._login(auth_api, test_user)

        rows = video_api.get_camera_tree().json()[:5]
        for row in rows:
            assert row["children"] == []
            assert row["model"]["children"] == []
            assert row["model"]["subId"] is None
            assert row["model"]["url"] == ""

    @allure.title("预置位摄像机前几条记录保持可空元数据字段")
    def test_preset_cameras_first_rows_keep_nullable_metadata_fields(self, auth_api, video_api, test_user):
        """校验前几条预置位摄像机记录保持当前可空元数据字段模式。"""
        self._login(auth_api, test_user)

        rows = video_api.get_preset_cameras().json()["data"][:5]
        for row in rows:
            assert row["typeName"] is None
            assert row["subId"] is None
            assert row["subName"] is None
            assert row["equipCode"] is None
            assert row["cameraIndexCode"] is None
            assert row["equipTypeCode"] is None
            assert row["ptypeName"] is None

    @allure.title("预置位摄像机前几条记录保持空子节点和默认布尔值")
    def test_preset_cameras_first_rows_keep_empty_children_and_false_flags(self, auth_api, video_api, test_user):
        """校验前几条预置位摄像机记录保持空 children 与默认布尔标记。"""
        self._login(auth_api, test_user)

        rows = video_api.get_preset_cameras().json()["data"][:5]
        for row in rows:
            assert row["children"] == []
            assert row["moveable"] is False
            assert row["railMachine"] is False
