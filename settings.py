from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QRadioButton, QPushButton
)
from config import load_config, save_config #Config I/O

class SettingsDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("設定")
        self.setFixedSize(400, 250)
        self.config = load_config()

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
        print("💾 設定保存中")
        if self.chatgpt_radio.isChecked():
            self.config["API"]["provider"] = "ChatGPT"
        else:
            self.config["API"]["provider"] = "Gemini"

        self.config["API"]["chatgpt_key"] = self.api_key_input.text()
        self.config["Shortcut"]["hotkey"] = self.hotkey_input.text()
        save_config(self.config)
        print("✅ 設定保存完了")
        self.hide()  # ← self.accept() OUT!
            
    def closeEvent(self, event):
        event.ignore()
        self.hide()