# -*- coding: utf-8 -*-
"""基础数据库通用异常与 HTTP 方法边界测试。"""
from __future__ import annotations

from pathlib import Path
import tempfile
import allure


class TestDatabaseAbnormalContractsMore:
    """补充校验基础数据库对空参数、非法 ID 和错误文件的兜底行为。"""

    @staticmethod
    def _login(auth_api, test_user):
        """统一执行登录，保证异常请求运行在已认证会话下。"""
        response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert response.status_code == 200
        assert response.json()["status"] == 0

    @allure.title("监控点删除前校验在空请求体下返回 400")
    def test_monitor_can_delete_empty_body_returns_http_400(self, auth_api, database_api, test_user):
        """校验删除前校验接口在空 ID 集合下不会伪成功，而是明确返回缺少请求体。"""
        self._login(auth_api, test_user)

        response = database_api.can_delete_monitor([])
        assert response.status_code == 400
        assert "Required request body is missing" in response.text
        assert "checkCanDeleteMonitor" in response.text

    @allure.title("监控点删除接口在空数组下保持幂等成功")
    def test_monitor_delete_empty_id_list_keeps_idempotent_success(self, auth_api, database_api, test_user):
        """校验批量删除接口在空数组下仍返回成功结果，便于前端直接透传空选择。"""
        self._login(auth_api, test_user)

        response = database_api.delete_monitor_by_ids([])
        assert response.status_code == 200

        body = response.json()
        assert body["status"] == 0
        assert body["message"] == "操作成功!"
        assert body["data"] is None

    @allure.title("监控点导入接口在上传非 Excel 文件时返回结构化校验错误")
    def test_monitor_import_rejects_non_excel_file_with_validation_message(self, auth_api, database_api, test_user):
        """校验导入接口在上传文本文件时不会 500，而是返回结构化导入失败提示。"""
        self._login(auth_api, test_user)

        with tempfile.NamedTemporaryFile(delete=False, suffix=".txt", mode="w", encoding="utf-8") as temp_file:
            temp_file.write("not excel")
            temp_path = temp_file.name

        try:
            response = database_api.import_excel("monitorImport.xls", temp_path)
            assert response.status_code == 200

            body = response.json()
            assert body["status"] == 0
            assert body["message"] == "导入出错:数据验证失败"
            assert isinstance(body["data"], list)
            assert len(body["data"]) > 0
            assert "InputStream" in body["data"][0]
        finally:
            Path(temp_path).unlink(missing_ok=True)

    @allure.title("监控点编辑页在非法 ID 下仍返回标准页面壳")
    def test_monitor_edit_page_invalid_id_still_returns_standard_html_shell(self, auth_api, database_api, test_user):
        """校验编辑页在非法监控点 ID 下仍能返回标准编辑页 HTML，而不是 500 错页。"""
        self._login(auth_api, test_user)

        response = database_api.get_monitor_edit_page("bad-id")
        assert response.status_code == 200
        assert "text/html" in response.headers.get("Content-Type", "")
        assert "<title>监控点编辑</title>" in response.text
        assert 'function appendToken()' in response.text


class TestDatabaseMethodBoundariesMore:
    """校验页面、导出和联动辅助接口使用非默认方法时的实际响应。"""

    @staticmethod
    def _login(auth_api, test_user):
        """先建立登录会话，避免接口响应被登录页替代。"""
        response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert response.status_code == 200
        assert response.json()["status"] == 0

    @staticmethod
    def _assert_empty_success(response):
        """统一校验方法探测接口返回成功状态和空响应体。"""
        assert response.status_code == 200
        assert response.content == b""

    @allure.title("监控点列表接口使用 OPTIONS 时返回空成功响应")
    def test_monitor_page_options_method_returns_empty_success(
        self,
        auth_api,
        request_util,
        config,
        test_user,
    ):
        """校验浏览器预检请求不会触发分页查询或服务端错误。"""
        self._login(auth_api, test_user)

        response = request_util.send_request(
            "options",
            config["database"]["monitor_page_url"],
        )

        self._assert_empty_success(response)

    @allure.title("监控点编辑页面使用 POST 时仍返回标准页面")
    def test_monitor_edit_page_post_method_keeps_html_shell(
        self,
        auth_api,
        request_util,
        config,
        test_user,
    ):
        """校验使用 POST 打开无效监控点编辑页时仍返回可渲染页面骨架。"""
        self._login(auth_api, test_user)

        response = request_util.send_request(
            "post",
            config["database"]["monitor_edit_page_url"],
            data={"id": "NO_SUCH_MONITOR_ID"},
        )

        assert response.status_code == 200
        assert "text/html" in response.headers.get("Content-Type", "")
        assert "<title>监控点编辑</title>" in response.text
        assert "var csrftoken" in response.text

    @allure.title("监控点导入页面使用 POST 时仍返回完整页面")
    def test_monitor_import_page_post_method_keeps_html_contract(
        self,
        auth_api,
        request_util,
        config,
        test_user,
    ):
        """校验导入页面兼容 POST 访问并保留页面标题和核心脚本。"""
        self._login(auth_api, test_user)

        response = request_util.send_request(
            "post",
            config["database"]["monitor_import_page_url"],
        )

        assert response.status_code == 200
        assert "text/html" in response.headers.get("Content-Type", "")
        assert "<title>导入页面</title>" in response.text
        assert "function importExcel" in response.text

    @allure.title("模板下载接口使用 POST 时返回空成功响应")
    def test_template_download_post_method_returns_empty_success(
        self,
        auth_api,
        request_util,
        config,
        test_user,
    ):
        """记录模板下载接口对 POST 的空响应行为，避免误判为文件下载成功。"""
        self._login(auth_api, test_user)

        response = request_util.send_request(
            "post",
            config["database"]["monitor_template_download_url"],
            data={"templateName": "monitor", "downloadName": "monitor"},
        )

        self._assert_empty_success(response)

    @allure.title("Excel 导出接口使用 POST 时返回空成功响应")
    def test_excel_export_post_method_returns_empty_success(
        self,
        auth_api,
        request_util,
        config,
        test_user,
    ):
        """校验导出接口错误使用 POST 时不会返回伪造的 Excel 文件内容。"""
        self._login(auth_api, test_user)

        response = request_util.send_request(
            "post",
            config["database"]["monitor_excel_export_url"],
            data={"templateName": "monitor", "downloadName": "monitor"},
        )

        self._assert_empty_success(response)

    @allure.title("联动关联设备接口使用 OPTIONS 时返回空成功响应")
    def test_related_equip_options_method_returns_empty_success(
        self,
        auth_api,
        request_util,
        config,
        test_user,
    ):
        """校验关联设备查询支持浏览器预检且不会返回业务数据。"""
        self._login(auth_api, test_user)

        response = request_util.send_request(
            "options",
            config["database"]["monitor_related_equip_url"],
        )

        self._assert_empty_success(response)

    @allure.title("联动摄像机接口使用 POST 时返回方法不支持")
    def test_camera_list_post_method_returns_405(
        self,
        auth_api,
        request_util,
        config,
        test_user,
    ):
        """校验摄像机只读接口严格限制为约定方法，错误方法不执行查询。"""
        self._login(auth_api, test_user)

        response = request_util.send_request(
            "post",
            config["database"]["monitor_camera_list_url"],
        )

        assert response.status_code == 405
        assert "Request method 'POST' not supported" in response.text

    @allure.title("联动预置位接口使用 POST 且缺参时返回空列表")
    def test_preset_list_post_without_params_returns_empty_list(
        self,
        auth_api,
        request_util,
        config,
        test_user,
    ):
        """校验预置位查询兼容 POST，缺少设备标识时安全退化为空列表。"""
        self._login(auth_api, test_user)

        response = request_util.send_request(
            "post",
            config["database"]["monitor_preset_list_url"],
        )

        assert response.status_code == 200
        assert "application/json" in response.headers.get("Content-Type", "")
        assert response.json() == []

    @allure.title("监控点 XML 导出接口使用 OPTIONS 时返回空成功响应")
    def test_monitor_xml_export_options_method_returns_empty_success(
        self,
        auth_api,
        request_util,
        config,
        test_user,
    ):
        """校验 XML 导出预检请求不会触发文件生成和下载。"""
        self._login(auth_api, test_user)

        response = request_util.send_request(
            "options",
            config["database"]["monitor_xml_export_url"],
        )

        self._assert_empty_success(response)
