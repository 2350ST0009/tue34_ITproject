import sys
import threading
import signal
from pynput import keyboard
from pynput.mouse import Controller as MouseController
from PyQt6.QtWidgets import QApplication, QSystemTrayIcon, QMenu
from PyQt6.QtCore import QObject, pyqtSignal, QTimer, Qt
from PyQt6.QtGui import QIcon, QPixmap, QPainter, QColor, QAction
from ui_controller import RingMenuWindow

class SignalBridge(QObject):
    show_menu_signal = pyqtSignal(tuple)

class LauncherApp:
    def __init__(self):
        self.qt_app = QApplication(sys.argv)
        # メニューを隠した（非表示にした）時にアプリ自体が終了するのを防ぐ
        self.qt_app.setQuitOnLastWindowClosed(False)

        self.window = RingMenuWindow()
        self.mouse = MouseController()
        
        self.bridge = SignalBridge()
        self.bridge.show_menu_signal.connect(self.window.show_at_mouse)

        # タスクトレイアイコンのセットアップ
        self.setup_tray()

        # Ctrl+C での終了対応（開発時のターミナル実行用）
        signal.signal(signal.SIGINT, signal.SIG_DFL)
        self.timer = QTimer()
        self.timer.timeout.connect(lambda: None)
        self.timer.start(500)

    def create_tray_icon(self):
        """画像ファイルなしでコードからトレイ用の丸いアイコンを生成する"""
        pixmap = QPixmap(64, 64)
        pixmap.fill(Qt.GlobalColor.transparent)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        # 外側の青い円
        painter.setBrush(QColor(80, 120, 255))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(4, 4, 56, 56)
        # 内側の白いリング風アクセント
        painter.setBrush(QColor(255, 255, 255))
        painter.drawEllipse(22, 22, 20, 20)
        painter.end()
        
        return QIcon(pixmap)

    def setup_tray(self):
        """Windowsのタスクトレイにアイコンと右クリックメニューを追加"""
        self.tray_icon = QSystemTrayIcon(self.create_tray_icon(), self.qt_app)
        self.tray_icon.setToolTip("Actions Ring Launcher (F9)")

        tray_menu = QMenu()

        # 1. 設定の再読み込み
        reload_action = QAction("設定の再読み込み (Reload Config)", self.qt_app)
        reload_action.triggered.connect(self.reload_settings)
        tray_menu.addAction(reload_action)

        tray_menu.addSeparator()

        # 2. 終了
        quit_action = QAction("終了 (Exit)", self.qt_app)
        quit_action.triggered.connect(self.quit_app)
        tray_menu.addAction(quit_action)

        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()

    def reload_settings(self):
        self.window.reload_config()
        # Windowsの通知バルーンで再読み込み完了をお知らせ
        self.tray_icon.showMessage(
            "Actions Ring",
            "config.yaml を再読み込みしました。",
            QSystemTrayIcon.MessageIcon.Information,
            2000
        )

    def quit_app(self):
        self.tray_icon.hide()
        self.qt_app.quit()

    def on_activate(self):
        pos = self.mouse.position
        self.bridge.show_menu_signal.emit(pos)

    def run_hotkey_listener(self):
        with keyboard.GlobalHotKeys({'<f9>': self.on_activate}) as h:
            h.join()

    def run(self):
        listener_thread = threading.Thread(target=self.run_hotkey_listener, daemon=True)
        listener_thread.start()
        sys.exit(self.qt_app.exec())

if __name__ == "__main__":
    app = LauncherApp()
    app.run()