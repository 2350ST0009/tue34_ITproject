import sys
import threading
import signal  # ⬅️ 追加：システム信号を扱うライブラリ
from pynput import keyboard
from pynput.mouse import Controller as MouseController
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QObject, pyqtSignal, QTimer  # ⬅️ QTimerを追加
from ui_controller import RingMenuWindow

class SignalBridge(QObject):
    show_menu_signal = pyqtSignal(tuple)

class LauncherApp:
    def __init__(self):
        self.qt_app = QApplication(sys.argv)
        self.window = RingMenuWindow()
        self.mouse = MouseController()
        
        self.bridge = SignalBridge()
        self.bridge.show_menu_signal.connect(self.window.show_at_mouse)

        # 🌟 ここがCtrl+Cで止めるための魔法のコード 🌟
        # 1. Ctrl+C（SIGINT）を受け取ったらデフォルトの終了処理をするように設定
        signal.signal(signal.SIGINT, signal.SIG_DFL)
        
        # 2. PyQtの処理中に500ミリ秒に1回、一瞬だけPythonに主導権を戻す空のタイマー
        self.timer = QTimer()
        self.timer.timeout.connect(lambda: None)
        self.timer.start(500)

    def on_activate(self):
        pos = self.mouse.position
        print(f"🔥 Hotkey detected at: {pos}")
        self.bridge.show_menu_signal.emit(pos)

    def run_hotkey_listener(self):
        with keyboard.GlobalHotKeys({'<f9>': self.on_activate}) as h:
            h.join()

    def run(self):
        listener_thread = threading.Thread(target=self.run_hotkey_listener, daemon=True)
        listener_thread.start()
        
        print("🚀 Launcher is running... Press F9 to test.")
        print("💡 You can now stop it with [Ctrl + C] smoothly!")
        sys.exit(self.qt_app.exec())

if __name__ == "__main__":
    app = LauncherApp()
    app.run()