import sys
import os
import math
import subprocess
import yaml
from PyQt6.QtWidgets import QWidget, QPushButton
from PyQt6.QtCore import Qt, QEvent
from PyQt6.QtGui import QPainter, QColor

class RingMenuWindow(QWidget):
    def __init__(self):
        super().__init__()
        
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(400, 400)

        if getattr(sys, 'frozen', False):
            base_dir = os.path.dirname(sys.executable)
        else:
            base_dir = os.path.dirname(os.path.abspath(__file__))

        self.config_file = os.path.join(base_dir, "config.yaml")
        self.buttons = []
        
        # 初期読み込みとボタン配置
        self.apps = self.load_config()
        self.setup_ring_menu()

    def load_config(self):
        if not os.path.exists(self.config_file):
            default_config = {
                "apps": [
                    {"name": "Notepad", "path": "notepad.exe"},
                    {"name": "Edge", "path": "msedge.exe"},
                    {"name": "Explorer", "path": "explorer.exe"},
                    {"name": "Calc", "path": "calc.exe"},
                ]
            }
            with open(self.config_file, "w", encoding="utf-8") as f:
                yaml.dump(default_config, f, allow_unicode=True, sort_keys=False)
            return default_config["apps"]

        with open(self.config_file, "r", encoding="utf-8") as f:
            config_data = yaml.safe_load(f)
            return config_data.get("apps", [])

    # 🌟 追加：設定ファイルを再読み込みしてボタンを作り直す処理
    def reload_config(self):
        self.hide()
        # 今あるボタンを画面から削除してリストを空にする
        for btn in self.buttons:
            btn.deleteLater()
        self.buttons.clear()

        # 最新の config.yaml を読み込んで再配置
        self.apps = self.load_config()
        self.setup_ring_menu()

    def setup_ring_menu(self):
        radius = 120
        center_x = self.width() // 2
        center_y = self.height() // 2

        for i, app in enumerate(self.apps):
            btn = QPushButton(app["name"], self)
            btn.setFixedSize(80, 40)
            
            btn.setStyleSheet("""
                QPushButton {
                    background-color: rgba(45, 45, 45, 200);
                    color: white;
                    border-radius: 10px;
                    border: 1px solid rgba(255, 255, 255, 50);
                }
                QPushButton:hover {
                    background-color: rgba(100, 100, 255, 220);
                }
            """)

            if len(self.apps) > 0:
                angle = math.radians(i * (360 / len(self.apps)) - 90)
            else:
                angle = 0
            
            x = int(center_x + radius * math.cos(angle) - btn.width() / 2)
            y = int(center_y + radius * math.sin(angle) - btn.height() / 2)
            
            btn.move(x, y)
            btn.clicked.connect(lambda checked, a=app: self.launch_app(a))
            btn.show()  # 再読み込み時にも確実に表示されるよう明示
            self.buttons.append(btn)

    def launch_app(self, app_info):
        try:
            subprocess.Popen(app_info['path'], shell=True)
        except Exception as e:
            print(f"Error: {e}")
        self.hide()

    def show_at_mouse(self, pos):
        if self.isVisible():
            self.hide()
            return

        target_x = int(pos[0] - self.width() / 2)
        target_y = int(pos[1] - self.height() / 2)
        self.move(target_x, target_y)
        self.show()
        self.activateWindow()

    def changeEvent(self, event):
        if event.type() == QEvent.Type.ActivationChange:
            if not self.isActiveWindow():
                self.hide()
        super().changeEvent(event)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(QColor(255, 255, 255, 40))
        painter.setBrush(QColor(255, 255, 255, 10))
        painter.drawEllipse(self.width()//2 - 60, self.height()//2 - 60, 120, 120)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.hide()