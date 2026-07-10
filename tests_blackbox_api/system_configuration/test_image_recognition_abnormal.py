# -*- coding: utf-8 -*-
"""图像识别配置异常参数、方法边界与写接口安全测试。"""
from __future__ import annotations

import allure
import tempfile
from pathlib import Path


class TestImageRecognitionAbnormalContracts:
    """覆盖错误分页、无效详情、空校验和损坏 JSON 场景。"""

    @staticmethod
    def _login(auth_api, test_user):
        """先建立登录会话，确保异常响应来自业务接口。"""
        response = auth_api.login(test_user["username"], test_user["password"])
        assert response.status_code == 200
        assert response.json()["status"] == 0

    @allure.title("图像识别 rows 传入非整数时返回校验错误")
    def test_image_recognition_page_rejects_invalid_rows(
        self,
        auth_api,
        request_util,
        config,
        test_user,
    ):
        """校验错误分页大小被查询对象参数校验拒绝。"""
        self._login(auth_api, test_user)

        response = request_util.send_request(
            "post",
            config["image_recognition"]["page_url"],
            data={"page": "1", "rows": "bad"},
        )

        assert response.status_code == 400
        assert "Validation failed" in response.text
        assert "imageRecognitionConfigQuery" in response.text

    @allure.title("图像识别 page 传入非整数时返回校验错误")
    def test_image_recognition_page_rejects_invalid_page(
        self,
        auth_api,
        request_util,
        config,
        test_user,
    ):
        """校验错误页码不会被静默转换为默认页。"""
        self._login(auth_api, test_user)

        response = request_util.send_request(
            "post",
            config["image_recognition"]["page_url"],
            data={"page": "bad", "rows": "1"},
        )

        assert response.status_code == 400
        assert "Validation failed" in response.text

    @allure.title("不存在的图像识别配置详情返回业务失败")
    def test_image_recognition_unknown_detail_returns_failure(
        self,
        auth_api,
        image_recognition_api,
        test_user,
    ):
        """校验无效配置标识不会返回其他配置详情。"""
        self._login(auth_api, test_user)

        body = image_recognition_api.get_detail("NO_SUCH_CONFIG_ID").json()

        assert body == {"code": 1000, "msg": "操作失败", "data": "操作失败"}

    @allure.title("空图像识别配置校验提示识别项不能为空")
    def test_image_recognition_validate_empty_payload_returns_prompt(
        self,
        auth_api,
        image_recognition_api,
        test_user,
    ):
        """校验空配置不会进入保存流程，并返回明确业务提示。"""
        self._login(auth_api, test_user)

        body = image_recognition_api.validate_config({}).json()

        assert body["code"] == 1
        assert body["msg"] == "识别项不能为空，请配置识别项！"
        assert body["data"] is None

    @allure.title("预置位查询收到损坏 JSON 时返回解析错误")
    def test_image_recognition_preset_rejects_malformed_json(
        self,
        auth_api,
        request_util,
        config,
        test_user,
    ):
        """校验无法解析的级联请求体被明确拒绝而不是返回错误数据。"""
        self._login(auth_api, test_user)

        response = request_util.send_request(
            "post",
            config["image_recognition"]["preset_url"],
            data="{bad-json",
            headers={"Content-Type": "application/json"},
        )

        assert response.status_code == 400
        assert "JSON parse error" in response.text
        assert "JsonParseException" in response.text


class TestImageRecognitionMethodContractsMore:
    """校验页面、分页、类型、详情和校验接口的方法边界。"""

    @staticmethod
    def _login(auth_api, test_user):
        """先建立登录会话，排除鉴权跳转对方法断言的影响。"""
        response = auth_api.login(test_user["username"], test_user["password"])
        assert response.status_code == 200
        assert response.json()["status"] == 0

    @allure.title("图像识别配置首页使用 POST 时仍返回完整页面")
    def test_image_recognition_config_post_keeps_html_contract(
        self,
        auth_api,
        request_util,
        config,
        test_user,
    ):
        """校验配置首页兼容 POST 并保留分页与导入导出入口。"""
        self._login(auth_api, test_user)

        response = request_util.send_request(
            "post",
            config["image_recognition"]["config_page_url"],
        )

        assert response.status_code == 200
        assert "<title>图像识别配置首页</title>" in response.text

    @allure.title("图像识别分页接口使用 OPTIONS 时返回空成功响应")
    def test_image_recognition_page_options_returns_empty_success(
        self,
        auth_api,
        request_util,
        config,
        test_user,
    ):
        """校验分页预检请求不会执行配置查询。"""
        self._login(auth_api, test_user)

        response = request_util.send_request(
            "options",
            config["image_recognition"]["page_url"],
        )

        assert response.status_code == 200
        assert response.content == b""

    @allure.title("图像识别类型接口使用 POST 时仍返回类型列表")
    def test_image_recognition_type_post_keeps_list_contract(
        self,
        auth_api,
        request_util,
        config,
        test_user,
    ):
        """校验识别类型字典兼容 POST 并保持标准成功包装。"""
        self._login(auth_api, test_user)

        response = request_util.send_request(
            "post",
            config["image_recognition"]["recognition_type_url"],
        )

        body = response.json()
        assert response.status_code == 200
        assert body["code"] == 0
        assert isinstance(body["data"], list)

    @allure.title("图像识别校验接口使用 GET 时返回方法不支持")
    def test_image_recognition_validate_get_returns_405(
        self,
        auth_api,
        request_util,
        config,
        test_user,
    ):
        """校验保存前校验接口拒绝 GET，避免空查询误触发业务逻辑。"""
        self._login(auth_api, test_user)

        response = request_util.send_request(
            "get",
            config["image_recognition"]["validate_url"],
        )

        assert response.status_code == 405
        assert "Request method 'GET' not supported" in response.text

    @allure.title("图像识别校验收到损坏 JSON 时返回识别项为空提示")
    def test_image_recognition_validate_malformed_json_returns_empty_item_prompt(
        self,
        auth_api,
        request_util,
        config,
        test_user,
    ):
        """记录校验接口当前将损坏 JSON 按空配置处理的兼容行为。"""
        self._login(auth_api, test_user)

        response = request_util.send_request(
            "post",
            config["image_recognition"]["validate_url"],
            data="{bad-json",
            headers={"Content-Type": "application/json"},
        )

        body = response.json()
        assert response.status_code == 200
        assert body["code"] == 1
        assert body["msg"] == "识别项不能为空，请配置识别项！"

    @allure.title("图像识别详情缺少配置标识时返回业务失败")
    def test_image_recognition_detail_missing_id_returns_failure(
        self,
        auth_api,
        request_util,
        config,
        test_user,
    ):
        """校验缺少详情主键不会返回任意已有图像识别配置。"""
        self._login(auth_api, test_user)

        response = request_util.send_request(
            "get",
            config["image_recognition"]["detail_url"],
        )

        assert response.status_code == 200
        assert response.json() == {"code": 1000, "msg": "操作失败", "data": "操作失败"}


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
