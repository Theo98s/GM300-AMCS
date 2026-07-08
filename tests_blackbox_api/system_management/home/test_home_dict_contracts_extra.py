# -*- coding: utf-8 -*-
"""Additional AMCS home-dictionary contract tests."""
from __future__ import annotations

import allure


@allure.feature("首页接口")
class TestHomeDictContractsExtra:
    """Extra contract checks for public dictionary payloads used by the home module."""

    @allure.title("设备区域字典编码保持唯一")
    def test_equip_area_dict_codes_are_unique(self, auth_api, home_api, test_user):
        """Verify EQUIP_AREA dictionary codes remain unique for dropdown rendering and filtering."""
        login_response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert login_response.json()["status"] == 0

        response = home_api.list_dict_no_root("EQUIP_AREA")
        body = response.json()

        codes = [item["code"] for item in body]
        assert len(codes) == len(set(codes))

    @allure.title("设备区域字典项保持 text 与 name 一致且 typekey 正确")
    def test_equip_area_dict_entries_keep_text_name_and_typekey_contract(self, auth_api, home_api, test_user):
        """Verify EQUIP_AREA dictionary entries keep consistent display and typekey fields."""
        login_response = auth_api.login(
            account=test_user["username"],
            password=test_user["password"],
        )
        assert login_response.json()["status"] == 0

        response = home_api.list_dict_no_root("EQUIP_AREA")
        body = response.json()

        for item in body:
            assert item["text"] == item["name"]
            assert item["typekey"] == "EQUIP_AREA"
            assert item["name"]

