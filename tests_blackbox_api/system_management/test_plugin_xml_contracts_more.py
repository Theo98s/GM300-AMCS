# -*- coding: utf-8 -*-
"""More AMCS plugin XML contract tests."""
from __future__ import annotations

import xml.etree.ElementTree as element_tree

import allure


@allure.feature("Menu And Plugin")
class TestPluginXmlContractsMore:
    """Extra structural checks for plugin menuContent XML."""

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
    def _main_plugin(plugin_api) -> dict:
        """Return the main AMCS plugin definition for XML parsing checks."""
        body = plugin_api.find_plugin().json()
        return next(item for item in body if item["pkey"] == "GM300-AMCS")

    @staticmethod
    def _menu_root(plugin_api):
        """Parse the menuContent XML from the main plugin."""
        plugin = TestPluginXmlContractsMore._main_plugin(plugin_api)
        return element_tree.fromstring(plugin["menuContent"])

    @allure.title("Plugin menuContent remains parseable resource XML")
    def test_plugin_menu_content_remains_parseable_resource_xml(self, auth_api, plugin_api, test_user):
        """Verify the plugin menu definition stays valid XML with the expected root tag and top groups."""
        self._login(auth_api, test_user)

        root = self._menu_root(plugin_api)
        groups = root.findall("./group")
        assert root.tag == "resource"
        assert len(groups) == 8
        assert [group.attrib["id"] for group in groups] == [
            "amcs_welcome",
            "video",
            "amcs_das",
            "amcs_patrol",
            "history",
            "base",
            "config",
            "sys",
        ]

    @allure.title("Plugin XML group page counts keep expected distribution")
    def test_plugin_menu_content_group_page_counts_keep_expected_distribution(
        self,
        auth_api,
        plugin_api,
        test_user,
    ):
        """Verify the main menu groups still expose the current page-count layout used by navigation."""
        self._login(auth_api, test_user)

        root = self._menu_root(plugin_api)
        page_counts = {
            group.attrib["id"]: len(group.findall("./page"))
            for group in root.findall("./group")
        }
        assert page_counts == {
            "amcs_welcome": 0,
            "video": 3,
            "amcs_das": 5,
            "amcs_patrol": 3,
            "history": 3,
            "base": 9,
            "config": 5,
            "sys": 5,
        }

    @allure.title("Plugin XML core group routes keep expected endpoint sets")
    def test_plugin_menu_content_core_group_routes_keep_expected_endpoint_sets(
        self,
        auth_api,
        plugin_api,
        test_user,
    ):
        """Verify the video, patrol, history, base, config, and system groups keep their current page routes."""
        self._login(auth_api, test_user)

        root = self._menu_root(plugin_api)
        route_map = {
            group.attrib["id"]: [page.attrib.get("url", "") for page in group.findall("./page")]
            for group in root.findall("./group")
        }
        assert route_map["video"] == [
            "/amcs/video/preview",
            "/amcs/video/playback",
            "/amcs/video/thermometry",
        ]
        assert route_map["amcs_patrol"] == [
            "/amcs/patrol/plan",
            "/amcs/patrol/card",
            "/amcs/patrol/record",
        ]
        assert route_map["history"] == [
            "/amcs/monitorLink/index",
            "/amcs/trend/index",
            "/amcs/alarm/index",
        ]
        assert "/monitor/index" in route_map["base"]
        assert "/amcs/video/preset" in route_map["config"]
        assert "/menu" in route_map["sys"]
