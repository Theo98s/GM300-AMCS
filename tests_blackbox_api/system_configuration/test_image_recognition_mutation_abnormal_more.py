# -*- coding: utf-8 -*-
"""图像识别配置写接口安全异常测试。"""
from __future__ import annotations

import tempfile
from pathlib import Path

import allure


@allure.feature("图像识别配置")
class TestImageRecognitionMutationAbnormalMore:
    """覆盖空保存、无效删除及错误导入文件，确保不会新增配置。"""

    @staticmethod
    def _login(auth_api, test_user):
        """先建立登录会话，确保写接口异常响应来自业务服务。"""
        response = auth_api.login(test_user["username"], test_user["password"])
        assert response.status_code == 200
        assert response.json()["status"] == 0

    @staticmethod
    def _snapshot(image_recognition_api):
        """记录当前配置总数和标识集合，供异常操作前后比较。"""
        body = image_recognition_api.list_configs(rows=200).json()
        return body["total"], sorted(row["id"] for row in body["rows"])

    @allure.title("图像识别空配置保存被业务校验拒绝")
    def test_image_recognition_save_empty_config_keeps_existing_ids(
        self,
        auth_api,
        image_recognition_api,
        test_user,
    ):
        """提交空配置后校验错误提示，并确认没有生成新配置。"""
        self._login(auth_api, test_user)
        before = self._snapshot(image_recognition_api)

        response = image_recognition_api.save_config({})
        body = response.json()

        assert response.status_code == 200
        assert body == {
            "code": 1000,
            "msg": "识别项不能为空，请配置识别项！",
            "data": None,
        }
        assert self._snapshot(image_recognition_api) == before

    @allure.title("图像识别保存接口缺少请求体时返回业务校验失败")
    def test_image_recognition_save_missing_body_returns_validation_failure(
        self,
        auth_api,
        request_util,
        config,
        test_user,
    ):
        """校验无请求体保存不会触发空记录写入。"""
        self._login(auth_api, test_user)

        response = request_util.send_request(
            "post",
            config["image_recognition"]["save_url"],
        )

        assert response.status_code == 200
        assert response.json() == {
            "code": 1000,
            "msg": "识别项不能为空，请配置识别项！",
            "data": None,
        }

    @allure.title("图像识别批量删除缺少标识时返回成功空列表")
    def test_image_recognition_delete_missing_ids_is_idempotent(
        self,
        auth_api,
        image_recognition_api,
        test_user,
    ):
        """校验空批量删除不会影响任何已有图像识别配置。"""
        self._login(auth_api, test_user)
        before = self._snapshot(image_recognition_api)

        response = image_recognition_api.delete_by_ids([])

        assert response.status_code == 200
        assert response.json() == {"code": 0, "msg": "操作成功", "data": []}
        assert self._snapshot(image_recognition_api) == before

    @allure.title("删除不存在的图像识别配置保持幂等成功")
    def test_image_recognition_delete_unknown_id_is_idempotent(
        self,
        auth_api,
        image_recognition_api,
        test_user,
    ):
        """校验无效配置标识不会误删除现有图像识别数据。"""
        self._login(auth_api, test_user)
        before = self._snapshot(image_recognition_api)

        response = image_recognition_api.delete_by_ids(["NO_SUCH_CONFIG_ID"])

        assert response.status_code == 200
        assert response.json() == {"code": 0, "msg": "操作成功", "data": []}
        assert self._snapshot(image_recognition_api) == before

    @allure.title("图像识别导入缺少 multipart 文件时返回格式错误")
    def test_image_recognition_import_without_file_returns_multipart_error(
        self,
        auth_api,
        request_util,
        config,
        test_user,
    ):
        """校验只传模板名不会进入图像识别数据导入流程。"""
        self._login(auth_api, test_user)

        response = request_util.send_request(
            "post",
            config["database"]["monitor_excel_import_url"],
            params={"templateName": config["image_recognition"]["export_template_name"]},
        )

        assert response.status_code == 200
        assert response.text == "Current request is not a multipart request"

    @allure.title("图像识别导入拒绝伪造 Excel 文件")
    def test_image_recognition_import_rejects_invalid_excel(
        self,
        auth_api,
        image_recognition_api,
        test_user,
    ):
        """上传文本内容伪装的 Excel，并校验接口返回数据验证失败。"""
        self._login(auth_api, test_user)
        temp_path = None
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".xls") as temp_file:
                temp_file.write(b"not-an-excel-file")
                temp_path = temp_file.name

            response = image_recognition_api.import_configs(temp_path)
            body = response.json()
            assert response.status_code == 200
            assert body["status"] == 0
            assert body["message"] == "导入出错:数据验证失败"
            assert any("InputStream" in message for message in body["data"])
        finally:
            if temp_path:
                Path(temp_path).unlink(missing_ok=True)
