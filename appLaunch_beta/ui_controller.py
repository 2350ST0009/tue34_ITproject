import sys
import math
import subprocess
from PyQt6.QtWidgets import QWidget, QPushButton
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QPainter, QColor

class RingMenuWindow(QWidget):
    def __init__(self):
        super().__init__()
        
        # 1. ウィンドウの基本設定
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |    # 枠なし
            Qt.WindowType.WindowStaysOnTopHint |   # 常に最前面
            Qt.WindowType.Tool                     # タスクバーに表示しない
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground) # 背景透過
        self.setFixedSize(400, 400) # メニューの表示領域

        # 2. 登録するアプリの設定（名前と実行ファイルのパス）
        # ※ご自身の環境に合わせてパスを書き換えてみてください
        self.apps = [
            {"name": "Notepad", "path": "notepad.exe"},
            {"name": "Edge", "path": "msedge.exe"},
            {"name": "Explorer", "path": "explorer.exe"},
            {"name": "Calc", "path": "calc.exe"},
            {"name": "Terminal", "path": "wt.exe"},
            {"name": "Paint", "path": "mspaint.exe"},
        ]

        self.buttons = []
        self.setup_ring_menu()

    def setup_ring_menu(self):
        """アプリの数に合わせて円形にボタンを配置する"""
        radius = 120  # 中心からの距離
        center_x = self.width() // 2
        center_y = self.height() // 2

        for i, app in enumerate(self.apps):
            btn = QPushButton(app["name"], self)
            btn.setFixedSize(80, 40)
            
            # スタイルを少しActions Ring風に
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

            # 角度の計算（真上から時計回り）
            angle = math.radians(i * (360 / len(self.apps)) - 90)
            
            # ボタンの中心座標を計算
            x = int(center_x + radius * math.cos(angle) - btn.width() / 2)
            y = int(center_y + radius * math.sin(angle) - btn.height() / 2)
            
            btn.move(x, y)
            
            # クリックイベントの登録（引数付きで呼び出すためにlambdaを使用）
            btn.clicked.connect(lambda checked, a=app: self.launch_app(a))
            self.buttons.append(btn)

    def launch_app(self, app_info):
        """アプリケーションを起動する"""
        try:
            print(f"🚀 Launching: {app_info['name']}")
            subprocess.Popen(app_info['path'], shell=True)
        except Exception as e:
            print(f"❌ Error: {e}")
        
        self.hide() # 起動したらメニューを閉じる

    def show_at_mouse(self, pos):
        """マウス位置にウィンドウを移動して表示"""
        target_x = int(pos[0] - self.width() / 2)
        target_y = int(pos[1] - self.height() / 2)
        self.move(target_x, target_y)
        self.show()
        self.activateWindow()

    def paintEvent(self, event):
        """中央の見た目を描画"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # 中心に薄いガイドライン用の円を描画
        painter.setPen(QColor(255, 255, 255, 40))
        painter.setBrush(QColor(255, 255, 255, 10))
        painter.drawEllipse(self.width()//2 - 60, self.height()//2 - 60, 120, 120)

    def keyPressEvent(self, event):
        """Escキーでメニューを閉じる"""
        if event.key() == Qt.Key.Key_Escape:
            self.hide()