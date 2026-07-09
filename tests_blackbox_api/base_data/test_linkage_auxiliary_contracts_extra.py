# -*- coding: utf-8 -*-
"""Additional AMCS linkage auxiliary query contract tests."""
from __future__ import annotations

import re

import allure


@allure.feature("Base Data")
class TestLinkageAuxiliaryContractsExtra:
    """Extra contract checks for linkage-related helper queries."""

    @staticmethod
    def _login(auth_api, test_user):
        """Log in once per test and assert the session is ready."""
        login_response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert login_response.status_code == 200
        assert login_response.json()["status"] == 0

    @staticmethod
    def _first_linkage_chain(database_api):
        """Return one related-equipment, camera, and preset chain for stable contract checks."""
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

    @staticmethod
    def _assert_nullable_video_fields(entry: dict):
        """Check common nullable video fields that appear across helper-query payloads."""
        assert isinstance(entry["equipId"], str) and entry["equipId"]
        assert isinstance(entry["equipName"], str) and entry["equipName"]
        assert re.fullmatch(r"\d+-\d+", entry["valueField"])
        assert isinstance(entry["channelNo"], int)
        assert entry["channelNo"] >= 0
        assert isinstance(entry["moveable"], bool)
        assert entry["cameraName"] is None or isinstance(entry["cameraName"], str)
        assert entry["nvrSerialNum"] is None or isinstance(entry["nvrSerialNum"], str)
        assert entry["type"] is None or isinstance(entry["type"], str)

    @allure.title("Linkage related-equipment rows keep nullable video field contracts")
    def test_linkage_related_equip_rows_keep_expected_nullable_types(self, auth_api, database_api, test_user):
        """Verify the first related-equipment rows keep stable nullable types and pair-code value fields."""
        self._login(auth_api, test_user)

        rows = database_api.query_related_equip_list().json()
        assert len(rows) > 0

        for row in rows[:5]:
            self._assert_nullable_video_fields(row)
            assert row["presetPointName"] is None or isinstance(row["presetPointName"], str)
            assert isinstance(row["presetPointIndex"], int)

    @allure.title("Linkage camera rows keep identity and value-field alignment")
    def test_linkage_camera_row_keeps_identity_and_value_field_contract(self, auth_api, database_api, test_user):
        """Verify linkage camera rows keep the current self-identity and channel-aligned valueField shape."""
        self._login(auth_api, test_user)

        related_equip, camera, _ = self._first_linkage_chain(database_api)
        camera_body = database_api.query_camera_list(related_equip["equipId"]).json()
        first_camera = camera_body["data"][0]

        self._assert_nullable_video_fields(first_camera)
        assert first_camera["id"] == camera["id"]
        assert first_camera["equipId"] == first_camera["id"]
        assert first_camera["valueField"] == f'{first_camera["channelNo"]}-0'
        assert first_camera["presetPointIndex"] == 0

    @allure.title("Linkage preset rows keep preset-index and value-field alignment")
    def test_linkage_preset_row_keeps_preset_index_alignment(self, auth_api, database_api, test_user):
        """Verify linkage preset rows keep their preset index encoded in valueField for UI linkage forms."""
        self._login(auth_api, test_user)

        related_equip, camera, preset = self._first_linkage_chain(database_api)
        preset_list = database_api.query_preset_list(camera["id"], related_equip["equipId"]).json()
        first_preset = preset_list[0]

        self._assert_nullable_video_fields(first_preset)
        assert first_preset["equipId"] == camera["id"]
        assert first_preset["valueField"] == f'{first_preset["channelNo"]}-{first_preset["presetPointIndex"]}'
        assert isinstance(first_preset["presetPointName"], str)
        assert first_preset["presetPointName"]
        assert first_preset["presetPointIndex"] > 0

    @allure.title("Linkage helper-query chain keeps shared core video fields")
    def test_linkage_auxiliary_chain_keeps_core_video_fields_consistent(self, auth_api, database_api, test_user):
        """Verify one related-equipment, camera, and preset chain keeps consistent core field names."""
        self._login(auth_api, test_user)

        related_equip, camera, preset = self._first_linkage_chain(database_api)
        for entry in (related_equip, camera, preset):
            self._assert_nullable_video_fields(entry)

        # Preset rows are expected to point back to the selected camera, while the camera row is self-owned.
        assert camera["equipId"] == camera["id"]
        assert preset["equipId"] == camera["id"]
        assert preset["valueField"].startswith(f'{preset["channelNo"]}-')
