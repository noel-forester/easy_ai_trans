from PyQt5.QtWidgets import QApplication, QWidget, QTextEdit, QVBoxLayout, QTabWidget
from PyQt5.QtCore import Qt
import sys


class OutputOverlay(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setGeometry(100, 100, 600, 400)

        # 背景つきコンテナ
        self.container = QWidget(self)
        self.container.setStyleSheet("background-color: rgba(255, 0, 0, 10); border-radius: 8px;")
        self.layout = QVBoxLayout(self.container)

        # タブ構成
        self.tabs = QTabWidget()
        self.tabs.setAutoFillBackground(False)
        self.tabs.tabBar().setAutoFillBackground(False)

        stacked = self.tabs.findChild(QWidget, None)
        stacked.setAutoFillBackground(False)
        stacked.setStyleSheet("background: transparent;")

        self.tabs.setStyleSheet("""
            QTabWidget::pane {
                background: transparent;
                border: none;
            }
            QTabBar::tab {
                background: transparent;
                color: white;
                border: none;
                padding: 5px;
            }
            QTabBar::tab:selected {
                background: rgba(255, 255, 255, 40);
            }
        """)

        self.chatgpt_output = QTextEdit()
        self.gemini_output = QTextEdit()

        for t in (self.chatgpt_output, self.gemini_output):
            t.setStyleSheet("""
                QTextEdit {
                    background-color: rgba(0, 255, 0, 0);
                    color: white;
                    border: none;
                }
            """)
            t.setAutoFillBackground(False)
            t.viewport().setAutoFillBackground(False)
            t.viewport().setStyleSheet("background-color: transparent;")

        self.tabs.addTab(self.chatgpt_output, "ChatGPT")
        self.tabs.addTab(self.gemini_output, "Gemini")
        self.layout.addWidget(self.tabs)
        
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = OutputOverlay()
    window.show()
    print("test2")
    sys.exit(app.exec_())