from PyQt6.QtWidgets import QDialog, QVBoxLayout, QCheckBox, QComboBox, QPushButton, QLabel, QHBoxLayout
import os
from models.settings import Settings
from .utils import load_stylesheet, get_data_directory

class SettingsDialog(QDialog):
    def __init__(self, settings, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.settings = settings
        self.parent_window = parent
        self.previous_theme = settings.theme
        self.init_ui()
        self.setStyleSheet(load_stylesheet(settings.theme))
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        layout.addWidget(QLabel("<b>General Settings</b>"))
        
        self.run_in_background_cb = QCheckBox("Run in background")
        self.run_in_background_cb.setChecked(self.settings.run_in_background)
        layout.addWidget(self.run_in_background_cb)

        self.auto_load_last_workflow_cb = QCheckBox("Auto-load last workflow")
        self.auto_load_last_workflow_cb.setChecked(self.settings.auto_load_last_workflow)
        layout.addWidget(self.auto_load_last_workflow_cb)
        
        layout.addWidget(QLabel("<b>Appearance</b>"))
        
        theme_layout = QHBoxLayout()
        theme_layout.addWidget(QLabel("Theme:"))
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Default", "Dark", "Light"])
        self.theme_combo.setCurrentText(self.settings.theme)
        self.theme_combo.currentTextChanged.connect(self.on_theme_changed)
        theme_layout.addWidget(self.theme_combo)
        layout.addLayout(theme_layout)
        
        button_layout = QHBoxLayout()
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.save_settings)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.cancel_settings)
        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def on_theme_changed(self, theme):
        try:
            self.setStyleSheet(load_stylesheet(theme))
        except Exception as e:
            print(f"Error previewing theme: {e}")
    
    def save_settings(self):
        self.settings.run_in_background = self.run_in_background_cb.isChecked()
        self.settings.auto_load_last_workflow = self.auto_load_last_workflow_cb.isChecked()
        self.settings.theme = self.theme_combo.currentText()
        
        try:
            settings_path = os.path.join(get_data_directory(), "settings.json")
            self.settings.save(settings_path)
            print(f"Settings saved to: {settings_path}")
        except Exception as e:
            print(f"Error saving settings: {e}")
            
        self.accept()
    
    def cancel_settings(self):
        if self.previous_theme != self.theme_combo.currentText():
            try:
                self.setStyleSheet(load_stylesheet(self.previous_theme))
            except Exception as e:
                print(f"Error restoring theme: {e}")
        self.reject()