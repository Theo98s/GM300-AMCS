# -*- coding: utf-8 -*-
"""图像识别配置接口功能测试。"""
from __future__ import annotations

import allure


@allure.feature("图像识别配置")
class TestImageRecognitionApi:
    """覆盖配置首页、分页列表、编辑页面和各级联字典接口。"""

    @staticmethod
    def _login(auth_api, test_user):
        """每条用例先登录，确保访问图像识别业务接口。"""
        response = auth_api.login(test_user["username"], test_user["password"])
        assert response.status_code == 200
        assert response.json()["status"] == 0

    @staticmethod
    def _assert_success_list(response):
        """统一校验图像识别字典接口的成功列表包装。"""
        assert response.status_code == 200
        body = response.json()
        assert body["code"] == 0
        assert body["msg"] == "操作成功"
        assert isinstance(body["data"], list)
        return body["data"]

    @allure.title("图像识别配置首页返回完整页面")
    def test_image_recognition_config_page(self, auth_api, image_recognition_api, test_user):
        """校验首页标题、分页地址和导入导出入口均存在。"""
        self._login(auth_api, test_user)

        response = image_recognition_api.get_config_page()

        assert response.status_code == 200
        assert "<title>图像识别配置首页</title>" in response.text
        assert "/imageRecognition/findPage" in response.text
        assert "/imageRecognition/importOrExport" in response.text

    @allure.title("图像识别配置列表返回标准分页结构")
    def test_image_recognition_page_contract(self, auth_api, image_recognition_api, test_user):
        """校验配置列表返回总数和数据行。"""
        self._login(auth_api, test_user)

        body = image_recognition_api.list_configs(rows=5).json()

        assert isinstance(body["total"], int)
        assert isinstance(body["rows"], list)
        assert len(body["rows"]) <= 5

    @allure.title("图像识别配置行包含设备、摄像机、预置位和识别类型")
    def test_image_recognition_row_contains_core_fields(
        self,
        auth_api,
        image_recognition_api,
        test_user,
    ):
        """校验首条配置具备列表展示和详情回查所需字段。"""
        self._login(auth_api, test_user)

        row = image_recognition_api.list_configs(rows=1).json()["rows"][0]

        assert set(row) >= {
            "id",
            "equipId",
            "equipName",
            "cameraId",
            "cameraName",
            "presetNum",
            "presetName",
            "recognitionType",
            "recognitionTypeName",
            "recognitionItems",
        }
        assert isinstance(row["recognitionItems"], list)

    @allure.title("图像识别类型字典返回可用类型")
    def test_image_recognition_type_list(self, auth_api, image_recognition_api, test_user):
        """校验识别类型代码、名称和显示文本可供新增页面使用。"""
        self._login(auth_api, test_user)

        rows = self._assert_success_list(image_recognition_api.list_recognition_types())

        assert rows
        assert set(rows[0]) >= {"id", "code", "name", "text", "typekey"}
        assert all(row["code"] and row["name"] for row in rows)

    @allure.title("已配置目标设备接口返回设备列表")
    def test_configured_equipment_list(self, auth_api, image_recognition_api, test_user):
        """校验查询筛选器可加载已有配置的设备标识和名称。"""
        self._login(auth_api, test_user)

        rows = self._assert_success_list(image_recognition_api.list_configured_equipment())

        assert rows
        assert set(rows[0]) >= {"equipId", "equipName"}

    @allure.title("无效设备不返回已配置摄像机")
    def test_unknown_equipment_has_no_configured_cameras(
        self,
        auth_api,
        image_recognition_api,
        test_user,
    ):
        """校验无效目标设备不会串出其他设备的摄像机配置。"""
        self._login(auth_api, test_user)

        rows = self._assert_success_list(
            image_recognition_api.list_configured_cameras("NO_SUCH_EQUIP_ID")
        )

        assert rows == []

    @allure.title("图像识别新增页面包含详情、校验和保存接口")
    def test_image_recognition_add_page_contains_core_actions(
        self,
        auth_api,
        image_recognition_api,
        test_user,
    ):
        """校验新增页面具备完整配置表单及三个核心接口地址。"""
        self._login(auth_api, test_user)

        response = image_recognition_api.get_edit_page()

        assert response.status_code == 200
        assert "<title>图像识别配置编辑页面</title>" in response.text
        assert "/imageRecognition/findConfigById" in response.text
        assert "/imageRecognition/validate" in response.text
        assert "/imageRecognition/saveOrUpdate" in response.text

    @allure.title("图像识别导入导出页面暴露 Excel 操作入口")
    def test_image_recognition_import_export_page(
        self,
        auth_api,
        image_recognition_api,
        test_user,
    ):
        """校验导入导出页面包含模板下载、文件导入和数据导出地址。"""
        self._login(auth_api, test_user)

        response = image_recognition_api.get_import_export_page()

        assert response.status_code == 200
        assert "<title>导入页面</title>" in response.text
        assert "/amcs/excel_2019/downloadTemp" in response.text
        assert "/amcs/excel_2019/import" in response.text
        assert "/amcs/excel_2019/export" in response.text

    @allure.title("新增配置可选择的被监测设备列表正常返回")
    def test_monitored_equipment_list(self, auth_api, image_recognition_api, test_user):
        """校验新增配置第一级设备下拉具有可用数据。"""
        self._login(auth_api, test_user)

        rows = self._assert_success_list(image_recognition_api.list_monitored_equipment())

        assert rows
        assert set(rows[0]) >= {"id", "text", "children"}
        assert rows[0]["id"] and rows[0]["text"]

    @allure.title("无效设备不返回新增配置摄像机")
    def test_unknown_equipment_has_no_available_cameras(
        self,
        auth_api,
        image_recognition_api,
        test_user,
    ):
        """校验新增级联查询对无效设备安全返回空列表。"""
        self._login(auth_api, test_user)

        rows = self._assert_success_list(
            image_recognition_api.list_equipment_cameras("NO_SUCH_EQUIP_ID")
        )

        assert rows == []

    @allure.title("无效设备不返回监控点识别项")
    def test_unknown_equipment_has_no_recognition_items(
        self,
        auth_api,
        image_recognition_api,
        test_user,
    ):
        """校验识别项级联接口不会返回其他设备监控点。"""
        self._login(auth_api, test_user)

        rows = self._assert_success_list(
            image_recognition_api.list_recognition_items("NO_SUCH_EQUIP_ID")
        )

        assert rows == []

    @allure.title("无效摄像机和预置位查询返回空识别绑定")
    def test_unknown_camera_and_preset_has_no_recognition_binding(
        self,
        auth_api,
        image_recognition_api,
        test_user,
    ):
        """校验不存在的摄像机预置位组合返回成功空数据。"""
        self._login(auth_api, test_user)

        response = image_recognition_api.get_type_by_camera_and_preset(
            "NO_SUCH_CAMERA_ID",
            "99999",
        )
        body = response.json()

        assert response.status_code == 200
        assert body["code"] == 0
        assert body["msg"] == "操作成功"
        assert body["data"] is None
