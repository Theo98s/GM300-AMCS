# -*- coding: utf-8 -*-
"""图像识别配置跨接口功能流程测试。"""
from __future__ import annotations

import json

import allure
import pytest


@allure.feature("图像识别配置")
class TestImageRecognitionFunctionalFlowsMore:
    """覆盖列表、详情、级联字典、识别项和监控点绑定一致性。"""

    @staticmethod
    def _login(auth_api, test_user):
        """先建立登录会话，确保所有级联查询复用相同权限。"""
        response = auth_api.login(test_user["username"], test_user["password"])
        assert response.status_code == 200
        assert response.json()["status"] == 0

    @staticmethod
    def _first_config(image_recognition_api):
        """获取首条图像识别配置作为只读流程样本。"""
        rows = image_recognition_api.list_configs(rows=1).json()["rows"]
        if not rows:
            pytest.skip("当前环境没有图像识别配置，跳过已有数据链路校验。")
        return rows[0]

    @staticmethod
    def _assert_success_list(response):
        """统一校验图像识别级联接口的成功列表包装。"""
        assert response.status_code == 200
        body = response.json()
        assert body["code"] == 0
        assert body["msg"] == "操作成功"
        assert isinstance(body["data"], list)
        return body["data"]

    @allure.title("图像识别列表与详情核心字段保持一致")
    def test_image_recognition_list_to_detail_consistency(
        self,
        auth_api,
        image_recognition_api,
        test_user,
    ):
        """校验列表标识可查询详情，设备、摄像机、预置位和识别类型一致。"""
        self._login(auth_api, test_user)
        row = self._first_config(image_recognition_api)

        body = image_recognition_api.get_detail(row["id"]).json()

        assert body["code"] == 0
        assert body["msg"] == "操作成功"
        detail = body["data"]
        for field in ("id", "equipId", "cameraId", "presetNum", "recognitionType"):
            assert detail[field] == row[field]
        assert detail["recognitionItems"] == row["recognitionItems"]

    @allure.title("图像识别详情参数保持可解析 JSON")
    def test_image_recognition_detail_params_are_parseable(
        self,
        auth_api,
        image_recognition_api,
        test_user,
    ):
        """校验识别算法参数可以解析，并保留掩膜数量和初始图片字段。"""
        self._login(auth_api, test_user)
        row = self._first_config(image_recognition_api)

        detail = image_recognition_api.get_detail(row["id"]).json()["data"]
        params = json.loads(detail["params"])

        assert isinstance(params, dict)
        assert params["maskNumber"] == detail["maskNumber"]
        assert isinstance(params["initialJpg"], str) and params["initialJpg"].endswith(".jpg")

    @allure.title("已配置设备可级联查询摄像机和预置位")
    def test_configured_equipment_camera_preset_chain(
        self,
        auth_api,
        image_recognition_api,
        test_user,
    ):
        """校验查询筛选器的设备、摄像机和预置位三级数据能够互相对应。"""
        self._login(auth_api, test_user)
        row = self._first_config(image_recognition_api)

        cameras = self._assert_success_list(
            image_recognition_api.list_configured_cameras(row["equipId"])
        )
        assert any(camera["cameraId"] == row["cameraId"] for camera in cameras)

        presets = self._assert_success_list(
            image_recognition_api.list_configured_presets(
                {"equipId": row["equipId"], "cameraId": row["cameraId"]}
            )
        )
        expected_preset_id = f'{row["cameraId"]}_{row["presetNum"]}'
        assert any(preset["presetId"] == expected_preset_id for preset in presets)

    @allure.title("新增配置设备可级联查询摄像机和预置位")
    def test_available_equipment_camera_preset_chain(
        self,
        auth_api,
        image_recognition_api,
        test_user,
    ):
        """校验新增表单可根据已有配置设备加载摄像机和候选预置位。"""
        self._login(auth_api, test_user)
        row = self._first_config(image_recognition_api)

        cameras = self._assert_success_list(
            image_recognition_api.list_equipment_cameras(row["equipId"])
        )
        assert any(camera["cameraId"] == row["cameraId"] for camera in cameras)

        presets = self._assert_success_list(
            image_recognition_api.list_presets(
                {"equipId": row["equipId"], "cameraId": row["cameraId"]}
            )
        )
        assert presets
        assert all(preset["id"] == row["cameraId"] for preset in presets)
        assert all(isinstance(preset["presetPointIndex"], int) for preset in presets)

    @allure.title("目标设备识别项包含配置已绑定监控点")
    def test_recognition_items_include_configured_monitor(
        self,
        auth_api,
        image_recognition_api,
        test_user,
    ):
        """校验配置详情中的识别项可在目标设备监控点列表中找到。"""
        self._login(auth_api, test_user)
        row = self._first_config(image_recognition_api)

        items = self._assert_success_list(
            image_recognition_api.list_recognition_items(row["equipId"])
        )
        monitor_ids = {item["monitorId"] for item in items}

        assert set(row["recognitionItems"]) <= monitor_ids
        assert all(item["equipId"] == row["equipId"] for item in items)

    @allure.title("摄像机预置位绑定结果与配置及监控点一致")
    def test_camera_preset_binding_matches_config_and_monitors(
        self,
        auth_api,
        image_recognition_api,
        test_user,
    ):
        """校验预置位反查的配置标识和监控点标识与列表数据一致。"""
        self._login(auth_api, test_user)
        row = self._first_config(image_recognition_api)

        body = image_recognition_api.get_type_by_camera_and_preset(
            row["cameraId"],
            row["presetNum"],
        ).json()

        assert body["code"] == 0
        assert body["data"]["imageRec"]["id"] == row["id"]
        assert body["data"]["imageRec"]["recognitionType"] == row["recognitionType"]
        monitor_ids = {monitor["id"] for monitor in body["data"]["monitor"]}
        assert set(row["recognitionItems"]) <= monitor_ids

    @allure.title("按识别类型筛选只返回对应配置")
    def test_image_recognition_filter_by_type(
        self,
        auth_api,
        image_recognition_api,
        test_user,
    ):
        """校验识别类型筛选条件生效且返回行类型一致。"""
        self._login(auth_api, test_user)
        row = self._first_config(image_recognition_api)

        body = image_recognition_api.list_configs(
            {"recognitionType": row["recognitionType"]},
            rows=50,
        ).json()

        assert body["rows"]
        assert all(item["recognitionType"] == row["recognitionType"] for item in body["rows"])

    @allure.title("不存在的识别类型筛选返回空分页")
    def test_image_recognition_unknown_type_returns_empty_page(
        self,
        auth_api,
        image_recognition_api,
        test_user,
    ):
        """校验无效识别类型不会命中已有图像识别配置。"""
        self._login(auth_api, test_user)

        body = image_recognition_api.list_configs(
            {"recognitionType": "NO_SUCH_RECOGNITION_TYPE"},
            rows=50,
        ).json()

        assert body == {"total": 0, "rows": []}

    @allure.title("已有图像识别配置可打开只读查看页面")
    def test_image_recognition_list_to_view_page(
        self,
        auth_api,
        image_recognition_api,
        test_user,
    ):
        """校验列表配置标识可传入查看页面并加载详情查询脚本。"""
        self._login(auth_api, test_user)
        row = self._first_config(image_recognition_api)

        response = image_recognition_api.get_edit_page(row["id"], view=True)

        assert response.status_code == 200
        assert row["id"] in response.text
        assert "/imageRecognition/findConfigById" in response.text
        assert "view=true" in response.url
