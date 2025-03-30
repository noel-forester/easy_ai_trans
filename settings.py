from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QRadioButton, QPushButton, QCheckBox
)
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QIcon
import os
import sys
from config import load_config, save_config #Config I/O

def resource_path(relative_path):
    base_path = getattr(sys, "_MEIPASS", os.path.dirname(__file__))
    return os.path.join(base_path, relative_path)

class SettingsDialog(QDialog):
    settings_saved = pyqtSignal()
    def __init__(self):
        super().__init__()
        self.setWindowTitle("設定")
        self.setWindowIcon(QIcon(resource_path("assets/icon.png")))
        self.setFixedSize(400, 250)
        self.config = load_config()
        config = load_config()
        layout = QVBoxLayout()

        # API選択
        layout.addWidget(QLabel("使用API"))
        api_layout = QHBoxLayout()
        self.chatgpt_radio = QRadioButton("ChatGPT")
        #self.gemini_radio = QRadioButton("Gemini")
        self.chatgpt_radio.setChecked(True)
        api_layout.addWidget(self.chatgpt_radio)
        #api_layout.addWidget(self.gemini_radio)
        layout.addLayout(api_layout)

        # APIキー
        layout.addWidget(QLabel("APIキー"))
        self.api_key_input = QLineEdit()
        layout.addWidget(self.api_key_input)

        # ホットキー
        layout.addWidget(QLabel("ショートカットキー"))
        self.hotkey_input = QLineEdit()
        layout.addWidget(self.hotkey_input)

        # 処理時間ログ表示
        self.show_timing_checkbox = QCheckBox("処理時間ログを表示する")
        self.show_timing_checkbox.setChecked(config["LOG"].get("show_timing_logs", "True") == "True")
        layout.addWidget(self.show_timing_checkbox)

        # 保存ボタン
        save_btn = QPushButton("保存")
        save_btn.clicked.connect(self.save_settings)
        layout.addWidget(save_btn)

        self.setLayout(layout)
        self.load_from_config()
        
        
    def load_from_config(self):
        provider = self.config.get("API", "provider", fallback="ChatGPT")
        if provider == "ChatGPT":
            self.chatgpt_radio.setChecked(True)
        else:
            self.gemini_radio.setChecked(True)

        self.api_key_input.setText(
            self.config.get("API", "chatgpt_key", fallback="")
        )

        self.hotkey_input.setText(
            self.config.get("Shortcut", "hotkey", fallback="ctrl+alt+t")
        )

    def save_settings(self):
        # config = load_config() ← これは不要！
        if self.chatgpt_radio.isChecked():
            self.config["API"]["provider"] = "ChatGPT"
        else:
            self.config["API"]["provider"] = "Gemini"

        self.config["API"]["chatgpt_key"] = self.api_key_input.text()
        self.config["Shortcut"]["hotkey"] = self.hotkey_input.text()

        if "LOG" not in self.config:
            self.config["LOG"] = {}

        self.config["LOG"]["show_timing_logs"] = str(self.show_timing_checkbox.isChecked())

        save_config(self.config)
        self.settings_saved.emit()
        self.hide()


            
    def closeEvent(self, event):
        event.ignore()
        self.hide()