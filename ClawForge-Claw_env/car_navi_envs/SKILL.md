# Car Navigation Environment - Agent Workflow Guide

## Overview

This environment simulates an in-car navigation assistant. Agents can search for POIs, start navigation, manage waypoints, set route preferences, query traffic, plan EV charging, and control the navigation process.

## Key Commands

### Search and Navigate
- `search-poi --category <cat>` - Search by category (charging, food, hotel, attraction, parking, gas, rest_area)
- `search-poi --keyword <kw>` - Search by keyword
- `start-nav --poi-id <id>` - Start navigation to a POI

### Waypoint Management
- `add-waypoint --poi-id <id>` - Add intermediate stop
- `remove-waypoint --waypoint-index <idx>` - Remove a waypoint

### Route Control
- `route-preference --preference <pref>` - Set preference (fastest/shortest/avoid_highway/eco/avoid_congestion)
- `reroute` - Recalculate route

### Information Queries
- `traffic` - Get current traffic conditions and ETA
- `charging-plan` - Plan EV charging stops

### Navigation Process
- `arrive-waypoint --waypoint-index <idx>` - Mark waypoint as visited
- `arrive-destination` - Complete navigation
- `cancel-nav` - Cancel current navigation

## Session Model

Sessions are managed by the trainer. The agent receives bindings via environment variables:
- `CAR_NAVI_SESSION_ID` - Current session identifier
- `CAR_NAVI_STATE_ROOT` - State file directory
- `CAR_NAVI_SCENARIO_ID` - Active scenario

## Workflow

1. Search for POI using category or keyword
2. Start navigation with `start-nav`
3. Add waypoints as needed with `add-waypoint`
4. Adjust route preference if needed
5. Query traffic periodically with `traffic`
6. Confirm arrivals with `arrive-waypoint` or `arrive-destination`
7. Cancel navigation if needed with `cancel-nav`

## Constraints

- Always use the bound session (do not pass `--session-id` manually)
- Actions are logged with timestamps
- State is persisted atomically with file locking