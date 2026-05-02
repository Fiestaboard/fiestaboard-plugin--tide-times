"""Tests for the tide_times plugin."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch, Mock

import pytest

from plugins.tide_times import TideTimesPlugin
from src.plugins.base import PluginResult

MANIFEST = json.loads("""
{
    "id": "tide_times",
    "name": "Tide Times",
    "version": "0.1.0",
    "settings_schema": {
        "type": "object",
        "properties": {
            "enabled": {
                "type": "boolean",
                "title": "Enabled",
                "default": false
            },
            "station_id": {
                "type": "string",
                "title": "Station ID",
                "description": "NOAA tide gauge station ID (e.g. 9414290 for San Francisco).",
                "default": "9414290"
            },
            "units": {
                "type": "string",
                "title": "Units",
                "description": "Measurement units.",
                "enum": [
                    "english",
                    "metric"
                ],
                "default": "english"
            },
            "refresh_seconds": {
                "type": "integer",
                "title": "Refresh Interval (seconds)",
                "description": "How often to fetch tide predictions.",
                "default": 1800,
                "minimum": 1800
            }
        },
        "required": [
            "station_id"
        ]
    }
}
""")

SAMPLE_RESPONSE = json.loads("""
{
    "metadata": {
        "id": "9414290",
        "name": "San Francisco, CA",
        "lat": "37.8063",
        "lon": "-122.4659"
    },
    "predictions": [
        {
            "t": "2026-05-01 02:15",
            "v": "5.4",
            "type": "H"
        },
        {
            "t": "2026-05-01 08:32",
            "v": "0.3",
            "type": "L"
        },
        {
            "t": "2026-05-01 14:48",
            "v": "4.9",
            "type": "H"
        },
        {
            "t": "2026-05-01 21:05",
            "v": "1.2",
            "type": "L"
        }
    ]
}
""")


@pytest.fixture
def plugin():
    return TideTimesPlugin(MANIFEST)


@pytest.fixture
def configured_plugin():
    p = TideTimesPlugin(MANIFEST)
    p.config = json.loads("""
{
    "station_id": "9414290",
    "units": "english"
}
""")
    return p


class TestTideTimesPlugin:

    def test_plugin_id(self, plugin):
        assert plugin.plugin_id == "tide_times"

    def test_manifest_valid(self):
        manifest_path = Path(__file__).parent.parent / "manifest.json"
        with open(manifest_path) as f:
            m = json.load(f)
        for field in ("id", "name", "version"):
            assert field in m

    @patch("plugins.tide_times.requests.get")
    def test_fetch_data_success(self, mock_get, configured_plugin):
        mock_response = Mock()
        mock_response.json.return_value = SAMPLE_RESPONSE
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        result = configured_plugin.fetch_data()

        assert result.available is True
        assert result.error is None
        assert result.data is not None
        assert "next_type" in result.data, "missing variable: next_type"
        assert "next_time" in result.data, "missing variable: next_time"
        assert "next_height" in result.data, "missing variable: next_height"
        assert "station_name" in result.data, "missing variable: station_name"

    @patch("plugins.tide_times.requests.get")
    def test_fetch_data_network_error(self, mock_get, configured_plugin):
        import requests as req_mod
        mock_get.side_effect = req_mod.exceptions.ConnectionError("network down")

        result = configured_plugin.fetch_data()

        assert result.available is False
        assert result.error is not None

    @patch("plugins.tide_times.requests.get")
    def test_fetch_data_bad_json(self, mock_get, configured_plugin):
        mock_response = Mock()
        mock_response.json.side_effect = ValueError("bad json")
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        result = configured_plugin.fetch_data()

        assert result.available is False

