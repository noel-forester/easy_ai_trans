from PyQt5.QtWidgets import QApplication, QWidget, QTextEdit, QPushButton, QVBoxLayout, QHBoxLayout, QSizeGrip, QSystemTrayIcon, QMenu, QAction
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QIcon
import sys
from PIL import Image
from core import capture_screen
from settings import SettingsDialog #設定画面

class OutputOverlay(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setGeometry(100, 100, 600, 400)

        # 背景つきコンテナ
        self.container = QWidget(self)
        self.container.setStyleSheet("background-color: rgba(0, 0, 0, 180); border-radius: 8px;")
        self.layout = QVBoxLayout(self.container)
        self.layout.setContentsMargins(10, 10, 10, 10)

        # 上部バー
        top_bar = QHBoxLayout()
        
        # 全画面キャプチャボタン
        self.capture_all_btn = QPushButton("📸")
        self.capture_all_btn.setToolTip("全画面キャプチャ")
        self.capture_all_btn.setStyleSheet("background: transparent; border: none; color: white; font-size: 12pt;")
        self.capture_all_btn.setFixedSize(32, 32)
        self.capture_all_btn.clicked.connect(self.capture_fullscreen)
        top_bar.addWidget(self.capture_all_btn)

        # ウィンドウ下キャプチャボタン
        self.capture_below_btn = QPushButton("⬇")
        self.capture_below_btn.setToolTip("ウィンドウ下をキャプチャ")
        self.capture_below_btn.setStyleSheet("background: transparent; border: none; color: white; font-size: 12pt;")
        self.capture_below_btn.setFixedSize(32, 32)
        self.capture_below_btn.clicked.connect(self.capture_below)
        top_bar.addWidget(self.capture_below_btn)

        top_bar.addStretch()

        self.close_btn = QPushButton("✕")
        self.close_btn.setStyleSheet("background: transparent; color: white; font-size: 14pt; border: none;")
        self.close_btn.setFixedSize(32, 32)
        self.close_btn.clicked.connect(self.hide)
        top_bar.addWidget(self.close_btn)

        self.layout.addLayout(top_bar)

        # ログ
        self.log = QTextEdit()
        self.log.setReadOnly(True)
        self.log.setStyleSheet("""
            QTextEdit {
                color: white;
                font-family: Consolas;
                font-size: 10pt;
                background-color: transparent;
                border: none;
            }
        """)
        self.layout.addWidget(self.log)

        # リサイズつまみ
        grip = QSizeGrip(self.container)
        self.layout.addWidget(grip, 0, Qt.AlignRight | Qt.AlignBottom)

        self.container.resize(self.size())

        # 通知領域アイコン
        self.tray = QSystemTrayIcon(QIcon("assets/icon.png"), self)
        self.tray.setToolTip("EasyTrans")
        self.tray.activated.connect(self.on_tray_activated)

        menu = QMenu()
        show_action = QAction("表示", self)
        settings_action = QAction("設定", self)
        quit_action = QAction("終了", self)

        show_action.triggered.connect(self.show)
        settings_action.triggered.connect(self.open_settings)  # あとで実装
        quit_action.triggered.connect(QApplication.quit)

        menu.addAction(show_action)
        menu.addAction(settings_action)
        menu.addSeparator()
        menu.addAction(quit_action)

        self.tray.setContextMenu(menu)
        self.tray.show()

        # 移動用
        self.offset = None
        
    def on_tray_activated(self, reason):
        if reason == QSystemTrayIcon.Trigger:  # ← 左クリック
            self.show()

    def resizeEvent(self, event):
        self.container.resize(self.size())

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.offset = event.globalPos() - self.frameGeometry().topLeft()

    def mouseMoveEvent(self, event):
        if self.offset is not None and event.buttons() == Qt.LeftButton:
            self.move(event.globalPos() - self.offset)

    def mouseReleaseEvent(self, event):
        self.offset = None

    def fake_translate(self):
        self.log.append("▼ 翻訳結果:\nGran: ええと...特にどこでもないよ。")
        self.log.moveCursor(self.log.textCursor().End)

    def open_settings(self):
        dlg = SettingsDialog()
        dlg.exec_()
    
    def get_monitor_index_for_window(self):
        import mss

        center = self.frameGeometry().center()
        screen_x = center.x()
        screen_y = center.y()

        with mss.mss() as sct:
            for i, m in enumerate(sct.monitors):
                if i == 0:
                    continue  # 仮想全体はスキップ！
                if (m["left"] <= screen_x < m["left"] + m["width"] and
                    m["top"] <= screen_y < m["top"] + m["height"]):
                    return i
        return 1  # fallback
    
    def capture_fullscreen(self):
        self.hide()
        QApplication.processEvents()
        monitor_index = self.get_monitor_index_for_window()
        path = capture_screen(mode="full", monitor_index=monitor_index)
        self.show()
        self.log.append(f"📸 全画面キャプチャ保存: {path}")
        self.log.moveCursor(self.log.textCursor().End)

        self.log.append("🔄 翻訳中...（API応答を待っています）")
        self.log.moveCursor(self.log.textCursor().End)

        from core import translate_image

        translated, encode_time, api_time = translate_image(path)
        self.log.append(f"🖼️ エンコード時間: {encode_time:.2f}s")
        self.log.append(f"🌐 API応答時間: {api_time:.2f}s")
        self.log.append(f"🗨 翻訳結果:\n{translated}")
        self.log.moveCursor(self.log.textCursor().End)

    def capture_below(self):
        # ウィンドウのスクリーン上の位置・サイズ
        global_pos = self.mapToGlobal(self.rect().topLeft())
        x = global_pos.x()
        y = global_pos.y()
        w = self.width()
        h = self.height()

        self.hide()
        QApplication.processEvents()

        from core import capture_screen
        monitor_index = self.get_monitor_index_for_window()
        path = capture_screen(mode="underlay", region=(x, y, w, h), monitor_index=monitor_index)


        self.show()
        self.log.append(f"🫥 背後領域キャプチャ保存: {path}")
        self.log.moveCursor(self.log.textCursor().End)
        
        self.log.append("🔄 翻訳中...（API応答を待っています）")
        self.log.moveCursor(self.log.textCursor().End)
        
        from core import translate_image

        translated, encode_time, api_time = translate_image(path)
        self.log.append(f"🖼️ エンコード時間: {encode_time:.2f}s")
        self.log.append(f"🌐 API応答時間: {api_time:.2f}s")
        self.log.append(f"🗨 翻訳結果:\n{translated}")
        self.log.moveCursor(self.log.textCursor().End)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = OutputOverlay()
    window.show()
    sys.exit(app.exec_())
