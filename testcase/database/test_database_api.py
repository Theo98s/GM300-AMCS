# -*- coding: utf-8 -*-
"""AMCS 基础数据库接口自动化用例。"""
from __future__ import annotations

import html
import json
import re
import tempfile
import time
import uuid
from pathlib import Path

import allure


@allure.feature("基础数据库")
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

    @allure.title("监控点模板导入接口返回结构化结果")
    def test_monitor_import(self, auth_api, database_api, test_user):
        """上传系统模板，校验监控点导入接口能返回结构化业务结果。"""
        self._login(auth_api, test_user)

        temp_path = self._download_template_to_tempfile(
            database_api,
            template_name="monitorTemplate.xls",
            download_name="monitor-template",
        )
        try:
            response = database_api.import_excel("monitorImport.xls", temp_path)
            assert response.status_code == 200

            body = response.json()
            assert body["status"] == 0
            assert "导入" in body["message"]
            assert isinstance(body["data"], list)
            assert len(body["data"]) > 0
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

    @allure.title("报警配置模板导入接口返回结构化结果")
    def test_alarm_config_import(self, auth_api, database_api, test_user):
        """上传报警配置模板，校验报警导入接口能返回明确业务结果。"""
        self._login(auth_api, test_user)

        temp_path = self._download_template_to_tempfile(
            database_api,
            template_name="alarmTemplate.xls",
            download_name="alarm-template",
        )
        try:
            response = database_api.import_excel("alarmImport.xls", temp_path)
            assert response.status_code == 200

            body = response.json()
            assert body["status"] == 0
            assert "导入" in body["message"]
            assert isinstance(body["data"], list)
            assert len(body["data"]) > 0
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

        related_equip = database_api.query_related_equip_list().json()[0]
        camera_response = database_api.query_camera_list(related_equip["equipId"]).json()
        camera = camera_response["data"][0]
        preset = database_api.query_preset_list(camera["id"], related_equip["equipId"]).json()[0]

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

    @allure.title("联动配置模板导入接口返回结构化结果")
    def test_linkage_config_import(self, auth_api, database_api, test_user):
        """上传联动配置模板，校验联动导入接口能返回明确结果。"""
        self._login(auth_api, test_user)

        temp_path = self._download_template_to_tempfile(
            database_api,
            template_name="linkageTemplate.xls",
            download_name="linkage-template",
        )
        try:
            response = database_api.import_excel("linkageImport.xls", temp_path)
            assert response.status_code == 200

            body = response.json()
            assert body["status"] == 0
            assert "导入" in body["message"]
            assert isinstance(body["data"], list)
            assert len(body["data"]) > 0
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
