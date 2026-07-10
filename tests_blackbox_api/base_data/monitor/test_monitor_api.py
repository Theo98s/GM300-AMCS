# -*- coding: utf-8 -*-
"""监控点、报警配置和联动配置基础接口测试。"""
from __future__ import annotations

import html
import json
import re
import tempfile
import time
import uuid
from pathlib import Path
import allure


class TestDatabaseApi:
    """覆盖监控点、报警配置、联动配置的核心接口场景。"""

    @staticmethod
    def _login(auth_api, test_user):
        """统一执行登录，避免每条用例重复拼接登录断言。"""
        login_response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert login_response.status_code == 200
        assert login_response.json()["status"] == 0

    @staticmethod
    def _build_unique_text(prefix: str) -> str:
        """生成可追踪的唯一业务字段，方便测试后回查与清理。"""
        return f"{prefix}-{time.strftime('%H%M%S')}-{uuid.uuid4().hex[:6]}"

    @staticmethod
    def _find_monitor_by_fields(database_api, alarm_datatype: str, scada_addr10: str) -> dict | None:
        """按测试生成的唯一字段反查监控点。"""
        rows = database_api.list_monitors().json()["rows"]
        for row in rows:
            if row.get("alarmDatatype") == alarm_datatype and row.get("scadaAddr10") == scada_addr10:
                return row
        return None

    @staticmethod
    def _extract_hidden_json(html_text: str, field_id: str):
        """从编辑页隐藏 input 中提取并反序列化 JSON 内容。"""
        match = re.search(rf'id="{field_id}" value="([^"]*)"', html_text)
        assert match, f"编辑页未找到隐藏字段: {field_id}"
        raw_value = html.unescape(match.group(1))
        assert raw_value, f"隐藏字段 {field_id} 为空"
        return json.loads(raw_value)

    @staticmethod
    def _extract_hidden_value(html_text: str, field_id: str) -> str:
        """从编辑页隐藏 input 中提取原始 value，便于校验空字符串场景。"""
        match = re.search(rf'id="{field_id}" value="([^"]*)"', html_text)
        assert match, f"编辑页未找到隐藏字段: {field_id}"
        return html.unescape(match.group(1))

    @staticmethod
    def _build_base_monitor_payload(database_api) -> dict:
        """基于现网已存在的遥信监控点复制一份最小可保存数据。"""
        rows = database_api.list_monitors().json()["rows"]
        source_row = next(
            row for row in rows if row.get("alarmClass") == "01" and row.get("securityequiptype") == "06"
        )
        return {
            "id": "",
            "alarmClass": "01",
            "securityequiptype": source_row["securityequiptype"],
            "equipId": source_row["equipId"],
            "monitorDeviceId": "",
            "monitorDeviceName": "",
            "yx": source_row["yx"],
            "isStored": 0,
            "delConditionIds": "",
        }

    @staticmethod
    def _cleanup_monitor_if_exists(database_api, monitor_id: str | None):
        """测试结束时删除新增监控点，避免污染环境。"""
        if not monitor_id:
            return
        database_api.can_delete_monitor([monitor_id])
        database_api.delete_monitor_by_ids([monitor_id])

    @staticmethod
    def _download_template_to_tempfile(database_api, template_name: str, download_name: str) -> str:
        """把模板下载到临时文件，供导入接口直接复用。"""
        response = database_api.download_template(template_name, download_name)
        assert response.status_code == 200
        suffix = Path(template_name).suffix or ".xls"
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
            temp_file.write(response.content)
            return temp_file.name

    @staticmethod
    def _export_excel_to_tempfile(database_api, template_name: str, download_name: str) -> str:
        """先导出系统现有数据，再把导出文件保存到临时文件供回灌导入。"""
        response = database_api.export_excel(template_name, download_name)
        assert response.status_code == 200
        assert len(response.content) > 0
        suffix = Path(template_name).suffix or ".xls"
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
            temp_file.write(response.content)
            return temp_file.name

    @staticmethod
    def _get_existing_monitor_row(database_api) -> dict:
        """获取一条现网已有监控点，供编辑页和详情类接口复用。"""
        rows = database_api.list_monitors().json()["rows"]
        assert len(rows) > 0
        return rows[0]

    @staticmethod
    def _get_linkage_target(database_api) -> tuple[dict, dict, dict]:
        """获取联动配置保存所需的设备、摄像机和预置位样本。"""
        related_equip_list = database_api.query_related_equip_list().json()
        assert len(related_equip_list) > 0
        related_equip = related_equip_list[0]

        camera_body = database_api.query_camera_list(related_equip["equipId"]).json()
        assert camera_body["status"] == 0
        assert len(camera_body["data"]) > 0
        camera = camera_body["data"][0]

        preset_list = database_api.query_preset_list(camera["id"], related_equip["equipId"]).json()
        assert len(preset_list) > 0
        preset = preset_list[0]
        return related_equip, camera, preset

    @allure.title("监控点新增接口可保存新记录")
    def test_monitor_add(self, auth_api, database_api, test_user):
        """校验监控点新增接口可成功保存，并能在列表中查到新数据。"""
        self._login(auth_api, test_user)

        alarm_datatype = self._build_unique_text("AUTO-监控点")
        scada_addr10 = self._build_unique_text("ADDR")
        payload = self._build_base_monitor_payload(database_api)
        payload.update(
            {
                "alarmDatatype": alarm_datatype,
                "scadaAddr10": scada_addr10,
            }
        )

        created_monitor_id = None
        try:
            validate_response = database_api.validate_monitor(payload)
            assert validate_response.status_code == 200
            assert validate_response.json()["status"] == 0

            save_response = database_api.save_or_update_monitor(payload)
            assert save_response.status_code == 200
            assert save_response.json()["status"] == 0

            created_row = self._find_monitor_by_fields(database_api, alarm_datatype, scada_addr10)
            assert created_row is not None
            created_monitor_id = created_row["id"]
            assert created_row["alarmClass"] == "01"
        finally:
            self._cleanup_monitor_if_exists(database_api, created_monitor_id)

    @allure.title("监控点重复校验接口可拦截同设备属性名称")
    def test_monitor_validate_rejects_duplicate_device_property_name(self, auth_api, database_api, test_user):
        """先新增一条监控点，再校验保存前校验会拦截重复的设备属性名称。"""
        self._login(auth_api, test_user)

        alarm_datatype = self._build_unique_text("AUTO-重复校验")
        scada_addr10 = self._build_unique_text("ADDR")
        payload = self._build_base_monitor_payload(database_api)
        payload.update(
            {
                "alarmDatatype": alarm_datatype,
                "scadaAddr10": scada_addr10,
            }
        )

        created_monitor_id = None
        try:
            assert database_api.validate_monitor(payload).json()["status"] == 0
            assert database_api.save_or_update_monitor(payload).json()["status"] == 0

            created_row = self._find_monitor_by_fields(database_api, alarm_datatype, scada_addr10)
            assert created_row is not None
            created_monitor_id = created_row["id"]

            duplicate_response = database_api.validate_monitor(payload)
            assert duplicate_response.status_code == 200

            body = duplicate_response.json()
            assert body["status"] == 1
            assert body["message"] == "同一设备属性名称不能重复!"
        finally:
            self._cleanup_monitor_if_exists(database_api, created_monitor_id)

    @allure.title("监控点删除接口可删除新增记录")
    def test_monitor_delete(self, auth_api, database_api, test_user):
        """先新增一条监控点，再校验删除接口能够把它移除。"""
        self._login(auth_api, test_user)

        alarm_datatype = self._build_unique_text("AUTO-删除")
        scada_addr10 = self._build_unique_text("ADDR")
        payload = self._build_base_monitor_payload(database_api)
        payload.update(
            {
                "alarmDatatype": alarm_datatype,
                "scadaAddr10": scada_addr10,
            }
        )

        validate_response = database_api.validate_monitor(payload)
        assert validate_response.json()["status"] == 0

        save_response = database_api.save_or_update_monitor(payload)
        assert save_response.json()["status"] == 0

        created_row = self._find_monitor_by_fields(database_api, alarm_datatype, scada_addr10)
        assert created_row is not None

        can_delete_response = database_api.can_delete_monitor([created_row["id"]])
        assert can_delete_response.status_code == 200
        assert can_delete_response.json()["status"] == 0

        delete_response = database_api.delete_monitor_by_ids([created_row["id"]])
        assert delete_response.status_code == 200
        assert delete_response.json()["status"] == 0

        deleted_row = self._find_monitor_by_fields(database_api, alarm_datatype, scada_addr10)
        assert deleted_row is None

    @allure.title("监控点删除前校验支持批量监控点 ID")
    def test_monitor_can_delete_accepts_multiple_created_ids(self, auth_api, database_api, test_user):
        """新建两条监控点后，校验删除前检查接口可一次处理多个监控点 ID。"""
        self._login(auth_api, test_user)

        created_monitor_ids = []
        try:
            for index in range(2):
                alarm_datatype = self._build_unique_text(f"AUTO-批量校验{index}")
                scada_addr10 = self._build_unique_text("ADDR")
                payload = self._build_base_monitor_payload(database_api)
                payload.update(
                    {
                        "alarmDatatype": alarm_datatype,
                        "scadaAddr10": scada_addr10,
                    }
                )
                assert database_api.validate_monitor(payload).json()["status"] == 0
                assert database_api.save_or_update_monitor(payload).json()["status"] == 0

                created_row = self._find_monitor_by_fields(database_api, alarm_datatype, scada_addr10)
                assert created_row is not None
                created_monitor_ids.append(created_row["id"])

            response = database_api.can_delete_monitor(created_monitor_ids)
            assert response.status_code == 200

            body = response.json()
            assert body["status"] == 0
            assert body["message"] == "数据查询成功!"
            assert body["data"]["image"] == []
        finally:
            for monitor_id in created_monitor_ids:
                self._cleanup_monitor_if_exists(database_api, monitor_id)

    @allure.title("监控点删除接口支持批量删除新增记录")
    def test_monitor_delete_accepts_multiple_created_ids(self, auth_api, database_api, test_user):
        """新建两条监控点后，校验批量删除接口可一次删除两条记录。"""
        self._login(auth_api, test_user)

        created_monitor_ids = []
        created_fields = []
        try:
            for index in range(2):
                alarm_datatype = self._build_unique_text(f"AUTO-批量删除{index}")
                scada_addr10 = self._build_unique_text("ADDR")
                payload = self._build_base_monitor_payload(database_api)
                payload.update(
                    {
                        "alarmDatatype": alarm_datatype,
                        "scadaAddr10": scada_addr10,
                    }
                )
                assert database_api.validate_monitor(payload).json()["status"] == 0
                assert database_api.save_or_update_monitor(payload).json()["status"] == 0

                created_row = self._find_monitor_by_fields(database_api, alarm_datatype, scada_addr10)
                assert created_row is not None
                created_monitor_ids.append(created_row["id"])
                created_fields.append((alarm_datatype, scada_addr10))

            response = database_api.delete_monitor_by_ids(created_monitor_ids)
            assert response.status_code == 200

            body = response.json()
            assert body["status"] == 0
            assert body["message"] == "操作成功!"

            for alarm_datatype, scada_addr10 in created_fields:
                assert self._find_monitor_by_fields(database_api, alarm_datatype, scada_addr10) is None
            created_monitor_ids.clear()
        finally:
            for monitor_id in created_monitor_ids:
                self._cleanup_monitor_if_exists(database_api, monitor_id)

    @allure.title("监控点模板导入接口返回结构化结果")
    def test_monitor_import(self, auth_api, database_api, test_user):
        """先导出监控点数据，再回灌导入校验接口闭环可用。"""
        self._login(auth_api, test_user)

        temp_path = self._export_excel_to_tempfile(
            database_api,
            template_name="monitorImport.xls",
            download_name="监控点",
        )
        try:
            response = database_api.import_excel("monitorImport.xls", temp_path)
            assert response.status_code == 200

            body = response.json()
            assert body["status"] == 0
            assert body["message"] == "导入完成！"
            assert isinstance(body["data"], list)
            assert len(body["data"]) > 0
            assert "成功新增" in body["data"][0]
        finally:
            Path(temp_path).unlink(missing_ok=True)

    @allure.title("监控点导出接口返回文件流")
    def test_monitor_export(self, auth_api, database_api, test_user):
        """校验监控点导出接口能返回 Excel 文件流。"""
        self._login(auth_api, test_user)

        response = database_api.export_excel("monitorImport.xls", "监控点")
        assert response.status_code == 200
        assert len(response.content) > 0
        assert "attachment" in response.headers.get("Content-Disposition", "")

    @allure.title("三类基础数据库导出接口返回 Excel 内容类型")
    def test_database_exports_use_excel_content_type(self, auth_api, database_api, test_user):
        """依次校验监控点、报警配置和联动配置导出接口都返回 Excel 内容类型。"""
        self._login(auth_api, test_user)

        export_cases = [
            ("monitorImport.xls", "监控点"),
            ("alarmImport.xls", "报警配置"),
            ("linkageImport.xls", "联动配置"),
        ]
        for template_name, download_name in export_cases:
            response = database_api.export_excel(template_name, download_name)
            assert response.status_code == 200
            assert "application/vnd.ms-excel" in response.headers.get("Content-Type", "")
            assert "attachment" in response.headers.get("Content-Disposition", "").lower()

    @allure.title("监控点列表接口返回标准字段")
    def test_monitor_list_returns_standard_fields(self, auth_api, database_api, test_user):
        """校验监控点列表接口可返回至少一条带关键字段的记录。"""
        self._login(auth_api, test_user)

        response = database_api.list_monitors()
        assert response.status_code == 200

        body = response.json()
        assert isinstance(body, dict)
        assert "rows" in body
        assert isinstance(body["rows"], list)
        assert len(body["rows"]) > 0

        first_row = body["rows"][0]
        assert set(first_row.keys()) >= {
            "id",
            "equipId",
            "equipName",
            "alarmDatatype",
            "alarmClass",
            "securityequiptype",
        }
        assert first_row["id"]
        assert first_row["equipName"]

    @allure.title("监控点列表可按唯一字段精确筛选新增记录")
    def test_monitor_list_can_filter_by_unique_fields(self, auth_api, database_api, test_user):
        """新增监控点后，校验列表接口可按业务唯一字段精确筛选出该记录。"""
        self._login(auth_api, test_user)

        alarm_datatype = self._build_unique_text("AUTO-筛选")
        scada_addr10 = self._build_unique_text("ADDR")
        payload = self._build_base_monitor_payload(database_api)
        payload.update(
            {
                "alarmDatatype": alarm_datatype,
                "scadaAddr10": scada_addr10,
            }
        )

        created_monitor_id = None
        try:
            assert database_api.validate_monitor(payload).json()["status"] == 0
            assert database_api.save_or_update_monitor(payload).json()["status"] == 0

            created_row = self._find_monitor_by_fields(database_api, alarm_datatype, scada_addr10)
            assert created_row is not None
            created_monitor_id = created_row["id"]

            response = database_api.list_monitors(
                {
                    "alarmDatatype": alarm_datatype,
                    "scadaAddr10": scada_addr10,
                }
            )
            assert response.status_code == 200

            body = response.json()
            assert body["total"] >= 1
            assert len(body["rows"]) >= 1
            assert any(
                row.get("alarmDatatype") == alarm_datatype and row.get("scadaAddr10") == scada_addr10
                for row in body["rows"]
            )
        finally:
            self._cleanup_monitor_if_exists(database_api, created_monitor_id)

    @allure.title("监控点列表对不存在筛选条件返回空结果")
    def test_monitor_list_returns_empty_rows_for_nonexistent_filter(self, auth_api, database_api, test_user):
        """校验监控点列表在不存在的业务字段筛选下返回空列表而不是报错。"""
        self._login(auth_api, test_user)

        response = database_api.list_monitors({"alarmDatatype": "NO_SUCH_AUTO_CASE_001"})
        assert response.status_code == 200

        body = response.json()
        assert body["total"] == 0
        assert body["rows"] == []

    @allure.title("监控点列表分页参数可限制返回条数")
    def test_monitor_list_respects_rows_pagination_parameter(self, auth_api, database_api, test_user):
        """校验监控点列表在 rows=1 时最多只返回一条记录。"""
        self._login(auth_api, test_user)

        response = database_api.list_monitors(page=1, rows=1)
        assert response.status_code == 200

        body = response.json()
        assert body["total"] >= 1
        assert len(body["rows"]) <= 1

    @allure.title("监控点列表翻页后返回不同记录")
    def test_monitor_list_second_page_returns_different_record(self, auth_api, database_api, test_user):
        """校验监控点列表在总数大于一条时，第二页能返回与第一页不同的记录。"""
        self._login(auth_api, test_user)

        first_page_response = database_api.list_monitors(page=1, rows=1)
        second_page_response = database_api.list_monitors(page=2, rows=1)
        assert first_page_response.status_code == 200
        assert second_page_response.status_code == 200

        first_page_body = first_page_response.json()
        second_page_body = second_page_response.json()
        assert first_page_body["total"] > 1
        assert len(first_page_body["rows"]) == 1
        assert len(second_page_body["rows"]) == 1
        assert first_page_body["rows"][0]["id"] != second_page_body["rows"][0]["id"]

    @allure.title("监控点列表在总数充足时返回指定页大小")
    def test_monitor_list_returns_requested_page_size_when_total_allows(self, auth_api, database_api, test_user):
        """校验监控点列表在总数大于页大小时，会按 rows 参数返回指定数量的记录。"""
        self._login(auth_api, test_user)

        response = database_api.list_monitors(page=1, rows=2)
        assert response.status_code == 200

        body = response.json()
        assert body["total"] >= 2
        assert len(body["rows"]) == 2

    @allure.title("监控点列表超出总页数时返回空结果")
    def test_monitor_list_returns_empty_rows_for_out_of_range_page(self, auth_api, database_api, test_user):
        """校验监控点列表在超出总页数的分页参数下返回空列表而不是报错。"""
        self._login(auth_api, test_user)

        response = database_api.list_monitors(page=100, rows=20)
        assert response.status_code == 200

        body = response.json()
        assert body["total"] >= 0
        assert body["rows"] == []

    @allure.title("监控点导入页包含三类导入导出配置")
    def test_monitor_import_page_contains_expected_sections(self, auth_api, database_api, test_user):
        """校验导入页已挂载监控点、报警配置和联动配置三类入口。"""
        self._login(auth_api, test_user)

        response = database_api.get_monitor_import_page()
        assert response.status_code == 200

        page_text = response.text
        assert "monitorTemplate.xls" in page_text
        assert "alarmTemplate.xls" in page_text
        assert "linkageTemplate.xls" in page_text
        assert "monitorImport.xls" in page_text
        assert "alarmImport.xls" in page_text
        assert "linkageImport.xls" in page_text

    @allure.title("监控点三类模板下载接口返回文件流")
    def test_monitor_template_downloads(self, auth_api, database_api, test_user):
        """依次校验监控点、报警配置和联动配置模板都可以正常下载。"""
        self._login(auth_api, test_user)

        template_cases = [
            ("monitorTemplate.xls", "监控点模板"),
            ("alarmTemplate.xls", "报警配置模板"),
            ("linkageTemplate.xls", "联动配置模板"),
        ]
        for template_name, download_name in template_cases:
            response = database_api.download_template(template_name, download_name)
            assert response.status_code == 200
            assert len(response.content) > 0
            assert "application/vnd.ms-excel" in response.headers.get("Content-Type", "")

    @allure.title("监控点三类模板下载响应包含附件头")
    def test_monitor_template_downloads_include_attachment_headers(self, auth_api, database_api, test_user):
        """校验三类模板下载接口都通过附件响应头返回可下载文件。"""
        self._login(auth_api, test_user)

        template_cases = [
            ("monitorTemplate.xls", "监控点模板"),
            ("alarmTemplate.xls", "报警配置模板"),
            ("linkageTemplate.xls", "联动配置模板"),
        ]
        for template_name, download_name in template_cases:
            response = database_api.download_template(template_name, download_name)
            assert response.status_code == 200
            assert "attachment" in response.headers.get("Content-Disposition", "").lower()

    @allure.title("监控点编辑页可返回隐藏配置字段")
    def test_monitor_edit_page_contains_hidden_json_fields(self, auth_api, database_api, test_user):
        """打开现有监控点编辑页，校验监控点和条件联动隐藏字段存在。"""
        self._login(auth_api, test_user)

        row = self._get_existing_monitor_row(database_api)
        response = database_api.get_monitor_edit_page(row["id"])
        assert response.status_code == 200

        page_text = response.text
        assert 'id="monitorJsonId"' in page_text
        assert 'id="conditionLinkageJsonId"' in page_text
        assert 'id="editMonitorId"' in page_text

    @allure.title("监控点编辑页监控点 JSON 与请求监控点 ID 一致")
    def test_monitor_edit_page_monitor_json_id_matches_requested_monitor(self, auth_api, database_api, test_user):
        """打开现有监控点编辑页，校验监控点隐藏 JSON 中的 id 与请求参数一致。"""
        self._login(auth_api, test_user)

        row = self._get_existing_monitor_row(database_api)
        response = database_api.get_monitor_edit_page(row["id"])
        assert response.status_code == 200

        monitor_json = self._extract_hidden_json(response.text, "monitorJsonId")
        assert monitor_json["id"] == row["id"]

    @allure.title("监控点编辑页 yx 标签配置可反序列化")
    def test_monitor_edit_page_yx_config_is_parseable_json(self, auth_api, database_api, test_user):
        """打开现有遥信监控点编辑页，校验 yx 标签配置仍是可解析的 JSON 字符串。"""
        self._login(auth_api, test_user)

        row = self._get_existing_monitor_row(database_api)
        response = database_api.get_monitor_edit_page(row["id"])
        assert response.status_code == 200

        monitor_json = self._extract_hidden_json(response.text, "monitorJsonId")
        yx_config = json.loads(monitor_json["yx"])
        assert set(yx_config.keys()) >= {"FALSE_LABEL", "TRUE_LABEL"}
        assert yx_config["FALSE_LABEL"]
        assert yx_config["TRUE_LABEL"]

    @allure.title("监控点编辑页监控点 JSON 保留可选设备字段")
    def test_monitor_edit_page_monitor_json_preserves_optional_device_fields(self, auth_api, database_api, test_user):
        """打开现有监控点编辑页，校验可选设备字段仍以字符串形式回显。"""
        self._login(auth_api, test_user)

        row = self._get_existing_monitor_row(database_api)
        response = database_api.get_monitor_edit_page(row["id"])
        assert response.status_code == 200

        monitor_json = self._extract_hidden_json(response.text, "monitorJsonId")
        assert isinstance(monitor_json["monitorDeviceId"], str)
        assert isinstance(monitor_json["monitorDeviceName"], str)
        assert isinstance(monitor_json["scadaAddr10"], str)
        assert monitor_json["isStored"] in {"0", "1"}

    @allure.title("监控点编辑页监控点 JSON 与新建数据一致")
    def test_monitor_edit_page_monitor_json_matches_created_monitor(self, auth_api, database_api, test_user):
        """新建监控点后回查编辑页，校验监控点隐藏 JSON 与保存结果一致。"""
        self._login(auth_api, test_user)

        alarm_datatype = self._build_unique_text("AUTO-回显")
        scada_addr10 = self._build_unique_text("ADDR")
        payload = self._build_base_monitor_payload(database_api)
        payload.update(
            {
                "alarmDatatype": alarm_datatype,
                "scadaAddr10": scada_addr10,
            }
        )

        created_monitor_id = None
        try:
            assert database_api.validate_monitor(payload).json()["status"] == 0
            assert database_api.save_or_update_monitor(payload).json()["status"] == 0

            created_row = self._find_monitor_by_fields(database_api, alarm_datatype, scada_addr10)
            assert created_row is not None
            created_monitor_id = created_row["id"]

            edit_response = database_api.get_monitor_edit_page(created_monitor_id)
            assert edit_response.status_code == 200

            monitor_json = self._extract_hidden_json(edit_response.text, "monitorJsonId")
            assert monitor_json["id"] == created_monitor_id
            assert monitor_json["alarmDatatype"] == alarm_datatype
            assert monitor_json["scadaAddr10"] == scada_addr10
            assert monitor_json["equipId"] == payload["equipId"]
            assert monitor_json["alarmClass"] == payload["alarmClass"]
        finally:
            self._cleanup_monitor_if_exists(database_api, created_monitor_id)

    @allure.title("新建监控点编辑页保留默认存储标记和 yx 配置")
    def test_monitor_edit_page_preserves_default_is_stored_and_yx_config(self, auth_api, database_api, test_user):
        """新建监控点后回查编辑页，校验默认存储标记和 yx 标签配置被正确保留。"""
        self._login(auth_api, test_user)

        alarm_datatype = self._build_unique_text("AUTO-默认配置")
        scada_addr10 = self._build_unique_text("ADDR")
        payload = self._build_base_monitor_payload(database_api)
        payload.update(
            {
                "alarmDatatype": alarm_datatype,
                "scadaAddr10": scada_addr10,
            }
        )

        created_monitor_id = None
        try:
            assert database_api.validate_monitor(payload).json()["status"] == 0
            assert database_api.save_or_update_monitor(payload).json()["status"] == 0

            created_row = self._find_monitor_by_fields(database_api, alarm_datatype, scada_addr10)
            assert created_row is not None
            created_monitor_id = created_row["id"]

            edit_response = database_api.get_monitor_edit_page(created_monitor_id)
            assert edit_response.status_code == 200

            monitor_json = self._extract_hidden_json(edit_response.text, "monitorJsonId")
            assert monitor_json["isStored"] == "0"
            assert json.loads(monitor_json["yx"]) == json.loads(payload["yx"])
        finally:
            self._cleanup_monitor_if_exists(database_api, created_monitor_id)

    @allure.title("纯监控点编辑页条件联动隐藏字段为空字符串")
    def test_monitor_edit_page_condition_linkage_field_is_empty_without_configs(self, auth_api, database_api, test_user):
        """新建不带报警和联动配置的监控点后，校验条件联动隐藏字段为空字符串。"""
        self._login(auth_api, test_user)

        alarm_datatype = self._build_unique_text("AUTO-空配置")
        scada_addr10 = self._build_unique_text("ADDR")
        payload = self._build_base_monitor_payload(database_api)
        payload.update(
            {
                "alarmDatatype": alarm_datatype,
                "scadaAddr10": scada_addr10,
            }
        )

        created_monitor_id = None
        try:
            assert database_api.validate_monitor(payload).json()["status"] == 0
            assert database_api.save_or_update_monitor(payload).json()["status"] == 0

            created_row = self._find_monitor_by_fields(database_api, alarm_datatype, scada_addr10)
            assert created_row is not None
            created_monitor_id = created_row["id"]

            edit_response = database_api.get_monitor_edit_page(created_monitor_id)
            assert edit_response.status_code == 200

            raw_condition_linkage = self._extract_hidden_value(edit_response.text, "conditionLinkageJsonId")
            assert raw_condition_linkage == ""
        finally:
            self._cleanup_monitor_if_exists(database_api, created_monitor_id)

    @allure.title("监控点编辑页隐藏编辑 ID 与新建记录 ID 一致")
    def test_monitor_edit_page_edit_monitor_id_matches_created_monitor(self, auth_api, database_api, test_user):
        """新建监控点后回查编辑页，校验隐藏的 editMonitorId 与列表中的监控点 ID 一致。"""
        self._login(auth_api, test_user)

        alarm_datatype = self._build_unique_text("AUTO-编辑ID")
        scada_addr10 = self._build_unique_text("ADDR")
        payload = self._build_base_monitor_payload(database_api)
        payload.update(
            {
                "alarmDatatype": alarm_datatype,
                "scadaAddr10": scada_addr10,
            }
        )

        created_monitor_id = None
        try:
            assert database_api.validate_monitor(payload).json()["status"] == 0
            assert database_api.save_or_update_monitor(payload).json()["status"] == 0

            created_row = self._find_monitor_by_fields(database_api, alarm_datatype, scada_addr10)
            assert created_row is not None
            created_monitor_id = created_row["id"]

            edit_response = database_api.get_monitor_edit_page(created_monitor_id)
            assert edit_response.status_code == 200

            edit_monitor_id = self._extract_hidden_value(edit_response.text, "editMonitorId")
            assert edit_monitor_id == created_monitor_id
        finally:
            self._cleanup_monitor_if_exists(database_api, created_monitor_id)

    @allure.title("监控点 XML 导出接口返回点表文件流")
    def test_monitor_xml_export(self, auth_api, database_api, test_user):
        """校验 XML 点表导出接口可返回非空文件内容。"""
        self._login(auth_api, test_user)

        response = database_api.export_monitor_xml()
        assert response.status_code == 200
        assert len(response.content) > 0
        assert "application/vnd.ms-excel" in response.headers.get("Content-Type", "")

    @allure.title("监控点 XML 导出接口返回附件响应头")
    def test_monitor_xml_export_includes_attachment_header(self, auth_api, database_api, test_user):
        """校验 XML 点表导出接口通过附件头返回可下载文件。"""
        self._login(auth_api, test_user)

        response = database_api.export_monitor_xml()
        assert response.status_code == 200
        assert "attachment" in response.headers.get("Content-Disposition", "").lower()

    @allure.title("报警配置新增可持久化到监控点条件配置")
    def test_alarm_config_add(self, auth_api, database_api, test_user):
        """新增带报警条件的监控点，并回查编辑页中的报警配置。"""
        self._login(auth_api, test_user)

        alarm_datatype = self._build_unique_text("AUTO-报警")
        scada_addr10 = self._build_unique_text("ADDR")
        payload = self._build_base_monitor_payload(database_api)
        payload.update(
            {
                "alarmDatatype": alarm_datatype,
                "scadaAddr10": scada_addr10,
                "conditions": [
                    {
                        "teleMinValue": "true",
                        "isenable": 1,
                        "alarmLevel": "01",
                        "alarmType": "01",
                        "trigecondition": 1,
                    }
                ],
            }
        )

        created_monitor_id = None
        try:
            assert database_api.validate_monitor(payload).json()["status"] == 0
            assert database_api.save_or_update_monitor(payload).json()["status"] == 0

            created_row = self._find_monitor_by_fields(database_api, alarm_datatype, scada_addr10)
            assert created_row is not None
            created_monitor_id = created_row["id"]

            edit_response = database_api.get_monitor_edit_page(created_monitor_id)
            assert edit_response.status_code == 200

            condition_linkage = self._extract_hidden_json(edit_response.text, "conditionLinkageJsonId")
            assert len(condition_linkage) == 1
            assert condition_linkage[0]["condition"]["alarmLevel"] == "01"
            assert condition_linkage[0]["condition"]["alarmType"] == "01"
            assert str(condition_linkage[0]["condition"]["isenable"]) == "1"
        finally:
            self._cleanup_monitor_if_exists(database_api, created_monitor_id)

    @allure.title("报警配置新增可回显触发条件和布尔阈值")
    def test_alarm_config_add_preserves_trigger_condition_fields(self, auth_api, database_api, test_user):
        """新增一条报警条件后，校验编辑页回显的触发条件和布尔阈值字段保持一致。"""
        self._login(auth_api, test_user)

        alarm_datatype = self._build_unique_text("AUTO-报警细节")
        scada_addr10 = self._build_unique_text("ADDR")
        payload = self._build_base_monitor_payload(database_api)
        payload.update(
            {
                "alarmDatatype": alarm_datatype,
                "scadaAddr10": scada_addr10,
                "conditions": [
                    {
                        "teleMinValue": "false",
                        "isenable": 1,
                        "alarmLevel": "03",
                        "alarmType": "02",
                        "trigecondition": 2,
                    }
                ],
            }
        )

        created_monitor_id = None
        try:
            assert database_api.validate_monitor(payload).json()["status"] == 0
            assert database_api.save_or_update_monitor(payload).json()["status"] == 0

            created_row = self._find_monitor_by_fields(database_api, alarm_datatype, scada_addr10)
            assert created_row is not None
            created_monitor_id = created_row["id"]

            edit_response = database_api.get_monitor_edit_page(created_monitor_id)
            assert edit_response.status_code == 200

            condition_linkage = self._extract_hidden_json(edit_response.text, "conditionLinkageJsonId")
            assert len(condition_linkage) == 1
            condition = condition_linkage[0]["condition"]
            assert condition["alarmLevel"] == "03"
            assert condition["alarmType"] == "02"
            assert condition["teleMinValue"] == "false"
            assert condition["trigecondition"] == "2"
            assert condition["datatypeId"] == created_monitor_id
        finally:
            self._cleanup_monitor_if_exists(database_api, created_monitor_id)

    @allure.title("报警配置新增可同时保存多条报警条件")
    def test_alarm_config_add_persists_multiple_conditions(self, auth_api, database_api, test_user):
        """新增包含两条报警条件的监控点，并校验编辑页回显顺序和字段都正确。"""
        self._login(auth_api, test_user)

        alarm_datatype = self._build_unique_text("AUTO-多报警")
        scada_addr10 = self._build_unique_text("ADDR")
        payload = self._build_base_monitor_payload(database_api)
        payload.update(
            {
                "alarmDatatype": alarm_datatype,
                "scadaAddr10": scada_addr10,
                "conditions": [
                    {
                        "teleMinValue": "true",
                        "isenable": 1,
                        "alarmLevel": "01",
                        "alarmType": "01",
                        "trigecondition": 1,
                    },
                    {
                        "teleMinValue": "false",
                        "isenable": 0,
                        "alarmLevel": "02",
                        "alarmType": "02",
                        "trigecondition": 2,
                    },
                ],
            }
        )

        created_monitor_id = None
        try:
            assert database_api.validate_monitor(payload).json()["status"] == 0
            assert database_api.save_or_update_monitor(payload).json()["status"] == 0

            created_row = self._find_monitor_by_fields(database_api, alarm_datatype, scada_addr10)
            assert created_row is not None
            created_monitor_id = created_row["id"]

            edit_response = database_api.get_monitor_edit_page(created_monitor_id)
            assert edit_response.status_code == 200

            condition_linkage = self._extract_hidden_json(edit_response.text, "conditionLinkageJsonId")
            assert len(condition_linkage) == 2
            # 后端回显顺序不稳定，这里按条件内容比对而不是按列表下标比对。
            returned_conditions = {
                (
                    item["condition"]["alarmLevel"],
                    item["condition"]["alarmType"],
                    str(item["condition"]["isenable"]),
                )
                for item in condition_linkage
            }
            assert returned_conditions == {
                ("01", "01", "1"),
                ("02", "02", "0"),
            }
        finally:
            self._cleanup_monitor_if_exists(database_api, created_monitor_id)

    @allure.title("监控点删除前校验返回结构化结果")
    def test_monitor_can_delete_returns_structured_result(self, auth_api, database_api, test_user):
        """新建一条监控点后，校验删除前检查接口返回固定结构。"""
        self._login(auth_api, test_user)

        alarm_datatype = self._build_unique_text("AUTO-预校验")
        scada_addr10 = self._build_unique_text("ADDR")
        payload = self._build_base_monitor_payload(database_api)
        payload.update(
            {
                "alarmDatatype": alarm_datatype,
                "scadaAddr10": scada_addr10,
            }
        )

        created_monitor_id = None
        try:
            assert database_api.validate_monitor(payload).json()["status"] == 0
            assert database_api.save_or_update_monitor(payload).json()["status"] == 0

            created_row = self._find_monitor_by_fields(database_api, alarm_datatype, scada_addr10)
            assert created_row is not None
            created_monitor_id = created_row["id"]

            response = database_api.can_delete_monitor([created_monitor_id])
            assert response.status_code == 200

            body = response.json()
            assert body["status"] == 0
            assert "data" in body
            assert "image" in body["data"]
            assert isinstance(body["data"]["image"], list)
        finally:
            self._cleanup_monitor_if_exists(database_api, created_monitor_id)

    @allure.title("监控点删除接口对不存在 ID 返回幂等成功")
    def test_monitor_delete_nonexistent_id_is_idempotent(self, auth_api, database_api, test_user):
        """校验删除接口对不存在的监控点 ID 不报错，并保持幂等成功。"""
        self._login(auth_api, test_user)

        response = database_api.delete_monitor_by_ids(["not-exists-id"])
        assert response.status_code == 200

        body = response.json()
        assert body["status"] == 0
        assert body["message"] == "操作成功!"

    @allure.title("监控点删除接口可兼容存在与不存在 ID 混合删除")
    def test_monitor_delete_accepts_mixed_existing_and_nonexistent_ids(self, auth_api, database_api, test_user):
        """新建一条监控点后，校验批量删除接口可兼容真实 ID 和不存在 ID 的混合场景。"""
        self._login(auth_api, test_user)

        alarm_datatype = self._build_unique_text("AUTO-混合删除")
        scada_addr10 = self._build_unique_text("ADDR")
        payload = self._build_base_monitor_payload(database_api)
        payload.update(
            {
                "alarmDatatype": alarm_datatype,
                "scadaAddr10": scada_addr10,
            }
        )

        created_monitor_id = None
        try:
            assert database_api.validate_monitor(payload).json()["status"] == 0
            assert database_api.save_or_update_monitor(payload).json()["status"] == 0

            created_row = self._find_monitor_by_fields(database_api, alarm_datatype, scada_addr10)
            assert created_row is not None
            created_monitor_id = created_row["id"]

            response = database_api.delete_monitor_by_ids([created_monitor_id, "not-exists-id"])
            assert response.status_code == 200

            body = response.json()
            assert body["status"] == 0
            assert body["message"] == "操作成功!"
            assert self._find_monitor_by_fields(database_api, alarm_datatype, scada_addr10) is None
            created_monitor_id = None
        finally:
            self._cleanup_monitor_if_exists(database_api, created_monitor_id)

    @allure.title("监控点删除前校验对不存在 ID 返回空依赖列表")
    def test_monitor_can_delete_nonexistent_ids_returns_empty_dependencies(self, auth_api, database_api, test_user):
        """校验删除前校验接口对不存在的监控点 ID 返回空依赖列表而不是报错。"""
        self._login(auth_api, test_user)

        response = database_api.can_delete_monitor(["not-exists-id-1", "not-exists-id-2"])
        assert response.status_code == 200

        body = response.json()
        assert body["status"] == 0
        assert body["message"] == "数据查询成功!"
        assert body["data"]["image"] == []

    @allure.title("报警配置模板导入接口返回结构化结果")
    def test_alarm_config_import(self, auth_api, database_api, test_user):
        """先导出报警配置数据，再回灌导入校验接口闭环可用。"""
        self._login(auth_api, test_user)

        temp_path = self._export_excel_to_tempfile(
            database_api,
            template_name="alarmImport.xls",
            download_name="报警配置",
        )
        try:
            response = database_api.import_excel("alarmImport.xls", temp_path)
            assert response.status_code == 200

            body = response.json()
            assert body["status"] == 0
            assert body["message"] == "导入完成！"
            assert isinstance(body["data"], list)
            assert len(body["data"]) > 0
            assert "成功新增" in body["data"][0]
        finally:
            Path(temp_path).unlink(missing_ok=True)

    @allure.title("报警配置导出接口返回文件流")
    def test_alarm_config_export(self, auth_api, database_api, test_user):
        """校验报警配置导出接口返回的内容是可下载文件。"""
        self._login(auth_api, test_user)

        response = database_api.export_excel("alarmImport.xls", "报警配置")
        assert response.status_code == 200
        assert len(response.content) > 0
        assert "attachment" in response.headers.get("Content-Disposition", "")

    @allure.title("联动配置新增可持久化到监控点条件配置")
    def test_linkage_config_add(self, auth_api, database_api, test_user):
        """新增带视频联动的监控点，并回查编辑页中的联动配置。"""
        self._login(auth_api, test_user)

        related_equip, camera, preset = self._get_linkage_target(database_api)

        alarm_datatype = self._build_unique_text("AUTO-联动")
        scada_addr10 = self._build_unique_text("ADDR")
        payload = self._build_base_monitor_payload(database_api)
        payload.update(
            {
                "alarmDatatype": alarm_datatype,
                "scadaAddr10": scada_addr10,
                "conditions": [
                    {
                        "teleMinValue": "true",
                        "isenable": 1,
                        "alarmLevel": "01",
                        "alarmType": "01",
                        "trigecondition": 1,
                        "linkages": [
                            {
                                "exeNo": 1,
                                "linktype": "1",
                                "isenable": 1,
                                "relateEquip": related_equip["equipId"],
                                "linkequip": camera["id"],
                                "monitorequip": preset["valueField"],
                                "residenceTime": "5",
                                "isremote": None,
                            }
                        ],
                    }
                ],
            }
        )

        created_monitor_id = None
        try:
            assert database_api.validate_monitor(payload).json()["status"] == 0
            assert database_api.save_or_update_monitor(payload).json()["status"] == 0

            created_row = self._find_monitor_by_fields(database_api, alarm_datatype, scada_addr10)
            assert created_row is not None
            created_monitor_id = created_row["id"]

            edit_response = database_api.get_monitor_edit_page(created_monitor_id)
            assert edit_response.status_code == 200

            condition_linkage = self._extract_hidden_json(edit_response.text, "conditionLinkageJsonId")
            linkage_list = condition_linkage[0]["linkageList"]
            assert len(linkage_list) > 0
            assert linkage_list[0]["linktype"] == "1"
            assert linkage_list[0]["linkequip"] == camera["id"]
            assert linkage_list[0]["monitorequip"] == preset["valueField"]
        finally:
            self._cleanup_monitor_if_exists(database_api, created_monitor_id)

    @allure.title("联动配置新增可回显执行顺序和远方标记默认值")
    def test_linkage_config_add_preserves_execution_order_and_remote_flag(self, auth_api, database_api, test_user):
        """新增一条联动动作后，校验编辑页回显的执行顺序和远方标记默认值。"""
        self._login(auth_api, test_user)

        related_equip, camera, preset = self._get_linkage_target(database_api)
        alarm_datatype = self._build_unique_text("AUTO-联动细节")
        scada_addr10 = self._build_unique_text("ADDR")
        payload = self._build_base_monitor_payload(database_api)
        payload.update(
            {
                "alarmDatatype": alarm_datatype,
                "scadaAddr10": scada_addr10,
                "conditions": [
                    {
                        "teleMinValue": "true",
                        "isenable": 1,
                        "alarmLevel": "01",
                        "alarmType": "01",
                        "trigecondition": 1,
                        "linkages": [
                            {
                                "exeNo": 7,
                                "linktype": "1",
                                "isenable": 1,
                                "relateEquip": related_equip["equipId"],
                                "linkequip": camera["id"],
                                "monitorequip": preset["valueField"],
                                "residenceTime": "11",
                                "isremote": None,
                            }
                        ],
                    }
                ],
            }
        )

        created_monitor_id = None
        try:
            assert database_api.validate_monitor(payload).json()["status"] == 0
            assert database_api.save_or_update_monitor(payload).json()["status"] == 0

            created_row = self._find_monitor_by_fields(database_api, alarm_datatype, scada_addr10)
            assert created_row is not None
            created_monitor_id = created_row["id"]

            edit_response = database_api.get_monitor_edit_page(created_monitor_id)
            assert edit_response.status_code == 200

            condition_linkage = self._extract_hidden_json(edit_response.text, "conditionLinkageJsonId")
            condition = condition_linkage[0]["condition"]
            linkage = condition_linkage[0]["linkageList"][0]
            assert condition["datatypeId"] == created_monitor_id
            assert linkage["exeNo"] == 7
            assert linkage["isremote"] == "0"
            assert linkage["presetName"] == preset["presetPointName"]
            assert int(linkage["residenceTime"]) == 11
        finally:
            self._cleanup_monitor_if_exists(database_api, created_monitor_id)

    @allure.title("联动配置新增可回显启停状态和停留时长")
    def test_linkage_config_add_persists_disable_flag_and_residence_time(self, auth_api, database_api, test_user):
        """新增一条禁用的联动动作，并校验编辑页回显的启停状态和停留时长。"""
        self._login(auth_api, test_user)

        related_equip, camera, preset = self._get_linkage_target(database_api)
        alarm_datatype = self._build_unique_text("AUTO-联动标志")
        scada_addr10 = self._build_unique_text("ADDR")
        payload = self._build_base_monitor_payload(database_api)
        payload.update(
            {
                "alarmDatatype": alarm_datatype,
                "scadaAddr10": scada_addr10,
                "conditions": [
                    {
                        "teleMinValue": "true",
                        "isenable": 1,
                        "alarmLevel": "01",
                        "alarmType": "01",
                        "trigecondition": 1,
                        "linkages": [
                            {
                                "exeNo": 1,
                                "linktype": "1",
                                "isenable": 0,
                                "relateEquip": related_equip["equipId"],
                                "linkequip": camera["id"],
                                "monitorequip": preset["valueField"],
                                "residenceTime": "9",
                                "isremote": None,
                            }
                        ],
                    }
                ],
            }
        )

        created_monitor_id = None
        try:
            assert database_api.validate_monitor(payload).json()["status"] == 0
            assert database_api.save_or_update_monitor(payload).json()["status"] == 0

            created_row = self._find_monitor_by_fields(database_api, alarm_datatype, scada_addr10)
            assert created_row is not None
            created_monitor_id = created_row["id"]

            edit_response = database_api.get_monitor_edit_page(created_monitor_id)
            assert edit_response.status_code == 200

            condition_linkage = self._extract_hidden_json(edit_response.text, "conditionLinkageJsonId")
            linkage = condition_linkage[0]["linkageList"][0]
            assert linkage["linktype"] == "1"
            assert linkage["linkequip"] == camera["id"]
            assert linkage["monitorequip"] == preset["valueField"]
            assert str(linkage["isenable"]) == "0"
            assert int(linkage["residenceTime"]) == 9
        finally:
            self._cleanup_monitor_if_exists(database_api, created_monitor_id)

    @allure.title("报警与联动配置可在同一条件下同时回显")
    def test_alarm_and_linkage_config_can_coexist_in_single_condition(self, auth_api, database_api, test_user):
        """新增同时包含报警字段和视频联动的条件，并校验编辑页两部分配置都被保留。"""
        self._login(auth_api, test_user)

        related_equip, camera, preset = self._get_linkage_target(database_api)
        alarm_datatype = self._build_unique_text("AUTO-组合配置")
        scada_addr10 = self._build_unique_text("ADDR")
        payload = self._build_base_monitor_payload(database_api)
        payload.update(
            {
                "alarmDatatype": alarm_datatype,
                "scadaAddr10": scada_addr10,
                "conditions": [
                    {
                        "teleMinValue": "true",
                        "isenable": 1,
                        "alarmLevel": "03",
                        "alarmType": "02",
                        "trigecondition": 1,
                        "linkages": [
                            {
                                "exeNo": 1,
                                "linktype": "1",
                                "isenable": 1,
                                "relateEquip": related_equip["equipId"],
                                "linkequip": camera["id"],
                                "monitorequip": preset["valueField"],
                                "residenceTime": "6",
                                "isremote": None,
                            }
                        ],
                    }
                ],
            }
        )

        created_monitor_id = None
        try:
            assert database_api.validate_monitor(payload).json()["status"] == 0
            assert database_api.save_or_update_monitor(payload).json()["status"] == 0

            created_row = self._find_monitor_by_fields(database_api, alarm_datatype, scada_addr10)
            assert created_row is not None
            created_monitor_id = created_row["id"]

            edit_response = database_api.get_monitor_edit_page(created_monitor_id)
            assert edit_response.status_code == 200

            condition_linkage = self._extract_hidden_json(edit_response.text, "conditionLinkageJsonId")
            assert len(condition_linkage) == 1
            assert condition_linkage[0]["condition"]["alarmLevel"] == "03"
            assert condition_linkage[0]["condition"]["alarmType"] == "02"
            assert condition_linkage[0]["condition"]["teleMinValue"] == "true"

            linkage = condition_linkage[0]["linkageList"][0]
            assert linkage["linktype"] == "1"
            assert linkage["linkequip"] == camera["id"]
            assert linkage["monitorequip"] == preset["valueField"]
            assert int(linkage["residenceTime"]) == 6
        finally:
            self._cleanup_monitor_if_exists(database_api, created_monitor_id)

    @allure.title("联动配置模板导入接口返回结构化结果")
    def test_linkage_config_import(self, auth_api, database_api, test_user):
        """先导出联动配置数据，再回灌导入并校验返回结果结构。"""
        self._login(auth_api, test_user)

        temp_path = self._export_excel_to_tempfile(
            database_api,
            template_name="linkageImport.xls",
            download_name="联动配置",
        )
        try:
            response = database_api.import_excel("linkageImport.xls", temp_path)
            assert response.status_code == 200

            body = response.json()
            assert body["status"] == 0
            assert body["message"] == "导入完成！"
            assert isinstance(body["data"], list)
            assert len(body["data"]) > 0
            # 现网导出的联动配置里存在部分无法反查到预置位/摄像机的数据，
            # 因此这里校验“回灌可执行且有成功行”，同时允许接口返回部分失败明细。
            assert "成功保存" in body["data"][0]
        finally:
            Path(temp_path).unlink(missing_ok=True)

    @allure.title("联动配置导出接口返回文件流")
    def test_linkage_config_export(self, auth_api, database_api, test_user):
        """校验联动配置导出接口返回的内容是可下载文件。"""
        self._login(auth_api, test_user)

        response = database_api.export_excel("linkageImport.xls", "联动配置")
        assert response.status_code == 200
        assert len(response.content) > 0
        assert "attachment" in response.headers.get("Content-Disposition", "")

    @allure.title("联动辅助查询接口可返回关联设备摄像机和预置位")
    def test_linkage_auxiliary_queries(self, auth_api, database_api, test_user):
        """校验联动新增依赖的三段辅助查询链路可正常取数。"""
        self._login(auth_api, test_user)

        related_equip_response = database_api.query_related_equip_list()
        assert related_equip_response.status_code == 200

        related_equip_list = related_equip_response.json()
        assert len(related_equip_list) > 0
        related_equip = related_equip_list[0]
        assert related_equip["equipId"]
        assert related_equip["equipName"]

        camera_response = database_api.query_camera_list(related_equip["equipId"])
        assert camera_response.status_code == 200

        camera_body = camera_response.json()
        assert camera_body["status"] == 0
        assert len(camera_body["data"]) > 0
        camera = camera_body["data"][0]
        assert camera["id"]
        assert camera["equipName"]

        preset_response = database_api.query_preset_list(camera["id"], related_equip["equipId"])
        assert preset_response.status_code == 200

        preset_list = preset_response.json()
        assert len(preset_list) > 0
        assert preset_list[0]["valueField"]

    @allure.title("联动关联设备列表返回标准视频字段")
    def test_linkage_related_equip_entries_contain_expected_keys(self, auth_api, database_api, test_user):
        """校验联动关联设备列表中的首条数据包含标准视频定位字段。"""
        self._login(auth_api, test_user)

        response = database_api.query_related_equip_list()
        assert response.status_code == 200

        body = response.json()
        assert len(body) > 0
        assert set(body[0].keys()) >= {
            "equipId",
            "equipName",
            "id",
            "cameraName",
            "channelNo",
            "nvrSerialNum",
            "valueField",
        }

    @allure.title("联动摄像机列表返回标准视频字段")
    def test_linkage_camera_entries_contain_expected_keys(self, auth_api, database_api, test_user):
        """校验联动摄像机列表中的首条数据包含标准视频定位字段。"""
        self._login(auth_api, test_user)

        related_equip, _, _ = self._get_linkage_target(database_api)
        response = database_api.query_camera_list(related_equip["equipId"])
        assert response.status_code == 200

        body = response.json()
        assert body["status"] == 0
        assert len(body["data"]) > 0
        assert set(body["data"][0].keys()) >= {
            "equipId",
            "equipName",
            "id",
            "cameraName",
            "channelNo",
            "nvrSerialNum",
            "valueField",
        }

    @allure.title("联动摄像机和预置位查询结果引用同一摄像机设备")
    def test_linkage_camera_and_preset_entries_reference_same_camera(self, auth_api, database_api, test_user):
        """校验预置位列表中的摄像机设备标识与摄像机查询结果一致。"""
        self._login(auth_api, test_user)

        related_equip, camera, preset = self._get_linkage_target(database_api)
        assert camera["equipId"] == camera["id"]
        assert preset["equipId"] == camera["equipId"]
        assert preset["presetPointName"]
        assert preset["valueField"]

    @allure.title("联动预置位列表返回标准视频字段")
    def test_linkage_preset_entries_contain_expected_keys(self, auth_api, database_api, test_user):
        """校验联动预置位列表中的首条数据包含标准视频定位字段。"""
        self._login(auth_api, test_user)

        related_equip, camera, _ = self._get_linkage_target(database_api)
        response = database_api.query_preset_list(camera["id"], related_equip["equipId"])
        assert response.status_code == 200

        body = response.json()
        assert len(body) > 0
        assert set(body[0].keys()) >= {
            "equipId",
            "equipName",
            "id",
            "cameraName",
            "channelNo",
            "nvrSerialNum",
            "valueField",
        }

    @allure.title("联动三段辅助查询返回一致的核心视频字段")
    def test_linkage_auxiliary_queries_share_same_core_keys(self, auth_api, database_api, test_user):
        """校验关联设备、摄像机和预置位三段查询都保留一致的核心视频字段。"""
        self._login(auth_api, test_user)

        related_equip, camera, _ = self._get_linkage_target(database_api)
        related_entry = database_api.query_related_equip_list().json()[0]
        camera_entry = database_api.query_camera_list(related_equip["equipId"]).json()["data"][0]
        preset_entry = database_api.query_preset_list(camera["id"], related_equip["equipId"]).json()[0]

        core_keys = {
            "equipId",
            "equipName",
            "id",
            "cameraName",
            "channelNo",
            "nvrSerialNum",
            "valueField",
        }
        assert core_keys <= set(related_entry.keys())
        assert core_keys <= set(camera_entry.keys())
        assert core_keys <= set(preset_entry.keys())

    @allure.title("联动辅助查询接口对无效参数返回空结果")
    def test_linkage_auxiliary_queries_return_empty_results_for_invalid_ids(self, auth_api, database_api, test_user):
        """校验联动辅助查询在无效设备和摄像机参数下不会报错，并返回空结果。"""
        self._login(auth_api, test_user)

        camera_response = database_api.query_camera_list("invalid-equip-id")
        assert camera_response.status_code == 200

        camera_body = camera_response.json()
        assert camera_body["status"] == 0
        assert camera_body["data"] == []

        preset_response = database_api.query_preset_list("invalid-camera-id", "invalid-equip-id")
        assert preset_response.status_code == 200
        assert preset_response.json() == []

    @allure.title("监控点导入页暴露三类 Excel 模板入口")
    def test_monitor_import_page_contains_all_template_names(self, auth_api, database_api, test_user):
        """校验基础数据导入页仍暴露监控点、报警配置和联动配置三类 Excel 模板。"""
        self._login(auth_api, test_user)

        response = database_api.get_monitor_import_page()
        assert response.status_code == 200

        assert "monitorImport.xls" in response.text
        assert "alarmImport.xls" in response.text
        assert "linkageImport.xls" in response.text

    @allure.title("基础数据 Excel 导出保留附件响应头和 xls 后缀")
    def test_database_excel_exports_keep_attachment_headers_and_xls_suffix(self, auth_api, database_api, test_user):
        """校验监控点、报警配置和联动配置导出结果仍都是可下载的 Excel 附件。"""
        self._login(auth_api, test_user)

        export_pairs = [
            ("monitorImport.xls", "监控点"),
            ("alarmImport.xls", "报警配置"),
            ("linkageImport.xls", "联动配置"),
        ]
        for template_name, download_name in export_pairs:
            response = database_api.export_excel(template_name, download_name)
            assert response.status_code == 200
            assert "attachment" in response.headers.get("Content-Disposition", "")
            assert ".xls" in response.headers.get("Content-Disposition", "")
            assert "application/vnd.ms-excel" in response.headers.get("Content-Type", "")

    @allure.title("联动辅助查询 valueField 使用成对编码格式")
    def test_linkage_auxiliary_value_field_uses_pair_format(self, auth_api, database_api, test_user):
        """校验关联设备、摄像机和预置位记录仍保持预期的成对编码 valueField 格式。"""
        self._login(auth_api, test_user)

        related_equip, camera, preset = self._get_linkage_target(database_api)
        related_entry = database_api.query_related_equip_list().json()[0]
        camera_entry = database_api.query_camera_list(related_equip["equipId"]).json()["data"][0]

        for entry in (related_entry, camera_entry, preset):
            assert re.fullmatch(r"\d+-\d+", entry["valueField"])

    @allure.title("联动辅助查询可空视频字段保持稳定类型")
    def test_linkage_auxiliary_nullable_video_fields_keep_expected_types(self, auth_api, database_api, test_user):
        """校验可空视频相关字段保持可空字符串，通道号保持非负整数。"""
        self._login(auth_api, test_user)

        related_equip, camera, preset = self._get_linkage_target(database_api)
        related_entry = database_api.query_related_equip_list().json()[0]
        camera_entry = database_api.query_camera_list(related_equip["equipId"]).json()["data"][0]
        preset_entry = database_api.query_preset_list(camera["id"], related_equip["equipId"]).json()[0]

        for entry in (related_entry, camera_entry, preset_entry):
            assert entry["cameraName"] is None or isinstance(entry["cameraName"], str)
            assert entry["nvrSerialNum"] is None or isinstance(entry["nvrSerialNum"], str)
            assert isinstance(entry["channelNo"], int)
            assert entry["channelNo"] >= 0
