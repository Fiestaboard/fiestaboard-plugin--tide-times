# Tide Times Setup Guide

Display today's high and low tide predictions for any NOAA tide gauge station.

## Overview

The Tide Times plugin queries the NOAA Tides and Currents API for tide predictions at a user-specified station ID. It shows the next high and low tide times and heights. No API key required.

- API reference: https://api.tidesandcurrents.noaa.gov/api/prod/

### Prerequisites

No API key required. Find your station ID at tidesandcurrents.noaa.gov.

## Quick Setup

1. **Enable** — Go to **Integrations** in your FiestaBoard settings and enable **Tide Times**.
2. **Configure** — Fill in the plugin settings (see Configuration Reference below).
3. **Template** — Add a page using the `tide_times` plugin variables:
   ```
   {{{ tide_times.status }}}
   ```
4. **View** — Navigate to your board page to see the live display.

## Template Variables

| Variable | Description | Example |
|---|---|---|
| `tide_times.next_type` | Next tide type (High or Low) | `High` |
| `tide_times.next_time` | Time of the next tide | `2:45 PM` |
| `tide_times.next_height` | Height of the next tide (ft or m) | `5.4 ft` |
| `tide_times.station_name` | Station name | `San Francisco, CA` |

## Configuration Reference

| Setting | Name | Description | Default |
|---|---|---|---|
| `enabled` | Enabled |  | `False` |
| `station_id` | Station ID | NOAA tide gauge station ID (e.g. 9414290 for San Francisco). | `9414290` |
| `units` | Units | Measurement units. | `english` |
| `refresh_seconds` | Refresh Interval (seconds) | How often to fetch tide predictions. | `1800` |

## Troubleshooting

- **Invalid station** — find your station ID at tidesandcurrents.noaa.gov/stations.html.
- **No predictions** — some stations may not have tidal predictions; try a nearby station.

