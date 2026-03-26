"""
Ninja Shield - PyQt6 GUI
Option 2: Tabbed Control Center
"""

import sys
import os
import json
import subprocess
import threading
from pathlib import Path

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTabWidget, QTableWidget, QTableWidgetItem, QPushButton, QLabel,
    QLineEdit, QDialog, QDialogButtonBox, QMessageBox, QHeaderView,
    QFrame, QSplitter, QTextEdit, QFormLayout, QScrollArea, QGridLayout,
    QAbstractItemView, QStatusBar, QProgressDialog, QProgressBar
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer, QSize
from PyQt6.QtGui import QFont, QColor, QPalette, QIcon

from fingerprint_engine import (
    generate_fingerprint, save_fingerprint, load_fingerprint,
    assign_vpn_city, list_profiles, get_timezone_for_city
)
from license_manager import check_license, activate_license
def resource_path(relative_path):
    """Get absolute path to resource - works for dev and PyInstaller."""
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)
PROFILES_DIR = os.path.join(os.path.expanduser("~"), "NinjaShield", "profiles")
os.makedirs(PROFILES_DIR, exist_ok=True)

# ─── Stylesheet ───────────────────────────────────────────────────────────────
STYLE = """
QMainWindow, QWidget {
    background-color: #12131a;
    color: #e5e7eb;
    font-family: 'Segoe UI', sans-serif;
    font-size: 13px;
}

QTabWidget::pane {
    border: none;
    background: #12131a;
}

QTabBar {
    background: #0e0f16;
}

QTabBar::tab {
    background: #0e0f16;
    color: #4b5563;
    padding: 10px 22px;
    border: none;
    border-bottom: 2px solid transparent;
    font-size: 12px;
    font-weight: 600;
}

QTabBar::tab:selected {
    color: #a78bfa;
    border-bottom: 2px solid #7c3aed;
    background: #1a1b2a;
}

QTabBar::tab:hover:!selected {
    color: #9ca3af;
    background: #161720;
}

QTableWidget {
    background: #12131a;
    border: none;
    gridline-color: #1e2033;
    color: #e5e7eb;
    font-size: 12px;
    selection-background-color: #1e1b3a;
    selection-color: #e5e7eb;
    outline: none;
}

QTableWidget::item {
    padding: 8px 10px;
    border-bottom: 1px solid #111521;
}

QTableWidget::item:selected {
    background: #1e1b3a;
    color: #e5e7eb;
}

QHeaderView::section {
    background: #0e0f16;
    color: #4b5563;
    padding: 8px 10px;
    border: none;
    border-bottom: 1px solid #1e2033;
    font-size: 11px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 1px;
}

QLineEdit {
    background: #1a1b2a;
    border: 1px solid #2a2b3d;
    border-radius: 6px;
    padding: 8px 12px;
    color: #e5e7eb;
    font-size: 12px;
}

QLineEdit:focus {
    border: 1px solid #7c3aed;
}

QLineEdit::placeholder {
    color: #4b5563;
}

QPushButton {
    border-radius: 6px;
    padding: 8px 16px;
    font-size: 12px;
    font-weight: 600;
    border: none;
}

QPushButton#btnPrimary {
    background: #7c3aed;
    color: #fff;
}
QPushButton#btnPrimary:hover { background: #6d28d9; }
QPushButton#btnPrimary:pressed { background: #5b21b6; }

QPushButton#btnGhost {
    background: #1e2033;
    color: #9ca3af;
    border: 1px solid #2a2b3d;
}
QPushButton#btnGhost:hover { background: #252640; color: #e5e7eb; }

QPushButton#btnDanger {
    background: #1f0a0a;
    color: #f87171;
    border: 1px solid #3f1e1e;
}
QPushButton#btnDanger:hover { background: #2d0f0f; }

QPushButton#btnGreen {
    background: #052e16;
    color: #4ade80;
    border: 1px solid #14532d;
}
QPushButton#btnGreen:hover { background: #073a1c; }

QPushButton:disabled {
    opacity: 0.4;
}

QLabel#sectionTitle {
    font-size: 18px;
    font-weight: 800;
    color: #e5e7eb;
}

QLabel#subTitle {
    font-size: 12px;
    color: #4b5563;
}

QFrame#topBar {
    background: #0e0f16;
    border-bottom: 1px solid #1e2033;
}

QFrame#footerBar {
    background: #0e0f16;
    border-top: 1px solid #1e2033;
}

QFrame#statCard {
    background: #0d1117;
    border: 1px solid #1e2130;
    border-radius: 8px;
}

QTextEdit {
    background: #0a0c10;
    border: 1px solid #1e2033;
    border-radius: 6px;
    color: #4ade80;
    font-family: 'Consolas', 'Courier New', monospace;
    font-size: 11px;
    padding: 8px;
}

QScrollBar:vertical {
    background: #0e0f16;
    width: 6px;
    border-radius: 3px;
}
QScrollBar::handle:vertical {
    background: #2a2b3d;
    border-radius: 3px;
    min-height: 20px;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0px; }

QStatusBar {
    background: #0a0b10;
    color: #4b5563;
    font-size: 11px;
    border-top: 1px solid #1e2033;
}

QDialog {
    background: #12131a;
}

QFormLayout QLabel {
    color: #9ca3af;
    font-size: 12px;
}

QProgressDialog {
    background: #12131a;
    color: #e5e7eb;
}

QMessageBox {
    background: #12131a;
    color: #e5e7eb;
}

QMessageBox QPushButton {
    min-width: 80px;
}
"""

# ─── Activation Window ───────────────────────────────────────────────────────
class ActivationWindow(QWidget):
    activated = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Ninja Shield — Activation")
        self.setWindowIcon(QIcon(resource_path("icon.ico")))
        self.setFixedSize(480, 340)
        self.setStyleSheet(STYLE)
        self._build_ui()
        self._check_existing()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 36, 40, 36)
        layout.setSpacing(0)

        # Logo
        logo = QLabel("◈  Ninja Shield")
        logo.setStyleSheet("font-size: 18px; font-weight: 800; color: #a78bfa;")
        layout.addWidget(logo)

        layout.addSpacing(6)

        sub = QLabel("License Activation")
        sub.setStyleSheet("font-size: 12px; color: #4b5563;")
        layout.addWidget(sub)

        layout.addSpacing(28)

        # Key input label
        key_label = QLabel("Enter your license key:")
        key_label.setStyleSheet("font-size: 12px; color: #9ca3af;")
        layout.addWidget(key_label)

        layout.addSpacing(8)

        # Key input
        self.key_input = QLineEdit()
        self.key_input.setPlaceholderText("FBPM-XXXX-XXXX-XXXX-XXXX")
        self.key_input.setFixedHeight(40)
        self.key_input.setStyleSheet("""
            QLineEdit {
                background: #1a1b2a;
                border: 1px solid #2a2b3d;
                border-radius: 6px;
                padding: 8px 14px;
                color: #e5e7eb;
                font-size: 13px;
                font-family: 'Consolas', monospace;
                letter-spacing: 1px;
            }
            QLineEdit:focus { border: 1px solid #7c3aed; }
        """)
        self.key_input.returnPressed.connect(self._activate)
        layout.addWidget(self.key_input)

        layout.addSpacing(12)

        # Activate button
        self.activate_btn = QPushButton("Activate License")
        self.activate_btn.setObjectName("btnPrimary")
        self.activate_btn.setFixedHeight(40)
        self.activate_btn.clicked.connect(self._activate)
        layout.addWidget(self.activate_btn)

        layout.addSpacing(16)

        # Status label
        self.status_label = QLabel("")
        self.status_label.setStyleSheet("font-size: 11px; color: #4b5563;")
        self.status_label.setWordWrap(True)
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)

        layout.addStretch()

        # Footer
        footer = QLabel("Each license is valid for one device only.")
        footer.setStyleSheet("font-size: 10px; color: #2a2b3d;")
        footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(footer)

    def _check_existing(self):
        """Check if machine already has a valid license on startup."""
        result = check_license()
        if result["status"] == "active":
            self.activated.emit()
        elif result["status"] == "expired":
            self.status_label.setStyleSheet("font-size: 11px; color: #f87171;")
            self.status_label.setText(
                f"⚠  Your license expired on "
                f"{result['expiry'].strftime('%B %d, %Y')}. "
                f"Please enter a new key to continue."
            )
        elif result["status"] == "tampered":
            self.status_label.setStyleSheet("font-size: 11px; color: #f87171;")
            self.status_label.setText("⚠  License file tampered. Please re-enter your key.")
        elif result["status"] == "wrong_machine":
            self.status_label.setStyleSheet("font-size: 11px; color: #f87171;")
            self.status_label.setText("⚠  This license belongs to a different machine.")

    def _activate(self):
        key = self.key_input.text().strip()
        if not key:
            self.status_label.setStyleSheet("font-size: 11px; color: #f87171;")
            self.status_label.setText("Please enter your license key.")
            return

        self.activate_btn.setEnabled(False)
        self.activate_btn.setText("Checking...")
        self.status_label.setText("")

        result = activate_license(key)

        if result["success"]:
            self.status_label.setStyleSheet("font-size: 11px; color: #4ade80;")
            self.status_label.setText(
                f"✓ Activated! Valid until "
                f"{result['expiry'].strftime('%B %d, %Y')} "
                f"({result['days_left']} days remaining)"
            )
            QTimer.singleShot(1500, self.activated.emit)
        else:
            self.status_label.setStyleSheet("font-size: 11px; color: #f87171;")
            self.status_label.setText(f"✕  {result['error']}")
            self.activate_btn.setEnabled(True)
            self.activate_btn.setText("Activate License")
# ─── Worker Thread for timezone lookup ───────────────────────────────────────
class TimezoneWorker(QThread):
    result = pyqtSignal(str, str)  # timezone, city
    error  = pyqtSignal(str)

    def __init__(self, city):
        super().__init__()
        self.city = city

    def run(self):
        try:
            tz = get_timezone_for_city(self.city)
            self.result.emit(tz, self.city)
        except Exception as e:
            self.error.emit(str(e))


# ─── Worker Thread for browser launch ────────────────────────────────────────
class LaunchWorker(QThread):
    log  = pyqtSignal(str)
    done = pyqtSignal()

    def __init__(self, profile_name):
        super().__init__()
        self.profile_name = profile_name

    def run(self):
        self.log.emit(f"Launching {self.profile_name}...")
        try:
            from browser_launcher import launch_browser
            import asyncio
            import traceback
            import sys

            if sys.platform == "win32":
                asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                loop.run_until_complete(launch_browser(self.profile_name, profiles_dir=PROFILES_DIR))
            finally:
                loop.close()
        except Exception as e:
            error_details = traceback.format_exc()
            self.log.emit(f"[ERROR] {e}")
            self.log.emit(f"[DETAILS] {error_details}")
            log_path = os.path.join(os.path.expanduser("~"), "NinjaShield", "error.log")
            with open(log_path, "w") as f:
                f.write(error_details)
            self.log.emit(f"[LOG SAVED] {log_path}")
        self.done.emit()
# ─── Create Profile Dialog ────────────────────────────────────────────────────
class CreateProfileDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Create New Profile")
        self.setMinimumWidth(420)
        self.setStyleSheet(STYLE)
        self.timezone_result = None
        self.tz_worker = None
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(24, 24, 24, 24)

        title = QLabel("Create New Profile")
        title.setObjectName("sectionTitle")
        layout.addWidget(title)

        sub = QLabel("Profile name and VPN city (optional)")
        sub.setObjectName("subTitle")
        layout.addWidget(sub)

        # Profile name
        form = QFormLayout()
        form.setSpacing(12)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("e.g. fb_account_01")
        form.addRow("Profile Name:", self.name_input)

        # VPN city
        city_row = QHBoxLayout()
        self.city_input = QLineEdit()
        self.city_input.setPlaceholderText("e.g. Dubai, UAE  (leave blank = no VPN)")
        self.city_input.textChanged.connect(self._on_city_changed)
        city_row.addWidget(self.city_input)

        self.lookup_btn = QPushButton("Lookup")
        self.lookup_btn.setObjectName("btnGhost")
        self.lookup_btn.setFixedWidth(75)
        self.lookup_btn.clicked.connect(self._lookup_timezone)
        city_row.addWidget(self.lookup_btn)

        city_widget = QWidget()
        city_widget.setLayout(city_row)
        form.addRow("VPN City:", city_widget)

        layout.addLayout(form)

        # Timezone status label
        self.tz_label = QLabel("Timezone: (auto-detected after lookup)")
        self.tz_label.setStyleSheet("color: #4b5563; font-size: 11px; font-family: 'Consolas', monospace;")
        layout.addWidget(self.tz_label)

        # Buttons
        btn_row = QHBoxLayout()
        btn_row.addStretch()
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setObjectName("btnGhost")
        cancel_btn.clicked.connect(self.reject)

        self.create_btn = QPushButton("Create Profile")
        self.create_btn.setObjectName("btnPrimary")
        self.create_btn.clicked.connect(self._on_create)

        btn_row.addWidget(cancel_btn)
        btn_row.addWidget(self.create_btn)
        layout.addLayout(btn_row)

    def _on_city_changed(self):
        self.timezone_result = None
        self.tz_label.setText("Timezone: (click Lookup to auto-detect)")
        self.tz_label.setStyleSheet("color: #4b5563; font-size: 11px;")

    def _lookup_timezone(self):
        city = self.city_input.text().strip()
        if not city:
            self.tz_label.setText("Timezone: No city entered")
            return

        self.lookup_btn.setText("...")
        self.lookup_btn.setEnabled(False)
        self.tz_label.setText("Looking up timezone...")
        self.tz_label.setStyleSheet("color: #f59e0b; font-size: 11px;")

        self.tz_worker = TimezoneWorker(city)
        self.tz_worker.result.connect(self._on_timezone_found)
        self.tz_worker.error.connect(self._on_timezone_error)
        self.tz_worker.start()

    def _on_timezone_found(self, tz, city):
        self.timezone_result = tz
        self.tz_label.setText(f"✓ Timezone: {tz}")
        self.tz_label.setStyleSheet("color: #4ade80; font-size: 11px; font-family: 'Consolas', monospace;")
        self.lookup_btn.setText("Lookup")
        self.lookup_btn.setEnabled(True)

    def _on_timezone_error(self, err):
        self.tz_label.setText(f"⚠ Lookup failed — will use fallback timezone")
        self.tz_label.setStyleSheet("color: #f87171; font-size: 11px;")
        self.lookup_btn.setText("Lookup")
        self.lookup_btn.setEnabled(True)

    def _on_create(self):
        name = self.name_input.text().strip()
        if not name:
            QMessageBox.warning(self, "Error", "Profile name cannot be empty.")
            return
        path = os.path.join(PROFILES_DIR, f"{name}.json")
        if os.path.exists(path):
            QMessageBox.warning(self, "Error", f"Profile '{name}' already exists.")
            return
        self.accept()

    def get_data(self):
        return {
            "name": self.name_input.text().strip(),
            "city": self.city_input.text().strip() or "No VPN (Local)",
            "timezone": self.timezone_result
        }


# ─── Edit VPN Dialog ─────────────────────────────────────────────────────────
class EditVPNDialog(QDialog):
    def __init__(self, profile_name, current_city, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Assign VPN — {profile_name}")
        self.setMinimumWidth(400)
        self.setStyleSheet(STYLE)
        self.tz_worker = None
        self.timezone_result = None
        self._build_ui(profile_name, current_city)

    def _build_ui(self, profile_name, current_city):
        layout = QVBoxLayout(self)
        layout.setSpacing(14)
        layout.setContentsMargins(24, 24, 24, 24)

        title = QLabel(f"Assign VPN City")
        title.setObjectName("sectionTitle")
        layout.addWidget(title)

        sub = QLabel(f"Profile: {profile_name}")
        sub.setObjectName("subTitle")
        layout.addWidget(sub)

        city_row = QHBoxLayout()
        self.city_input = QLineEdit()
        self.city_input.setText(current_city if current_city != "No VPN (Local)" else "")
        self.city_input.setPlaceholderText("e.g. London, UK")
        self.city_input.textChanged.connect(self._on_city_changed)
        city_row.addWidget(self.city_input)

        self.lookup_btn = QPushButton("Lookup")
        self.lookup_btn.setObjectName("btnGhost")
        self.lookup_btn.setFixedWidth(75)
        self.lookup_btn.clicked.connect(self._lookup_timezone)
        city_row.addWidget(self.lookup_btn)

        layout.addLayout(city_row)

        self.tz_label = QLabel("Timezone: auto-detected on lookup")
        self.tz_label.setStyleSheet("color: #4b5563; font-size: 11px; font-family: 'Consolas', monospace;")
        layout.addWidget(self.tz_label)

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setObjectName("btnGhost")
        cancel_btn.clicked.connect(self.reject)
        save_btn = QPushButton("Save")
        save_btn.setObjectName("btnPrimary")
        save_btn.clicked.connect(self.accept)
        btn_row.addWidget(cancel_btn)
        btn_row.addWidget(save_btn)
        layout.addLayout(btn_row)

    def _on_city_changed(self):
        self.timezone_result = None
        self.tz_label.setText("Timezone: (click Lookup to auto-detect)")
        self.tz_label.setStyleSheet("color: #4b5563; font-size: 11px;")

    def _lookup_timezone(self):
        city = self.city_input.text().strip()
        if not city:
            return
        self.lookup_btn.setText("...")
        self.lookup_btn.setEnabled(False)
        self.tz_label.setText("Looking up...")
        self.tz_label.setStyleSheet("color: #f59e0b; font-size: 11px;")
        self.tz_worker = TimezoneWorker(city)
        self.tz_worker.result.connect(self._on_tz_found)
        self.tz_worker.error.connect(lambda e: self._on_tz_err())
        self.tz_worker.start()

    def _on_tz_found(self, tz, city):
        self.timezone_result = tz
        self.tz_label.setText(f"✓ Timezone: {tz}")
        self.tz_label.setStyleSheet("color: #4ade80; font-size: 11px; font-family: 'Consolas', monospace;")
        self.lookup_btn.setText("Lookup")
        self.lookup_btn.setEnabled(True)

    def _on_tz_err(self):
        self.tz_label.setText("⚠ Lookup failed — fallback timezone will be used")
        self.tz_label.setStyleSheet("color: #f87171; font-size: 11px;")
        self.lookup_btn.setText("Lookup")
        self.lookup_btn.setEnabled(True)

    def get_data(self):
        city = self.city_input.text().strip() or "No VPN (Local)"
        return {"city": city, "timezone": self.timezone_result}


# ─── Proxy Dialog ─────────────────────────────────────────────────────────────
class ProxyDialog(QDialog):
    def __init__(self, profile_name, current_proxy=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Proxy — {profile_name}")
        self.setMinimumWidth(400)
        self.setStyleSheet(STYLE)
        self._build_ui(profile_name, current_proxy)

    def _build_ui(self, profile_name, current_proxy):
        layout = QVBoxLayout(self)
        layout.setSpacing(14)
        layout.setContentsMargins(24, 24, 24, 24)

        title = QLabel("Assign Proxy")
        title.setObjectName("sectionTitle")
        layout.addWidget(title)

        hint = QLabel(
            "Formats:\n"
            "  http://host:port\n"
            "  http://user:pass@host:port\n"
            "  socks5://user:pass@host:port"
        )
        hint.setStyleSheet("color: #4b5563; font-size: 11px; font-family: 'Consolas', monospace;")
        layout.addWidget(hint)

        self.proxy_input = QLineEdit()
        self.proxy_input.setPlaceholderText("http://user:pass@host:port")
        if current_proxy and current_proxy.get("host"):
            proto = current_proxy.get("protocol", "http")
            user  = current_proxy.get("username", "")
            pw    = current_proxy.get("password", "")
            host  = current_proxy.get("host", "")
            port  = current_proxy.get("port", 80)
            if user:
                self.proxy_input.setText(f"{proto}://{user}:{pw}@{host}:{port}")
            else:
                self.proxy_input.setText(f"{proto}://{host}:{port}")
        layout.addWidget(self.proxy_input)

        btn_row = QHBoxLayout()
        btn_row.addStretch()

        if current_proxy and current_proxy.get("host"):
            remove_btn = QPushButton("Remove Proxy")
            remove_btn.setObjectName("btnDanger")
            remove_btn.clicked.connect(lambda: self.done(2))
            btn_row.addWidget(remove_btn)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setObjectName("btnGhost")
        cancel_btn.clicked.connect(self.reject)
        save_btn = QPushButton("Save")
        save_btn.setObjectName("btnPrimary")
        save_btn.clicked.connect(self.accept)
        btn_row.addWidget(cancel_btn)
        btn_row.addWidget(save_btn)
        layout.addLayout(btn_row)

    def get_proxy_url(self):
        return self.proxy_input.text().strip()


# ─── Fingerprint View Dialog ──────────────────────────────────────────────────
class FingerprintDialog(QDialog):
    def __init__(self, profile_name, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Fingerprint — {profile_name}")
        self.setMinimumSize(500, 500)
        self.setStyleSheet(STYLE)
        self._build_ui(profile_name)

    def _build_ui(self, profile_name):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        title = QLabel(f"Fingerprint: {profile_name}")
        title.setObjectName("sectionTitle")
        layout.addWidget(title)

        fp = load_fingerprint(profile_name, PROFILES_DIR)
        text = QTextEdit()
        text.setReadOnly(True)

        lines = []
        skip = {"plugins", "fonts"}
        for k, v in fp.items():
            if k in skip:
                continue
            lines.append(f"{k:<28} {v}")
        text.setPlainText("\n".join(lines))
        layout.addWidget(text)

        close_btn = QPushButton("Close")
        close_btn.setObjectName("btnGhost")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn, alignment=Qt.AlignmentFlag.AlignRight)


# ─── Profiles Tab ─────────────────────────────────────────────────────────────
class ProfilesTab(QWidget):
    status_message = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self._workers = []
        self._build_ui()
        self.refresh()

    def _build_ui(self):
        self._workers = []
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Toolbar
        toolbar = QFrame()
        toolbar.setObjectName("topBar")
        toolbar.setFixedHeight(56)
        tbar_layout = QHBoxLayout(toolbar)
        tbar_layout.setContentsMargins(16, 0, 16, 0)
        tbar_layout.setSpacing(10)

        self.search = QLineEdit()
        self.search.setPlaceholderText("🔍  Search profiles...")
        self.search.textChanged.connect(self._filter)
        self.search.setFixedHeight(34)
        tbar_layout.addWidget(self.search)

        new_btn = QPushButton("+ New Profile")
        new_btn.setObjectName("btnPrimary")
        new_btn.setFixedHeight(34)
        new_btn.clicked.connect(self._create_profile)
        tbar_layout.addWidget(new_btn)

        layout.addWidget(toolbar)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["#", "Profile Name", "VPN City", "Timezone", "Screen", "Status"])
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        self.table.setColumnWidth(0, 45)
        self.table.setColumnWidth(4, 100)
        self.table.setColumnWidth(5, 80)
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.table.setShowGrid(False)
        self.table.setAlternatingRowColors(False)
        layout.addWidget(self.table)

        # Footer action bar
        footer = QFrame()
        footer.setObjectName("footerBar")
        footer.setFixedHeight(54)
        foot_layout = QHBoxLayout(footer)
        foot_layout.setContentsMargins(16, 0, 16, 0)
        foot_layout.setSpacing(8)

        self.launch_btn = QPushButton("▶  Launch")
        self.launch_btn.setObjectName("btnGreen")
        self.launch_btn.setFixedHeight(34)
        self.launch_btn.clicked.connect(self._launch_selected)

        self.vpn_btn = QPushButton("✎  VPN City")
        self.vpn_btn.setObjectName("btnGhost")
        self.vpn_btn.setFixedHeight(34)
        self.vpn_btn.clicked.connect(self._edit_vpn)

        self.proxy_btn = QPushButton("⇄  Proxy")
        self.proxy_btn.setObjectName("btnGhost")
        self.proxy_btn.setFixedHeight(34)
        self.proxy_btn.clicked.connect(self._edit_proxy)

        self.fp_btn = QPushButton("🔍  Fingerprint")
        self.fp_btn.setObjectName("btnGhost")
        self.fp_btn.setFixedHeight(34)
        self.fp_btn.clicked.connect(self._view_fp)

        self.regen_btn = QPushButton("↻  Regenerate")
        self.regen_btn.setObjectName("btnGhost")
        self.regen_btn.setFixedHeight(34)
        self.regen_btn.clicked.connect(self._regen_fp)

        self.del_btn = QPushButton("✕  Delete")
        self.del_btn.setObjectName("btnDanger")
        self.del_btn.setFixedHeight(34)
        self.del_btn.clicked.connect(self._delete_profile)

        self.clear_btn = QPushButton("🧹  Clear Cache")
        self.clear_btn.setObjectName("btnGhost")
        self.clear_btn.setFixedHeight(34)
        self.clear_btn.clicked.connect(self._clear_selected_cache)

        self.clear_all_btn = QPushButton("🧹  Clear All Cache")
        self.clear_all_btn.setObjectName("btnGhost")
        self.clear_all_btn.setFixedHeight(34)
        self.clear_all_btn.clicked.connect(self._clear_all_cache)

        self.count_label = QLabel("")
        self.count_label.setStyleSheet("color: #4b5563; font-size: 11px;")

        foot_layout.addWidget(self.launch_btn)
        foot_layout.addWidget(self.vpn_btn)
        foot_layout.addWidget(self.proxy_btn)
        foot_layout.addWidget(self.fp_btn)
        foot_layout.addWidget(self.regen_btn)
        foot_layout.addWidget(self.del_btn)
        foot_layout.addWidget(self.clear_btn)
        foot_layout.addWidget(self.clear_all_btn)
        foot_layout.addStretch()
        foot_layout.addWidget(self.count_label)

        layout.addWidget(footer)

    def refresh(self):
        profiles = list_profiles(PROFILES_DIR)
        self._populate(profiles)

    def _populate(self, profiles):
        self.table.setRowCount(0)
        for i, name in enumerate(profiles):
            fp = load_fingerprint(name, PROFILES_DIR)
            self.table.insertRow(i)

            num_item = QTableWidgetItem(str(i + 1))
            num_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            num_item.setForeground(QColor("#4b5563"))
            self.table.setItem(i, 0, num_item)

            name_item = QTableWidgetItem(name)
            name_item.setForeground(QColor("#e5e7eb"))
            self.table.setItem(i, 1, name_item)

            city = fp.get("vpn_city", "No VPN")
            flag = fp.get("vpn_flag", "🖥️")
            city_item = QTableWidgetItem(f"{flag}  {city}")
            city_item.setForeground(QColor("#9ca3af"))
            city_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(i, 2, city_item)

            tz_item = QTableWidgetItem(fp.get("timezone", "—"))
            tz_item.setForeground(QColor("#6b7280"))
            tz_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(i, 3, tz_item)

            screen = f"{fp['screen_width']}×{fp['screen_height']}"
            screen_item = QTableWidgetItem(screen)
            screen_item.setForeground(QColor("#6b7280"))
            self.table.setItem(i, 4, screen_item)

            has_proxy = bool(fp.get("proxy", {}).get("host"))
            status_text = "proxy" if has_proxy else "vpn" if city != "No VPN (Local)" else "local"
            status_item = QTableWidgetItem(status_text)
            color_map = {"proxy": "#60a5fa", "vpn": "#a78bfa", "local": "#4b5563"}
            status_item.setForeground(QColor(color_map.get(status_text, "#4b5563")))
            status_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(i, 5, status_item)

            self.table.setRowHeight(i, 38)

        self.count_label.setText(f"{len(profiles)} profile{'s' if len(profiles) != 1 else ''}")

    def _filter(self, text):
        profiles = list_profiles(PROFILES_DIR)
        filtered = [p for p in profiles if text.lower() in p.lower()]
        self._populate(filtered)

    def _selected_name(self):
        row = self.table.currentRow()
        if row < 0:
            return None
        return self.table.item(row, 1).text()

    def _create_profile(self):
        dlg = CreateProfileDialog(self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            data = dlg.get_data()
            self.status_message.emit(f"Creating profile '{data['name']}'...")
            fp = generate_fingerprint(data["name"], data["city"], data["timezone"])
            save_fingerprint(fp, PROFILES_DIR)
            self.refresh()
            self.status_message.emit(f"✓ Profile '{data['name']}' created  |  VPN: {data['city']}")

    def _launch_selected(self):
        name = self._selected_name()
        if not name:
            QMessageBox.information(self, "Select Profile", "Please select a profile to launch.")
            return
        fp   = load_fingerprint(name, PROFILES_DIR)
        city = fp.get("vpn_city", "No VPN (Local)")
        if city != "No VPN (Local)" and not fp.get("proxy", {}).get("host"):
            reply = QMessageBox.question(
                self, "VPN Required",
                f"This profile requires VPN connected to:\n\n  {fp.get('vpn_flag','')}  {city}\n\nIs your VPN connected?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply != QMessageBox.StandardButton.Yes:
                return

        self.status_message.emit(f"Launching {name}...")
        worker = LaunchWorker(name)
        worker.log.connect(lambda msg: self.status_message.emit(msg))
        worker.done.connect(lambda: self.status_message.emit(f"✓ {name} browser closed"))
        self._workers.append(worker)
        worker.start()

    def _edit_vpn(self):
        name = self._selected_name()
        if not name:
            QMessageBox.information(self, "Select Profile", "Please select a profile first.")
            return
        fp   = load_fingerprint(name, PROFILES_DIR)
        dlg  = EditVPNDialog(name, fp.get("vpn_city", "No VPN (Local)"), self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            data = dlg.get_data()
            city = data["city"]
            self.status_message.emit(f"Updating VPN for '{name}'...")
            if data["timezone"]:
                fp2 = load_fingerprint(name, PROFILES_DIR)
                from fingerprint_engine import _get_region_info
                region = _get_region_info(city)
                fp2["vpn_city"]  = city
                fp2["vpn_flag"]  = region["flag"]
                fp2["vpn_hint"]  = f"Connect VPN to {city}"
                fp2["languages"] = region["languages"]
                fp2["timezone"]  = data["timezone"]
                save_fingerprint(fp2, PROFILES_DIR)
            else:
                assign_vpn_city(name, city, PROFILES_DIR)
            self.refresh()
            self.status_message.emit(f"✓ VPN updated for '{name}' → {city}")

    def _edit_proxy(self):
        name = self._selected_name()
        if not name:
            QMessageBox.information(self, "Select Profile", "Please select a profile first.")
            return
        fp  = load_fingerprint(name, PROFILES_DIR)
        dlg = ProxyDialog(name, fp.get("proxy"), self)
        result = dlg.exec()

        if result == QDialog.DialogCode.Accepted:
            raw = dlg.get_proxy_url()
            if raw:
                from urllib.parse import urlparse
                parsed = urlparse(raw if "://" in raw else f"http://{raw}")
                fp["proxy"] = {
                    "protocol": parsed.scheme or "http",
                    "host":     parsed.hostname,
                    "port":     parsed.port or 80,
                    "username": parsed.username or "",
                    "password": parsed.password or "",
                }
                save_fingerprint(fp, PROFILES_DIR)
                self.refresh()
                self.status_message.emit(f"✓ Proxy assigned to '{name}'")
        elif result == 2:  # Remove
            if "proxy" in fp:
                del fp["proxy"]
                save_fingerprint(fp, PROFILES_DIR)
            self.refresh()
            self.status_message.emit(f"✓ Proxy removed from '{name}'")

    def _view_fp(self):
        name = self._selected_name()
        if not name:
            QMessageBox.information(self, "Select Profile", "Please select a profile first.")
            return
        FingerprintDialog(name, self).exec()

    def _regen_fp(self):
        name = self._selected_name()
        if not name:
            QMessageBox.information(self, "Select Profile", "Please select a profile first.")
            return
        import random as _r
        fp      = load_fingerprint(name, PROFILES_DIR)
        old_city = fp.get("vpn_city", "No VPN (Local)")
        old_tz   = fp.get("timezone")
        seed_name = f"{name}_{_r.randint(100,999)}"
        new_fp    = generate_fingerprint(seed_name, old_city, old_tz)
        new_fp["profile_name"] = name
        save_fingerprint(new_fp, PROFILES_DIR)
        self.refresh()
        self.status_message.emit(f"✓ Fingerprint regenerated for '{name}'")

    def _clear_selected_cache(self):
        name = self._selected_name()
        if not name:
            QMessageBox.information(self, "Select Profile", "Please select a profile first.")
            return
        browser_data = os.path.join(PROFILES_DIR, f"browser_data_{name}")
        if not os.path.exists(browser_data):
            self.status_message.emit(f"No browser data found for '{name}'")
            return
        cache_folders = ["Cache", "Code Cache", "GPUCache", "DawnCache", "ShaderCache"]
        freed = 0
        for folder in cache_folders:
            path = os.path.join(browser_data, folder)
            if os.path.exists(path):
                for dirpath, dirnames, filenames in os.walk(path):
                    for f in filenames:
                        try:
                            fp = os.path.join(dirpath, f)
                            freed += os.path.getsize(fp)
                            os.remove(fp)
                        except Exception:
                            pass
                try:
                    import shutil
                    shutil.rmtree(path)
                except Exception:
                    pass
        freed_mb = round(freed / (1024 * 1024), 2)
        self.status_message.emit(f"✓ Cache cleared for '{name}' — {freed_mb} MB freed")

    def _clear_all_cache(self):
        reply = QMessageBox.question(
            self, "Clear All Cache",
            "Clear cache for ALL profiles?\n\nLogin sessions will be kept safe.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply != QMessageBox.StandardButton.Yes:
            return
        profiles = list_profiles(PROFILES_DIR)
        cache_folders = ["Cache", "Code Cache", "GPUCache", "DawnCache", "ShaderCache"]
        total_freed = 0
        for name in profiles:
            browser_data = os.path.join(PROFILES_DIR, f"browser_data_{name}")
            if not os.path.exists(browser_data):
                continue
            for folder in cache_folders:
                path = os.path.join(browser_data, folder)
                if os.path.exists(path):
                    for dirpath, dirnames, filenames in os.walk(path):
                        for f in filenames:
                            try:
                                fp = os.path.join(dirpath, f)
                                total_freed += os.path.getsize(fp)
                                os.remove(fp)
                            except Exception:
                                pass
                    try:
                        import shutil
                        shutil.rmtree(path)
                    except Exception:
                        pass
        freed_mb = round(total_freed / (1024 * 1024), 2)
        self.status_message.emit(f"✓ All cache cleared — {freed_mb} MB freed across {len(profiles)} profiles")

    def _delete_profile(self):
        name = self._selected_name()
        if not name:
            QMessageBox.information(self, "Select Profile", "Please select a profile first.")
            return
        reply = QMessageBox.question(
            self, "Delete Profile",
            f"Delete '{name}' and all browser data?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            import shutil
            json_path = os.path.join(PROFILES_DIR, f"{name}.json")
            if os.path.exists(json_path):
                os.remove(json_path)
            browser_data = os.path.join(PROFILES_DIR, f"browser_data_{name}")
            if os.path.exists(browser_data):
                shutil.rmtree(browser_data)
            self.refresh()
            self.status_message.emit(f"✓ Deleted '{name}'")


# ─── Launch Tab ───────────────────────────────────────────────────────────────
class LaunchTab(QWidget):
    status_message = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self._workers = []
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        title = QLabel("Launch Profile")
        title.setObjectName("sectionTitle")
        layout.addWidget(title)

        sub = QLabel("Select a profile and launch its browser session")
        sub.setObjectName("subTitle")
        layout.addWidget(sub)

        # Profile selector
        row = QHBoxLayout()
        self.profile_combo = QLineEdit()
        self.profile_combo.setPlaceholderText("Type or select profile name...")
        self.profile_combo.setFixedHeight(36)
        row.addWidget(self.profile_combo)

        refresh_btn = QPushButton("↻")
        refresh_btn.setObjectName("btnGhost")
        refresh_btn.setFixedSize(36, 36)
        refresh_btn.clicked.connect(self._refresh_list)
        row.addWidget(refresh_btn)

        layout.addLayout(row)

        # Profile quick-select list
        self.profile_list = QTableWidget()
        self.profile_list.setColumnCount(3)
        self.profile_list.setHorizontalHeaderLabels(["Profile", "VPN City", "Timezone"])
        self.profile_list.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.profile_list.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.profile_list.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.profile_list.verticalHeader().setVisible(False)
        self.profile_list.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.profile_list.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.profile_list.setShowGrid(False)
        self.profile_list.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.profile_list.clicked.connect(self._on_list_click)
        layout.addWidget(self.profile_list)

        launch_btn = QPushButton("▶  Launch Selected Profile")
        launch_btn.setObjectName("btnGreen")
        launch_btn.setFixedHeight(40)
        launch_btn.clicked.connect(self._launch)
        layout.addWidget(launch_btn)

        # Log output
        log_label = QLabel("Launch Log")
        log_label.setStyleSheet("color: #4b5563; font-size: 11px; font-weight: 700; text-transform: uppercase;")
        layout.addWidget(log_label)

        self.log = QTextEdit()
        self.log.setReadOnly(True)
        self.log.setMaximumHeight(160)
        layout.addWidget(self.log)

        self._refresh_list()

    def _refresh_list(self):
        profiles = list_profiles(PROFILES_DIR)
        self.profile_list.setRowCount(0)
        for i, name in enumerate(profiles):
            fp = load_fingerprint(name, PROFILES_DIR)
            self.profile_list.insertRow(i)
            self.profile_list.setItem(i, 0, QTableWidgetItem(name))
            city = fp.get("vpn_city", "No VPN")
            flag = fp.get("vpn_flag", "🖥️")
            self.profile_list.setItem(i, 1, QTableWidgetItem(f"{flag}  {city}"))
            self.profile_list.setItem(i, 2, QTableWidgetItem(fp.get("timezone", "—")))
            self.profile_list.setRowHeight(i, 36)

    def _on_list_click(self, index):
        name = self.profile_list.item(index.row(), 0).text()
        self.profile_combo.setText(name)

    def _launch(self):
        name = self.profile_combo.text().strip()
        if not name:
            QMessageBox.information(self, "Select Profile", "Enter or select a profile name.")
            return
        profiles = list_profiles(PROFILES_DIR)
        if name not in profiles:
            QMessageBox.warning(self, "Not Found", f"Profile '{name}' not found.")
            return

        fp   = load_fingerprint(name, PROFILES_DIR)
        city = fp.get("vpn_city", "No VPN (Local)")
        if city != "No VPN (Local)" and not fp.get("proxy", {}).get("host"):
            reply = QMessageBox.question(
                self, "VPN Required",
                f"Connect VPN to:\n\n  {fp.get('vpn_flag','')}  {city}\n\nReady?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply != QMessageBox.StandardButton.Yes:
                return

        self.log.append(f"[{name}] Starting browser...")
        worker = LaunchWorker(name)
        worker.log.connect(lambda msg: self.log.append(msg))
        worker.done.connect(lambda: self.log.append(f"[{name}] Browser closed."))
        self._workers.append(worker)
        worker.start()
        

# ─── Camoufox Setup Dialog ────────────────────────────────────────────────────
class CamoufoxDownloadWorker(QThread):
    progress_text    = pyqtSignal(str)
    progress_percent = pyqtSignal(int)   # 0–100
    finished         = pyqtSignal(bool, str)  # success, error_message

    def run(self):
        try:
            import requests, tempfile, shlex, os, zipfile
            from camoufox.pkgman import CamoufoxFetcher, INSTALL_DIR, OS_NAME

            self.progress_text.emit("Fetching latest Camoufox release info...")
            fetcher = CamoufoxFetcher()
            url = fetcher.url

            # Clean up old install
            fetcher.cleanup()
            INSTALL_DIR.mkdir(parents=True, exist_ok=True)

            self.progress_text.emit("Downloading Camoufox browser engine (~530 MB)...")

            tmp_path = os.path.join(tempfile.gettempdir(), "camoufox_download.zip")
            downloaded = 0

            with requests.get(url, stream=True, timeout=60) as resp:
                resp.raise_for_status()
                total = int(resp.headers.get("Content-Length", 0))

                with open(tmp_path, "wb") as tmp:
                    for chunk in resp.iter_content(chunk_size=1024 * 256):
                        if chunk:
                            tmp.write(chunk)
                            downloaded += len(chunk)
                            if total > 0:
                                pct = min(int(downloaded * 100 / total), 98)
                                self.progress_percent.emit(pct)
                                mb_done = downloaded / 1_048_576
                                mb_total = total / 1_048_576
                                self.progress_text.emit(
                                    f"Downloading... {mb_done:.0f} MB / {mb_total:.0f} MB ({pct}%)"
                                )

            self.progress_text.emit("Extracting Camoufox...")
            self.progress_percent.emit(99)

            # Extract directly from disk file — never load 530MB into RAM
            with zipfile.ZipFile(tmp_path, "r") as zf:
                zf.extractall(str(INSTALL_DIR))

            os.unlink(tmp_path)

            fetcher.set_version()

            if OS_NAME != "win":
                os.system(f"chmod -R 755 {shlex.quote(str(INSTALL_DIR))}")  # nosec

            self.progress_percent.emit(100)
            self.finished.emit(True, "")
        except Exception as e:
            import traceback
            self.finished.emit(False, f"{e}\n{traceback.format_exc()}")
class CamoufoxSetupDialog(QDialog):
    setup_complete = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Ninja Shield — First Time Setup")
        self.setFixedSize(480, 260)
        self.setStyleSheet(STYLE)
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.WindowTitleHint)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(16)

        title = QLabel("Browser Engine Required")
        title.setStyleSheet("font-size: 16px; font-weight: 800; color: #a78bfa;")
        layout.addWidget(title)

        desc = QLabel(
            "Ninja Shield uses Camoufox — a privacy-hardened Firefox engine.\n"
            "It needs to be downloaded once (~530 MB).\n\n"
            "This only happens on first launch. Click Download to continue."
        )
        desc.setWordWrap(True)
        desc.setStyleSheet("color: #9ca3af; font-size: 13px; line-height: 1.5;")
        layout.addWidget(desc)

        self.status_label = QLabel("")
        self.status_label.setStyleSheet("color: #a78bfa; font-size: 12px;")
        self.status_label.setWordWrap(True)
        layout.addWidget(self.status_label)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setFixedHeight(18)
        self.progress_bar.setStyleSheet(
            "QProgressBar { border: 1px solid #374151; border-radius: 4px; "
            "background: #1f2937; color: #e5e7eb; font-size: 11px; text-align: center; } "
            "QProgressBar::chunk { background: #7c3aed; border-radius: 3px; }"
        )
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        layout.addStretch()

        btn_row = QHBoxLayout()
        self.btn_download = QPushButton("Download & Continue")
        self.btn_download.setObjectName("btnPrimary")
        self.btn_download.setFixedHeight(38)
        self.btn_download.clicked.connect(self._start_download)
        btn_row.addWidget(self.btn_download)

        self.btn_exit = QPushButton("Exit")
        self.btn_exit.setObjectName("btnGhost")
        self.btn_exit.setFixedHeight(38)
        self.btn_exit.clicked.connect(self.reject)
        btn_row.addWidget(self.btn_exit)

        layout.addLayout(btn_row)

    def _start_download(self):
        self.btn_download.setEnabled(False)
        self.btn_download.setText("Downloading...")
        self.btn_exit.setText("Cancel")
        self.btn_exit.setEnabled(True)
        self.status_label.setText("Please wait, downloading...")

        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(True)

        self._ui_timer = QTimer(self)
        self._ui_timer.setInterval(50)
        self._ui_timer.timeout.connect(lambda: QApplication.processEvents())
        self._ui_timer.start()

        self.worker = CamoufoxDownloadWorker()
        self.worker.progress_text.connect(self.status_label.setText)
        self.worker.progress_percent.connect(self.progress_bar.setValue)
        self.worker.finished.connect(self._on_finished)
        self.btn_exit.clicked.disconnect()
        self.btn_exit.clicked.connect(self._cancel_download)
        self.worker.start()

    def _cancel_download(self):
        if hasattr(self, 'worker') and self.worker.isRunning():
            self.worker.terminate()
            self.worker.wait()
        self.reject()

    def _on_finished(self, success, error_msg):
        if hasattr(self, '_ui_timer'):
            self._ui_timer.stop()
        if success:
            self.status_label.setText("✓ Download complete! Launching Ninja Shield...")
            self.setup_complete.emit()
            self.accept()
        else:
            self.status_label.setStyleSheet("color: #f87171; font-size: 12px;")
            self.status_label.setText(f"Download failed:\n{error_msg}\n\nCheck your internet connection and try again.")
            self.btn_download.setEnabled(True)
            self.btn_download.setText("Retry Download")
            self.btn_exit.setEnabled(True)


def is_camoufox_installed() -> bool:
    """Check if Camoufox browser binary is already downloaded."""
    try:
        from camoufox.pkgman import camoufox_path, INSTALL_DIR
        import os
        if os.path.exists(INSTALL_DIR) and os.listdir(INSTALL_DIR):
            return True
        camoufox_path(download_if_missing=False)
        return True
    except Exception:
        return False
# ─── Main Window ──────────────────────────────────────────────────────────────
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Ninja Shield v4")
        self.setWindowIcon(QIcon(resource_path("icon.ico")))
        self.setMinimumSize(900, 620)
        self.setStyleSheet(STYLE)
        Path(PROFILES_DIR).mkdir(exist_ok=True)
        self._build_ui()

    def closeEvent(self, event):
        import tempfile
        import os

        lock_file = os.path.join(tempfile.gettempdir(), "ninjashield.lock")

        try:
            if os.path.exists(lock_file):
                os.remove(lock_file)
        except:
            pass

        event.accept()
        QApplication.instance().quit()
        os._exit(0)
    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Header
        header = QFrame()
        header.setObjectName("topBar")
        header.setFixedHeight(52)
        h_layout = QHBoxLayout(header)
        h_layout.setContentsMargins(20, 0, 20, 0)

        logo_label = QLabel("Ninja Shield")
        logo_label.setStyleSheet("font-size: 15px; font-weight: 800; color: #a78bfa; letter-spacing: -0.3px; background: transparent;")
        h_layout.addWidget(logo_label)
        h_layout.addStretch()

        # License days remaining badge
        self.license_badge = QLabel("")
        self.license_badge.setStyleSheet(
            "background: #1a1b2a; border: 1px solid #2a2b3d; border-radius: 5px;"
            "color: #4ade80; font-size: 11px; font-family: 'Consolas', monospace;"
            "padding: 3px 10px;"
        )
        self._refresh_license_badge()
        h_layout.addWidget(self.license_badge)

        h_layout.addSpacing(10)

        version_label = QLabel("v4.0")
        version_label.setStyleSheet("color: #2a2b3d; font-size: 11px; font-family: 'Consolas', monospace;")
        h_layout.addWidget(version_label)

        main_layout.addWidget(header)

        # Tabs
        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)

        self.profiles_tab = ProfilesTab()
        self.profiles_tab.status_message.connect(self._set_status)

        self.launch_tab = LaunchTab()
        self.launch_tab.status_message.connect(self._set_status)

        self.tabs.addTab(self.profiles_tab, "  Profiles  ")
        self.tabs.addTab(self.launch_tab,   "  Launch    ")

        main_layout.addWidget(self.tabs)

        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self._set_status("Ready")

    def _refresh_license_badge(self):
        """Update the license days-remaining badge in the header."""
        try:
            result = check_license()
            if result["status"] == "active":
                days = result["days_left"]
                if days <= 5:
                    color = "#f87171"    # red — nearly expired
                elif days <= 15:
                    color = "#f59e0b"    # amber — warning
                else:
                    color = "#4ade80"    # green — healthy
                self.license_badge.setStyleSheet(
                    f"background: #1a1b2a; border: 1px solid #2a2b3d; border-radius: 5px;"
                    f"color: {color}; font-size: 11px; font-family: 'Consolas', monospace;"
                    f"padding: 3px 10px;"
                )
                self.license_badge.setText(f"🔑  {days} days left")
            else:
                self.license_badge.setStyleSheet(
                    "background: #1f0a0a; border: 1px solid #3f1e1e; border-radius: 5px;"
                    "color: #f87171; font-size: 11px; font-family: 'Consolas', monospace;"
                    "padding: 3px 10px;"
                )
                self.license_badge.setText("🔑  License expired")
        except Exception:
            self.license_badge.setText("")

    def _set_status(self, msg):
        self.status_bar.showMessage(f"  {msg}", 8000)


# ─── Entry Point ──────────────────────────────────────────────────────────────
def main():
    import tempfile
    import atexit

    # Single instance lock — prevents multiple app instances
    lock_file = os.path.join(tempfile.gettempdir(), "ninjashield.lock")
    try:
        if os.path.exists(lock_file):
            try:
                with open(lock_file, 'r') as f:
                    old_pid = int(f.read().strip())


                import psutil
                if psutil.pid_exists(old_pid):
                    app = QApplication(sys.argv)
                    QMessageBox.warning(
                        None,
                        "Ninja Shield Already Running",
                        "Ninja Shield is already running.\nCheck your taskbar."
                    )
                    sys.exit(0)
                else:
                    # 🔥 OLD PID DEAD → REMOVE STALE LOCK
                    os.remove(lock_file)
            except:
                # 🔥 CORRUPT LOCK FILE → REMOVE IT
                try:
                    os.remove(lock_file)
                except:
                    pass
    except Exception:
        pass

    # Write current PID to lock file
    with open(lock_file, 'w') as f:
        f.write(str(os.getpid()))
    def remove_lock():
        try:
            if os.path.exists(lock_file):
                os.remove(lock_file)
        except:
            pass

    atexit.register(remove_lock)

    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(resource_path("icon.ico")))
    app.setApplicationName("Ninja Shield")

    # Check Camoufox binary before anything else
    if not is_camoufox_installed():
        setup = CamoufoxSetupDialog()
        if setup.exec() != QDialog.DialogCode.Accepted:
            sys.exit(0)

    result = check_license()

    if result["status"] == "active":
        window = MainWindow()
        window.show()
        app._main_window = window
    else:
        activation = ActivationWindow()

        def on_activated():
            activation.hide()
            window = MainWindow()
            window.show()
            app._main_window = window

        activation.activated.connect(on_activated)
        activation.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
