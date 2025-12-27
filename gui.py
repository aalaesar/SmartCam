#!/usr/bin/env python3
"""
Smart Cam Controller GUI

by BreadCodes
"""

import json
import sys
from typing import Optional

from PySide6.QtCore import QThread, Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QApplication,
    QGridLayout,
    QGroupBox,
    QInputDialog,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QStatusBar,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from smartcam import SmartCameraAPI


class APIWorker(QThread):
    finished = Signal(object)
    error = Signal(str)

    def __init__(self, func, *args, **kwargs):
        super().__init__()
        self.func = func
        self.args = args
        self.kwargs = kwargs

    def run(self):
        try:
            result = self.func(*self.args, **self.kwargs)
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))


class SmartCamGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.api: Optional[SmartCameraAPI] = None
        self.worker: Optional[APIWorker] = None
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("SmartCam Controller")
        self.setMinimumSize(900, 700)

        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Connection panel
        connection_group = self.create_connection_panel()
        main_layout.addWidget(connection_group)

        # Tabs for different operations
        self.tabs = QTabWidget()
        self.tabs.addTab(self.create_system_tab(), "System")
        self.tabs.addTab(self.create_network_tab(), "Network")
        self.tabs.addTab(self.create_image_tab(), "Image")
        self.tabs.addTab(self.create_io_tab(), "I/O & LED")
        self.tabs.addTab(self.create_events_tab(), "Events")
        self.tabs.addTab(self.create_media_tab(), "Media")
        self.tabs.addTab(self.create_stream_tab(), "Streams")
        self.tabs.setEnabled(False)  # Disabled until connected
        main_layout.addWidget(self.tabs)

        # Output display
        output_group = QGroupBox("Output")
        output_layout = QVBoxLayout()
        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        self.output_text.setFont(QFont("Arial", 10))
        output_layout.addWidget(self.output_text)

        # Clear button
        clear_btn = QPushButton("Clear Output")
        clear_btn.clicked.connect(self.output_text.clear)
        output_layout.addWidget(clear_btn)

        output_group.setLayout(output_layout)
        main_layout.addWidget(output_group)

        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Disconnected")

    def create_connection_panel(self):
        group = QGroupBox("Connection Settings")
        layout = QGridLayout()

        # IP Address
        layout.addWidget(QLabel("IP Address:"), 0, 0)
        self.ip_input = QLineEdit("192.168.1.200")
        layout.addWidget(self.ip_input, 0, 1)

        # Username
        layout.addWidget(QLabel("Username:"), 0, 2)
        self.username_input = QLineEdit("admin")
        layout.addWidget(self.username_input, 0, 3)

        # Password
        layout.addWidget(QLabel("Password:"), 1, 0)
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.password_input, 1, 1)

        # Connect button
        self.connect_btn = QPushButton("Connect")
        self.connect_btn.clicked.connect(self.connect_camera)
        layout.addWidget(self.connect_btn, 1, 2, 1, 2)

        group.setLayout(layout)
        return group

    def create_system_tab(self):
        widget = QWidget()
        layout = QGridLayout()

        buttons = [
            ("Get Device Info", self.get_device_info),
            ("Get Date/Time", self.get_date),
            ("Get Timezone List", self.get_timezone_list),
            ("Restart Camera", self.restart_camera),
            ("Factory Reset", self.factory_reset),
        ]

        row, col = 0, 0
        for text, func in buttons:
            btn = QPushButton(text)
            btn.clicked.connect(func)
            layout.addWidget(btn, row, col)
            col += 1
            if col > 2:
                col = 0
                row += 1

        layout.setRowStretch(row + 1, 1)
        widget.setLayout(layout)
        return widget

    def create_network_tab(self):
        widget = QWidget()
        layout = QGridLayout()

        buttons = [
            ("Get Interface", self.get_interface),
            ("Get WiFi Status", self.get_wifi),
            ("Scan WiFi Networks", self.scan_wifi),
            ("Enable WiFi", self.enable_wifi),
            ("Disable WiFi", self.disable_wifi),
            ("Connect WiFi", self.connect_wifi),
        ]

        row, col = 0, 0
        for text, func in buttons:
            btn = QPushButton(text)
            btn.clicked.connect(func)
            layout.addWidget(btn, row, col)
            col += 1
            if col > 2:
                col = 0
                row += 1

        layout.setRowStretch(row + 1, 1)
        widget.setLayout(layout)
        return widget

    def create_image_tab(self):
        widget = QWidget()
        layout = QGridLayout()

        buttons = [
            ("Get Camera Settings", self.get_camera),
            ("Get Image Enhancements", self.get_image_enhancements),
            ("Get Flip Settings", self.get_flip),
            ("Enable Vertical Flip", lambda: self.set_vertical_flip(True)),
            ("Disable Vertical Flip", lambda: self.set_vertical_flip(False)),
            ("Enable Horizontal Flip", lambda: self.set_horizontal_flip(True)),
            ("Disable Horizontal Flip", lambda: self.set_horizontal_flip(False)),
            ("Get Overlay Settings", self.get_overlay),
            ("Enable Time Overlay", lambda: self.set_overlay(True)),
            ("Disable Time Overlay", lambda: self.set_overlay(False)),
        ]

        row, col = 0, 0
        for text, func in buttons:
            btn = QPushButton(text)
            btn.clicked.connect(func)
            layout.addWidget(btn, row, col)
            col += 1
            if col > 2:
                col = 0
                row += 1

        layout.setRowStretch(row + 1, 1)
        widget.setLayout(layout)
        return widget

    def create_io_tab(self):
        widget = QWidget()
        layout = QGridLayout()

        buttons = [
            ("Get LED Status", self.get_other_outputs),
            ("Turn LED On", lambda: self.set_status_led("On")),
            ("Turn LED Off", lambda: self.set_status_led("Off")),
            ("Get Alarm Input", self.get_alarm_input),
            ("Get Alarm Output", self.get_alarm_output),
        ]

        row, col = 0, 0
        for text, func in buttons:
            btn = QPushButton(text)
            btn.clicked.connect(func)
            layout.addWidget(btn, row, col)
            col += 1
            if col > 2:
                col = 0
                row += 1

        layout.setRowStretch(row + 1, 1)
        widget.setLayout(layout)
        return widget

    def create_events_tab(self):
        widget = QWidget()
        layout = QGridLayout()

        buttons = [
            ("Get Video Analysis", self.get_video_analysis),
            (
                "Enable Motion Detection",
                lambda: self.set_detection_type("MotionDetection"),
            ),
            ("Disable Motion Detection", lambda: self.set_detection_type("Off")),
            ("Get Audio Detection", self.get_audio_detection),
            ("Get Alarm Settings", self.get_alarm),
        ]

        row, col = 0, 0
        for text, func in buttons:
            btn = QPushButton(text)
            btn.clicked.connect(func)
            layout.addWidget(btn, row, col)
            col += 1
            if col > 2:
                col = 0
                row += 1

        layout.setRowStretch(row + 1, 1)
        widget.setLayout(layout)
        return widget

    def create_media_tab(self):
        widget = QWidget()
        layout = QGridLayout()

        buttons = [
            ("Get Audio Input", self.get_audio_input),
            ("Get Audio Output", self.get_audio_output),
        ]

        row, col = 0, 0
        for text, func in buttons:
            btn = QPushButton(text)
            btn.clicked.connect(func)
            layout.addWidget(btn, row, col)
            col += 1
            if col > 2:
                col = 0
                row += 1

        layout.setRowStretch(row + 1, 1)
        widget.setLayout(layout)
        return widget

    def create_stream_tab(self):
        widget = QWidget()
        layout = QVBoxLayout()

        btn = QPushButton("Show All RTSP Stream URLs")
        btn.clicked.connect(self.show_streams)
        layout.addWidget(btn)

        self.stream_output = QTextEdit()
        self.stream_output.setReadOnly(True)
        self.stream_output.setFont(QFont("Arial", 10))
        layout.addWidget(self.stream_output)

        widget.setLayout(layout)
        return widget

    def connect_camera(self):
        ip = self.ip_input.text().strip()
        username = self.username_input.text().strip()
        password = self.password_input.text()

        if not ip or not username or not password:
            QMessageBox.warning(self, "Error", "Please fill in all connection fields")
            return

        try:
            self.api = SmartCameraAPI(ip, username, password)
            self.tabs.setEnabled(True)
            self.connect_btn.setText("Connected")
            self.connect_btn.setEnabled(False)
            self.status_bar.showMessage(f"Connected to {ip}")
            self.append_output(f"Connected to {ip} as {username}")
        except Exception as e:
            QMessageBox.critical(self, "Connection Error", str(e))

    def run_api_call(self, func, *args, **kwargs):
        if not self.api:
            QMessageBox.warning(self, "Error", "Not connected to camera")
            return

        self.status_bar.showMessage("Processing...")
        self.worker = APIWorker(func, *args, **kwargs)
        self.worker.finished.connect(self.on_api_success)
        self.worker.error.connect(self.on_api_error)
        self.worker.start()

    def on_api_success(self, result):
        self.status_bar.showMessage("Ready")
        if result:
            if isinstance(result, (dict, list)):
                self.append_output(json.dumps(result, indent=2))
            else:
                self.append_output(str(result))
        else:
            self.append_output("Operation completed (no data returned)")

    def on_api_error(self, error):
        self.status_bar.showMessage("Error occurred")
        QMessageBox.critical(self, "API Error", error)
        self.append_output(f"ERROR: {error}")

    def append_output(self, text):
        self.output_text.append(text)
        self.output_text.append("-" * 80)

    # System operations
    def get_device_info(self):
        if not self.api:
            return
        self.run_api_call(self.api.get_device_info)

    def get_date(self):
        if not self.api:
            return
        self.run_api_call(self.api.get_date)

    def get_timezone_list(self):
        if not self.api:
            return
        self.run_api_call(self.api.get_timezone_list)

    def restart_camera(self):
        if not self.api:
            return
        reply = QMessageBox.question(
            self,
            "Confirm Restart",
            "Are you sure you want to restart the camera?",
            QMessageBox.Yes | QMessageBox.No,
        )
        if reply == QMessageBox.Yes:
            self.run_api_call(self.api.perform_restart)

    def factory_reset(self):
        if not self.api:
            return
        text, ok = QInputDialog.getText(
            self, "Factory Reset", "Type 'RESET' to confirm factory reset:"
        )
        if ok and text == "RESET":
            self.run_api_call(self.api.perform_factory_reset)
        elif ok:
            QMessageBox.warning(self, "Cancelled", "Factory reset cancelled")

    # Network operations
    def get_interface(self):
        if not self.api:
            return
        self.run_api_call(self.api.get_interface)

    def get_wifi(self):
        if not self.api:
            return
        self.run_api_call(self.api.get_wifi)

    def scan_wifi(self):
        if not self.api:
            return
        self.run_api_call(self.api.scan_wifi)

    def enable_wifi(self):
        if not self.api:
            return
        self.run_api_call(self.api.set_wifi_enabled, True)

    def disable_wifi(self):
        if not self.api:
            return
        self.run_api_call(self.api.set_wifi_enabled, False)

    def connect_wifi(self):
        if not self.api:
            return
        ssid, ok1 = QInputDialog.getText(self, "WiFi SSID", "Enter WiFi SSID:")
        if not ok1 or not ssid:
            return

        password, ok2 = QInputDialog.getText(
            self, "WiFi Password", "Enter WiFi password:", QLineEdit.Password
        )
        if not ok2:
            return

        self.run_api_call(self.api.connect_wifi, ssid, password)

    # Image operations
    def get_camera(self):
        if not self.api:
            return
        self.run_api_call(self.api.get_camera)

    def get_image_enhancements(self):
        if not self.api:
            return
        self.run_api_call(self.api.get_image_enhancements)

    def get_flip(self):
        if not self.api:
            return
        self.run_api_call(self.api.get_flip)

    def set_vertical_flip(self, enabled):
        if not self.api:
            return
        self.run_api_call(self.api.set_vertical_flip, enabled)

    def set_horizontal_flip(self, enabled):
        if not self.api:
            return
        self.run_api_call(self.api.set_horizontal_flip, enabled)

    def get_overlay(self):
        if not self.api:
            return
        self.run_api_call(self.api.get_overlay)

    def set_overlay(self, enabled):
        if not self.api:
            return
        self.run_api_call(self.api.set_overlay, enabled)

    # I/O operations
    def get_other_outputs(self):
        if not self.api:
            return
        self.run_api_call(self.api.get_other_outputs)

    def set_status_led(self, state):
        if not self.api:
            return
        self.run_api_call(self.api.set_status_led, state)

    def get_alarm_input(self):
        if not self.api:
            return
        self.run_api_call(self.api.get_alarm_input)

    def get_alarm_output(self):
        if not self.api:
            return
        self.run_api_call(self.api.get_alarm_output)

    # Events operations
    def get_video_analysis(self):
        if not self.api:
            return
        self.run_api_call(self.api.get_video_analysis)

    def set_detection_type(self, detection_type):
        if not self.api:
            return
        self.run_api_call(self.api.set_detection_type, detection_type)

    def get_audio_detection(self):
        if not self.api:
            return
        self.run_api_call(self.api.get_audio_detection)

    def get_alarm(self):
        if not self.api:
            return
        self.run_api_call(self.api.get_alarm)

    # Media operations
    def get_audio_input(self):
        if not self.api:
            return
        self.run_api_call(self.api.get_audio_input)

    def get_audio_output(self):
        if not self.api:
            return
        self.run_api_call(self.api.get_audio_output)

    # Stream operations
    def show_streams(self):
        if not self.api:
            QMessageBox.warning(self, "Error", "Not connected to camera")
            return

        output = "Available RTSP Stream URLs:\n"
        output += "=" * 80 + "\n\n"

        for profile in self.api.get_stream_profiles():
            url = self.api.get_rtsp_url(profile["id"])
            output += f"Profile {profile['id']}: {profile['resolution']} @ {profile['fps']}fps\n"
            output += f"  URL: {url}\n"
            output += f'  VLC: vlc "{url}"\n'
            output += f'  ffplay: ffplay -rtsp_transport tcp -i "{url}"\n\n'

        self.stream_output.setPlainText(output)
        self.append_output("Stream URLs displayed in Streams tab")


def main():
    print("""
------------------------------
SmartCam
Copyright © 2025 BreadCodes
https://github.com/breadbored/SmartCam
------------------------------
    """)
    app = QApplication(sys.argv)
    window = SmartCamGUI()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
