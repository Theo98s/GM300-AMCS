# -*- coding: utf-8 -*-
"""基础数据库导入导出和请求格式异常测试。"""
from __future__ import annotations

import allure
from pathlib import Path
import tempfile


class TestDatabaseExportAbnormalContractsMore:
    """补充模板下载、导出和联动辅助查询的异常参数行为。"""

    @staticmethod
    def _login(auth_api, test_user):
        """每条用例先登录，保证异常断言不受权限拦截干扰。"""
        login_response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert login_response.status_code == 200
        assert login_response.json()["status"] == 0

    @staticmethod
    def _assert_empty_binary_response(response):
        """统一校验服务端对未知导出资源返回空响应体。"""
        assert response.status_code == 200
        assert response.content == b""
        assert response.headers.get("Content-Type") is None
        assert response.headers.get("Content-Disposition") is None

    @allure.title("模板下载接口缺少 templateName 时返回 400")
    def test_template_download_missing_template_name_returns_400(self, auth_api, request_util, config, test_user):
        """校验模板下载缺少必填模板名时返回明确参数错误。"""
        self._login(auth_api, test_user)

        response = request_util.send_request(
            "get",
            config["database"]["monitor_template_download_url"],
            allow_redirects=False,
        )

        assert response.status_code == 400
        assert "Required String parameter 'templateName' is not present" in response.text

    @allure.title("模板下载接口未知模板名时返回空响应")
    def test_template_download_unknown_template_returns_empty_response(
        self,
        auth_api,
        database_api,
        test_user,
    ):
        """校验不存在的模板文件不会返回错误页，而是返回 200 空体。"""
        self._login(auth_api, test_user)

        response = database_api.download_template("NO_SUCH_TEMPLATE", "bad.xls")

        self._assert_empty_binary_response(response)

    @allure.title("Excel 导出接口缺少导出参数时返回空响应")
    def test_excel_export_missing_params_returns_empty_response(self, auth_api, request_util, config, test_user):
        """校验导出接口缺少模板参数时保持 200 空体契约。"""
        self._login(auth_api, test_user)

        response = request_util.send_request(
            "get",
            config["database"]["monitor_excel_export_url"],
            allow_redirects=False,
        )

        self._assert_empty_binary_response(response)

    @allure.title("Excel 导出接口未知模板名时返回空响应")
    def test_excel_export_unknown_template_returns_empty_response(self, auth_api, database_api, test_user):
        """校验未知导出模板不会生成文件，也不会返回错误页。"""
        self._login(auth_api, test_user)

        response = database_api.export_excel("NO_SUCH_EXPORT", "bad.xls")

        self._assert_empty_binary_response(response)

    @allure.title("监控点 XML 导出接口使用 GET 方法时返回 405")
    def test_monitor_xml_export_get_method_returns_405(self, auth_api, request_util, config, test_user):
        """校验 XML 点表导出只接受 POST 方法，GET 会明确返回方法不支持。"""
        self._login(auth_api, test_user)

        response = request_util.send_request(
            "get",
            config["database"]["monitor_xml_export_url"],
            allow_redirects=False,
        )

        assert response.status_code == 405
        assert "Request method 'GET' not supported" in response.text

    @allure.title("联动摄像机查询使用未知设备 ID 时返回空数据")
    def test_linkage_camera_unknown_equip_id_returns_empty_data(self, auth_api, database_api, test_user):
        """校验不存在的关联设备 ID 不会报错，而是返回成功空列表。"""
        self._login(auth_api, test_user)

        response = database_api.query_camera_list("NO_SUCH_EQUIP_001")

        assert response.status_code == 200
        body = response.json()
        assert body["status"] == 0
        assert body["message"] == "成功"
        assert body["data"] == []

    @allure.title("联动预置位查询缺少参数时返回空列表")
    def test_linkage_preset_missing_params_returns_empty_list(self, auth_api, request_util, config, test_user):
        """校验预置位辅助查询缺少摄像机和关联设备参数时返回空列表。"""
        self._login(auth_api, test_user)

        response = request_util.send_request(
            "get",
            config["database"]["monitor_preset_list_url"],
        )

        assert response.status_code == 200
        assert response.json() == []

    @allure.title("联动预置位查询使用未知参数时返回空列表")
    def test_linkage_preset_unknown_params_returns_empty_list(self, auth_api, database_api, test_user):
        """校验不存在的摄像机和设备组合不会返回脏数据。"""
        self._login(auth_api, test_user)

        response = database_api.query_preset_list("NO_SUCH_CAMERA_001", "NO_SUCH_EQUIP_001")

        assert response.status_code == 200
        assert response.json() == []


class TestDatabaseImportAbnormalContractsMore:
    """补充校验三类基础数据导入接口对错误文件的统一兜底行为。"""

    @staticmethod
    def _login(auth_api, test_user):
        """统一执行登录，保证导入异常请求使用有效会话。"""
        response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert response.status_code == 200
        assert response.json()["status"] == 0

    @staticmethod
    def _create_text_file() -> str:
        """创建一个非 Excel 临时文件，用于触发导入文件格式校验。"""
        with tempfile.NamedTemporaryFile(delete=False, suffix=".txt", mode="w", encoding="utf-8") as temp_file:
            temp_file.write("not excel")
            return temp_file.name

    @staticmethod
    def _assert_import_validation_error(response):
        """断言错误文件导入返回结构化校验失败结果。"""
        assert response.status_code == 200

        body = response.json()
        assert body["status"] == 0
        assert body["message"] == "导入出错:数据验证失败"
        assert isinstance(body["data"], list)
        assert len(body["data"]) > 0
        assert "InputStream" in body["data"][0]

    @allure.title("报警配置导入接口拒绝非 Excel 文件")
    def test_alarm_config_import_rejects_non_excel_file(self, auth_api, database_api, test_user):
        """校验报警配置导入接口上传文本文件时返回导入校验失败，而不是 500。"""
        self._login(auth_api, test_user)
        temp_path = self._create_text_file()

        try:
            response = database_api.import_excel("alarmImport.xls", temp_path)
            self._assert_import_validation_error(response)
        finally:
            Path(temp_path).unlink(missing_ok=True)

    @allure.title("联动配置导入接口拒绝非 Excel 文件")
    def test_linkage_config_import_rejects_non_excel_file(self, auth_api, database_api, test_user):
        """校验联动配置导入接口上传文本文件时返回导入校验失败，而不是 500。"""
        self._login(auth_api, test_user)
        temp_path = self._create_text_file()

        try:
            response = database_api.import_excel("linkageImport.xls", temp_path)
            self._assert_import_validation_error(response)
        finally:
            Path(temp_path).unlink(missing_ok=True)

    @allure.title("未知导入模板上传非 Excel 文件时仍返回结构化校验错误")
    def test_unknown_template_import_rejects_non_excel_file_with_structured_error(
        self,
        auth_api,
        database_api,
        test_user,
    ):
        """校验未知模板名配合错误文件时，接口仍返回统一的结构化导入失败结果。"""
        self._login(auth_api, test_user)
        temp_path = self._create_text_file()

        try:
            response = database_api.import_excel("unknownImport.xls", temp_path)
            self._assert_import_validation_error(response)
        finally:
            Path(temp_path).unlink(missing_ok=True)


class TestDatabaseRequestFormatAbnormalMore:
    """校验列表、删除校验和导入接口收到错误请求格式时的响应。"""

    @staticmethod
    def _login(auth_api, test_user):
        """先完成登录，确保验证的是基础数据库接口本身。"""
        response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert response.status_code == 200
        assert response.json()["status"] == 0

    @allure.title("监控点列表收到损坏 JSON 时仍返回默认分页数据")
    def test_monitor_page_malformed_json_keeps_default_page_contract(
        self,
        auth_api,
        request_util,
        config,
        test_user,
    ):
        """校验列表接口忽略无法解析的 JSON，并保持分页响应结构。"""
        self._login(auth_api, test_user)

        response = request_util.send_request(
            "post",
            config["database"]["monitor_page_url"],
            data="{bad-json",
            headers={"Content-Type": "application/json"},
        )

        assert response.status_code == 200
        assert "application/json" in response.headers.get("Content-Type", "")
        body = response.json()
        assert isinstance(body["total"], int)
        assert isinstance(body["rows"], list)

    @allure.title("监控点删除前校验接口使用 GET 时返回方法不支持")
    def test_monitor_can_delete_get_method_returns_405(
        self,
        auth_api,
        request_util,
        config,
        test_user,
    ):
        """校验删除前校验只接受约定方法，错误方法不会触发业务处理。"""
        self._login(auth_api, test_user)

        response = request_util.send_request(
            "get",
            config["database"]["monitor_can_delete_url"],
        )

        assert response.status_code == 405
        assert "Request method 'GET' not supported" in response.text

    @allure.title("监控点删除前校验接收不存在标识时返回空依赖")
    def test_monitor_can_delete_plain_text_unknown_id_returns_empty_dependencies(
        self,
        auth_api,
        request_util,
        config,
        test_user,
    ):
        """校验不存在的监控点标识不会产生依赖数据，也不会修改任何记录。"""
        self._login(auth_api, test_user)

        response = request_util.send_request(
            "post",
            config["database"]["monitor_can_delete_url"],
            data="NO_SUCH_MONITOR_ID",
            headers={"Content-Type": "text/plain"},
        )

        assert response.status_code == 200
        assert response.json() == {
            "status": 0,
            "message": "数据查询成功!",
            "data": {"image": []},
        }

    @allure.title("Excel 导入接口缺少 multipart 文件时返回格式错误")
    def test_excel_import_without_multipart_file_returns_format_error(
        self,
        auth_api,
        request_util,
        config,
        test_user,
    ):
        """校验只传模板名但不上传文件时，接口返回明确的 multipart 错误。"""
        self._login(auth_api, test_user)

        response = request_util.send_request(
            "post",
            config["database"]["monitor_excel_import_url"],
            params={"templateName": "monitor"},
        )

        assert response.status_code == 200
        assert response.text == "Current request is not a multipart request"

    @allure.title("Excel 导入接口使用 GET 时返回 multipart 格式错误")
    def test_excel_import_get_method_returns_format_error(
        self,
        auth_api,
        request_util,
        config,
        test_user,
    ):
        """校验错误请求方法不会触发导入，并返回稳定的格式错误信息。"""
        self._login(auth_api, test_user)

        response = request_util.send_request(
            "get",
            config["database"]["monitor_excel_import_url"],
            params={"templateName": "monitor"},
        )

        assert response.status_code == 200
        assert response.text == "Current request is not a multipart request"
