# -*- coding: utf-8 -*-
"""基础数据库监控点、报警、联动与批量功能流程测试。"""
from __future__ import annotations

from .test_database_api import TestDatabaseApi as DatabaseApiHelper
import allure
from pathlib import Path


class TestDatabaseFunctionalFlowsMore:
    """补充覆盖监控点新增后修改、补配报警和补配联动的功能流。"""

    @allure.title("监控点支持新增后修改基础字段")
    def test_monitor_update_flow_can_modify_unique_business_fields(self, auth_api, database_api, test_user):
        """先新增监控点，再修改业务唯一字段，并校验列表与编辑页都同步更新。"""
        DatabaseApiHelper._login(auth_api, test_user)

        original_alarm_datatype = DatabaseApiHelper._build_unique_text("AUTO-功能修改")
        original_scada_addr10 = DatabaseApiHelper._build_unique_text("ADDR")
        payload = DatabaseApiHelper._build_base_monitor_payload(database_api)
        payload.update(
            {
                "alarmDatatype": original_alarm_datatype,
                "scadaAddr10": original_scada_addr10,
            }
        )

        created_monitor_id = None
        try:
            assert database_api.validate_monitor(payload).json()["status"] == 0
            assert database_api.save_or_update_monitor(payload).json()["status"] == 0

            created_row = DatabaseApiHelper._find_monitor_by_fields(
                database_api,
                original_alarm_datatype,
                original_scada_addr10,
            )
            assert created_row is not None
            created_monitor_id = created_row["id"]

            updated_alarm_datatype = f"{original_alarm_datatype}-UPD"
            updated_scada_addr10 = f"{original_scada_addr10}9"
            update_payload = DatabaseApiHelper._build_base_monitor_payload(database_api)
            update_payload.update(
                {
                    "id": created_monitor_id,
                    "alarmDatatype": updated_alarm_datatype,
                    "scadaAddr10": updated_scada_addr10,
                }
            )

            assert database_api.validate_monitor(update_payload).json()["status"] == 0
            update_response = database_api.save_or_update_monitor(update_payload)
            assert update_response.status_code == 200
            assert update_response.json()["status"] == 0

            updated_row = DatabaseApiHelper._find_monitor_by_fields(
                database_api,
                updated_alarm_datatype,
                updated_scada_addr10,
            )
            assert updated_row is not None
            assert updated_row["id"] == created_monitor_id
            assert DatabaseApiHelper._find_monitor_by_fields(
                database_api,
                original_alarm_datatype,
                original_scada_addr10,
            ) is None

            edit_response = database_api.get_monitor_edit_page(created_monitor_id)
            assert edit_response.status_code == 200
            monitor_json = DatabaseApiHelper._extract_hidden_json(edit_response.text, "monitorJsonId")
            assert monitor_json["id"] == created_monitor_id
            assert monitor_json["alarmDatatype"] == updated_alarm_datatype
            assert monitor_json["scadaAddr10"] == updated_scada_addr10
        finally:
            DatabaseApiHelper._cleanup_monitor_if_exists(database_api, created_monitor_id)

    @allure.title("监控点支持新增后补加报警条件")
    def test_monitor_update_flow_can_append_alarm_condition(self, auth_api, database_api, test_user):
        """先新增空监控点，再二次保存补加报警条件，并校验编辑页已回显。"""
        DatabaseApiHelper._login(auth_api, test_user)

        alarm_datatype = DatabaseApiHelper._build_unique_text("AUTO-功能报警")
        scada_addr10 = DatabaseApiHelper._build_unique_text("ADDR")
        payload = DatabaseApiHelper._build_base_monitor_payload(database_api)
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

            created_row = DatabaseApiHelper._find_monitor_by_fields(database_api, alarm_datatype, scada_addr10)
            assert created_row is not None
            created_monitor_id = created_row["id"]

            update_payload = DatabaseApiHelper._build_base_monitor_payload(database_api)
            update_payload.update(
                {
                    "id": created_monitor_id,
                    "alarmDatatype": alarm_datatype,
                    "scadaAddr10": scada_addr10,
                    "conditions": [
                        {
                            "teleMinValue": "true",
                            "isenable": 1,
                            "alarmLevel": "02",
                            "alarmType": "01",
                            "trigecondition": 1,
                            "linkages": [],
                        }
                    ],
                }
            )

            assert database_api.validate_monitor(update_payload).json()["status"] == 0
            update_response = database_api.save_or_update_monitor(update_payload)
            assert update_response.status_code == 200
            assert update_response.json()["status"] == 0

            edit_response = database_api.get_monitor_edit_page(created_monitor_id)
            assert edit_response.status_code == 200
            condition_linkage = DatabaseApiHelper._extract_hidden_json(edit_response.text, "conditionLinkageJsonId")
            assert len(condition_linkage) == 1
            condition = condition_linkage[0]["condition"]
            assert condition["datatypeId"] == created_monitor_id
            assert condition["alarmLevel"] == "02"
            assert condition["alarmType"] == "01"
            assert condition["teleMinValue"] == "true"
            assert condition["trigecondition"] == "1"
        finally:
            DatabaseApiHelper._cleanup_monitor_if_exists(database_api, created_monitor_id)

    @allure.title("监控点支持新增后补加联动配置")
    def test_monitor_update_flow_can_append_linkage_config(self, auth_api, database_api, test_user):
        """先新增空监控点，再二次保存补加联动动作，并校验编辑页回显联动链路。"""
        DatabaseApiHelper._login(auth_api, test_user)

        related_equip, camera, preset = DatabaseApiHelper._get_linkage_target(database_api)
        alarm_datatype = DatabaseApiHelper._build_unique_text("AUTO-功能联动")
        scada_addr10 = DatabaseApiHelper._build_unique_text("ADDR")
        payload = DatabaseApiHelper._build_base_monitor_payload(database_api)
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

            created_row = DatabaseApiHelper._find_monitor_by_fields(database_api, alarm_datatype, scada_addr10)
            assert created_row is not None
            created_monitor_id = created_row["id"]

            update_payload = DatabaseApiHelper._build_base_monitor_payload(database_api)
            update_payload.update(
                {
                    "id": created_monitor_id,
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
                                    "exeNo": 3,
                                    "linktype": "1",
                                    "isenable": 1,
                                    "relateEquip": related_equip["equipId"],
                                    "linkequip": camera["id"],
                                    "monitorequip": preset["valueField"],
                                    "residenceTime": "8",
                                    "isremote": None,
                                }
                            ],
                        }
                    ],
                }
            )

            assert database_api.validate_monitor(update_payload).json()["status"] == 0
            update_response = database_api.save_or_update_monitor(update_payload)
            assert update_response.status_code == 200
            assert update_response.json()["status"] == 0

            edit_response = database_api.get_monitor_edit_page(created_monitor_id)
            assert edit_response.status_code == 200
            condition_linkage = DatabaseApiHelper._extract_hidden_json(edit_response.text, "conditionLinkageJsonId")
            assert len(condition_linkage) == 1
            condition = condition_linkage[0]["condition"]
            linkage = condition_linkage[0]["linkageList"][0]
            assert condition["datatypeId"] == created_monitor_id
            assert linkage["linktype"] == "1"
            assert linkage["linkequip"] == camera["id"]
            assert linkage["monitorequip"] == preset["valueField"]
            assert linkage["presetName"] == preset["presetPointName"]
            assert linkage["isremote"] == "0"
            assert linkage["exeNo"] == 3
            assert int(linkage["residenceTime"]) == 8
        finally:
            DatabaseApiHelper._cleanup_monitor_if_exists(database_api, created_monitor_id)


class TestDatabaseBatchFunctionalFlowsMore:
    """补充覆盖导入页、模板下载、导出回灌导入等批量操作场景。"""

    @staticmethod
    def _roundtrip_cases() -> list[tuple[str, str, str]]:
        """返回三类基础数据库导出再导入的测试参数。"""
        return [
            ("monitorImport.xls", "监控点", "成功新增"),
            ("alarmImport.xls", "报警配置", "成功新增"),
            ("linkageImport.xls", "联动配置", "成功保存"),
        ]

    @staticmethod
    def _template_cases() -> list[tuple[str, str]]:
        """返回三类基础数据库模板下载参数。"""
        return [
            ("monitorTemplate.xls", "监控点模板"),
            ("alarmTemplate.xls", "报警配置模板"),
            ("linkageTemplate.xls", "联动配置模板"),
        ]

    @allure.title("基础数据库导入页可驱动三类模板入口初始化")
    def test_database_import_page_can_bootstrap_three_template_entry_points(
        self,
        auth_api,
        database_api,
        test_user,
    ):
        """登录后打开基础数据导入页，校验三类模板和三类导入参数都已暴露。"""
        DatabaseApiHelper._login(auth_api, test_user)

        response = database_api.get_monitor_import_page()
        assert response.status_code == 200

        page_text = response.text
        for template_name, _ in self._template_cases():
            assert template_name in page_text
        for import_name, _, _ in self._roundtrip_cases():
            assert import_name in page_text

    @allure.title("基础数据库三类模板可在同一会话内连续下载")
    def test_database_operator_can_download_three_templates_in_single_session(
        self,
        auth_api,
        database_api,
        test_user,
    ):
        """登录一次后，连续下载监控点、报警配置和联动配置模板。"""
        DatabaseApiHelper._login(auth_api, test_user)

        for template_name, download_name in self._template_cases():
            response = database_api.download_template(template_name, download_name)
            assert response.status_code == 200
            assert len(response.content) > 0
            assert "attachment" in response.headers.get("Content-Disposition", "").lower()

    @allure.title("基础数据库三类导出文件可在同一会话内连续回灌导入")
    def test_database_operator_can_roundtrip_three_exported_datasets_in_single_session(
        self,
        auth_api,
        database_api,
        test_user,
    ):
        """依次导出监控点、报警配置和联动配置，再立即把导出文件回灌导入。"""
        DatabaseApiHelper._login(auth_api, test_user)

        temp_paths: list[str] = []
        try:
            for template_name, download_name, success_fragment in self._roundtrip_cases():
                temp_path = DatabaseApiHelper._export_excel_to_tempfile(
                    database_api,
                    template_name=template_name,
                    download_name=download_name,
                )
                temp_paths.append(temp_path)

                response = database_api.import_excel(template_name, temp_path)
                assert response.status_code == 200

                body = response.json()
                assert body["status"] == 0
                assert body["message"] == "导入完成！"
                assert isinstance(body["data"], list)
                assert len(body["data"]) > 0
                assert success_fragment in body["data"][0]
        finally:
            for temp_path in temp_paths:
                Path(temp_path).unlink(missing_ok=True)
