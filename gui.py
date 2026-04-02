import sys
import os
import threading
import json
from pathlib import Path
import time


def _app_root() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent


APP_ROOT = _app_root()

from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QComboBox, QTextEdit,
    QCheckBox, QSpinBox, QGroupBox, QFormLayout, QGridLayout
)
from PyQt6.QtCore import Qt

import sounddevice as sd

# ===== IMPORT YOUR MODULES =====
import chaos_controls.chaos as chaos
import no_cursing.noswears as noswear
from ScreenTurn import screen_flip



import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--chaos", action="store_true")
parser.add_argument("--shuffle", action="store_true")
parser.add_argument("--no_turn", action="store_true")
parser.add_argument("--invert", action="store_true")
parser.add_argument("--flip", action="store_true")
parser.add_argument("--noswear", action="store_true")
parser.add_argument("--duration", type=int, default=None)  # optional custom duration
args, unknown = parser.parse_known_args()



# ===== STATE =====
running_features = {
    "chaos": False,
    "noswear": False,
    "shuffle": False,
    "no_turn": False,
    "invert": False,
    "flip_screen": False,
}

CONFIG_PATH = APP_ROOT / "config.json"

DEFAULT_CONFIG = {
    "enabled": {
        "chaos": True,
        "shuffle": True,
        "no_turn": True,
        "invert": True,
        "flip_screen": True,
        "noswear": True,
    },
    "durations": {
        "chaos": 120,
        "shuffle": 15,
        "no_turn": 10,
        "invert": 10,
        "flip_screen": 120,
    },
    "mic": {
        "device_index": None,
    },
}


class BreadGUI(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("🍞 BSRCP - BreadsStreamRedeemControlPanel")
        self.setFixedSize(640, 520)
        self.setStyleSheet(self.dark_theme())

        self.config = self.load_config()

        self.layout = QVBoxLayout()

        title = QLabel("🍞BSRCP - BreadsStreamRedeemControlPanel🍞")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 18px; font-weight: bold;")

        self.layout.addWidget(title)

        # ===== SETTINGS =====
        settings_group = QGroupBox("Settings")
        settings_group.setStyleSheet("QGroupBox { font-weight: bold; }")
        settings_layout = QGridLayout()

        self.enable_chaos = QCheckBox("Enable")
        self.enable_shuffle = QCheckBox("Enable")
        self.enable_no_turn = QCheckBox("Enable")
        self.enable_invert = QCheckBox("Enable")
        self.enable_flip = QCheckBox("Enable")
        self.enable_noswear = QCheckBox("Enable")

        self.chaos_time = QSpinBox()
        self.shuffle_time = QSpinBox()
        self.no_turn_time = QSpinBox()
        self.invert_time = QSpinBox()
        self.flip_time = QSpinBox()

        for spin in (self.chaos_time, self.shuffle_time, self.no_turn_time, self.invert_time, self.flip_time):
            spin.setRange(1, 3600)
            spin.setSuffix(" s")

        settings_layout.addWidget(QLabel("Chaos (time)"), 0, 0)
        settings_layout.addWidget(self.chaos_time, 0, 1)
        settings_layout.addWidget(self.enable_chaos, 0, 2)

        settings_layout.addWidget(QLabel("Shuffle WASD"), 1, 0)
        settings_layout.addWidget(self.shuffle_time, 1, 1)
        settings_layout.addWidget(self.enable_shuffle, 1, 2)

        settings_layout.addWidget(QLabel("No Turning"), 2, 0)
        settings_layout.addWidget(self.no_turn_time, 2, 1)
        settings_layout.addWidget(self.enable_no_turn, 2, 2)

        settings_layout.addWidget(QLabel("Invert Mouse"), 3, 0)
        settings_layout.addWidget(self.invert_time, 3, 1)
        settings_layout.addWidget(self.enable_invert, 3, 2)

        settings_layout.addWidget(QLabel("Flip Screen"), 4, 0)
        settings_layout.addWidget(self.flip_time, 4, 1)
        settings_layout.addWidget(self.enable_flip, 4, 2)

        settings_layout.addWidget(QLabel("No Swear"), 5, 0)
        settings_layout.addWidget(QLabel("(mic feature)"), 5, 1)
        settings_layout.addWidget(self.enable_noswear, 5, 2)

        settings_group.setLayout(settings_layout)
        self.layout.addWidget(settings_group)

        # ===== CHAOS =====
        chaos_layout = QHBoxLayout()
        self.chaos_btn = QPushButton("Start Chaos")
        self.chaos_btn.clicked.connect(self.toggle_chaos)

        chaos_layout.addWidget(QLabel("Chaos"))
        chaos_layout.addWidget(self.chaos_btn)

        self.layout.addLayout(chaos_layout)

        # ===== INDIVIDUAL CHAOS ACTIONS =====
        actions_group = QGroupBox("Chaos Actions")
        actions_group.setStyleSheet("QGroupBox { font-weight: bold; }")
        actions_form = QFormLayout()

        self.shuffle_btn = QPushButton("Run Shuffle")
        self.shuffle_btn.clicked.connect(self.run_shuffle)
        actions_form.addRow(QLabel("Shuffle WASD"), self.shuffle_btn)

        self.no_turn_btn = QPushButton("Run No Turning")
        self.no_turn_btn.clicked.connect(self.run_no_turn)
        actions_form.addRow(QLabel("No Turning"), self.no_turn_btn)

        self.invert_btn = QPushButton("Run Invert")
        self.invert_btn.clicked.connect(self.run_invert)
        actions_form.addRow(QLabel("Invert Mouse"), self.invert_btn)

        self.flip_btn = QPushButton("Run Flip Screen")
        self.flip_btn.clicked.connect(self.run_flip_screen)
        actions_form.addRow(QLabel("Flip Screen"), self.flip_btn)

        actions_group.setLayout(actions_form)
        self.layout.addWidget(actions_group)

        # ===== NOSWEAR =====
        noswear_layout = QHBoxLayout()

        self.mic_select = QComboBox()
        self.mic_devices = []

        devices = sd.query_devices()
        print("\n==== AVAILABLE MICS ====")
        for i, device in enumerate(devices):
            if device['max_input_channels'] > 0:
                print(f"{i}: {device['name']}")
                self.mic_select.addItem(f"{i}: {device['name']}")
                self.mic_devices.append(i)
        print("========================\n")

        self.noswear_btn = QPushButton("Start No Swear")
        self.noswear_btn.clicked.connect(self.toggle_noswear)

        noswear_layout.addWidget(QLabel("No Swear"))
        noswear_layout.addWidget(self.mic_select)
        noswear_layout.addWidget(self.noswear_btn)

        self.layout.addLayout(noswear_layout)

        # ===== LIVE TRANSCRIPT =====
        self.transcript_box = QTextEdit()
        self.transcript_box.setReadOnly(True)
        self.transcript_box.setPlaceholderText("Live transcript will appear here...")

        self.layout.addWidget(QLabel("Live Transcript"))
        self.layout.addWidget(self.transcript_box)

        self.setLayout(self.layout)

        # Hook transcript callback
        noswear.set_transcript_callback(self.update_transcript)

        self.apply_config_to_ui()
        self.wire_config_handlers()
        self.apply_enabled_states()

    # ===== HELPERS =====
    def get_selected_mic(self):
        index = self.mic_select.currentIndex()
        return self.mic_devices[index]

    def update_transcript(self, text):
        self.transcript_box.append(text)

    def load_config(self):
        if CONFIG_PATH.exists():
            try:
                data = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
                # shallow merge defaults
                merged = json.loads(json.dumps(DEFAULT_CONFIG))
                merged["enabled"].update(data.get("enabled", {}))
                merged["durations"].update(data.get("durations", {}))
                merged["mic"] = {**DEFAULT_CONFIG["mic"], **data.get("mic", {})}
                return merged
            except Exception:
                return json.loads(json.dumps(DEFAULT_CONFIG))
        return json.loads(json.dumps(DEFAULT_CONFIG))

    def save_config(self):
        CONFIG_PATH.write_text(json.dumps(self.config, indent=2), encoding="utf-8")

    def apply_config_to_ui(self):
        self.enable_chaos.setChecked(bool(self.config["enabled"].get("chaos", True)))
        self.enable_shuffle.setChecked(bool(self.config["enabled"].get("shuffle", True)))
        self.enable_no_turn.setChecked(bool(self.config["enabled"].get("no_turn", True)))
        self.enable_invert.setChecked(bool(self.config["enabled"].get("invert", True)))
        self.enable_flip.setChecked(bool(self.config["enabled"].get("flip_screen", True)))
        self.enable_noswear.setChecked(bool(self.config["enabled"].get("noswear", True)))

        self.chaos_time.setValue(int(self.config["durations"].get("chaos", 120)))
        self.shuffle_time.setValue(int(self.config["durations"].get("shuffle", 15)))
        self.no_turn_time.setValue(int(self.config["durations"].get("no_turn", 10)))
        self.invert_time.setValue(int(self.config["durations"].get("invert", 10)))
        self.flip_time.setValue(int(self.config["durations"].get("flip_screen", 120)))

        saved_mic = self.config.get("mic", {}).get("device_index")
        if saved_mic is not None and saved_mic in self.mic_devices:
            self.mic_select.setCurrentIndex(self.mic_devices.index(saved_mic))

    def wire_config_handlers(self):
        def on_enabled_change():
            self.config["enabled"]["chaos"] = self.enable_chaos.isChecked()
            self.config["enabled"]["shuffle"] = self.enable_shuffle.isChecked()
            self.config["enabled"]["no_turn"] = self.enable_no_turn.isChecked()
            self.config["enabled"]["invert"] = self.enable_invert.isChecked()
            self.config["enabled"]["flip_screen"] = self.enable_flip.isChecked()
            self.config["enabled"]["noswear"] = self.enable_noswear.isChecked()
            self.save_config()
            self.apply_enabled_states()

        for cb in (self.enable_chaos, self.enable_shuffle, self.enable_no_turn, self.enable_invert, self.enable_flip, self.enable_noswear):
            cb.stateChanged.connect(on_enabled_change)

        def on_duration_change():
            self.config["durations"]["chaos"] = int(self.chaos_time.value())
            self.config["durations"]["shuffle"] = int(self.shuffle_time.value())
            self.config["durations"]["no_turn"] = int(self.no_turn_time.value())
            self.config["durations"]["invert"] = int(self.invert_time.value())
            self.config["durations"]["flip_screen"] = int(self.flip_time.value())
            self.save_config()

        for sp in (self.chaos_time, self.shuffle_time, self.no_turn_time, self.invert_time, self.flip_time):
            sp.valueChanged.connect(on_duration_change)

        def on_mic_change():
            self.config.setdefault("mic", dict(DEFAULT_CONFIG["mic"]))
            idx = self.mic_select.currentIndex()
            if 0 <= idx < len(self.mic_devices):
                self.config["mic"]["device_index"] = self.mic_devices[idx]
            self.save_config()

        self.mic_select.currentIndexChanged.connect(lambda _i: on_mic_change())

    def apply_enabled_states(self):
        self.chaos_btn.setEnabled(self.enable_chaos.isChecked())
        self.shuffle_btn.setEnabled(self.enable_shuffle.isChecked())
        self.no_turn_btn.setEnabled(self.enable_no_turn.isChecked())
        self.invert_btn.setEnabled(self.enable_invert.isChecked())
        self.flip_btn.setEnabled(self.enable_flip.isChecked())
        self.noswear_btn.setEnabled(self.enable_noswear.isChecked())
        self.mic_select.setEnabled(self.enable_noswear.isChecked())

    # ===== TOGGLES =====
    def toggle_chaos(self):
        if not self.enable_chaos.isChecked():
            return
        if not running_features["chaos"]:
            running_features["chaos"] = True
            self.chaos_btn.setText("Stop Chaos")
            chaos.start_chaos(duration=int(self.chaos_time.value()))
        else:
            chaos.stop_chaos()
            running_features["chaos"] = False
            self.chaos_btn.setText("Start Chaos")

    def toggle_noswear(self):
        if not self.enable_noswear.isChecked():
            return
        if not running_features["noswear"]:
            running_features["noswear"] = True
            self.noswear_btn.setText("Stop No Swear")
            mic_index = self.get_selected_mic()
            noswear.start(mic_index)
        else:
            noswear.stop()
            running_features["noswear"] = False
            self.noswear_btn.setText("Start No Swear")

    def run_shuffle(self):
        if not self.enable_shuffle.isChecked():
            return
        chaos.start_shuffle(duration=int(self.shuffle_time.value()))

    def run_no_turn(self):
        if not self.enable_no_turn.isChecked():
            return
        chaos.start_no_turn(duration=int(self.no_turn_time.value()))

    def run_invert(self):
        if not self.enable_invert.isChecked():
            return
        chaos.start_invert(duration=int(self.invert_time.value()))

    def run_flip_screen(self):
        if not self.enable_flip.isChecked():
            return

        duration = int(self.flip_time.value())

        def worker():
            try:
                screen_flip.flip_screen()
                screen_flip.set_vtube_rotation(180)
                time.sleep(duration)
            finally:
                screen_flip.flip_screen()
                screen_flip.set_vtube_rotation(0)

        threading.Thread(target=worker, daemon=True).start()

    # ===== STYLE =====
    def dark_theme(self):
        return """
        QWidget {
            background-color: #1e1e2e;
            color: #ffffff;
        }
        QPushButton {
            background-color: #3a3a5e;
            border-radius: 8px;
            padding: 6px;
        }
        QPushButton:hover {
            background-color: #50507a;
        }
        QPushButton:disabled {
            background-color: #2a2a40;
            color: #777;
        }
        QComboBox {
            background-color: #2a2a40;
        }
        QTextEdit {
            background-color: #111122;
            border: 1px solid #444;
        }
        """



if __name__ == "__main__":
    if getattr(sys, "frozen", False):
        os.chdir(APP_ROOT)

    cli_redeem = any(
        (
            args.chaos,
            args.shuffle,
            args.no_turn,
            args.invert,
            args.flip,
            args.noswear,
        )
    )

    # Do not pass Streamer.bot flags (e.g. --chaos) into Qt; it may treat them as unknown options.
    app = QApplication([sys.argv[0]])
    window = BreadGUI()

    # ===== HEADLESS MODE FOR STREAMER.BOT =====
    if cli_redeem:
        window.hide()
    else:
        window.show()

    if cli_redeem:
        def trigger_from_args():
            def sec(spin_widget):
                return int(spin_widget.value()) if args.duration is None else int(args.duration)

            if args.chaos:
                chaos.start_chaos(duration=sec(window.chaos_time))
            if args.shuffle:
                chaos.start_shuffle(duration=sec(window.shuffle_time))
            if args.no_turn:
                chaos.start_no_turn(duration=sec(window.no_turn_time))
            if args.invert:
                chaos.start_invert(duration=sec(window.invert_time))
            if args.flip:
                window.run_flip_screen()
            if args.noswear:
                mic_index = window.get_selected_mic()
                noswear.start(mic_index)

        threading.Thread(target=trigger_from_args, daemon=True).start()

    sys.exit(app.exec())