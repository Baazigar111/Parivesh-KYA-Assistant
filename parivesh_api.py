"""
parivesh_api.py
---------------
API client and local caching for PARIVESH 2.0 master datasets (Activities and Sub-Activities).
"""

import os
import json
import logging
import requests

logger = logging.getLogger(__name__)

BASE_API_URL = "https://parivesh.nic.in/parivesh_api/kya"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Referer": "https://parivesh.nic.in/",
}


def load_activities():
    """
    Loads activities from local cache 'parivesh_activities.json' if present;
    otherwise queries the live /getactivities endpoint.
    """
    if os.path.exists("parivesh_activities.json"):
        try:
            with open("parivesh_activities.json", "r", encoding="utf-8") as f:
                data = json.load(f)
                if data:
                    return data
        except Exception as e:
            logger.warning("Failed to read local parivesh_activities.json: %s", e)

    try:
        res = requests.get(f"{BASE_API_URL}/getactivities", headers=HEADERS, timeout=10)
        if res.status_code == 200:
            return res.json()
    except Exception as e:
        logger.error("Error fetching activities from API: %s", e)

    return []


def get_subactivities(activity_id):
    """
    Fetches the sub-activities list for a given activity ID.
    """
    url = f"{BASE_API_URL}/getSubactivity?id={activity_id}"
    try:
        res = requests.get(url, headers=HEADERS, timeout=10)
        if res.status_code == 200:
            data = res.json()
            if isinstance(data, list):
                return data
            if isinstance(data, dict):
                return data.get("data", data.get("result", []))
    except Exception as e:
        logger.warning("Could not load sub-activities for ID %s: %s", activity_id, e)
    return []
