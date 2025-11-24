import json
from .action import Action
from datetime import datetime

class ScheduledExecution:
    def __init__(self, execution_datetime=None, repeat_interval=None, execution_count=0):
        self.execution_datetime = execution_datetime
        self.repeat_interval = repeat_interval
        self.execution_count = execution_count
    
    def to_dict(self):
        execution_datetime = self.execution_datetime
        if isinstance(execution_datetime, datetime):
            execution_datetime = execution_datetime.isoformat()
            
        return {
            "execution_datetime": execution_datetime,
            "repeat_interval": self.repeat_interval,
            "execution_count": self.execution_count
        }
    
    @classmethod
    def from_dict(cls, data):
        execution_datetime = data.get("execution_datetime")
        if execution_datetime and isinstance(execution_datetime, str):
            try:
                execution_datetime = datetime.fromisoformat(execution_datetime)
            except ValueError:
                pass
                
        return cls(
            execution_datetime=execution_datetime,
            repeat_interval=data.get("repeat_interval"),
            execution_count=data.get("execution_count", 0)
        )

class Workflow:
    def __init__(self, name="New Workflow"):
        self.name = name
        self.actions = []
        self.start_time = None
        self.repeat_interval = None
        self.execution_count = 0
        self.scheduled_executions = []

    def add_action(self, action):
        self.actions.append(action)

    def remove_action(self, index):
        if 0 <= index < len(self.actions):
            del self.actions[index]
    
    def add_scheduled_execution(self, execution_datetime=None, repeat_interval=None, execution_count=0):
        """Add a new scheduled execution time for this workflow"""
        self.scheduled_executions.append(
            ScheduledExecution(execution_datetime, repeat_interval, execution_count)
        )
    
    def remove_scheduled_execution(self, index):
        """Remove a scheduled execution by index"""
        if 0 <= index < len(self.scheduled_executions):
            del self.scheduled_executions[index]

    def to_dict(self):
        if not self.scheduled_executions and self.start_time:
            self.add_scheduled_execution(
                execution_datetime=self.start_time,
                repeat_interval=self.repeat_interval,
                execution_count=self.execution_count
            )
            
        return {
            "name": self.name,
            "actions": [action.to_dict() for action in self.actions],
            "start_time": self.start_time,
            "repeat_interval": self.repeat_interval,
            "execution_count": self.execution_count,
            "scheduled_executions": [execution.to_dict() for execution in self.scheduled_executions]
        }

    @classmethod
    def from_dict(cls, data):
        workflow = cls(data["name"])
        workflow.actions = [Action.from_dict(action_data) for action_data in data["actions"]]
        
        workflow.start_time = data.get("start_time")
        workflow.repeat_interval = data.get("repeat_interval")
        workflow.execution_count = data.get("execution_count", 0)
        
        if "scheduled_executions" in data:
            workflow.scheduled_executions = [
                ScheduledExecution.from_dict(execution_data) 
                for execution_data in data["scheduled_executions"]
            ]
        elif workflow.start_time and not workflow.scheduled_executions:
            workflow.add_scheduled_execution(
                execution_datetime=workflow.start_time,
                repeat_interval=workflow.repeat_interval,
                execution_count=workflow.execution_count
            )
            
        return workflow

    def save(self, filepath):
        with open(filepath, 'w') as f:
            json.dump(self.to_dict(), f)

    @classmethod
    def load(cls, filepath):
        with open(filepath, 'r') as f:
            return cls.from_dict(json.load(f))