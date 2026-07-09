# -*- coding: utf-8 -*-
"""AMCS 视频监控补充契约测试。"""
from __future__ import annotations

import allure


@allure.feature("视频监控")
class TestVideoContractsExtra:
    """补充校验预置位摄像机与树结构返回的稳定性。"""

    @allure.title("预置位摄像机列表前几项 id 保持唯一")
    def test_preset_camera_ids_are_unique(self, auth_api, video_api, test_user):
        """校验预置位摄像机列表第一页结果的 id 保持唯一。"""
        login_response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert login_response.json()["status"] == 0

        body = video_api.get_preset_cameras().json()["data"]
        ids = [item["id"] for item in body]
        assert len(ids) == len(set(ids))

    @allure.title("预置位摄像机列表可空所亭字段保持可空字符串契约")
    def test_preset_camera_station_fields_keep_nullable_string_contract(self, auth_api, video_api, test_user):
        """校验预置位摄像机的站点相关字段在返回记录中保持可空字符串契约。"""
        login_response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert login_response.json()["status"] == 0

        body = video_api.get_preset_cameras().json()["data"]
        for item in body[:5]:
            assert item["subId"] is None or isinstance(item["subId"], str)
            assert item["subName"] is None or isinstance(item["subName"], str)
