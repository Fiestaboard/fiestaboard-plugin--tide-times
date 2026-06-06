"""Display today's high and low tide predictions for any NOAA tide gauge station."""

from __future__ import annotations

import logging
from typing import Any, Dict, List
import requests

from src.plugins.base import PluginBase, PluginResult

logger = logging.getLogger(__name__)

API_URL = "https://api.tidesandcurrents.noaa.gov/api/prod/datagetter"
USER_AGENT = "FiestaBoard Tide Times Plugin (https://github.com/Fiestaboard/fiestaboard-plugin--tide-times)"


class TideTimesPlugin(PluginBase):
    """Tide Times plugin for FiestaBoard."""

    @property
    def plugin_id(self) -> str:
        return "tide_times"

    def fetch_data(self) -> PluginResult:
        import datetime
        try:
            station_id = self.config.get("station_id") or "9414290"
            units = self.config.get("units") or "english"
            today = datetime.date.today().strftime("%Y%m%d")

            response = requests.get(
                API_URL,
                params={
                    "begin_date": today,
                    "end_date": today,
                    "station": station_id,
                    "product": "predictions",
                    "datum": "MLLW",
                    "time_zone": "lst_ldt",
                    "interval": "hilo",
                    "units": units,
                    "application": "FiestaBoard",
                    "format": "json",
                },
                headers={"User-Agent": USER_AGENT},
                timeout=10,
            )
            response.raise_for_status()
            data = response.json()

            predictions = data.get("predictions", [])
            if not predictions:
                error = data.get("error", {}).get("message", "No predictions returned")
                return PluginResult(available=False, error=error)

            # Find the next tide (first one after now)
            now = datetime.datetime.now()
            next_tide = None
            for pred in predictions:
                t_str = pred.get("t", "")
                try:
                    t = datetime.datetime.strptime(t_str, "%Y-%m-%d %H:%M")
                except ValueError:
                    continue
                if t >= now:
                    next_tide = pred
                    break

            if next_tide is None:
                next_tide = predictions[0]

            tide_type = "High" if next_tide.get("type", "H") == "H" else "Low"
            t_str = next_tide.get("t", "")
            try:
                t = datetime.datetime.strptime(t_str, "%Y-%m-%d %H:%M")
                next_time = t.strftime("%-I:%M %p")
            except ValueError:
                next_time = t_str
            height = next_tide.get("v", "?")
            unit_label = "ft" if units == "english" else "m"
            next_height = f"{height} {unit_label}"

            station_info = data.get("metadata", {})
            station_name = str(station_info.get("name", station_id))

            return PluginResult(
                available=True,
                data={
                    "next_type": tide_type,
                    "next_time": next_time,
                    "next_height": next_height,
                    "station_name": station_name,
                },
            )
        except Exception as e:
            logger.exception("Error fetching tide times")
            return PluginResult(available=False, error=str(e))

    def validate_config(self, config: Dict[str, Any]) -> List[str]:
        errors = []
        if not config.get("station_id"):
            errors.append("station_id is required")
        if config.get("units") not in (None, "english", "metric"):
            errors.append("units must be 'english' or 'metric'")
        return errors

    def cleanup(self) -> None:
        pass
