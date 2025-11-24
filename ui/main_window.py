from PyQt6.QtWidgets import (
    QMainWindow, QListWidget, QPushButton, QVBoxLayout, QWidget, 
    QMessageBox, QMenuBar, QStatusBar, QSystemTrayIcon, QMenu, QApplication
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon, QAction
import os
import sys
from .workflow_window import WorkflowWindow
from .settings_dialog import SettingsDialog
from controllers.workflow_controller import WorkflowController
from .utils import load_stylesheet

class MainWindow(QMainWindow):
    def __init__(self, settings):
        super().__init__()
        self.settings = settings
        self.setWindowTitle("Clicky")
        self.setGeometry(100, 100, 400, 300)
        self.workflow_controller = WorkflowController()
        self.workflow_windows = []
        self.setup_tray_icon()
        self.init_ui()
        self.apply_theme()
        
    def setup_tray_icon(self):
        self.tray_icon = QSystemTrayIcon(self)
        
        app_icon = self.get_app_icon()
        self.tray_icon.setIcon(app_icon)
        self.setWindowIcon(app_icon)
        
        tray_menu = QMenu()
        
        self.show_action = QAction("Show Window", self)
        self.show_action.triggered.connect(self.show_from_tray)
        tray_menu.addAction(self.show_action)
        
        tray_menu.addSeparator()
        
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.exit_application)
        tray_menu.addAction(exit_action)
        
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.activated.connect(self.tray_icon_activated)
        
        if self.settings.run_in_background:
            self.tray_icon.show()
    
    def get_app_icon(self):
        icon_paths = [
            "resources/images/app_icon.ico",
            "resources/images/app_icon.png",
            "resources/images/icon.png",
            "resources/app_icon.png",
            "app_icon.png",
            "icon.png"
        ]
        
        base_path = os.path.dirname(os.path.abspath(__file__))
        for path in icon_paths:
            full_path = os.path.join(base_path, "..", path)
            if os.path.exists(full_path):
                return QIcon(full_path)
            elif os.path.exists(path):
                return QIcon(path)
        
        icon = QIcon.fromTheme("applications-system")
        
        if icon.isNull():
            return QIcon.fromTheme("application-x-executable")
        
        return icon
    
    def tray_icon_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            if self.isVisible():
                self.hide()
            else:
                self.show_from_tray()
    
    def show_from_tray(self):
        self.show()
        self.setWindowState(self.windowState() & ~Qt.WindowState.WindowMinimized | Qt.WindowState.WindowActive)
        self.activateWindow()

    def exit_application(self):
        for window in self.workflow_windows[:]:
            window.close()
        
        self.tray_icon.hide()
        QApplication.quit()

    def init_ui(self):
        menu_bar = QMenuBar()
        file_menu = menu_bar.addMenu("File")
        file_menu.addAction("New Workflow", self.new_workflow)
        file_menu.addAction("Open Workflow", self.open_workflow)
        file_menu.addAction("Exit", self.exit_application)
        edit_menu = menu_bar.addMenu("Edit")
        edit_menu.addAction("Settings", self.open_settings)
        help_menu = menu_bar.addMenu("Help")
        help_menu.addAction("About", self.show_about)
        self.setMenuBar(menu_bar)

        central_widget = QWidget()
        layout = QVBoxLayout()
        self.workflow_list = QListWidget()
        self.workflow_list.itemDoubleClicked.connect(self.open_workflow_from_item)
        layout.addWidget(self.workflow_list)

        new_btn = QPushButton("New Workflow")
        new_btn.clicked.connect(self.new_workflow)
        layout.addWidget(new_btn)

        open_btn = QPushButton("Open Workflow")
        open_btn.clicked.connect(self.open_workflow)
        layout.addWidget(open_btn)

        delete_btn = QPushButton("Delete Workflow")
        delete_btn.clicked.connect(self.delete_workflow)
        layout.addWidget(delete_btn)

        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")

        self.load_workflows()

    def apply_theme(self):
        self.setStyleSheet(load_stylesheet(self.settings.theme))

    def load_workflows(self):
        self.workflow_list.clear()
        workflows = self.workflow_controller.list_workflows()
        self.workflow_list.addItems(workflows)

    def new_workflow(self):
        from models.workflow import Workflow
        workflow = Workflow()
        workflow_window = WorkflowWindow(workflow, self.workflow_controller, self)
        workflow_window.show()
        self.workflow_windows.append(workflow_window)
        self.status_bar.showMessage("New workflow created")

    def open_workflow_from_item(self, item):
        workflow_name = item.text()
        self.open_workflow_by_name(workflow_name)

    def open_workflow(self):
        selected = self.workflow_list.currentItem()
        if selected:
            workflow_name = selected.text()
            self.open_workflow_by_name(workflow_name)
        else:
            QMessageBox.warning(self, "Warning", "Please select a workflow to open.")
            self.status_bar.showMessage("No workflow selected")

    def open_workflow_by_name(self, workflow_name):
        try:
            workflow = self.workflow_controller.load_workflow(workflow_name)
            workflow_window = WorkflowWindow(workflow, self.workflow_controller, self)
            workflow_window.apply_theme(self.settings.theme)
            workflow_window.show()
            self.workflow_windows.append(workflow_window)
            self.status_bar.showMessage(f"Opened workflow: {workflow_name}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load workflow: {e}")
            self.status_bar.showMessage(f"Error loading workflow: {e}")

    def delete_workflow(self):
        selected = self.workflow_list.currentItem()
        if selected:
            workflow_name = selected.text()
            reply = QMessageBox.question(self, "Confirm Delete", f"Delete '{workflow_name}'?",
                                         QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                try:
                    import os
                    os.remove(os.path.join(self.workflow_controller.workflows_dir, workflow_name + ".json"))
                    self.load_workflows()
                    self.status_bar.showMessage(f"Deleted workflow: {workflow_name}")
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Failed to delete workflow: {e}")
                    self.status_bar.showMessage(f"Error deleting workflow: {e}")
        else:
            QMessageBox.warning(self, "Warning", "Please select a workflow to delete.")
            self.status_bar.showMessage("No workflow selected")

    def open_settings(self):
        dialog = SettingsDialog(self.settings, self)
        if dialog.exec():
            self.apply_theme()

            if self.settings.run_in_background:
                self.tray_icon.show()
            else:
                self.tray_icon.hide()
                
            self.status_bar.showMessage(f"Settings saved. Theme: {self.settings.theme}")

    def show_about(self):
        QMessageBox.information(self, "About", "Automator v1.0\nCreated by Kazakuba")
        
    def closeEvent(self, event):
        if self.settings.run_in_background:
            event.ignore()
            
            if not hasattr(self, '_minimized_before'):
                self.tray_icon.showMessage(
                    "Automator Running in Background",
                    "The application will continue running in the background. Click the tray icon to show the window again.",
                    QSystemTrayIcon.MessageIcon.Information,
                    5000
                )
                self._minimized_before = True
                
            self.hide()
        else:
            reply = QMessageBox.question(
                self, 
                "Exit Confirmation",
                "Are you sure you want to exit? This will stop all running workflows.",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                for window in self.workflow_windows[:]:
                    window.close()
                event.accept()
            else:
                event.ignore()