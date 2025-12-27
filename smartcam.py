#!/usr/bin/env python3
"""
Smart Cam Controller
Designed for the SNH-P6410BN, but maybe it'll work for your Smart Cam too

by BreadCodes
"""

import json
from typing import Any, Optional

import requests
from requests.auth import HTTPDigestAuth


class SmartCameraAPI:
    def __init__(self, ip: str, username: str = "admin", password: str = ""):
        self.ip = ip
        self.username = username
        self.password = password
        self.base_url = f"http://{ip}/stw-cgi-rest"
        self.auth = HTTPDigestAuth(username, password)

    def _request(
        self, endpoint: str, method: str = "GET", body: Optional[dict] = None
    ) -> Any:
        url = f"{self.base_url}{endpoint}"

        try:
            if method == "GET":
                response = requests.get(url, auth=self.auth)
            elif method == "PUT":
                headers = {"Content-Type": "application/json"}
                response = requests.put(
                    url,
                    auth=self.auth,
                    headers=headers,
                    data=json.dumps(body) if body else None,
                )
            else:
                raise ValueError(f"Unsupported method: {method}")

            if response.status_code >= 200 and response.status_code < 300:
                try:
                    return response.json()
                except json.JSONDecodeError:
                    return response.text
            else:
                print(f"Error: HTTP {response.status_code}")
                print(response.text)
                return None

        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            return None

    def get_device_info(self):
        return self._request("/system/deviceinfo")

    def get_date(self):
        return self._request("/system/date")

    def get_timezone_list(self):
        return self._request("/system/date/timezonelist")

    def perform_restart(self):
        return self._request("/system/power", "PUT")

    def perform_factory_reset(self):
        return self._request("/system/factoryreset", "PUT")

    def get_interface(self):
        return self._request("/network/interface")

    def get_wifi(self):
        return self._request("/network/wifi")

    def scan_wifi(self):
        return self._request("/network/wifi/scan")

    def set_wifi_enabled(self, enabled: bool):
        return self._request("/network/wifi", "PUT", {"Enable": enabled})

    def connect_wifi(self, ssid: str, password: str):
        return self._request(
            "/network/wifi/connect",
            "PUT",
            {"SSID": ssid, "Password": password, "SecurityMode": "PSK"},
        )

    def get_camera(self):
        return self._request("/image/camera")

    def get_image_enhancements(self):
        return self._request("/image/imageenhancements")

    def get_flip(self):
        return self._request("/image/flip")

    def set_vertical_flip(self, enabled: bool):
        return self._request("/image/flip", "PUT", {"VerticalFlipEnable": enabled})

    def set_horizontal_flip(self, enabled: bool):
        return self._request("/image/flip", "PUT", {"HorizontalFlipEnable": enabled})

    def get_overlay(self):
        return self._request("/image/overlay")

    def set_overlay(self, enabled: bool):
        return self._request("/image/overlay", "PUT", {"TimeEnable": enabled})

    def get_other_outputs(self):
        return self._request("/io/otheroutputs")

    def set_status_led(self, state: str):
        return self._request("/io/otheroutputs", "PUT", {"StatusLED.State": state})

    def get_audio_input(self):
        return self._request("/media/audioinput")

    def get_audio_output(self):
        return self._request("/media/audiooutput")

    def get_video_analysis(self):
        return self._request("/eventsources/videoanalysis")

    def set_detection_type(self, detection_type: str):
        return self._request(
            "/eventsources/videoanalysis", "PUT", {"DetectionType": detection_type}
        )

    def get_audio_detection(self):
        return self._request("/eventsources/audiodetection")

    def get_alarm(self):
        return self._request("/eventsources/alarm")

    def get_alarm_input(self):
        return self._request("/io/alarminput")

    def get_alarm_output(self):
        return self._request("/io/alarmoutput")

    def get_rtsp_url(self, profile_id: int, port: int = 554) -> str:
        return f"rtsp://{self.username}:{self.password}@{self.ip}:{port}/profile{profile_id}/media.smp"

    def get_stream_profiles(self):
        return [
            {"id": 1, "resolution": "1920x1080", "fps": 1},
            {"id": 2, "resolution": "640x360", "fps": 10},
            {"id": 3, "resolution": "640x360", "fps": 30},
            {"id": 4, "resolution": "1280x720", "fps": 30},
            {"id": 5, "resolution": "1920x1080", "fps": 30},
            {"id": 6, "resolution": "640x360", "fps": 30},
        ]
