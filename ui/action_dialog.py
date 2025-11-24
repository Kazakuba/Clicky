from PyQt6.QtWidgets import QDialog, QWidget, QVBoxLayout, QComboBox, QLabel, QLineEdit, QPushButton, QStackedWidget
from controllers.action_controller import ActionController
from .utils import load_stylesheet

class ActionDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add/Edit Action")
        self.action_controller = ActionController()
        self.action_controller.set_parent(self)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        self.type_combo = QComboBox()
        self.type_combo.addItems(["Click", "Hold", "Scroll", "Drag", "Keyboard", "Script", "Wait for", "Press Key", "Move Mouse To"])
        self.type_combo.currentIndexChanged.connect(self.update_params)
        layout.addWidget(QLabel("Action Type:"))
        layout.addWidget(self.type_combo)

        self.stacked_widget = QStackedWidget()
        layout.addWidget(self.stacked_widget)

        #Click
        click_widget = QWidget()
        click_layout = QVBoxLayout()
        self.click_x = QLineEdit()
        self.click_y = QLineEdit()
        click_capture_btn = QPushButton("Capture Coordinates")
        click_capture_btn.setObjectName("captureButton")
        click_capture_btn.setProperty("type", "coordinate-capture")
        click_capture_btn.clicked.connect(self.capture_coordinates)
        self.click_clicks = QLineEdit("1")
        click_layout.addWidget(QLabel("X:"))
        click_layout.addWidget(self.click_x)
        click_layout.addWidget(QLabel("Y:"))
        click_layout.addWidget(self.click_y)
        click_layout.addWidget(click_capture_btn)
        click_layout.addWidget(QLabel("Clicks:"))
        click_layout.addWidget(self.click_clicks)
        click_widget.setLayout(click_layout)
        self.stacked_widget.addWidget(click_widget)

        #Hold
        hold_widget = QWidget()
        hold_layout = QVBoxLayout()
        self.hold_x = QLineEdit()
        self.hold_y = QLineEdit()
        hold_capture_btn = QPushButton("Capture Coordinates")
        hold_capture_btn.setObjectName("captureButton")
        hold_capture_btn.setProperty("type", "coordinate-capture")
        hold_capture_btn.clicked.connect(self.capture_coordinates)
        self.hold_duration = QLineEdit("1")
        hold_layout.addWidget(QLabel("X:"))
        hold_layout.addWidget(self.hold_x)
        hold_layout.addWidget(QLabel("Y:"))
        hold_layout.addWidget(self.hold_y)
        hold_layout.addWidget(hold_capture_btn)
        hold_layout.addWidget(QLabel("Duration (seconds):"))
        hold_layout.addWidget(self.hold_duration)
        hold_widget.setLayout(hold_layout)
        self.stacked_widget.addWidget(hold_widget)

        #Scroll
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout()
        self.scroll_x = QLineEdit()
        self.scroll_y = QLineEdit()
        scroll_capture_btn = QPushButton("Capture Coordinates")
        scroll_capture_btn.setObjectName("captureButton")
        scroll_capture_btn.setProperty("type", "coordinate-capture")
        scroll_capture_btn.clicked.connect(self.capture_coordinates)
        self.scroll_amount = QLineEdit("10")
        scroll_layout.addWidget(QLabel("X:"))
        scroll_layout.addWidget(self.scroll_x)
        scroll_layout.addWidget(QLabel("Y:"))
        scroll_layout.addWidget(self.scroll_y)
        scroll_layout.addWidget(scroll_capture_btn)
        scroll_layout.addWidget(QLabel("Amount:"))
        scroll_layout.addWidget(self.scroll_amount)
        scroll_widget.setLayout(scroll_layout)
        self.stacked_widget.addWidget(scroll_widget)

        #Drag
        drag_widget = QWidget()
        drag_layout = QVBoxLayout()
        self.drag_x1 = QLineEdit()
        self.drag_y1 = QLineEdit()
        drag_capture_start_btn = QPushButton("Capture Start")
        drag_capture_start_btn.setObjectName("captureButton")
        drag_capture_start_btn.setProperty("type", "coordinate-capture")
        drag_capture_start_btn.clicked.connect(self.capture_start_coordinates)
        self.drag_x2 = QLineEdit()
        self.drag_y2 = QLineEdit()
        drag_capture_end_btn = QPushButton("Capture End")
        drag_capture_end_btn.setObjectName("captureButton")
        drag_capture_end_btn.setProperty("type", "coordinate-capture")
        drag_capture_end_btn.clicked.connect(self.capture_end_coordinates)
        drag_layout.addWidget(QLabel("Start X:"))
        drag_layout.addWidget(self.drag_x1)
        drag_layout.addWidget(QLabel("Start Y:"))
        drag_layout.addWidget(self.drag_y1)
        drag_layout.addWidget(drag_capture_start_btn)
        drag_layout.addWidget(QLabel("End X:"))
        drag_layout.addWidget(self.drag_x2)
        drag_layout.addWidget(QLabel("End Y:"))
        drag_layout.addWidget(self.drag_y2)
        drag_layout.addWidget(drag_capture_end_btn)
        drag_widget.setLayout(drag_layout)
        self.stacked_widget.addWidget(drag_widget)

        #Keyboard
        keyboard_widget = QWidget()
        keyboard_layout = QVBoxLayout()
        self.keyboard_keys = QLineEdit()
        keyboard_layout.addWidget(QLabel("Keys:"))
        keyboard_layout.addWidget(self.keyboard_keys)
        keyboard_widget.setLayout(keyboard_layout)
        self.stacked_widget.addWidget(keyboard_widget)

        #Script
        script_widget = QWidget()
        script_layout = QVBoxLayout()
        self.script_command = QLineEdit()
        script_layout.addWidget(QLabel("Command:"))
        script_layout.addWidget(self.script_command)
        script_widget.setLayout(script_layout)
        self.stacked_widget.addWidget(script_widget)

        #Wait for
        wait_widget = QWidget()
        wait_layout = QVBoxLayout()
        self.wait_time = QLineEdit("1")
        wait_layout.addWidget(QLabel("Wait Time (seconds):"))
        wait_layout.addWidget(self.wait_time)
        wait_widget.setLayout(wait_layout)
        self.stacked_widget.addWidget(wait_widget)

        #Press Key
        press_key_widget = QWidget()
        press_key_layout = QVBoxLayout()
        self.press_key = QLineEdit()
        press_key_layout.addWidget(QLabel("Key (e.g., Enter, F11):"))
        press_key_layout.addWidget(self.press_key)
        press_key_widget.setLayout(press_key_layout)
        self.stacked_widget.addWidget(press_key_widget)

        #Move Mouse To
        move_widget = QWidget()
        move_layout = QVBoxLayout()
        self.move_x = QLineEdit()
        self.move_y = QLineEdit()
        move_capture_btn = QPushButton("Capture Coordinates")
        move_capture_btn.setObjectName("captureButton")
        move_capture_btn.setProperty("type", "coordinate-capture")
        move_capture_btn.clicked.connect(self.capture_coordinates)
        move_layout.addWidget(QLabel("X:"))
        move_layout.addWidget(self.move_x)
        move_layout.addWidget(QLabel("Y:"))
        move_layout.addWidget(self.move_y)
        move_layout.addWidget(move_capture_btn)
        move_widget.setLayout(move_layout)
        self.stacked_widget.addWidget(move_widget)

        ok_btn = QPushButton("OK")
        ok_btn.clicked.connect(self.accept)
        layout.addWidget(ok_btn)
        self.setLayout(layout)
        self.update_params()
        self.setStyleSheet(load_stylesheet())
        
        additional_style = """
        QPushButton[type="coordinate-capture"] {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 rgba(80, 120, 180, 230), stop:1 rgba(60, 100, 160, 240));
            border: 2px solid rgba(100, 140, 200, 180);
            font-weight: bold;
            color: white;
        }
        QPushButton[type="coordinate-capture"]:hover {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 rgba(100, 140, 200, 240), stop:1 rgba(80, 120, 180, 250));
            border: 2px solid rgba(120, 160, 220, 200);
        }
        """
        self.setStyleSheet(self.styleSheet() + additional_style)

    def update_params(self):
        self.stacked_widget.setCurrentIndex(self.type_combo.currentIndex())

    def capture_coordinates(self):
        self.action_controller.capture_coordinates()

    def capture_start_coordinates(self):
        self.action_controller.capture_start_coordinates()

    def capture_end_coordinates(self):
        self.action_controller.capture_end_coordinates()

    def get_action(self):
        action_type = self.type_combo.currentText().lower()
        params = {}
        if action_type == "click":
            params["x"] = int(self.click_x.text())
            params["y"] = int(self.click_y.text())
            params["clicks"] = int(self.click_clicks.text())
        elif action_type == "hold":
            params["x"] = int(self.hold_x.text())
            params["y"] = int(self.hold_y.text())
            params["duration"] = float(self.hold_duration.text())
        elif action_type == "scroll":
            params["x"] = int(self.scroll_x.text())
            params["y"] = int(self.scroll_y.text())
            params["amount"] = int(self.scroll_amount.text())
        elif action_type == "drag":
            params["x1"] = int(self.drag_x1.text())
            params["y1"] = int(self.drag_y1.text())
            params["x2"] = int(self.drag_x2.text())
            params["y2"] = int(self.drag_y2.text())
        elif action_type == "keyboard":
            params["keys"] = self.keyboard_keys.text()
        elif action_type == "script":
            params["command"] = self.script_command.text()
        elif action_type == "wait for":
            params["time"] = float(self.wait_time.text())
        elif action_type == "press key":
            params["key"] = self.press_key.text()
        elif action_type == "move mouse to":
            params["x"] = int(self.move_x.text())
            params["y"] = int(self.move_y.text())
        return self.action_controller.create_action(action_type, params)