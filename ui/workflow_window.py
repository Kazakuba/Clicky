from PyQt6.QtWidgets import (
    QMainWindow, QVBoxLayout, QStatusBar, QHBoxLayout, QWidget, QLabel, 
    QLineEdit, QPushButton, QTreeWidget, QTreeWidgetItem, QInputDialog, 
    QMessageBox, QGroupBox, QDateTimeEdit, QSpinBox, QScrollArea, QCheckBox,
    QTimeEdit
)
from PyQt6.QtCore import Qt, QThreadPool, QDateTime, QTime
from .action_dialog import ActionDialog
from services.automation_service import AutomationService
from services.scheduling_service import SchedulingService
from .utils import load_stylesheet
from datetime import datetime

class ScheduleWidget(QWidget):
    def __init__(self, parent=None, datetime_val=None, repeat_interval=None, execution_count=0, is_daily=False):
        super().__init__(parent)
        self.init_ui(datetime_val, repeat_interval, execution_count, is_daily)
        
    def init_ui(self, datetime_val, repeat_interval, execution_count, is_daily):
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        self.daily_checkbox = QCheckBox("Daily execution")
        self.daily_checkbox.setToolTip("When checked, the workflow will run at the specified time every day")
        self.daily_checkbox.stateChanged.connect(self.toggle_daily_mode)
        layout.addWidget(self.daily_checkbox)
        
        self.date_time_container = QWidget()
        date_time_layout = QHBoxLayout(self.date_time_container)
        date_time_layout.setContentsMargins(0, 0, 0, 0)
        
        date_time_layout.addWidget(QLabel("Date & Time:"))
        self.date_time_edit = QDateTimeEdit()
        self.date_time_edit.setCalendarPopup(True)
        self.date_time_edit.setDisplayFormat("yyyy-MM-dd HH:mm:ss")
        
        self.time_only_edit = QTimeEdit()
        self.time_only_edit.setDisplayFormat("HH:mm:ss")
        self.time_only_edit.setVisible(False)
        
        if datetime_val:
            if isinstance(datetime_val, str):
                try:
                    if len(datetime_val) <= 8 and datetime_val.count(":") == 2:
                        time = QTime.fromString(datetime_val, "HH:mm:ss")
                        self.time_only_edit.setTime(time)
                        self.date_time_edit.setTime(time)
                        is_daily = True
                    else:
                        dt = QDateTime.fromString(datetime_val, "yyyy-MM-dd HH:mm:ss")
                        self.date_time_edit.setDateTime(dt)
                        self.time_only_edit.setTime(dt.time())
                except:
                    self.date_time_edit.setDateTime(QDateTime.currentDateTime())
                    self.time_only_edit.setTime(QDateTime.currentDateTime().time())
            elif isinstance(datetime_val, datetime):
                qdt = QDateTime(
                    datetime_val.year, datetime_val.month, datetime_val.day,
                    datetime_val.hour, datetime_val.minute, datetime_val.second
                )
                self.date_time_edit.setDateTime(qdt)
                self.time_only_edit.setTime(qdt.time())
            else:
                self.date_time_edit.setDateTime(QDateTime.currentDateTime())
                self.time_only_edit.setTime(QDateTime.currentDateTime().time())
        else:
            self.date_time_edit.setDateTime(QDateTime.currentDateTime())
            self.time_only_edit.setTime(QDateTime.currentDateTime().time())
        
        self.daily_checkbox.setChecked(is_daily)
        
        date_time_layout.addWidget(self.date_time_edit)
        date_time_layout.addWidget(self.time_only_edit)
        layout.addWidget(self.date_time_container)
        
        repeat_layout = QHBoxLayout()
        repeat_layout.addWidget(QLabel("Repeat Interval (seconds):"))
        self.repeat_interval_spin = QSpinBox()
        self.repeat_interval_spin.setRange(0, 86400)
        self.repeat_interval_spin.setSpecialValueText("No Repeat")
        
        if repeat_interval:
            self.repeat_interval_spin.setValue(int(repeat_interval))
        else:
            self.repeat_interval_spin.setValue(0)
            
        repeat_layout.addWidget(self.repeat_interval_spin)
        layout.addLayout(repeat_layout)
        
        executions_layout = QHBoxLayout()
        executions_layout.addWidget(QLabel("Number of Executions:"))
        self.execution_count_spin = QSpinBox()
        self.execution_count_spin.setRange(0, 10000)
        self.execution_count_spin.setSpecialValueText("Infinite")
        
        if execution_count:
            self.execution_count_spin.setValue(int(execution_count))
        else:
            self.execution_count_spin.setValue(0)
            
        executions_layout.addWidget(self.execution_count_spin)
        layout.addLayout(executions_layout)
        
        separator = QWidget()
        separator.setFixedHeight(1)
        separator.setStyleSheet("background-color: rgba(150, 150, 200, 120);")
        layout.addWidget(separator)
        
        self.toggle_daily_mode()
    
    def toggle_daily_mode(self):
        """Toggle between full date/time and daily time-only mode"""
        is_daily = self.daily_checkbox.isChecked()
        
        self.date_time_edit.setVisible(not is_daily)
        self.time_only_edit.setVisible(is_daily)
        
        if is_daily:
            self.time_only_edit.setTime(self.date_time_edit.time())
    
    def get_data(self):
        """Return the schedule data as a dictionary"""
        is_daily = self.daily_checkbox.isChecked()
        
        if is_daily:
            return {
                "execution_datetime": self.time_only_edit.time().toString("HH:mm:ss"),
                "repeat_interval": self.repeat_interval_spin.value() if self.repeat_interval_spin.value() > 0 else None,
                "execution_count": self.execution_count_spin.value(),
                "is_daily": True
            }
        else:
            return {
                "execution_datetime": self.date_time_edit.dateTime().toString("yyyy-MM-dd HH:mm:ss"),
                "repeat_interval": self.repeat_interval_spin.value() if self.repeat_interval_spin.value() > 0 else None,
                "execution_count": self.execution_count_spin.value(),
                "is_daily": False
            }

class WorkflowWindow(QMainWindow):
    def __init__(self, workflow, workflow_controller, parent=None):
        super().__init__(parent)
        self.workflow = workflow
        self.workflow_controller = workflow_controller
        self.automation_service = AutomationService()
        self.scheduling_service = SchedulingService()
        self.threadpool = QThreadPool()
        self.parent_window = parent
        self.setWindowTitle(f"Workflow: {self.workflow.name}")
        self.setGeometry(200, 200, 800, 600)
        self.schedule_widgets = []
        self.init_ui()
        
        if hasattr(parent, 'settings') and hasattr(parent.settings, 'theme'):
            self.apply_theme(parent.settings.theme)
        else:
            self.apply_theme("Default")

    def init_ui(self):
        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)
        
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("Name:"))
        self.name_edit = QLineEdit(self.workflow.name)
        name_layout.addWidget(self.name_edit)
        main_layout.addLayout(name_layout)

        actions_group = QGroupBox("Actions")
        actions_layout = QVBoxLayout(actions_group)
        
        self.actions_tree = QTreeWidget()
        self.actions_tree.setHeaderLabels(["Action Type", "Parameters"])
        self.actions_tree.itemDoubleClicked.connect(self.edit_action)
        actions_layout.addWidget(self.actions_tree)

        action_btn_layout = QHBoxLayout()
        add_btn = QPushButton("Add Action")
        add_btn.clicked.connect(self.add_action)
        action_btn_layout.addWidget(add_btn)
        edit_btn = QPushButton("Edit Action")
        edit_btn.clicked.connect(self.edit_action)
        action_btn_layout.addWidget(edit_btn)
        delete_btn = QPushButton("Delete Action")
        delete_btn.clicked.connect(self.delete_action)
        action_btn_layout.addWidget(delete_btn)
        actions_layout.addLayout(action_btn_layout)
        
        main_layout.addWidget(actions_group)

        schedule_group = QGroupBox("Execution Schedule")
        schedule_layout = QVBoxLayout(schedule_group)
        
        self.schedule_scroll = QScrollArea()
        self.schedule_scroll.setWidgetResizable(True)
        self.schedule_container = QWidget()
        self.schedule_container_layout = QVBoxLayout(self.schedule_container)
        self.schedule_scroll.setWidget(self.schedule_container)
        schedule_layout.addWidget(self.schedule_scroll)
        
        schedule_btn_layout = QHBoxLayout()
        add_schedule_btn = QPushButton("Add Execution Time")
        add_schedule_btn.clicked.connect(self.add_schedule)
        schedule_btn_layout.addWidget(add_schedule_btn)
        
        clear_schedules_btn = QPushButton("Clear All Schedules")
        clear_schedules_btn.clicked.connect(self.clear_schedules)
        schedule_btn_layout.addWidget(clear_schedules_btn)
        schedule_layout.addLayout(schedule_btn_layout)
        
        main_layout.addWidget(schedule_group)
        
        self.load_schedules()

        control_btn_layout = QHBoxLayout()
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.save_workflow)
        control_btn_layout.addWidget(save_btn)
        start_btn = QPushButton("Start")
        start_btn.clicked.connect(self.start_workflow)
        control_btn_layout.addWidget(start_btn)
        stop_btn = QPushButton("Stop")
        stop_btn.clicked.connect(self.stop_workflow)
        control_btn_layout.addWidget(stop_btn)
        main_layout.addLayout(control_btn_layout)

        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")

        self.setCentralWidget(main_widget)
        self.load_actions()

    def apply_theme(self, theme="Default"):
        self.setStyleSheet(load_stylesheet(theme))

    def load_actions(self):
        self.actions_tree.clear()
        for action in self.workflow.actions:
            item = QTreeWidgetItem([action.action_type.capitalize(), str(action.params)])
            self.actions_tree.addTopLevelItem(item)
    
    def load_schedules(self):
        self.clear_schedules(confirm=False)
        
        if hasattr(self.workflow, 'scheduled_executions') and self.workflow.scheduled_executions:
            for scheduled_execution in self.workflow.scheduled_executions:
                is_daily = False
                exec_datetime = scheduled_execution.execution_datetime
                if isinstance(exec_datetime, str) and len(exec_datetime) <= 8 and exec_datetime.count(":") == 2:
                    is_daily = True
                
                self.add_schedule_widget(
                    scheduled_execution.execution_datetime,
                    scheduled_execution.repeat_interval,
                    scheduled_execution.execution_count,
                    is_daily
                )
        elif self.workflow.start_time:
            is_daily = False
            if self.workflow.start_time and len(self.workflow.start_time) <= 8 and self.workflow.start_time.count(":") == 2:
                is_daily = True
                
            self.add_schedule_widget(
                self.workflow.start_time,
                self.workflow.repeat_interval,
                self.workflow.execution_count,
                is_daily
            )
    
    def add_schedule(self):
        self.add_schedule_widget()
        self.status_bar.showMessage("Added new execution time")
    
    def add_schedule_widget(self, datetime_val=None, repeat_interval=None, execution_count=0, is_daily=False):
        container = QWidget()
        container_layout = QHBoxLayout(container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        
        schedule_widget = ScheduleWidget(
            self, datetime_val, repeat_interval, execution_count, is_daily
        )
        container_layout.addWidget(schedule_widget, 1)
        
        remove_btn = QPushButton("✕")
        remove_btn.setFixedWidth(30)
        remove_btn.setToolTip("Remove this execution time")
        remove_btn.clicked.connect(lambda: self.remove_schedule(container))
        container_layout.addWidget(remove_btn, 0)
        
        self.schedule_container_layout.addWidget(container)
        self.schedule_widgets.append((container, schedule_widget))
    
    def remove_schedule(self, container):
        for i, (cont, widget) in enumerate(self.schedule_widgets):
            if cont == container:
                self.schedule_container_layout.removeWidget(container)
                container.deleteLater()
                self.schedule_widgets.pop(i)
                self.status_bar.showMessage("Removed execution time")
                break
    
    def clear_schedules(self, confirm=True):
        if confirm:
            reply = QMessageBox.question(
                self, "Confirm", "Clear all scheduled executions?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply != QMessageBox.StandardButton.Yes:
                return
        
        for container, _ in self.schedule_widgets:
            self.schedule_container_layout.removeWidget(container)
            container.deleteLater()
        
        self.schedule_widgets.clear()
        if confirm:
            self.status_bar.showMessage("Cleared all execution times")

    def add_action(self):
        dialog = ActionDialog(self)
        if hasattr(self, 'parent_window') and hasattr(self.parent_window, 'settings'):
            dialog.setStyleSheet(load_stylesheet(self.parent_window.settings.theme))
        
        if dialog.exec():
            action = dialog.get_action()
            self.workflow.add_action(action)
            self.load_actions()
            self.status_bar.showMessage("Action added")

    def edit_action(self, item=None):
        if not item:
            item = self.actions_tree.currentItem()
        if item:
            index = self.actions_tree.indexOfTopLevelItem(item)
            action = self.workflow.actions[index]
            dialog = ActionDialog(self)
            
            if hasattr(self, 'parent_window') and hasattr(self.parent_window, 'settings'):
                dialog.setStyleSheet(load_stylesheet(self.parent_window.settings.theme))
            
            action_type = action.action_type
            found = False
            for i in range(dialog.type_combo.count()):
                combo_text = dialog.type_combo.itemText(i)
                if combo_text.lower() == action_type.lower():
                    dialog.type_combo.setCurrentIndex(i)
                    found = True
                    break
                    
            if not found:
                print(f"Warning: Could not find action type '{action_type}' in combo box")
            
            dialog.update_params()
            
            params = action.params
            action_type_lower = action_type.lower()
            
            if action_type_lower == "click":
                dialog.click_x.setText(str(params.get("x", "")))
                dialog.click_y.setText(str(params.get("y", "")))
                dialog.click_clicks.setText(str(params.get("clicks", "1")))
            elif action_type_lower == "hold":
                dialog.hold_x.setText(str(params.get("x", "")))
                dialog.hold_y.setText(str(params.get("y", "")))
                dialog.hold_duration.setText(str(params.get("duration", "1")))
            elif action_type_lower == "scroll":
                dialog.scroll_x.setText(str(params.get("x", "")))
                dialog.scroll_y.setText(str(params.get("y", "")))
                dialog.scroll_amount.setText(str(params.get("amount", "10")))
            elif action_type_lower == "drag":
                dialog.drag_x1.setText(str(params.get("x1", "")))
                dialog.drag_y1.setText(str(params.get("y1", "")))
                dialog.drag_x2.setText(str(params.get("x2", "")))
                dialog.drag_y2.setText(str(params.get("y2", "")))
            elif action_type_lower == "keyboard":
                dialog.keyboard_keys.setText(params.get("keys", ""))
            elif action_type_lower == "script":
                dialog.script_command.setText(params.get("command", ""))
            elif action_type_lower == "wait for":
                dialog.wait_time.setText(str(params.get("time", "1")))
            elif action_type_lower == "press key":
                dialog.press_key.setText(params.get("key", ""))
            elif action_type_lower == "move mouse to":
                dialog.move_x.setText(str(params.get("x", "")))
                dialog.move_y.setText(str(params.get("y", "")))
                
            if dialog.exec():
                new_action = dialog.get_action()
                self.workflow.actions[index] = new_action
                self.load_actions()
                self.status_bar.showMessage("Action edited")
        else:
            QMessageBox.warning(self, "Warning", "Select an action to edit.")
            self.status_bar.showMessage("No action selected")

    def delete_action(self):
        selected = self.actions_tree.currentItem()
        if selected:
            index = self.actions_tree.indexOfTopLevelItem(selected)
            self.workflow.remove_action(index)
            self.load_actions()
            self.status_bar.showMessage("Action deleted")
        else:
            QMessageBox.warning(self, "Warning", "Select an action to edit.")
            self.status_bar.showMessage("No action selected")

    def save_workflow(self):
        self.workflow.name = self.name_edit.text()
        
        self.workflow.scheduled_executions = []
        
        for _, schedule_widget in self.schedule_widgets:
            schedule_data = schedule_widget.get_data()
            self.workflow.add_scheduled_execution(
                execution_datetime=schedule_data["execution_datetime"],
                repeat_interval=schedule_data["repeat_interval"],
                execution_count=schedule_data["execution_count"]
            )
        
        filename, ok = QInputDialog.getText(self, "Save Workflow", "Enter filename:", text=self.workflow.name)
        if ok and filename:
            try:
                self.workflow_controller.save_workflow(self.workflow, filename)
                QMessageBox.information(self, "Success", "Workflow saved.")
                self.status_bar.showMessage("Workflow saved")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save workflow: {e}")
                self.status_bar.showMessage(f"Error saving workflow: {e}")

    def start_workflow(self):
        self.workflow.scheduled_executions = []
        for _, schedule_widget in self.schedule_widgets:
            schedule_data = schedule_widget.get_data()
            self.workflow.add_scheduled_execution(
                execution_datetime=schedule_data["execution_datetime"],
                repeat_interval=schedule_data["repeat_interval"],
                execution_count=schedule_data["execution_count"]
            )
        
        QMessageBox.information(
            self, 
            "Workflow Scheduled",
            "Your workflow has been scheduled. Please note:\n\n"
            "1. The application must be running for workflows to execute.\n"
            "2. You can minimize the application or enable 'Run in background' in settings.\n"
            "3. Daily schedules will execute every day at the specified time as long as the app is running.\n"
            "4. Consider adding this application to your startup programs if you want workflows to run automatically."
        )
            
        self.scheduling_service.schedule_workflow(self.workflow, self.run_workflow)
        self.scheduling_service.start_scheduler()
        self.status_bar.showMessage("Workflow started")

    def run_workflow(self):
        try:
            self.automation_service.execute_workflow(self.workflow)
            self.status_bar.showMessage("Workflow executed")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Workflow execution failed: {e}")
            self.status_bar.showMessage(f"Error: {e}")

    def stop_workflow(self):
        self.scheduling_service.clear_jobs_for_workflow(self.workflow.name)
        self.status_bar.showMessage("Workflow stopped")
