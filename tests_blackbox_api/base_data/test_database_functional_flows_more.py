# -*- coding: utf-8 -*-
"""AMCS 基础数据功能流补充测试。"""
from __future__ import annotations

from .test_database_api import TestDatabaseApi as DatabaseApiHelper

import allure


@allure.feature("基础数据")
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
