from models.action import Action
from pynput import mouse
from pynput.mouse import Controller as MouseController
from pynput.mouse import Button
from PyQt6.QtWidgets import QApplication, QLabel
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QCursor, QPixmap
import platform
import ctypes
import os
import tempfile

class ActionController:
    def __init__(self):
        self.parent = None
        self.status_label = None
        self.mouse = MouseController()
        self.original_cursor_saved = False

    def capture_coordinates(self):
        self._set_coordinate_cursor()
        self._show_status_window("Click anywhere to capture coordinates")
        self.clicked_x, self.clicked_y = None, None
        with mouse.Listener(on_click=self.on_click) as listener:
            listener.join()
        self._restore_cursor()
        self._hide_status_window()
        current_widget = self.parent.stacked_widget.currentWidget()
        if current_widget == self.parent.stacked_widget.widget(0):
            self.parent.click_x.setText(str(self.clicked_x))
            self.parent.click_y.setText(str(self.clicked_y))
        elif current_widget == self.parent.stacked_widget.widget(1):
            self.parent.hold_x.setText(str(self.clicked_x))
            self.parent.hold_y.setText(str(self.clicked_y))
        elif current_widget == self.parent.stacked_widget.widget(2):
            self.parent.scroll_x.setText(str(self.clicked_x))
            self.parent.scroll_y.setText(str(self.clicked_y))
        elif current_widget == self.parent.stacked_widget.widget(8):
            self.parent.move_x.setText(str(self.clicked_x))
            self.parent.move_y.setText(str(self.clicked_y))
        return self.clicked_x, self.clicked_y

    def capture_start_coordinates(self):
        self._set_coordinate_cursor()
        self._show_status_window("Click anywhere to capture start coordinates")
        self.clicked_x, self.clicked_y = None, None
        with mouse.Listener(on_click=self.on_click) as listener:
            listener.join()
        self._restore_cursor()
        self._hide_status_window()
        self.parent.drag_x1.setText(str(self.clicked_x))
        self.parent.drag_y1.setText(str(self.clicked_y))
        return self.clicked_x, self.clicked_y

    def capture_end_coordinates(self):
        self._set_coordinate_cursor()
        self._show_status_window("Click anywhere to capture end coordinates")
        self.clicked_x, self.clicked_y = None, None
        with mouse.Listener(on_click=self.on_click) as listener:
            listener.join()
        self._restore_cursor()
        self._hide_status_window()
        self.parent.drag_x2.setText(str(self.clicked_x))
        self.parent.drag_y2.setText(str(self.clicked_y))
        return self.clicked_x, self.clicked_y

    def _set_coordinate_cursor(self):
        system = platform.system()
        
        QApplication.setOverrideCursor(Qt.CursorShape.CrossCursor)
        
        if system == 'Windows':
            try:
                self._set_windows_system_cursor()
            except Exception as e:
                print(f"Could not set Windows system cursor: {e}")

    def _restore_cursor(self):
        QApplication.restoreOverrideCursor()
        
        system = platform.system()
        if system == 'Windows':
            try:
                self._restore_windows_system_cursor()
            except Exception as e:
                print(f"Could not restore Windows system cursor: {e}")

    def _set_windows_system_cursor(self):
        """Set Windows system cursor to crosshair using SetSystemCursor"""
        OCR_NORMAL = 32512
        OCR_CROSS = 32515
        
        user32 = ctypes.WinDLL('user32', use_last_error=True)
        
        crosshair_cursor = user32.LoadCursorW(0, OCR_CROSS)
        
        result = user32.SetSystemCursor(crosshair_cursor, OCR_NORMAL)
        
        if not result:
            error = ctypes.get_last_error()
            print(f"SetSystemCursor failed with error code: {error}")
            
        self.original_cursor_saved = True

    def _restore_windows_system_cursor(self):
        """Restore all system cursors to their original defaults"""
        if self.original_cursor_saved:
            try:
                user32 = ctypes.WinDLL('user32', use_last_error=True)
                
                SPI_SETCURSORS = 0x0057
                
                result = user32.SystemParametersInfoW(SPI_SETCURSORS, 0, 0, 0)
                
                if not result:
                    error = ctypes.get_last_error()
                    print(f"SystemParametersInfoW failed with error code: {error}")
                    
                self.original_cursor_saved = False
            except Exception as e:
                print(f"Error restoring system cursors: {e}")

    def _show_status_window(self, message):
        if self.status_label is None:
            self.status_label = QLabel(message)
            self.status_label.setWindowFlags(Qt.WindowType.ToolTip | Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
            self.status_label.setStyleSheet("""
                background-color: rgba(40, 40, 120, 220);
                color: white;
                padding: 10px;
                border-radius: 10px;
                font-weight: bold;
                font-size: 14px;
            """)
            self.status_label.adjustSize()
        else:
            self.status_label.setText(message)
            
        screen = QApplication.primaryScreen().geometry()
        x = (screen.width() - self.status_label.width()) // 2
        y = 50
        self.status_label.move(x, y)
        self.status_label.show()

    def _hide_status_window(self):
        if self.status_label:
            self.status_label.hide()

    def on_click(self, x, y, button, pressed):
        if pressed:
            self.clicked_x, self.clicked_y = x, y
            return False

    def create_action(self, action_type, params):
        return Action(action_type, **params)

    def set_parent(self, parent):
        self.parent = parent