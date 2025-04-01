from PyQt5.QtWidgets import (
    QDialog, QLabel, QLineEdit, QPushButton, QVBoxLayout,
    QCheckBox, QComboBox, QTextEdit
)
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QIcon
from config import load_config, save_config
import sys, os

def resource_path(relative_path):
    base_path = getattr(sys, "_MEIPASS", os.path.dirname(__file__))
    return os.path.join(base_path, relative_path)

class SettingsDialog(QDialog):
    settings_saved = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle("設定")
        self.setWindowIcon(QIcon(resource_path("assets/icon.png")))
        self.config = load_config()
        layout = QVBoxLayout()

        # --- API プロバイダー選択 ---
        # layout.addWidget(QLabel("使用するAPI"))
        # self.chatgpt_radio = QRadioButton("ChatGPT")
        # self.gemini_radio = QRadioButton("Gemini")
        # self.both_radio = QRadioButton("Both")
        # api_layout = QHBoxLayout()
        # api_layout.addWidget(self.chatgpt_radio)
        # api_layout.addWidget(self.gemini_radio)
        # api_layout.addWidget(self.both_radio)
        # layout.addLayout(api_layout)

        # --- APIキー ---
        layout.addWidget(QLabel("ChatGPT APIキー"))
        self.chatgpt_key_input = QLineEdit()
        layout.addWidget(self.chatgpt_key_input)

        layout.addWidget(QLabel("Gemini APIキー"))
        self.gemini_key_input = QLineEdit()
        layout.addWidget(self.gemini_key_input)

        # --- ChatGPT モデル選択 ---
        self.chatgpt_model_combo = QComboBox()
        self.chatgpt_model_button = QPushButton("ChatGPTモデル一覧取得")
        layout.addWidget(QLabel("ChatGPT モデル"))
        layout.addWidget(self.chatgpt_model_combo)
        layout.addWidget(self.chatgpt_model_button)
        self.chatgpt_model_button.clicked.connect(self.fetch_chatgpt_models)

        # --- Gemini モデル選択 ---
        self.gemini_model_combo = QComboBox()
        self.gemini_model_button = QPushButton("Geminiモデル一覧取得")
        layout.addWidget(QLabel("Gemini モデル"))
        layout.addWidget(self.gemini_model_combo)
        layout.addWidget(self.gemini_model_button)
        self.gemini_model_button.clicked.connect(self.fetch_gemini_models)

        # --- プロンプト編集 ---
        layout.addWidget(QLabel("翻訳プロンプト"))
        self.prompt_edit = QTextEdit()
        layout.addWidget(self.prompt_edit)

        # --- オプション: 処理時間ログ表示 ---
        self.show_timing_checkbox = QCheckBox("処理時間ログを表示する")
        layout.addWidget(self.show_timing_checkbox)

        # --- 保存ボタン ---
        save_button = QPushButton("保存")
        save_button.clicked.connect(self.save_settings)
        layout.addWidget(save_button)

        self.setLayout(layout)
        self.load_from_config()

    def load_from_config(self):
        cfg = self.config
        api = cfg["API"]

        # API選択
        # self.chatgpt_radio.setChecked(api.get("provider", "ChatGPT") == "ChatGPT")
        # self.gemini_radio.setChecked(api.get("provider", "") == "Gemini")
        # self.both_radio.setChecked(api.get("provider", "") == "Both")

        # APIキーなど
        self.chatgpt_key_input.setText(api.get("chatgpt_key", ""))
        self.gemini_key_input.setText(api.get("gemini_key", ""))
        self.prompt_edit.setPlainText(api.get("prompt", ""))

        # モデル一覧（保存されてたら読み込む）
        chatgpt_model_list = api.get("chatgpt_model_list", "")
        if chatgpt_model_list:
            self.chatgpt_model_combo.clear()
            self.chatgpt_model_combo.addItems(chatgpt_model_list.split(","))

        gemini_model_list = api.get("gemini_model_list", "")
        if gemini_model_list:
            self.gemini_model_combo.clear()
            self.gemini_model_combo.addItems(gemini_model_list.split(","))

        # 選択モデル（存在すればセット）
        self.chatgpt_model_combo.setCurrentText(api.get("chatgpt_model", "gpt-4o"))
        self.gemini_model_combo.setCurrentText(api.get("gemini_model", "models/gemini-1.5-pro"))

        # その他オプション
        self.show_timing_checkbox.setChecked(
            cfg["LOG"].get("show_timing_logs", "True") == "True"
        )


    def save_settings(self):
        api = self.config["API"]
        # if self.chatgpt_radio.isChecked():
        #     api["provider"] = "ChatGPT"
        # elif self.gemini_radio.isChecked():
        #     api["provider"] = "Gemini"
        # else:
        #     api["provider"] = "Both"

        api["chatgpt_key"] = self.chatgpt_key_input.text()
        api["gemini_key"] = self.gemini_key_input.text()
        api["chatgpt_model"] = self.chatgpt_model_combo.currentText()
        api["gemini_model"] = self.gemini_model_combo.currentText()
        api["prompt"] = self.prompt_edit.toPlainText()

        # 🔽 モデル一覧をiniに保存
        api["chatgpt_model_list"] = ",".join(
            [self.chatgpt_model_combo.itemText(i) for i in range(self.chatgpt_model_combo.count())]
        )
        api["gemini_model_list"] = ",".join(
            [self.gemini_model_combo.itemText(i) for i in range(self.gemini_model_combo.count())]
        )

        self.config["LOG"]["show_timing_logs"] = str(self.show_timing_checkbox.isChecked())

        save_config(self.config)
        self.settings_saved.emit()
        self.hide()

    def closeEvent(self, event):
        event.ignore()
        self.hide()

    def fetch_chatgpt_models(self):
        try:
            from openai import OpenAI
            key = self.chatgpt_key_input.text()
            client = OpenAI(api_key=key)
            models = client.models.list()
            ids = sorted([m.id for m in models.data if m.id.startswith("gpt")])
            self.chatgpt_model_combo.clear()
            self.chatgpt_model_combo.addItems(ids)
        except Exception as e:
            self.chatgpt_model_combo.clear()
            self.chatgpt_model_combo.addItem(f"取得失敗: {e}")

    def fetch_gemini_models(self):
        try:
            import google.generativeai as genai
            key = self.gemini_key_input.text()
            genai.configure(api_key=key)
            models = genai.list_models()
            ids = sorted([m.name for m in models if "gemini" in m.name.lower()])
            self.gemini_model_combo.clear()
            self.gemini_model_combo.addItems(ids)
        except Exception as e:
            self.gemini_model_combo.clear()
            self.gemini_model_combo.addItem(f"取得失敗: {e}")
